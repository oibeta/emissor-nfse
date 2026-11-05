"""
Valida o XML da DPS contra os esquemas XSD oficiais v1.01, antes de
enviar para a SEFIN.

DEFEITO CONHECIDO DO XSD OFICIAL
--------------------------------
O tipo TSSerieDPS declara o pattern '^0{0,4}\\d{1,5}$'. Em XML Schema,
patterns já são ancorados implicitamente e '^' e '$' valem como
caracteres LITERAIS — quem escreveu o esquema usou sintaxe de regex
comum. Na prática, nenhum número de série passa: o único valor aceito
seria a string '^70000$', com os símbolos.

A SEFIN aceita séries normais, então o servidor não valida por esse
pattern. Aqui esse erro específico é ignorado, e só esse — qualquer outro
erro de validação continua barrando o envio.

Dos 53 patterns do esquema, esse é o único afetado.

DOIS PACOTES DE ESQUEMAS
------------------------
schemas/ tem os esquemas da produção (09/02/2026). schemas_restrita/ tem os
da produção restrita (20/10/2026, NT 009), que já mudaram. A DPS é validada
pelo pacote do ambiente dela (tpAmb). O pacote novo corrigiu o pattern da
série, então o defeito acima só aparece no da produção.

Dependência: pip install lxml
"""

from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path

import lxml.etree as ET

SCHEMA_DPS = {
    "1": Path(__file__).parent / "schemas" / "DPS_v1.01.xsd",            # produção
    "2": Path(__file__).parent / "schemas_restrita" / "DPS_v1.01.xsd",   # produção restrita
}

class DPSInvalida(ValueError):
    """O XML não bate com o esquema oficial."""


_cache: dict[str, ET.XMLSchema] = {}


@contextmanager
def _dentro_de(pasta: Path):
    """
    Carrega o esquema de dentro da própria pasta, com nome relativo.

    O lxml transforma o caminho absoluto numa URL, e caminho do Windows
    com acento ou espaço ("Emissão de NFS-e") vira percent-encoding que
    ele não consegue reabrir. Entrando na pasta, o nome do arquivo fica
    puro ASCII e os `include` do esquema resolvem sozinhos.
    """
    anterior = Path.cwd()
    os.chdir(pasta)
    try:
        yield
    finally:
        os.chdir(anterior)


def _schema(caminho: Path) -> ET.XMLSchema:
    chave = str(caminho)
    if chave not in _cache:
        if not caminho.exists():
            raise DPSInvalida(
                f"esquema XSD não encontrado em {caminho}\n"
                "  os .xsd devem estar em schemas/ e schemas_restrita/, ao lado do validar.py"
            )
        with _dentro_de(caminho.parent):
            _cache[chave] = ET.XMLSchema(ET.parse(caminho.name))
    return _cache[chave]

# Assinatura textual do defeito descrito acima.
_FALSO_POSITIVO = re.compile(
    r"'\{http://www\.sped\.fazenda\.gov\.br/nfse\}serie'.*facet 'pattern'"
)


def erros(xml: bytes, *, schema_path: Path | None = None) -> list[str]:
    """Devolve a lista de erros reais de validação. Vazia = XML válido."""
    doc = ET.fromstring(xml)
    if schema_path is None:
        tp_amb = doc.findtext(".//{http://www.sped.fazenda.gov.br/nfse}tpAmb")
        if tp_amb not in SCHEMA_DPS:
            return [f"tpAmb {tp_amb!r} desconhecido: esperado 1 ou 2"]
        schema_path = SCHEMA_DPS[tp_amb]
    schema = _schema(schema_path)
    if schema.validate(doc):
        return []
    return [
        f"linha {e.line}: {e.message}"
        for e in schema.error_log
        if not _FALSO_POSITIVO.search(e.message)
    ]


def exige_valido(xml: bytes, *, schema_path: Path | None = None) -> None:
    """Levanta DPSInvalida se o XML não estiver conforme o esquema."""
    problemas = erros(xml, schema_path=schema_path)
    if problemas:
        raise DPSInvalida(
            "XML da DPS não bate com o esquema oficial v1.01:\n  - "
            + "\n  - ".join(problemas)
        )
