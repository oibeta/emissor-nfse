"""
Transporte até a API do Sistema Nacional NFS-e (SEFIN Nacional).

A conexão é mTLS: o servidor exige certificado do cliente em toda chamada
— sem ele, nem a documentação abre (responde 496, "No Cert"). Só a
biblioteca padrão é usada aqui; a criptografia vem do módulo `assinar`.

SOBRE A CHAVE PRIVADA EM DISCO
------------------------------
O `ssl` do Python só carrega certificado de cliente a partir de ARQUIVO —
não aceita a chave em memória. Então, na hora de abrir a conexão, a chave
é gravada num arquivo temporário, carregada, e o arquivo é sobrescrito e
apagado em seguida. A partir daí ela vive só na memória do processo.

A janela é de milissegundos, mas existe. O arquivo é criado com permissão
restrita ao usuário e sempre removido, inclusive se a conexão falhar.

O PDF (DANFSe) NÃO VEM DAQUI
----------------------------
A API do PDF foi suspensa em 03/08/2026 (NT 008/2026). A resposta da
emissão traz o XML da nota, que é o documento fiscal; o PDF sai do
danfse.py, ou da consulta pública pela chave de acesso.

Dependência: pip install cryptography (via assinar.py)
"""

from __future__ import annotations

import gzip
import http.client
import json
import os
import ssl
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from urllib.parse import urlsplit

from cryptography.hazmat.primitives import serialization

from assinar import Certificado

BASES = {
    "restrita": "https://sefin.producaorestrita.nfse.gov.br/SefinNacional",
    "producao": "https://sefin.nfse.gov.br/SefinNacional",
}
CONSULTA_PUBLICA = "https://www.nfse.gov.br/consultapublica"  # PDF pela chave, sem login

TIMEOUT = 60


class ErroSefin(Exception):
    """A SEFIN recusou, ou a conversa não foi possível."""

    def __init__(self, mensagem, *, status=None, corpo=None):
        super().__init__(mensagem)
        self.status = status
        self.corpo = corpo


@dataclass
class Resposta:
    status: int
    corpo: dict | None
    bruto: bytes

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300


