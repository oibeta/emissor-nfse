"""
O comando único da emissão. O agente usa só ele; ninguém edita a fila na mão.

    python codigo/nfse.py certificado              validade do .pfx e da senha (sem internet)
    python codigo/nfse.py conexao [restrita|producao]   testa o caminho até a SEFIN
    python codigo/nfse.py adicionar <pedido.json>  põe um pedido na fila, com as conferências
    python codigo/nfse.py listar                   mostra a fila
    python codigo/nfse.py aprovar <id> <ambiente>  registra o ok da pessoa (ambiente: restrita|producao)
    python codigo/nfse.py recusar <id>             tira o pedido do caminho
    python codigo/nfse.py emitir <id>              emite um pedido aprovado
    python codigo/nfse.py verificar <id>           pergunta à SEFIN se a DPS do pedido virou nota
    python codigo/nfse.py respondido <id> <como>   anota a resposta ao cliente ("enviado" ou "rascunho")

A fila é o arquivo fila.csv na raiz do projeto: separado por ponto e vírgula,
em UTF-8, para abrir direto no Excel. Feche o Excel antes de emitir: com o
arquivo aberto, o Windows não deixa gravar.

NUNCA EMITE DUAS VEZES
----------------------
1. Só emite linha com status "Aprovado".
2. Grava "Emitindo" e o número da DPS ANTES de enviar. Se a rodada morrer no
   meio, a linha não volta sozinha para "Aprovado".
3. Se a linha já tem número de DPS (tentativa anterior), pergunta à SEFIN se
   essa DPS virou nota antes de qualquer coisa.
4. O ambiente aprovado tem que ser o mesmo do empresa.json. Diferente ou
   vazio: recusa. Um ok dado para nota real nunca vira nota de teste, nem o
   contrário.
"""
from __future__ import annotations

import base64
import csv
import dataclasses
import gzip
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from dps import (  # noqa: E402
    BRASILIA, Endereco, Nota, Prestador, Servico, Tomador, id_dps, monta_dps, so_digitos, vencimento,
)

RAIZ = AQUI.parent
EMPRESA = RAIZ / "empresa.json"
FILA = RAIZ / "fila.csv"
NOTAS = RAIZ / "notas"

COLUNAS = [
    "id_pedido", "status", "ambiente", "recebido_em", "remetente", "assunto",
    "tomador_cnpj", "tomador_nome", "tomador_cep", "tomador_numero", "tomador_complemento",
    "valor", "competencia", "descricao", "prazo_dias", "vencimento",
    "alertas", "aprovado_em", "n_dps", "numero_nfse", "chave_acesso", "emitida_em",
    "arquivo_xml", "arquivo_pdf", "resposta",
]
OBRIGATORIOS = ["id_pedido", "tomador_cnpj", "tomador_nome", "tomador_cep", "tomador_numero",
                "valor", "competencia", "descricao"]


class Recusa(Exception):
    """O pedido não pode seguir. A mensagem diz por quê e o que fazer."""


# --------------------------------------------------------------------------
# Fila
# --------------------------------------------------------------------------

def ler_fila() -> list[dict]:
    if not FILA.exists():
        return []
    with FILA.open(encoding="utf-8-sig", newline="") as f:
        return [{c: (linha.get(c) or "") for c in COLUNAS} for linha in csv.DictReader(f, delimiter=";")]


def gravar_fila(linhas: list[dict]) -> None:
    try:
        with FILA.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUNAS, delimiter=";")
            w.writeheader()
            w.writerows(linhas)
    except PermissionError:
        raise Recusa("não consegui gravar o fila.csv: feche o arquivo no Excel e rode de novo") from None


def achar(linhas: list[dict], id_pedido: str) -> dict:
    for linha in linhas:
        if linha["id_pedido"] == id_pedido:
            return linha
    raise Recusa(f"o pedido {id_pedido!r} não está na fila")


