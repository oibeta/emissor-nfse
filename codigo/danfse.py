"""
Gera o DANFSe (PDF da NFS-e) a partir do XML, no modelo "DANFSe v2.0".

    python danfse.py --modelo <danfse do portal.pdf>   (uma vez: cria o molde)
    python danfse.py <nota.xml> [saida.pdf]

Dependências: pip install pymupdf segno lxml

POR QUE EXISTE
--------------
O governo suspendeu a API do PDF em 03/08/2026 (NT 008/2026 v1.02, na pasta
docs/oficial/). Desde então quem emite gera o PDF. O portal ainda gera,
mas tem captcha e avisa que corta robôs.

ANTES DO PRIMEIRO USO: CRIE O SEU MOLDE
---------------------------------------
O molde (danfse_modelo.pdf) não vem no pacote, porque ele sai de uma nota de
verdade. Baixe da consulta pública (https://www.nfse.gov.br/consultapublica) o
PDF de uma nota sua emitida pelo portal, no modelo DANFSe v2.0, e rode:

    python danfse.py --modelo <esse pdf>

O script apaga os valores e o QR Code e guarda só as linhas, os rótulos, o
sombreamento e o logo, exatamente no modelo oficial. Abra o molde e confira que
nenhum dado da nota sobrou nele.

COMO FUNCIONA
-------------
Este script escreve os valores do XML nas mesmas posições que o portal usa, e
desenha o QR Code. Os textos seguem o que o portal escreve, inclusive as manias
dele (IBGE como "35.50308", "R$ 0,00" no total com IBS/CBS), para o PDF sair
igual ao do portal. Compare o primeiro PDF gerado com o do portal, lado a lado.

O QUE NÃO COBRE (e recusa, em vez de gerar PDF errado)
------------------------------------------------------
Destinatário, intermediário, grupo IBS/CBS preenchido, retenções e
informações complementares próprias. Se a sua nota tiver algum desses, o erro
diz o que falta; amplie o script pela NT 008, ou use o PDF do portal.
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pymupdf
import segno
from lxml import etree

AQUI = Path(__file__).parent
MODELO = AQUI / "danfse_modelo.pdf"
NS = {"n": "http://www.sped.fazenda.gov.br/nfse"}
QR_URL = "https://www.nfse.gov.br/ConsultaPublica/?tpc=1&chave="
QR_RECT = pymupdf.Rect(491.99, 44.76, 536.99, 89.76)  # 1,59 cm; a NT pede no mínimo 1,52 cm
FONTE = "helv"  # o portal usa Microsoft Sans Serif, que não roda no Linux; a Helvetica tem a mesma métrica da Arial

# Colunas e linhas de base do portal (pontos, A4), lidas de um DANFSe v2.0 do portal.
C1, C2, C3, C4 = 11.91, 156.47, 301.04, 445.61
# Largura: até a borda do quadro (586,8) menos a margem; a Helvetica é um pouco mais larga que a fonte do portal.
DESCRICAO_Y, DESCRICAO_PASSO, DESCRICAO_LARGURA, DESCRICAO_LINHAS = 321.80, 7.93, 571, 6

UF = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO", "21": "MA", "22": "PI",
      "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE", "29": "BA", "31": "MG", "32": "ES",
      "33": "RJ", "35": "SP", "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
SIMPLES = {"1": "Não Optante", "2": "Optante - Microempreendedor Individual (MEI)",
           "3": "Optante - Microempresa ou Empresa de Pequeno Porte (ME/EPP)"}
REGIME_SN = {"1": "Regime de apuração dos tributos federais e municipal pelo Simples Nacional",
             "2": "Regime de apuração dos tributos federais pelo SN e o ISSQN pela NFS-e conforme respectiva legislação municipal do tributo",
             "3": "Regime de apuração dos tributos federais e municipal pela NFS-e conforme respectivas legilações federal e municipal de cada tributo"}
EMITENTE = {"1": "Prestador", "2": "Tomador", "3": "Intermediário"}
SITUACAO = {"100": "NFS-e Gerada", "101": "NFS-e de Substituição Gerada", "102": "NFS-e de Decisão Judicial ou Administrativa", "103": "NFS-e Avulsa Gerada"}
TRIB_ISSQN = {"1": "Operação Tributável", "2": "Imunidade", "3": "Exportação de Serviço", "4": "Não Incidência"}
RET_ISSQN = {"1": "Não Retido", "2": "Retido pelo Tomador", "3": "Retido pelo Intermediário"}
NAO_COBERTO = ["n:DPS/n:infDPS/n:dest", "n:DPS/n:infDPS/n:interm", "n:DPS/n:infDPS/n:IBSCBS",
               "n:DPS/n:infDPS/n:infAdic", "n:DPS/n:infDPS/n:valores/n:trib/n:tribFed",
               "n:DPS/n:infDPS/n:valores/n:vDescCondIncond", "n:DPS/n:infDPS/n:valores/n:vDedRed"]


def truncar(s: str, n: int) -> str:
    """Regra da NT: passou do limite, corta e põe reticências (o portal: "Optante - Microempresa ou Empresa de ...")."""
    return s if len(s) <= n else s[:n] + "..."


def cnpj(s: str) -> str:
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}" if len(s) == 14 else s


def cep(s: str) -> str:
    return f"{s[:2]}.{s[2:5]}-{s[5:]}" if len(s) == 8 else s


def ibge(s: str) -> str:
    return f"{s[:2]}.{s[2:]}"  # assim mesmo no portal: 3550308 -> 35.50308


def municipio_do_cep(cep_: str) -> str:
    """Nome do município pelo ViaCEP. Só é chamado quando o XML não nomeia o município."""
    try:
        with urllib.request.urlopen(f"https://viacep.com.br/ws/{cep_}/json/", timeout=10) as r:
            return json.load(r).get("localidade", "")
    except (OSError, ValueError):
        return ""


def reais(v: str | Decimal) -> str:
    return "R$ " + f"{Decimal(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def data_hora(s: str) -> str:
    return datetime.fromisoformat(s).strftime("%d/%m/%Y %H:%M:%S")  # hora local da nota, sem converter


def quebrar(texto: str, largura: float, tamanho: float) -> list[str]:
    """Quebra por palavra, respeitando as quebras de linha do próprio texto (o portal também respeita)."""
    linhas = []
    for paragrafo in texto.splitlines():
        atual = ""
        for palavra in paragrafo.split():
            teste = f"{atual} {palavra}".strip()
            if atual and pymupdf.get_text_length(teste, FONTE, tamanho) > largura:
                linhas.append(atual)
                atual = palavra
            else:
                atual = teste
        if atual:
            linhas.append(atual)
    return linhas


def ler(xml: bytes) -> dict:
    raiz = etree.fromstring(xml)
    inf = raiz.find("n:infNFSe", NS)
    if inf is None:
        raise ValueError("o XML não é de uma NFS-e emitida (falta infNFSe)")
    for caminho in NAO_COBERTO:
        if inf.find(caminho, NS) is not None:
            raise ValueError(f"o molde não cobre o grupo {caminho.split(':')[-1]}: gerar o PDF no portal")

    def t(caminho: str, base=inf) -> str:
        e = base.find(caminho, NS)
        return (e.text or "").strip() if e is not None else ""

    dps = inf.find("n:DPS/n:infDPS", NS)
    nomes = {t("n:emit/n:enderNac/n:cMun"): t("n:xLocEmi"),
             t("n:cLocIncid"): t("n:xLocIncid"),
             t("n:serv/n:locPrest/n:cLocPrestacao", dps): t("n:xLocPrestacao")}

    def endereco(base) -> tuple[str, str, str]:
        """(Endereço, Município / UF, Código IBGE / CEP) de emit/enderNac ou toma/end."""
        if base is None:
            return "-", "-", "-"
        nac = base.find("n:endNac", NS)
        cmun = t("n:cMun", base) or (t("n:cMun", nac) if nac is not None else "")
        cep_ = t("n:CEP", base) or (t("n:CEP", nac) if nac is not None else "")
        nome = nomes.get(cmun)
        if not nome and cep_:
            nome = municipio_do_cep(cep_)  # rede só neste caso raro: município que o XML não nomeia
        partes = [t(c, base) for c in ("n:xLgr", "n:nro", "n:xCpl", "n:xBairro")]
        return (", ".join(p for p in partes if p) or "-",
                f"{nome} / {UF.get(cmun[:2], '-')}" if nome else "-",
                f"{ibge(cmun)} / {cep(cep_)}" if cmun else "-")

    emit, toma = inf.find("n:emit", NS), dps.find("n:toma", NS)
    e_end, e_mun, e_ibge = endereco(emit.find("n:enderNac", NS))
    t_end, t_mun, t_ibge = endereco(toma.find("n:end", NS) if toma is not None else None)
    chave = inf.get("Id").removeprefix("NFS")
    c_prest = t("n:serv/n:locPrest/n:cLocPrestacao", dps)
    trib_nac = t("n:serv/n:cServ/n:cTribNac", dps)
    valor = t("n:valores/n:vServPrest/n:vServ", dps)
    return {
        "chave": chave, "tpAmb": t("n:tpAmb", dps),
        "municipio_cab": f"Município: {t('n:xLocEmi')} - {t('n:enderNac/n:UF', emit)}",
        "ambGer": t("n:ambGer"),
        "nNFSe": t("n:nNFSe"), "dCompet": datetime.fromisoformat(t("n:dCompet", dps)).strftime("%d/%m/%Y"),
        "dhProc": data_hora(t("n:dhProc")), "nDPS": t("n:nDPS", dps), "serie": str(int(t("n:serie", dps))),
        "dhEmi": data_hora(t("n:dhEmi", dps)), "tpEmit": EMITENTE.get(t("n:tpEmit", dps), "-"),
        "cStat": truncar(SITUACAO.get(t("n:cStat"), "-"), 37),
        "e_cnpj": cnpj(t("n:CNPJ", emit)), "e_nome": t("n:xNome", emit), "e_end": e_end, "e_mun": e_mun, "e_ibge": e_ibge,
        "e_fone": t("n:fone", emit) or "-", "e_email": t("n:email", emit) or "-", "e_im": t("n:IM", emit) or "-",
        "simples": truncar(SIMPLES.get(t("n:prest/n:regTrib/n:opSimpNac", dps), "-"), 37),
        "regime": REGIME_SN.get(t("n:prest/n:regTrib/n:regApTribSN", dps), "-"),
        "t_cnpj": cnpj(t("n:CNPJ", toma)) if toma is not None else "-",
        "t_nome": t("n:xNome", toma) if toma is not None else "-",
        "t_im": (t("n:IM", toma) if toma is not None else "") or "-",
        "t_fone": (t("n:fone", toma) if toma is not None else "") or "-",
        "t_email": (t("n:email", toma) if toma is not None else "") or "-",
        "t_end": t_end, "t_mun": t_mun, "t_ibge": t_ibge,
        "trib": f"{trib_nac[:2]}.{trib_nac[2:4]}.{trib_nac[4:]} / {t('n:serv/n:cServ/n:cTribMun', dps) or '-'}",
        "nbs": t("n:serv/n:cServ/n:cNBS", dps) or "-",
        "local": f"{t('n:xLocPrestacao')} / {UF.get(c_prest[:2], '-')} / -",
        "x_trib": t("n:xTribMun") or t("n:xTribNac"),
        "descricao": t("n:serv/n:cServ/n:xDescServ", dps),
        "trib_issqn": TRIB_ISSQN.get(t("n:valores/n:trib/n:tribMun/n:tribISSQN", dps), "-"),
        "incid": f"{t('n:xLocIncid')} / {UF.get(t('n:cLocIncid')[:2], '-')} / -",
        "ret_issqn": RET_ISSQN.get(t("n:valores/n:trib/n:tribMun/n:tpRetISSQN", dps), "-"),
        "valor": reais(valor), "vLiq": reais(t("n:valores/n:vLiq") or valor),
    }


def campos(d: dict) -> list[tuple[float, float, float, str]]:
    """(x, linha de base, tamanho, texto) de cada valor, nas posições do portal."""
    return [
        (302.04, 809.66, 7, f"{d['nNFSe']} / {d['chave']}"),           # canhoto
        (C4, 18.73, 8, d["municipio_cab"]),
        (C4, 25.94, 6, f"Ambiente Gerador: {d['ambGer']}"),
        (C4, 32.74, 6, f"Tipo de Ambiente: {d['tpAmb']}"),
        (C1, 58.94, 7, d["chave"]),
        (C1, 79.16, 7, d["nNFSe"]), (C2, 79.16, 7, d["dCompet"]), (C3, 79.16, 7, d["dhProc"]),
        (C1, 99.39, 7, d["nDPS"]), (C2, 99.39, 7, d["serie"]), (C3, 99.39, 7, d["dhEmi"]),
        (C1, 119.61, 7, d["tpEmit"]), (C2, 119.61, 7, d["cStat"]), (C3, 119.61, 7, "-"),  # finalidade: só com IBS/CBS
        (C2, 139.19, 7, d["e_cnpj"]), (C3, 139.19, 7, d["e_im"]), (C4, 139.19, 7, d["e_fone"]),
        (C1, 158.26, 7, d["e_nome"]), (C3, 158.26, 7, d["e_mun"]), (C4, 158.26, 7, d["e_ibge"]),
        (C1, 177.33, 7, d["e_end"]), (C3, 177.33, 7, d["e_email"]),
        (C1, 196.41, 7, d["simples"]), (C2, 196.41, 7, d["regime"]),
        (C2, 215.98, 7, d["t_cnpj"]), (C3, 215.98, 7, d["t_im"]), (C4, 215.98, 7, d["t_fone"]),
        (C1, 235.06, 7, d["t_nome"]), (C3, 235.06, 7, d["t_mun"]), (C4, 235.06, 7, d["t_ibge"]),
        (C1, 254.13, 7, d["t_end"]), (C3, 254.13, 7, d["t_email"]),
        (C2, 290.55, 7, d["trib"]), (C3, 290.55, 7, d["nbs"]), (C4, 290.55, 7, d["local"]),
        (C1, 302.73, 7, d["x_trib"]),
        (C2, 380.99, 7, d["trib_issqn"]), (C3, 380.99, 7, d["incid"]),
        # Simples Nacional: BC, alíquota e ISSQN apurado não vêm no XML.
        (C1, 400.06, 7, "-"), (C2, 400.06, 7, "-"), (C3, 400.06, 7, d["ret_issqn"]), (C4, 400.06, 7, "-"),
        # Tributação federal: sem retenções (tribFed é recusado em ler()).
        (C2, 419.64, 7, "-"), (C3, 419.64, 7, "-"), (C4, 419.64, 7, "-"),
        (C1, 438.71, 7, "-"), (C2, 438.71, 7, "-"), (C3, 438.71, 7, "-"),
        # IBS/CBS: o grupo é recusado em ler(); sem ele, o portal escreve assim.
        (C2, 458.29, 7, "- / -"), (C3, 458.29, 7, "- / - / - / -"),
        (C1, 477.36, 7, "R$ 0,00"), (C2, 477.36, 7, "-"), (C3, 477.36, 7, "- / - / -"), (C4, 477.36, 7, "- / -"),
        (C1, 496.43, 7, "-"), (C2, 496.43, 7, "-"), (C3, 496.43, 7, "-"), (C4, 496.43, 7, "-"),
        (C1, 515.51, 7, "-"), (C2, 515.51, 7, "-"), (C3, 515.51, 7, "-"), (C4, 515.51, 7, "-"),
        (C2, 535.08, 7, d["valor"]), (C3, 535.08, 7, "-"), (C4, 535.08, 7, "-"),
        # ponytail: "R$ 0,00" no líquido + IBS/CBS copia o portal (sem o grupo IBS/CBS ele escreve zero).
        (C1, 554.16, 7, "-"), (C2, 554.16, 7, d["vLiq"]), (C3, 554.16, 7, "R$ 0,00"), (C4, 554.16, 7, "R$ 0,00"),
        (C1, 587.06, 7, "Totais aproximados dos Tributos cfe. Lei n° 12.741/2012: Federais: -; Estaduais: -; Municipais: -;"),
    ]


def gerar(xml: bytes, modelo: Path = MODELO) -> bytes:
    if not modelo.exists():
        raise FileNotFoundError(f"molde não encontrado em {modelo}: rode antes  python danfse.py --modelo <danfse do portal.pdf>")
    d = ler(xml)
    doc = pymupdf.open(modelo)
    pagina = doc[0]
    for x, y, tamanho, texto in campos(d):
        pagina.insert_text((x, y), texto, fontname=FONTE, fontsize=tamanho)
    # Descrição do serviço: quebra por palavra; se não couber no quadro, diminui a letra.
    for tamanho in (7, 6, 5):
        linhas = quebrar(d["descricao"], DESCRICAO_LARGURA, tamanho)
        passo = DESCRICAO_PASSO * tamanho / 7
        cabem = int(DESCRICAO_LINHAS * DESCRICAO_PASSO / passo)
        if len(linhas) <= cabem:
            break
    else:
        raise ValueError(f"a descrição não cabe no quadro ({len(linhas)} linhas): gerar o PDF no portal")
    for i, linha in enumerate(linhas):
        pagina.insert_text((C1, DESCRICAO_Y + i * passo), linha, fontname=FONTE, fontsize=tamanho)
    if d["tpAmb"] == "2":  # NT 008, item 2.4.3: teste em produção restrita
        pagina.insert_text((239, 34), "NFS-e SEM VALIDADE JURÍDICA", fontname="hebo", fontsize=9, color=(1, 0, 0))
    qr = io.BytesIO()
    segno.make(QR_URL + d["chave"], error="m").save(qr, kind="png", scale=8, border=0)
    pagina.insert_image(QR_RECT, stream=qr.getvalue())
    doc.set_metadata({"title": f"DANFSe {d['nNFSe']}", "creator": "nfse-app"})
    return doc.tobytes(deflate=True, garbage=4)


def fazer_modelo(portal_pdf: Path, saida: Path = MODELO) -> None:
    """Apaga os valores e o QR Code de um DANFSe do portal. Ficam linhas, rótulos, sombra e logo."""
    fixos = {"A autenticidade", "pela leitura", "chave de acesso no", "DESTINATÁRIO DA OPERAÇÃO", "INTERMEDIÁRIO DA OPERAÇÃO"}
    doc = pymupdf.open(portal_pdf)
    pagina = doc[0]
    for bloco in pagina.get_text("dict")["blocks"]:
        for linha in bloco.get("lines", []):
            for s in linha["spans"]:
                if s["font"].startswith("Microsoft") and not any(s["text"].startswith(f) for f in fixos):
                    pagina.add_redact_annot(s["bbox"], fill=False)  # sem pintar: preserva o sombreamento
    pagina.add_redact_annot(QR_RECT, fill=False)
    pagina.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    doc.set_metadata({})
    doc.save(saida, deflate=True, garbage=4)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--modelo"] and len(sys.argv) == 3:
        fazer_modelo(Path(sys.argv[2]))
        print(f"molde salvo em {MODELO}")
    elif len(sys.argv) in (2, 3):
        origem = Path(sys.argv[1])
        destino = Path(sys.argv[2]) if len(sys.argv) == 3 else origem.with_suffix(".pdf")
        destino.write_bytes(gerar(origem.read_bytes()))
        print(f"PDF salvo em {destino}")
    else:
        sys.exit(__doc__)
