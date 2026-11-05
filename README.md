# Emissor de NFS-e com ChatGPT ou Claude

O assistente de IA lê os pedidos de nota fiscal que chegam no seu Gmail, organiza numa fila, mostra os dados para você conferir e, com o seu ok, emite a NFS-e pelo Sistema Nacional (o Emissor Nacional do gov.br). Ele também gera o PDF da nota e responde ao cliente.

Funciona no **app do ChatGPT** ou no **app do Claude**, para computador. O programa da emissão é o mesmo nos dois.

Você não precisa saber programar. O próprio assistente conduz a instalação, passo a passo, e explica cada coisa.

> **Aviso.** Este projeto é distribuído como está, sem garantia. Ele não substitui a sua contabilidade: os códigos de serviço, o regime e a alíquota da sua empresa são responsabilidade sua e de quem faz a sua contabilidade. Nota fiscal emitida não tem desfazer. Use por sua conta e risco (ver `LICENSE`).

## O que você precisa

- **Uma empresa que já emite NFS-e pelo Emissor Nacional** (https://www.nfse.gov.br/EmissorNacional), no **Simples Nacional (ME ou EPP)**.
- **Certificado digital A1 da empresa**: o arquivo `.pfx` e a senha dele. Não sabe o que é? Tudo bem, o assistente explica no primeiro passo.
- **Um dos dois apps, no computador** (Windows ou Mac):
  - **ChatGPT**, num plano com ChatGPT Work e tarefas agendadas; ou
  - **Claude**, na aba **Code**, num plano com tarefas agendadas.
- **O Gmail** onde chegam os pedidos de nota.
- **Uma nota já emitida pelo portal**, em PDF e XML. Ela serve de modelo.

## Como instalar

1. **Baixe este projeto.** No GitHub, abra **Releases** e baixe o `.zip` da versão mais recente (ou **Code > Download ZIP**). Descompacte numa pasta do seu computador, por exemplo `Documentos/Emissor NFS-e`.
2. **Abra o projeto no app:**
   - **ChatGPT:** crie um projeto local com essa pasta (**Edit project > Add folder**).
   - **Claude:** na aba **Code**, comece uma sessão escolhendo essa pasta.
3. **Deixe o app pedindo a sua aprovação antes de rodar comandos.**
   - **ChatGPT:** "Ask for approval", no controle abaixo da caixa de mensagem. Não use "Full access".
   - **Claude:** o modo que pede permissão ("Ask permissions"). Não use "Bypass permissions" nem o modo automático.
   O motivo está na nota de segurança abaixo.
4. **Escreva no chat:** `configurar`

A partir daí o assistente segue o roteiro do arquivo `INSTALACAO.md`: são 11 passos, e ele guarda onde parou. Se você interromper, é só abrir o projeto de novo e escrever `continuar a configuração`.

## Como fica o dia a dia

1. Nos horários que você escolher, uma tarefa agendada olha o Gmail e coloca os pedidos novos na fila (`fila.csv`, que abre no Excel).
2. O assistente mostra o resumo de cada pedido e pergunta se pode emitir.
3. Você confere e responde `emitir`. O app pede permissão para usar a internet: é o envio para a Receita. Aprove.
4. A nota sai, o PDF é gerado, e a resposta ao cliente é enviada ou fica em rascunho, como você preferir.

**Nada é emitido sem o seu ok.**

## Atualizações

A Receita muda o formato da nota de tempos em tempos (a próxima mudança é a da NT 009, da Reforma Tributária). O roteiro confere isso antes do teste e antes da primeira nota real, e para se o formato mudou. Quando sair uma versão nova deste projeto, ela aparece em **Releases**.

---

## Nota de segurança: por que roda no seu computador

**O certificado digital assina em nome da sua empresa.** Quem tem o arquivo `.pfx` e a senha consegue emitir nota fiscal como se fosse você. Por isso este projeto foi desenhado para que o certificado nunca saia do seu computador:

- **A emissão roda no app, no seu computador, e não na nuvem.** As versões em nuvem dos assistentes (ChatGPT Work na nuvem, Claude na web) não têm, hoje (novembro de 2026), um lugar documentado para guardar certificado e senha com segurança. Para emitir pela nuvem, o certificado teria que ser enviado aos servidores da empresa do assistente.
- **O arquivo `.pfx` fica numa pasta sua, fora deste projeto** e fora de pastas que sincronizam com a nuvem (Google Drive, OneDrive, iCloud). Ele nunca vai para o chat, para o GitHub nem para o email.
- **A senha fica no cofre do sistema**: o Gerenciador de Credenciais no Windows ou as Chaves no Mac. É **você** quem digita a senha, no Terminal, num comando que confere se ela abre o certificado. **Ela nunca é digitada no chat.**
- **A única conexão da emissão é com a Receita** (`sefin.nfse.gov.br`), mais a consulta de CEP (ViaCEP). E o app pede a sua permissão antes de usar a internet.

**O que você precisa saber, com honestidade:**

- **O assistente vê os dados das notas:** nome e CNPJ dos clientes, valores e descrições. Ele não precisa ver nem o conteúdo do certificado nem a senha, e as regras do projeto (`AGENTS.md`) proíbem que ele tente.
- **Qualquer programa rodando na sua conta pode pedir a senha ao cofre, inclusive o assistente.** O que impede isso é a combinação de três coisas: as regras do projeto, o modo que pede a sua aprovação (o app mostra o que vai rodar e pede o seu ok) e você ler o que ele pede antes de aprovar. **Por isso, não libere tudo sem aprovação neste projeto.**
- **Se a senha aparecer no chat por engano, troque a senha do certificado.** Na dúvida, fale com quem emitiu o certificado.
- **O certificado A1 vence em 1 ano.** A rotina avisa 45 dias antes.

---

## O que tem aqui

| Pasta ou arquivo | O que é |
|---|---|
| `INSTALACAO.md` | O roteiro de instalação que o assistente segue com você |
| `AGENTS.md` | As regras que o assistente lê antes de qualquer trabalho neste projeto |
| `CLAUDE.md` | Faz o Claude ler o `AGENTS.md` (o ChatGPT lê o `AGENTS.md` direto) |
| `.agents/skills/emissao-nfse/` | O procedimento da rotina: achar pedidos, preparar, emitir, responder |
| `.claude/skills/emissao-nfse/` | Aponta o Claude para o mesmo procedimento |
| `codigo/` | O programa da emissão (Python), com os testes |
| `modelos/` | Modelos dos arquivos de configuração |
| `docs/oficial/` | A documentação oficial do Sistema Nacional NFS-e (manuais, leiautes, esquemas, NT 008 e NT 009) |
| `docs/GUIA-TECNICO.md` | Detalhes técnicos e as armadilhas da API, para quem quiser entender ou adaptar |

Os seus arquivos (`empresa.json`, `rotina.md`, `fila.csv`, `notas/`) ficam só no seu computador. O `.gitignore` impede que vão para o GitHub.

## Limites

- Cobre o caso mais comum: **Simples Nacional ME/EPP**, ISS tributável e não retido, cliente no Brasil, sem retenções federais e sem os campos da Reforma Tributária (IBS/CBS). Outro caso pede adaptação no código, seguindo `docs/oficial/`.
- O computador precisa estar ligado e o app aberto nos horários da rotina.
- Nota fiscal não tem desfazer: erro vira cancelamento ou substituição no portal. Confira antes de dizer `emitir`.
