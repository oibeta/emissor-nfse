"""
Confere a fila e as travas da emissão sem rede: a SEFIN, o CEP e o PDF são
dublês, e tudo acontece numa pasta temporária. Nada é enviado, e a fila de
verdade não é tocada.

    python testar_fila.py
"""
from __future__ import annotations

import base64
import gzip
import json
import os
import tempfile
from pathlib import Path

import nfse
from assinar import Certificado
from sefin import ErroSefin
from testar_offline import certificado_descartavel

XML_NOTA = b'<NFSe xmlns="http://www.sped.fazenda.gov.br/nfse"><infNFSe><nNFSe>7</nNFSe></infNFSe></NFSe>'


class SefinDubla:
    def __init__(self, falhas=()):
        self.falhas = list(falhas)   # exceções a levantar, uma por envio, antes de aceitar
        self.envios = 0
        self.existentes = set()

    def dps_ja_existe(self, id_dps):
        return id_dps in self.existentes

    def emitir(self, corpo):
        self.envios += 1
        if self.falhas:
            raise self.falhas.pop(0)
        return {"chaveAcesso": "9" * 50,
                "nfseXmlGZipB64": base64.b64encode(gzip.compress(XML_NOTA)).decode()}


def cep(_):
    return {"cep": "01310100", "cmun": "3550308", "logradouro": "Avenida Paulista", "bairro": "Bela Vista"}


def pdf_quebrado(_):
    raise RuntimeError("sem molde")


def recusa(func, *args, **kw) -> str:
    try:
        func(*args, **kw)
    except nfse.Recusa as e:
        return str(e)
    raise AssertionError(f"{func.__name__}{args} devia ter recusado")


def main() -> None:
    pasta = Path(tempfile.mkdtemp())
    nfse.EMPRESA, nfse.FILA, nfse.NOTAS = pasta / "empresa.json", pasta / "fila.csv", pasta / "notas"
    nfse.EMPRESA.write_text(json.dumps({
        "ambiente": "restrita", "cnpj": "00000000000191", "cloc_emi": "3550308", "cloc_prestacao": "3550308",
        "ctrib_nac": "010101", "ctrib_mun": "", "serie": "00001", "aliq_simples_nacional": "6.00",
        "texto_fixo_descricao": "PIX: chave-exemplo",
    }), encoding="utf-8")

    senha = "teste"
    pfx = certificado_descartavel(senha)
    cert = Certificado(pfx, senha)
    os.remove(pfx)

    def pedido(id_, **extra):
        p = {"id_pedido": id_, "tomador_cnpj": "11.222.333/0001-81", "tomador_nome": "Cliente Exemplo S.A.",
             "tomador_cep": "01310-100", "tomador_numero": "1000", "valor": "1.500,00",
             "competencia": "2026-10-01", "descricao": "Serviço. Vencimento: {vencimento}.", "prazo_dias": "30"}
        p.update(extra)
        caminho = pasta / f"{id_}.json"
        caminho.write_text(json.dumps(p), encoding="utf-8")
        return str(caminho)

    # adicionar: conferências e repetição
    nfse.cmd_adicionar(pedido("A1"))
    nfse.cmd_adicionar(pedido("A2", tomador_cnpj="00.000.000/0001-91", valor="0"))
    nfse.cmd_adicionar(pedido("A1"))  # repetido: não entra
    fila = nfse.ler_fila()
    assert [x["id_pedido"] for x in fila] == ["A1", "A2"]
    assert fila[0]["valor"] == "1500.00" and not fila[0]["alertas"]
    assert "própria empresa" in fila[1]["alertas"] and "zero" in fila[1]["alertas"]

    # sem aprovação não emite
    assert "Aprovado" in recusa(nfse.cmd_emitir, "A1", sefin=SefinDubla(), cert=cert, cep=cep)

    # ok dado para produção com o empresa.json em restrita: recusa
    nfse.cmd_aprovar("A1", "producao")
    assert "producao" in recusa(nfse.cmd_emitir, "A1", sefin=SefinDubla(), cert=cert, cep=cep)

    # relógio adiantado (E0008): refaz com a hora do servidor e envia de novo, uma vez
    nfse.cmd_aprovar("A1", "restrita")
    e0008 = ErroSefin("recusada", status=400, corpo={
        "erros": [{"Codigo": "E0008"}], "dataHoraProcessamento": "2026-10-23T10:00:00"})
    s = SefinDubla(falhas=[e0008])
    linha = nfse.cmd_emitir("A1", sefin=s, cert=cert, cep=cep, gerar_pdf=pdf_quebrado)
    assert s.envios == 2
    assert linha["status"] == "Emitida" and linha["numero_nfse"] == "7" and linha["n_dps"] == "1"
    assert (nfse.NOTAS / "NFSe-00007_Cliente Exemplo SA_TESTE.xml").read_bytes() == XML_NOTA
    assert "PDF não gerado" in linha["alertas"]  # PDF falhar não desfaz a nota

    # emitida não emite de novo, nem com novo ok
    assert "Emitida" in recusa(nfse.cmd_emitir, "A1", sefin=SefinDubla(), cert=cert, cep=cep)
    assert "Emitida" in recusa(nfse.cmd_aprovar, "A1", "restrita")

    # conexão cai no envio: fica em Emitindo e exige verificar
    nfse.cmd_adicionar(pedido("B1"))
    nfse.cmd_aprovar("B1", "restrita")
    assert "verificar" in recusa(nfse.cmd_emitir, "B1", sefin=SefinDubla(falhas=[OSError("timeout")]), cert=cert, cep=cep)
    b1 = nfse.achar(nfse.ler_fila(), "B1")
    assert b1["status"] == "Emitindo" and b1["n_dps"] == "2"
    assert "verificar" in recusa(nfse.cmd_emitir, "B1", sefin=SefinDubla(), cert=cert, cep=cep)

    # a tentativa anterior virou nota: mesmo com novo ok, não reenvia
    fila = nfse.ler_fila()
    nfse.achar(fila, "B1")["status"] = "Erro"
    nfse.gravar_fila(fila)
    nfse.cmd_aprovar("B1", "restrita")
    s = SefinDubla()
    s.existentes.add("DPS" + "3550308" + "2" + "00000000000191" + "00001" + "2".zfill(15))
    assert "NÃO REENVIAR" in recusa(nfse.cmd_emitir, "B1", sefin=s, cert=cert, cep=cep)
    assert s.envios == 0

    # recusa da SEFIN vira Erro com a mensagem, e não é reenviada sozinha
    nfse.cmd_adicionar(pedido("C1"))
    nfse.cmd_aprovar("C1", "restrita")
    e0014 = ErroSefin("recusada", status=400, corpo={"erros": [{"Codigo": "E0014"}]})
    assert "E0014" in recusa(nfse.cmd_emitir, "C1", sefin=SefinDubla(falhas=[e0014]), cert=cert, cep=cep)
    assert nfse.achar(nfse.ler_fila(), "C1")["status"] == "Erro"

    # o fila.csv abre no Excel: ponto e vírgula e UTF-8 com BOM
    assert nfse.FILA.read_bytes().startswith(b"\xef\xbb\xbfid_pedido;status;")

    print("ok: conferências, aprovação, ambiente, E0008, PDF, emitir duas vezes, queda no envio, recusa da SEFIN")


if __name__ == "__main__":
    main()
