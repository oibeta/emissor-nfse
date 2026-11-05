"""
A senha do certificado digital, guardada no cofre do sistema operacional.

    python codigo/senha.py          (guarda a senha; uma vez só)

Quem roda este comando é a PESSOA, no Terminal (Mac) ou no PowerShell
(Windows). Nunca o agente, e a senha nunca é digitada no chat.

ONDE A SENHA FICA
-----------------
No cofre do sistema: Gerenciador de Credenciais no Windows, Chaves (Keychain)
no Mac. Ele é protegido pela conta do computador: a senha não fica em arquivo
do projeto, em variável de ambiente nem no histórico do terminal. O acesso é
pelo pacote `keyring`, usado em escala e mantido.

POR QUE CONFERIR ANTES DE GUARDAR
---------------------------------
Senha errada guardada é pior que senha nenhuma: tudo parece pronto, e o erro
só aparece na hora de emitir. Abrir o .pfx aqui custa um segundo.

Dependências: pip install keyring cryptography
"""
from __future__ import annotations

import getpass
import json
import os
import sys
from pathlib import Path

SERVICO = "nfse-chatgpt-work"
EMPRESA = Path(__file__).resolve().parent.parent / "empresa.json"


class SenhaAusente(Exception):
    """A senha não está em lugar nenhum que este módulo saiba procurar."""


def _usuario() -> str:
    """Uma senha por CNPJ, para quem emite por mais de uma empresa."""
    return json.loads(EMPRESA.read_text(encoding="utf-8"))["cnpj"]


def obter() -> str:
    """
    A senha, sem perguntar nada. Primeiro NFSE_SENHA no ambiente, depois o
    cofre do sistema. Faltando, é erro com instrução, nunca um input():
    quem chama pode estar numa tarefa agendada, sem ninguém na frente.
    """
    if os.environ.get("NFSE_SENHA"):
        return os.environ["NFSE_SENHA"]
    import keyring
    guardada = keyring.get_password(SERVICO, _usuario())
    if guardada:
        return guardada
    raise SenhaAusente(
        "a senha do certificado não está guardada. A pessoa precisa rodar,\n"
        "no Terminal ou no PowerShell, uma vez:  python codigo/senha.py"
    )


def esta_guardada() -> bool:
    try:
        obter()
        return True
    except Exception:
        return False


def confere(pfx: Path, senha: str) -> str:
    """Abre o .pfx com a senha. Devolve a validade; levanta erro se não abrir."""
    from cryptography.hazmat.primitives.serialization import pkcs12
    try:
        _, cert, _ = pkcs12.load_key_and_certificates(pfx.read_bytes(), senha.encode("utf-8"))
    except Exception:
        raise ValueError("essa senha não abre o certificado") from None
    if cert is None:
        raise ValueError("o arquivo abriu, mas não traz certificado")
    return f"{cert.not_valid_after_utc:%d/%m/%Y}"


def main() -> int:
    if not EMPRESA.exists():
        print(f"Falta o arquivo {EMPRESA.name}. Termine antes o passo dos dados da empresa.")
        return 1
    pfx = Path(json.loads(EMPRESA.read_text(encoding="utf-8")).get("certificado_pfx", ""))
    if not pfx.is_file():
        print(f"Não achei o certificado em: {pfx}\nConfira o campo certificado_pfx no {EMPRESA.name}.")
        return 1

    print("\nGUARDAR A SENHA DO CERTIFICADO DIGITAL\n")
    print("A senha vai para o cofre do seu computador. Ela não aparece na tela")
    print("enquanto você digita: isso é normal. Digite e aperte Enter.\n")
    senha = getpass.getpass("Senha do certificado: ")
    if not senha:
        print("\nSenha vazia. Nada foi guardado.")
        return 1
    try:
        validade = confere(pfx, senha)
    except ValueError as e:
        print(f"\n{e}. Nada foi guardado. Confira a senha e rode de novo.")
        return 1

    import keyring
    keyring.set_password(SERVICO, _usuario(), senha)
    print(f"\nPronto. A senha abre o certificado (válido até {validade}) e foi guardada.")
    print("Pode voltar para o ChatGPT e dizer: senha guardada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
