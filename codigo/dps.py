"""
Monta o XML da DPS (Declaração de Prestação de Serviços) no padrão
Sistema Nacional NFS-e, leiaute v1.01.

Referência: Manual de Contribuintes - Emissor Público (v1.2, out/2025)
            Esquemas XSD v1.01 (20260209)

Este módulo só monta o XML. Assinatura e envio ficam em outros módulos.
Só usa a biblioteca padrão.

O QUE ESTE MÓDULO COBRE
-----------------------
O caso mais comum de prestador de serviço: optante do Simples Nacional
(ME/EPP), ISSQN tributável e não retido, tomador com CNPJ ou CPF no
Brasil, sem destinatário, sem intermediário, sem retenções federais e sem
o grupo IBS/CBS. Para qualquer outro caso, acrescente os grupos seguindo
o Anexo I e valide contra o XSD (validar.py).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from xml.etree import ElementTree as ET

NS = "http://www.sped.fazenda.gov.br/nfse"
VER_APLIC = "nfse-app/0.1"  # identifica o seu aplicativo na DPS; troque se quiser
BRASILIA = timezone(timedelta(hours=-3))  # sem horário de verão desde 2019


# --------------------------------------------------------------------------
# Feriados nacionais e dias úteis
# --------------------------------------------------------------------------

def _pascoa(ano: int) -> date:
    """Domingo de Páscoa pelo algoritmo de Meeus/Butcher."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    lu = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * lu) // 451
    mes, dia = divmod(h + lu - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def feriados_nacionais(ano: int) -> set[date]:
    """
    Feriados nacionais brasileiros (Lei 662/1949, Lei 6.802/1980 e
    os móveis derivados da Páscoa). São os que fecham banco em todo
    o país — feriado municipal ou estadual não entra.
    """
    p = _pascoa(ano)
    return {
        date(ano, 1, 1),    # Confraternização Universal
        p - timedelta(48),  # Carnaval (segunda)
        p - timedelta(47),  # Carnaval (terça)
        p - timedelta(2),   # Sexta-feira Santa
        date(ano, 4, 21),   # Tiradentes
        date(ano, 5, 1),    # Dia do Trabalho
        p + timedelta(60),  # Corpus Christi
        date(ano, 9, 7),    # Independência
        date(ano, 10, 12),  # Nossa Senhora Aparecida
        date(ano, 11, 2),   # Finados
        date(ano, 11, 15),  # Proclamação da República
        date(ano, 11, 20),  # Consciência Negra (Lei 14.759/2023)
        date(ano, 12, 25),  # Natal
    }


def eh_dia_util(d: date) -> bool:
    return d.weekday() < 5 and d not in feriados_nacionais(d.year)


def proximo_dia_util(d: date) -> date:
    while not eh_dia_util(d):
        d += timedelta(days=1)
    return d


def vencimento(emissao: date, prazo_dias: int) -> date:
    """
    Vencimento = emissão + prazo em dias CORRIDOS. Caindo em dia não
    útil, empurra para o próximo dia útil.
    """
    return proximo_dia_util(emissao + timedelta(days=prazo_dias))


# --------------------------------------------------------------------------
# Saneamento de texto
# --------------------------------------------------------------------------

def limpa_texto(s: str, limite: int) -> str:
    """
    A SEFIN rejeita caracteres de controle e recusa texto acima do
    limite do campo. Normaliza para NFC, remove controles, colapsa
    espaços e corta no limite.
    """
    s = unicodedata.normalize("NFC", s)
    s = "".join(ch for ch in s if ch == "\n" or not unicodedata.category(ch).startswith("C"))
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s[:limite]


def so_digitos(s: str) -> str:
    return re.sub(r"\D", "", s or "")


def dec2(v) -> str:
    """Valor monetário com 2 casas, ponto decimal, sem separador de milhar."""
    return f"{Decimal(str(v)).quantize(Decimal('0.01'))}"


# --------------------------------------------------------------------------
# Dados de entrada
# --------------------------------------------------------------------------

@dataclass
class Endereco:
    cep: str
    cmun: str          # código IBGE, 7 dígitos
    logradouro: str
    numero: str
    bairro: str
    complemento: str = ""


@dataclass
class Prestador:
    """
    FAIXAS DE SÉRIE DA DPS, por tipo de emissor (Anexo I do leiaute):

        00001 a 49999 — emissão com aplicativo próprio   <- este script
        50000 a 69999 — emissor móvel
        70000 a 79999 — emissor Web                      <- o portal
        80000 a 89999 — transcrição manual (Web)

    Série fora da faixa do emissor é recusada com E0010. As notas
    emitidas pelo portal saem na série 70000; por API, não podem.
    """
    cnpj: str
    cloc_emi: str          # IBGE do município do emitente
    serie: str = "00001"   # faixa 00001-49999 = aplicativo próprio; ver acima
    # Regime tributário: confira na sua nota emitida pelo portal (Anexo I, grupo regTrib).
    op_simp_nac: str = "3"     # 1 = Não optante; 2 = MEI; 3 = Optante ME/EPP
    reg_ap_trib_sn: str = "1"  # só para opSimpNac 3: 1 = federais e municipal pelo SN
    reg_esp_trib: str = "0"    # 0 = Nenhum


@dataclass
class Tomador:
    cnpj_cpf: str
    nome: str
    endereco: Endereco | None = None
    email: str = ""


@dataclass
class Servico:
    ctrib_nac: str          # código de tributação nacional, 6 dígitos (Anexo B)
    ctrib_mun: str          # complementar do município (3 dígitos); "" se não houver
    descricao: str
    cloc_prestacao: str     # IBGE onde o serviço é prestado


@dataclass
class Nota:
    n_dps: int
    competencia: date
    valor: Decimal | float | str
    prestador: Prestador
    tomador: Tomador
    servico: Servico
    aliq_simples_nacional: str  # alíquota efetiva do Simples, ex. "6.00"; muda com o faturamento
    tp_amb: str = "2"           # 2 = produção restrita (teste); 1 = produção
    dh_emi: datetime = field(default_factory=lambda: agora_com_folga())


# --------------------------------------------------------------------------
# Hora de emissão
# --------------------------------------------------------------------------

FOLGA_RELOGIO = 30  # segundos


def agora_com_folga(segundos: int = FOLGA_RELOGIO) -> datetime:
    """
    Hora de emissão com uma folga para trás.

    A SEFIN recusa (E0008) quando a data de emissão da DPS é posterior à
    hora em que ela processa. Relógio de máquina costuma andar alguns
    segundos à frente, e o tempo de rede não compensa isso. A folga cobre
    o caso comum. Desvio maior: leia `dataHoraProcessamento` na resposta
    de erro, refaça a DPS com essa hora e reenvie uma vez.

    Sempre no horário de Brasília, mesmo que a máquina (ou o container
    na nuvem) esteja em UTC.
    """
    return datetime.now(BRASILIA) - timedelta(seconds=segundos)


# --------------------------------------------------------------------------
# Montagem do XML
# --------------------------------------------------------------------------

def id_dps(nota: Nota) -> str:
    """
    ID da DPS: 'DPS' + IBGE(7) + tipo de inscrição(1) + inscrição federal(14)
    + série(5) + número(15). Tipo 2 = CNPJ.
    """
    p = nota.prestador
    return (
        "DPS"
        + p.cloc_emi.zfill(7)
        + "2"
        + so_digitos(p.cnpj).zfill(14)
        + p.serie.zfill(5)
        + str(nota.n_dps).zfill(15)
    )


def _sub(pai, tag, texto=None):
    el = ET.SubElement(pai, tag)
    if texto is not None:
        el.text = str(texto)
    return el


def _endereco(pai, end: Endereco):
    e = _sub(pai, "end")
    nac = _sub(e, "endNac")
    _sub(nac, "cMun", so_digitos(end.cmun).zfill(7))
    _sub(nac, "CEP", so_digitos(end.cep).zfill(8))
    _sub(e, "xLgr", limpa_texto(end.logradouro, 255))
    _sub(e, "nro", limpa_texto(end.numero, 60))
    if end.complemento:
        _sub(e, "xCpl", limpa_texto(end.complemento, 156))
    _sub(e, "xBairro", limpa_texto(end.bairro, 60))


def monta_dps(nota: Nota) -> bytes:
    """Monta o XML da DPS. A ordem dos elementos segue o XSD."""
    ET.register_namespace("", NS)
    dps = ET.Element(f"{{{NS}}}DPS", {"versao": "1.01"})
    inf = _sub(dps, "infDPS")
    inf.set("Id", id_dps(nota))

    p, t, s = nota.prestador, nota.tomador, nota.servico

    _sub(inf, "tpAmb", nota.tp_amb)
    _sub(inf, "dhEmi", nota.dh_emi.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":"
         + nota.dh_emi.strftime("%z")[-2:])
    _sub(inf, "verAplic", VER_APLIC)
    _sub(inf, "serie", p.serie)
    _sub(inf, "nDPS", str(nota.n_dps))
    _sub(inf, "dCompet", nota.competencia.isoformat())
    _sub(inf, "tpEmit", "1")                      # 1 = Prestador
    # ponytail: a produção restrita já segue o leiaute da NT 009 (esquemas de
    # 20/10/2026), que exige finNFSe aqui; a produção ainda não aceita o campo.
    # Quando a produção adotar a NT 009, envie sempre e troque schemas/ por
    # schemas_restrita/ (ver docs/GUIA-TECNICO.md).
    if nota.tp_amb == "2":
        _sub(inf, "finNFSe", "0")                 # 0 = NFS-e regular
    _sub(inf, "cLocEmi", so_digitos(p.cloc_emi).zfill(7))

    # --- prestador ---
    prest = _sub(inf, "prest")
    _sub(prest, "CNPJ", so_digitos(p.cnpj).zfill(14))
    rt = _sub(prest, "regTrib")
    _sub(rt, "opSimpNac", p.op_simp_nac)
    if p.op_simp_nac == "3":
        _sub(rt, "regApTribSN", p.reg_ap_trib_sn)
    _sub(rt, "regEspTrib", p.reg_esp_trib)

    # --- tomador ---
    toma = _sub(inf, "toma")
    doc = so_digitos(t.cnpj_cpf)
    _sub(toma, "CNPJ" if len(doc) == 14 else "CPF", doc)
    _sub(toma, "xNome", limpa_texto(t.nome, 150))
    if t.endereco:
        _endereco(toma, t.endereco)
    if t.email:
        _sub(toma, "email", t.email[:80])

    # --- serviço ---
    serv = _sub(inf, "serv")
    loc = _sub(serv, "locPrest")
    _sub(loc, "cLocPrestacao", so_digitos(s.cloc_prestacao).zfill(7))
    cs = _sub(serv, "cServ")
    _sub(cs, "cTribNac", so_digitos(s.ctrib_nac).zfill(6))
    if s.ctrib_mun:
        _sub(cs, "cTribMun", s.ctrib_mun)
    _sub(cs, "xDescServ", limpa_texto(s.descricao, 2000))

    # --- valores ---
    val = _sub(inf, "valores")
    vsp = _sub(val, "vServPrest")
    _sub(vsp, "vServ", dec2(nota.valor))
    trib = _sub(val, "trib")
    tm = _sub(trib, "tribMun")
    _sub(tm, "tribISSQN", "1")        # 1 = Operação tributável
    _sub(tm, "tpRetISSQN", "1")       # 1 = Não retido
    tt = _sub(trib, "totTrib")
    _sub(tt, "pTotTribSN", nota.aliq_simples_nacional)

    return ET.tostring(dps, encoding="utf-8", xml_declaration=True)
