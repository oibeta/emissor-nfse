"""
Assina a DPS em XMLDSIG, no formato que o Sistema Nacional NFS-e aceita,
e prepara o corpo da requisição.

O .pfx é lido aqui e a chave privada fica só em memória. A senha vem de
quem chama (por exemplo, da variável de ambiente NFSE_SENHA): nunca do
código, nunca de arquivo do projeto.

TRÊS DETALHES QUE A SEFIN EXIGE E QUE NÃO SÃO O PADRÃO ÓBVIO
------------------------------------------------------------
1. Canonicalização exclusiva **com comentários**
   (`xml-exc-c14n#WithComments`). O default da maioria das bibliotecas é
   sem comentários, e a assinatura é recusada.
2. O elemento `Signature` vai **sem o prefixo `ds:`**. Com prefixo, é
   recusado.
3. SHA-256 na assinatura e no digest. SHA-1 não serve.

Errar qualquer um dos três dá rejeição sem mensagem que explique a causa.

Dependências: pip install lxml signxml cryptography
"""

from __future__ import annotations

import base64
import gzip
from pathlib import Path

import lxml.etree as ET
from cryptography.hazmat.primitives.serialization import pkcs12
from signxml import XMLSigner, XMLVerifier, methods
from signxml import namespaces as signxml_ns

NS = "http://www.sped.fazenda.gov.br/nfse"
C14N_SEFIN = "http://www.w3.org/2001/10/xml-exc-c14n#WithComments"


class CertificadoInvalido(Exception):
    """O .pfx não abriu, ou não tem o que precisa."""


class AssinaturaInvalida(Exception):
    """A assinatura gerada não se verifica."""


class Certificado:
    """Certificado A1 (PKCS#12). Mantém chave e certificado em memória."""

    def __init__(self, caminho_pfx: str | Path, senha: str):
        self.caminho = Path(caminho_pfx)
        try:
            dados = self.caminho.read_bytes()
        except OSError as e:
            raise CertificadoInvalido(f"não consegui ler {self.caminho}: {e}") from e

        try:
            chave, cert, _ = pkcs12.load_key_and_certificates(dados, senha.encode())
        except Exception as e:
            raise CertificadoInvalido(
                "não consegui abrir o .pfx — senha errada ou arquivo corrompido"
            ) from e

        if chave is None or cert is None:
            raise CertificadoInvalido("o .pfx não traz chave privada e certificado")

        self.chave = chave
        self.cert = cert

    @property
    def titular(self) -> str:
        return self.cert.subject.rfc4514_string()

    @property
    def validade(self):
        return self.cert.not_valid_before_utc, self.cert.not_valid_after_utc

    def dias_para_vencer(self) -> int:
        from datetime import datetime, timezone
        return (self.cert.not_valid_after_utc - datetime.now(timezone.utc)).days


def assinar_dps(xml: bytes, cert: Certificado, *, verificar: bool = True) -> bytes:
    """
    Assina o XML da DPS. A assinatura referencia o Id do `infDPS` e entra
    como irmã dele, dentro do elemento `DPS`.

    Com `verificar=True` (padrão), confere a própria assinatura antes de
    devolver — barato, e pega erro de canonicalização antes de gastar uma
    viagem até a SEFIN.
    """
    doc = ET.fromstring(xml)

    inf = doc.find(f".//{{{NS}}}infDPS")
    if inf is None:
        raise AssinaturaInvalida("elemento infDPS não encontrado no XML")

    ref_id = inf.get("Id")
    if not ref_id:
        raise AssinaturaInvalida("infDPS está sem o atributo Id")

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256",
        c14n_algorithm=C14N_SEFIN,
    )
    # Sem o prefixo ds: — a SEFIN recusa com ele.
    signer.namespaces = {None: signxml_ns.ds}

    assinado = signer.sign(
        doc,
        key=cert.chave,
        cert=[cert.cert],
        reference_uri=f"#{ref_id}",
    )

    if verificar:
        try:
            XMLVerifier().verify(assinado, x509_cert=cert.cert)
        except Exception as e:
            raise AssinaturaInvalida(
                f"a assinatura gerada não se verifica: {e}"
            ) from e

    return ET.tostring(assinado, encoding="utf-8", xml_declaration=True)


def corpo_requisicao(xml_assinado: bytes) -> dict[str, str]:
    """
    Monta o corpo do POST /nfse: o XML assinado, comprimido em gzip e
    codificado em base64, sob a chave `dpsXmlGZipB64`.
    """
    comprimido = gzip.compress(xml_assinado)
    return {"dpsXmlGZipB64": base64.b64encode(comprimido).decode("ascii")}