@contextmanager
def _contexto_ssl(cert: Certificado):
    """Contexto SSL com o certificado do cliente, sem deixar rastro em disco."""
    fd, caminho = tempfile.mkstemp(suffix=".pem")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(
                cert.chave.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
            f.write(cert.cert.public_bytes(serialization.Encoding.PEM))
        os.chmod(caminho, 0o600)

        ctx = ssl.create_default_context()
        ctx.load_cert_chain(certfile=caminho)
        yield ctx
    finally:
        # sobrescreve antes de apagar
        try:
            tamanho = os.path.getsize(caminho)
            with open(caminho, "r+b") as f:
                f.write(b"\0" * tamanho)
                f.flush()
                os.fsync(f.fileno())
        except OSError:
            pass
        try:
            os.remove(caminho)
        except OSError:
            pass


class Sefin:
    """Cliente da API SEFIN Nacional."""

    def __init__(self, cert: Certificado, ambiente: str = "restrita"):
        if ambiente not in BASES:
            raise ValueError(f"ambiente deve ser 'restrita' ou 'producao', não {ambiente!r}")
        self.cert = cert
        self.ambiente = ambiente
        self.base = BASES[ambiente]

    # ------------------------------------------------------------------
    # transporte
    # ------------------------------------------------------------------

    def _chamar(self, metodo: str, url: str, corpo: dict | None = None) -> Resposta:
        partes = urlsplit(url)
        caminho = partes.path + (f"?{partes.query}" if partes.query else "")

        headers = {"Accept": "application/json", "User-Agent": "nfse-app/0.1"}
        dados = None
        if corpo is not None:
            dados = json.dumps(corpo).encode("utf-8")
            headers["Content-Type"] = "application/json"

        with _contexto_ssl(self.cert) as ctx:
            conn = http.client.HTTPSConnection(
                partes.hostname, partes.port or 443, context=ctx, timeout=TIMEOUT
            )
            try:
                conn.request(metodo, caminho, body=dados, headers=headers)
                resp = conn.getresponse()
                bruto = resp.read()
                status = resp.status
                encoding = (resp.getheader("Content-Encoding") or "").lower()
            except ssl.SSLError as e:
                raise ErroSefin(
                    f"handshake TLS falhou — o certificado foi aceito? ({e})"
                ) from e
            except OSError as e:
                raise ErroSefin(f"não consegui falar com a SEFIN: {e}") from e
            finally:
                conn.close()

        if encoding == "gzip" and bruto[:2] == b"\x1f\x8b":
            bruto = gzip.decompress(bruto)

        try:
            dados_resp = json.loads(bruto) if bruto else None
        except (ValueError, UnicodeDecodeError):
            dados_resp = None

        return Resposta(status=status, corpo=dados_resp, bruto=bruto)

    # ------------------------------------------------------------------
    # operações
    # ------------------------------------------------------------------

    def dps_ja_existe(self, id_dps: str) -> bool:
        """
        Diz se essa DPS já foi processada. É a checagem que evita nota
        duplicada depois de uma falha de rede, e a que confirma se um
        número de DPS já foi usado.
        """
        r = self._chamar("HEAD", f"{self.base}/dps/{id_dps}")
        if r.status == 404:
            return False
        if r.ok:
            return True
        raise ErroSefin(
            f"consulta da DPS devolveu {r.status}", status=r.status, corpo=r.corpo
        )

    def nfse_da_dps(self, id_dps: str) -> dict | None:
        """Recupera a NFS-e gerada a partir do ID da DPS, se houver."""
        r = self._chamar("GET", f"{self.base}/dps/{id_dps}")
        if r.status == 404:
            return None
        if not r.ok:
            raise ErroSefin(
                f"consulta da DPS devolveu {r.status}", status=r.status, corpo=r.corpo
            )
        return r.corpo

    def emitir(self, corpo: dict) -> dict:
        """
        Envia a DPS assinada e devolve a resposta da SEFIN, com a chave de
        acesso e o XML da NFS-e.

        `corpo` vem de `assinar.corpo_requisicao()`.

        TRAVA DE AMBIENTE: antes de enviar, confere que o campo tpAmb
        dentro do XML corresponde ao servidor para onde vai. Emitir em
        produção exige que as DUAS coisas digam produção, deliberadamente
        — assim ninguém emite nota com valor fiscal por engano ao trocar
        só uma das configurações.
        """
        self._conferir_ambiente(corpo)
        r = self._chamar("POST", f"{self.base}/nfse", corpo)
        if not r.ok:
            raise ErroSefin(
                f"a SEFIN recusou a emissão (HTTP {r.status})",
                status=r.status,
                corpo=r.corpo,
            )
        return r.corpo or {}

    def _conferir_ambiente(self, corpo: dict) -> None:
        """O tpAmb do XML tem que casar com o servidor de destino."""
        import base64 as _b64
        import gzip as _gzip
        import re as _re

        try:
            xml = _gzip.decompress(_b64.b64decode(corpo["dpsXmlGZipB64"]))
        except Exception as e:
            raise ErroSefin(f"não consegui ler o corpo da requisição: {e}") from e

        m = _re.search(rb"<tpAmb>\s*(\d)\s*</tpAmb>", xml)
        if not m:
            raise ErroSefin("o XML não declara tpAmb — recusando por precaução")

        tp_amb = m.group(1).decode()
        esperado = "1" if self.ambiente == "producao" else "2"

        if tp_amb != esperado:
            nome = {"1": "produção (VALOR FISCAL)", "2": "homologação (teste)"}
            raise ErroSefin(
                f"ambiente inconsistente, emissão recusada.\n"
                f"  o XML diz tpAmb={tp_amb} — {nome[tp_amb]}\n"
                f"  o destino é '{self.ambiente}' — {self.base}\n"
                f"  os dois precisam concordar antes de emitir"
            )

    def diagnostico(self) -> dict:
        """
        Confere, antes de qualquer emissão, se o caminho está aberto:
        certificado válido e handshake mTLS fechando.
        """
        resultado = {
            "ambiente": self.ambiente,
            "base": self.base,
            "titular": self.cert.titular,
            "dias_para_vencer": self.cert.dias_para_vencer(),
        }
        try:
            # uma DPS que não existe: 404 já prova que o handshake fechou
            self.dps_ja_existe("DPS" + "0" * 42)
            resultado["mtls"] = "ok"
        except ErroSefin as e:
            resultado["mtls"] = f"falhou: {e}"
        return resultado


def proximo_numero_dps(sefin: Sefin, montar_id, inicio: int, limite: int = 50) -> int:
    """
    Descobre o próximo número de DPS livre, perguntando à SEFIN.

    `montar_id` recebe um número e devolve o ID de DPS correspondente.
    Começa em `inicio` (o contador local) e sobe até achar um número que
    a SEFIN ainda não conhece — assim o contador local pode dessincronizar
    sem estragar nada: quem manda é a SEFIN.
    """
    for n in range(inicio, inicio + limite):
        if not sefin.dps_ja_existe(montar_id(n)):
            return n
    raise ErroSefin(
        f"{limite} números a partir de {inicio} já estavam usados — "
        "o contador local está muito defasado, confira antes de seguir"
    )
