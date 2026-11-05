"""
Confere a montagem, a validação e a assinatura da DPS sem rede e sem
certificado de verdade: gera um certificado descartável na hora e usa
dados fictícios. Nada é enviado à SEFIN.

    python testar_offline.py

Rode antes de qualquer mudança nos módulos, e depois.
"""
from __future__ import annotations

import base64
import gzip
import os
import tempfile
from datetime import date, datetime, timedelta, timezone
from dataclasses import replace
from decimal import Decimal

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, pkcs12
from cryptography.x509.oid import NameOID

import validar
from assinar import Certificado, assinar_dps, corpo_requisicao
from dps import Endereco, Nota, Prestador, Servico, Tomador, id_dps, monta_dps, vencimento
from sefin import ErroSefin, Sefin


def certificado_descartavel(senha: str) -> str:
    """Um .pfx autoassinado, só para testar a assinatura."""
    chave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nome = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "EMPRESA TESTE LTDA:00000000000191")])
    agora = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(nome).issuer_name(nome)
            .public_key(chave.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(agora).not_valid_after(agora + timedelta(days=30))
            .sign(chave, hashes.SHA256()))
    fd, caminho = tempfile.mkstemp(suffix=".pfx")
    with os.fdopen(fd, "wb") as f:
        f.write(pkcs12.serialize_key_and_certificates(b"teste", chave, cert, None,
                                                      BestAvailableEncryption(senha.encode())))
    return caminho


def nota_ficticia() -> Nota:
    return Nota(
        n_dps=1,
        competencia=date(2026, 10, 1),
        valor=Decimal("1500.00"),
        prestador=Prestador(cnpj="00.000.000/0001-91", cloc_emi="3550308"),
        tomador=Tomador(
            cnpj_cpf="11.222.333/0001-81", nome="CLIENTE EXEMPLO S.A.",
            endereco=Endereco(cep="01310-100", cmun="3550308", logradouro="Avenida Paulista",
                              numero="1000", bairro="Bela Vista", complemento="Andar 1"),
        ),
        servico=Servico(ctrib_nac="010101", ctrib_mun="", cloc_prestacao="3550308",
                        descricao="Serviço de teste.\nVencimento: 10/11/2026."),
        aliq_simples_nacional="6.00",
        tp_amb="2",
    )


def main() -> None:
    nota = nota_ficticia()

    # Id da DPS: DPS + IBGE(7) + tipo(1) + CNPJ(14) + série(5) + número(15) = 45 caracteres
    i = id_dps(nota)
    assert i == "DPS" + "3550308" + "2" + "00000000000191" + "00001" + "1".zfill(15), i
    assert len(i) == 45

    xml = monta_dps(nota)
    assert b"<dhEmi>" in xml and b"-03:00</dhEmi>" in xml, "dhEmi tem que sair no fuso de Brasília"

    problemas = validar.erros(xml)
    assert not problemas, "DPS fora do XSD:\n" + "\n".join(problemas)

    # Cada ambiente com o seu leiaute: a restrita (NT 009) exige finNFSe, a produção ainda não o aceita.
    assert b"<finNFSe>0</finNFSe>" in xml
    xml_prod = monta_dps(replace(nota, tp_amb="1"))
    assert b"finNFSe" not in xml_prod
    problemas = validar.erros(xml_prod)
    assert not problemas, "DPS de produção fora do XSD:\n" + "\n".join(problemas)
    assert validar.erros(xml_prod, schema_path=validar.SCHEMA_DPS["2"]), "sem finNFSe a restrita recusa (E1235)"

    senha = "senha-de-teste"
    pfx = certificado_descartavel(senha)
    try:
        cert = Certificado(pfx, senha)
        assinado = assinar_dps(xml, cert)  # verifica a própria assinatura
    finally:
        os.remove(pfx)

    assert b"<Signature xmlns=" in assinado, "Signature tem que vir sem o prefixo ds:"
    assert b"xml-exc-c14n#WithComments" in assinado
    assert b"rsa-sha256" in assinado and b"xmlenc#sha256" in assinado
    assert not validar.erros(assinado), "a DPS assinada tem que continuar válida no XSD"

    corpo = corpo_requisicao(assinado)
    assert gzip.decompress(base64.b64decode(corpo["dpsXmlGZipB64"])) == assinado

    # Trava de ambiente: XML de teste (tpAmb 2) nunca vai para produção.
    try:
        Sefin(cert, "producao")._conferir_ambiente(corpo)
        raise AssertionError("a trava de ambiente deixou passar tpAmb 2 para produção")
    except ErroSefin:
        pass
    Sefin(cert, "restrita")._conferir_ambiente(corpo)  # o par certo passa

    # Vencimento: 30 dias corridos; caindo em fim de semana ou feriado, vai para o dia útil seguinte.
    assert vencimento(date(2026, 10, 3), 30) == date(2026, 11, 3)   # 02/11 é Finados, segunda
    assert vencimento(date(2026, 10, 1), 10) == date(2026, 10, 13)  # 11/10 domingo, 12/10 feriado

    print("ok: Id, XSD, assinatura, corpo da requisição, trava de ambiente e vencimento")


if __name__ == "__main__":
    main()