def empresa() -> dict:
    if not EMPRESA.exists():
        raise Recusa("falta o empresa.json na raiz do projeto (passo dos dados da empresa)")
    return json.loads(EMPRESA.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Conferências
# --------------------------------------------------------------------------

def _dv(digitos: str, pesos: list[int]) -> int:
    r = sum(int(d) * p for d, p in zip(digitos, pesos)) % 11
    return 0 if r < 2 else 11 - r


def documento_valido(doc: str) -> bool:
    """Dígito verificador de CNPJ (14) ou CPF (11)."""
    d = so_digitos(doc)
    if len(d) == 14 and len(set(d)) > 1:
        p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        return _dv(d[:12], p1) == int(d[12]) and _dv(d[:13], [6] + p1) == int(d[13])
    if len(d) == 11 and len(set(d)) > 1:
        return (_dv(d[:9], list(range(10, 1, -1))) == int(d[9])
                and _dv(d[:10], list(range(11, 1, -1))) == int(d[10]))
    return False


def normaliza_valor(s: str) -> str:
    """'1.500,00' ou '1500.00' -> '1500.00'."""
    s = str(s).strip().replace("R$", "").strip()
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        v = Decimal(s).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise Recusa(f"valor ilegível: {s!r}") from None
    return str(v)


def alertas_do_pedido(p: dict, emp: dict, fila: list[dict]) -> list[str]:
    a = [f"falta {c}" for c in OBRIGATORIOS if not str(p.get(c, "")).strip()]
    if p.get("tomador_cnpj"):
        if not documento_valido(p["tomador_cnpj"]):
            a.append("CNPJ/CPF do tomador não passa no dígito verificador")
        if so_digitos(p["tomador_cnpj"]) == so_digitos(emp["cnpj"]):
            a.append("o CNPJ do tomador é o da própria empresa: a leitura pegou o bloco errado")
    if p.get("valor"):
        v = Decimal(p["valor"])
        if v <= 0:
            a.append("valor zero ou negativo")
        elif v >= Decimal("10000000"):
            a.append("valor com mais de 7 dígitos: confira os centavos")
    if p.get("competencia"):
        try:
            if date.fromisoformat(p["competencia"]) > date.today():
                a.append("competência no futuro")
        except ValueError:
            a.append("competência fora do formato aaaa-mm-dd")
    if not (p.get("prazo_dias") or p.get("vencimento")):
        a.append("sem prazo_dias nem vencimento")
    if any(x["id_pedido"] == p.get("id_pedido") for x in fila):
        a.append("pedido repetido: já está na fila")
    return a


# --------------------------------------------------------------------------
# Peças da emissão
# --------------------------------------------------------------------------

def consulta_cep(cep: str) -> dict:
    """Logradouro, bairro e código IBGE pelo ViaCEP. Precisa de internet."""
    cep = so_digitos(cep)
    try:
        with urllib.request.urlopen(f"https://viacep.com.br/ws/{cep}/json/", timeout=15) as r:
            d = json.load(r)
    except (OSError, ValueError) as e:
        raise Recusa(f"não consegui consultar o CEP {cep}: {e}") from None
    if d.get("erro") or not d.get("ibge"):
        raise Recusa(f"o CEP {cep} não existe no ViaCEP: confira o pedido")
    return {"cep": cep, "cmun": d["ibge"], "logradouro": d.get("logradouro") or "-", "bairro": d.get("bairro") or "-"}


def sem_acento(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[^A-Za-z0-9 ]+", "", s).strip()


def monta_nota(linha: dict, emp: dict, hoje: date) -> Nota:
    if linha["vencimento"]:
        venc = date.fromisoformat(linha["vencimento"])
    else:
        venc = vencimento(hoje, int(linha["prazo_dias"]))  # calculado agora, na emissão
    descricao = linha["descricao"].replace("{vencimento}", f"{venc:%d/%m/%Y}")
    if emp.get("texto_fixo_descricao"):
        descricao += "\n" + emp["texto_fixo_descricao"]
    return Nota(
        n_dps=0,
        competencia=date.fromisoformat(linha["competencia"]),
        valor=Decimal(linha["valor"]),
        prestador=Prestador(
            cnpj=emp["cnpj"], cloc_emi=emp["cloc_emi"], serie=emp.get("serie", "00001"),
            op_simp_nac=emp.get("op_simp_nac", "3"), reg_ap_trib_sn=emp.get("reg_ap_trib_sn", "1"),
            reg_esp_trib=emp.get("reg_esp_trib", "0"),
        ),
        tomador=Tomador(cnpj_cpf=linha["tomador_cnpj"], nome=linha["tomador_nome"]),
        servico=Servico(ctrib_nac=emp["ctrib_nac"], ctrib_mun=emp.get("ctrib_mun", ""),
                        cloc_prestacao=emp["cloc_prestacao"], descricao=descricao),
        aliq_simples_nacional=emp["aliq_simples_nacional"],
        tp_amb="1" if emp["ambiente"] == "producao" else "2",
    )


def _codigos(e) -> set[str]:
    corpo = e.corpo if isinstance(e.corpo, dict) else {}
    return {str(x.get("codigo") or x.get("Codigo") or "") for x in corpo.get("erros", []) if isinstance(x, dict)}


def _abrir_sefin(emp: dict, ambiente: str):
    from assinar import Certificado
    from sefin import Sefin
    from senha import obter
    cert = Certificado(emp["certificado_pfx"], obter())
    return cert, Sefin(cert, ambiente)


# --------------------------------------------------------------------------
# Comandos
# --------------------------------------------------------------------------

def cmd_adicionar(caminho: str) -> None:
    emp, fila = empresa(), ler_fila()
    p = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if p.get("valor"):
        p["valor"] = normaliza_valor(p["valor"])
    alertas = alertas_do_pedido(p, emp, fila)
    linha = {c: str(p.get(c, "") or "") for c in COLUNAS}
    linha.update(status="Aguardando aprovação", ambiente="", alertas=" | ".join(alertas),
                 recebido_em=linha["recebido_em"] or datetime.now(BRASILIA).isoformat(timespec="minutes"))
    if "pedido repetido: já está na fila" in alertas:
        print(f"NÃO ADICIONADO: o pedido {linha['id_pedido']} já está na fila.")
        return
    fila.append(linha)
    gravar_fila(fila)
    print(f"Adicionado: {linha['id_pedido']} | {linha['tomador_nome']} | R$ {linha['valor']}"
          + (f"\nALERTAS: {linha['alertas']}" if alertas else "\nsem alertas"))


def cmd_listar() -> None:
    for x in ler_fila():
        print(f"{x['id_pedido']:<16} {x['status']:<22} R$ {x['valor']:>12}  {x['tomador_nome'][:40]}"
              + (f"  nº {x['numero_nfse']}" if x["numero_nfse"] else "")
              + (f"  ⚠ {x['alertas']}" if x["alertas"] else ""))


def cmd_aprovar(id_pedido: str, ambiente: str) -> None:
    if ambiente not in ("restrita", "producao"):
        raise Recusa("ambiente tem que ser 'restrita' ou 'producao'")
    fila = ler_fila()
    linha = achar(fila, id_pedido)
    if linha["status"] not in ("Aguardando aprovação", "Aprovado", "Erro"):
        raise Recusa(f"o pedido está como {linha['status']!r}; só se aprova o que aguarda aprovação ou deu erro")
    linha.update(status="Aprovado", ambiente=ambiente, aprovado_em=datetime.now(BRASILIA).isoformat(timespec="minutes"))
    gravar_fila(fila)
    print(f"Aprovado: {id_pedido} em {ambiente}")


def cmd_recusar(id_pedido: str) -> None:
    fila = ler_fila()
    linha = achar(fila, id_pedido)
    if linha["status"] in ("Emitindo", "Emitida"):
        raise Recusa(f"o pedido está como {linha['status']!r}: nota emitida se cancela no portal, não aqui")
    linha["status"] = "Recusado"
    gravar_fila(fila)
    print(f"Recusado: {id_pedido}")


def cmd_emitir(id_pedido: str, *, sefin=None, cert=None, cep=consulta_cep, gerar_pdf=None) -> dict:
    """Os parâmetros com padrão existem para o teste trocar rede e PDF por dublês."""
    from assinar import assinar_dps, corpo_requisicao
    from sefin import ErroSefin, proximo_numero_dps
    from validar import exige_valido

    emp, fila = empresa(), ler_fila()
    linha = achar(fila, id_pedido)

    if linha["status"] == "Emitindo":
        raise Recusa("a última tentativa parou no meio. Rode  nfse.py verificar " + id_pedido + "  antes de qualquer coisa")
    if linha["status"] != "Aprovado":
        raise Recusa(f"o pedido está como {linha['status']!r}; só se emite o que está 'Aprovado'")
    if linha["ambiente"] != emp["ambiente"]:
        raise Recusa(f"o ok foi dado para {linha['ambiente'] or '(nenhum ambiente)'!r} e o empresa.json está em "
                     f"{emp['ambiente']!r}. Peça a aprovação de novo, dizendo o ambiente")
    if linha["alertas"]:
        print(f"(alertas aprovados pela pessoa: {linha['alertas']})")

    if sefin is None:
        cert, sefin = _abrir_sefin(emp, emp["ambiente"])

    hoje = datetime.now(BRASILIA).date()
    nota = monta_nota(linha, emp, hoje)

    # Tentativa anterior com número de DPS: a SEFIN diz se ela virou nota.
    if linha["n_dps"] and sefin.dps_ja_existe(id_dps(dataclasses.replace(nota, n_dps=int(linha["n_dps"])))):
        linha["status"] = "Erro"
        linha["alertas"] = "A DPS DA TENTATIVA ANTERIOR JÁ VIROU NOTA. NÃO REENVIAR. Rode verificar."
        gravar_fila(fila)
        raise Recusa(linha["alertas"])

    nota.tomador.endereco = Endereco(numero=linha["tomador_numero"], complemento=linha["tomador_complemento"],
                                     **cep(linha["tomador_cep"]))
    usados = [int(x["n_dps"]) for x in fila if x["n_dps"].isdigit()]
    inicio = max(usados + [int(emp.get("ultimo_n_dps_antes_da_fila", 0))]) + 1
    nota.n_dps = proximo_numero_dps(sefin, lambda n: id_dps(dataclasses.replace(nota, n_dps=n)), inicio)

    def prepara() -> dict:
        xml = monta_dps(nota)
        exige_valido(xml)
        return corpo_requisicao(assinar_dps(xml, cert))

    corpo = prepara()
    linha.update(status="Emitindo", n_dps=str(nota.n_dps))
    gravar_fila(fila)  # trava ANTES de enviar

    try:
        try:
            resposta = sefin.emitir(corpo)
        except ErroSefin as e:
            hora = (e.corpo or {}).get("dataHoraProcessamento") if isinstance(e.corpo, dict) else None
            if "E0008" not in _codigos(e) or not hora:
                raise
            # relógio adiantado: refaz com a hora do servidor e tenta uma vez
            servidor = datetime.fromisoformat(hora)
            if servidor.tzinfo is None:  # sem fuso, a SEFIN fala em horário de Brasília
                servidor = servidor.replace(tzinfo=BRASILIA)
            nota.dh_emi = servidor.astimezone(BRASILIA) - timedelta(seconds=30)
            resposta = sefin.emitir(prepara())
    except ErroSefin as e:
        linha.update(status="Erro", alertas=f"SEFIN recusou: {e} {e.corpo or ''}"[:3000])
        gravar_fila(fila)
        raise Recusa(linha["alertas"] + "\n(códigos em docs/oficial/codigos-rejeicao.md)") from None
    except Exception as e:
        # Não dá para saber se a SEFIN recebeu: fica em Emitindo, e verificar resolve.
        raise Recusa(f"a conexão caiu no envio ({e}). A linha ficou em 'Emitindo'. Rode verificar {id_pedido}") from None

    chave = resposta.get("chaveAcesso") or resposta.get("chave") or ""
    xml_nota = gzip.decompress(base64.b64decode(resposta["nfseXmlGZipB64"])) if resposta.get("nfseXmlGZipB64") else b""
    m = re.search(rb"<nNFSe>\s*(\d+)\s*</nNFSe>", xml_nota)
    numero = m.group(1).decode() if m else ""

    NOTAS.mkdir(exist_ok=True)
    base = f"NFSe-{int(numero or 0):05d}_{sem_acento(linha['tomador_nome'])[:40]}"
    if emp["ambiente"] != "producao":
        base += "_TESTE"
    (NOTAS / f"{base}.xml").write_bytes(xml_nota)  # o XML é o documento fiscal: grava antes do PDF
    linha.update(status="Emitida", chave_acesso=chave, numero_nfse=numero,
                 emitida_em=datetime.now(BRASILIA).isoformat(timespec="minutes"),
                 arquivo_xml=f"notas/{base}.xml")
    gravar_fila(fila)
    print(f"EMITIDA: nº {numero} | chave {chave}")

    try:
        if gerar_pdf is None:
            from danfse import gerar as gerar_pdf
        (NOTAS / f"{base}.pdf").write_bytes(gerar_pdf(xml_nota))
        linha["arquivo_pdf"] = f"notas/{base}.pdf"
        print(f"PDF: notas/{base}.pdf")
    except Exception as e:  # o PDF falhar não desfaz a nota
        linha["alertas"] = (linha["alertas"] + " | " if linha["alertas"] else "") + \
            f"PDF não gerado ({e}); baixe em https://www.nfse.gov.br/consultapublica pela chave"
        print("A NOTA FOI EMITIDA, mas o PDF falhou: " + str(e))
    gravar_fila(fila)
    return linha


def cmd_verificar(id_pedido: str) -> None:
    emp, fila = empresa(), ler_fila()
    linha = achar(fila, id_pedido)
    if not linha["n_dps"]:
        print("Esse pedido nunca chegou a ser enviado (sem número de DPS). Pode aprovar e emitir.")
        return
    _, sefin = _abrir_sefin(emp, emp["ambiente"])
    nota = monta_nota(linha, emp, datetime.now(BRASILIA).date())
    i = id_dps(dataclasses.replace(nota, n_dps=int(linha["n_dps"])))
    r = sefin.nfse_da_dps(i)
    if r is None:
        print(f"A DPS {i} NÃO virou nota. Pode marcar como Erro, aprovar de novo e emitir.")
        if linha["status"] == "Emitindo":
            linha["status"] = "Erro"
            gravar_fila(fila)
    else:
        print(f"A DPS {i} JÁ VIROU NOTA. Não reenvie. Resposta da SEFIN:\n{json.dumps(r, ensure_ascii=False)[:800]}")


def cmd_respondido(id_pedido: str, como: str) -> None:
    fila = ler_fila()
    linha = achar(fila, id_pedido)
    if linha["status"] != "Emitida":
        raise Recusa("só se responde pedido com nota emitida")
    linha["resposta"] = f"{como} em {datetime.now(BRASILIA):%d/%m/%Y %H:%M}"
    gravar_fila(fila)
    print(f"Anotado: {id_pedido} {linha['resposta']}")


def cmd_certificado() -> None:
    from assinar import Certificado
    from senha import SenhaAusente, obter
    emp = empresa()
    try:
        cert = Certificado(emp["certificado_pfx"], obter())
    except SenhaAusente as e:
        raise Recusa(str(e)) from None
    dias = cert.dias_para_vencer()
    print(f"Certificado ok: {cert.titular}\nVence em {cert.validade[1]:%d/%m/%Y} ({dias} dias)")
    if dias < 45:
        print("ATENÇÃO: renove o certificado. Vencido, a emissão para.")


def cmd_conexao(ambiente: str = "restrita") -> None:
    _, sefin = _abrir_sefin(empresa(), ambiente)
    r = sefin.diagnostico()
    print(json.dumps(r, ensure_ascii=False, indent=2))
    if r.get("mtls") != "ok":
        raise Recusa("a conexão com a SEFIN não fechou. Veja a mensagem acima (internet liberada? certificado certo?)")


def main(argv: list[str]) -> int:
    comandos = {
        "certificado": (cmd_certificado, 0), "conexao": (cmd_conexao, (0, 1)), "adicionar": (cmd_adicionar, 1),
        "listar": (cmd_listar, 0), "aprovar": (cmd_aprovar, 2), "recusar": (cmd_recusar, 1),
        "emitir": (cmd_emitir, 1), "verificar": (cmd_verificar, 1), "respondido": (cmd_respondido, 2),
    }
    if not argv or argv[0] not in comandos:
        print(__doc__)
        return 2
    func, n = comandos[argv[0]]
    args = argv[1:]
    if len(args) not in (n if isinstance(n, tuple) else (n,)):
        print(__doc__)
        return 2
    try:
        func(*args)
    except Recusa as e:
        print(f"PAROU: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
