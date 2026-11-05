# Emissor de NFS-e: regras para o agente (ChatGPT ou Claude)

Este projeto emite NFS-e pelo Sistema Nacional (API SEFIN Nacional) a partir de pedidos que chegam no Gmail. Nota fiscal não tem desfazer. Na dúvida, pare e pergunte.

## Por onde começar

- Se `progresso.md` não existe, ou tem passo sem `[x]`: a instalação não terminou. Quando a pessoa disser "configurar", "continuar a configuração" ou pedir para emitir, siga `INSTALACAO.md` a partir do primeiro passo aberto.
- Instalação completa: o trabalho do dia a dia está no skill `emissao-nfse` (`.agents/skills/emissao-nfse/SKILL.md`). No Claude, o skill aparece por `.claude/skills/emissao-nfse/`, que só aponta para esse mesmo arquivo: mude o procedimento só no `.agents/`.

## Quem é a pessoa

Alguém que emite nota da própria empresa e **não é técnico**. Fale em português do Brasil, simples, uma coisa por vez. Explique termo técnico na primeira vez que ele aparecer. Comando que a pessoa precisa rodar: dê pronto para copiar, com o caminho completo, e diga onde colar (Terminal no Mac, PowerShell no Windows).

## Regras que não mudam

**Certificado e senha**
1. **Nunca peça a senha do certificado no chat.** Ela é guardada pela própria pessoa, com `python codigo/senha.py`, no Terminal. Se a pessoa colar a senha no chat: não repita, não grave em lugar nenhum, e recomende trocar a senha do certificado.
2. **Nunca leia a senha do cofre** (keyring, Gerenciador de Credenciais, Chaves) por conta própria, nem por código escrito na hora. Só os comandos de `codigo/nfse.py` usam a senha.
3. **Nunca abra, copie, mova, converta, envie ou anexe o arquivo `.pfx`.** Ele fica fora da pasta do projeto. Nunca o coloque na pasta do projeto nem no Git.

**Fila e emissão**
4. **A fila (`fila.csv`) só muda pelos comandos de `codigo/nfse.py`.** Nunca edite o arquivo direto.
5. **Só aprove com o ok explícito da pessoa, nesta conversa, para aquele pedido.** "Emitir", "pode emitir", "ok" em resposta ao resumo do pedido valem. Silêncio, ok antigo ou ok para outro pedido não valem.
6. **Em produção, o ok tem que ser para produção.** Antes de aprovar, diga o ambiente no resumo ("nota REAL, com valor fiscal" ou "nota de TESTE").
7. **Uma rodada agendada nunca aprova e nunca emite.** Ela só acha pedidos, põe na fila e mostra o resumo.
8. **Nunca troque o `ambiente` do `empresa.json` para `producao`** fora do passo 11 de `INSTALACAO.md`, e só depois que a pessoa digitar a frase de confirmação.
9. **Nunca tente emitir de novo um pedido em "Emitindo" ou "Erro" sem rodar `nfse.py verificar`.** Se a SEFIN disser que a DPS já virou nota, não reenvie.

**Código**
10. **Use os comandos de `codigo/nfse.py`.** Não reescreva a montagem do XML, a assinatura nem o envio: eles têm detalhes que a SEFIN exige e que não estão óbvios (ver `docs/GUIA-TECNICO.md`).
11. Se precisar mudar algo em `codigo/`, rode antes e depois `python codigo/testar_offline.py` e `python codigo/testar_fila.py`. Os dois têm que terminar com `ok`.
12. **Não use Git.** Este projeto não precisa de controle de versão: não rode `git` (status, diff, log, add, commit, nem para conferir formatação). A pasta pode estar dentro de um repositório maior, que não é deste projeto e cujo conteúdo não é da sua conta. Só use Git se a pessoa pedir explicitamente.
13. **Fique dentro da pasta do projeto.** Não leia, liste nem procure arquivos fora dela, com uma exceção: o caminho do certificado que a pessoa informou, e só pelos comandos de `codigo/`.

## Fontes de verdade

- `empresa.json`: dados fixos da empresa, ambiente, códigos, alíquota. Leia sempre do arquivo; nunca escreva esses valores de memória.
- `rotina.md`: como achar os pedidos, a mensagem padrão, o modo de resposta, a frequência.
- `docs/oficial/`: manual, anexos (leiaute campo a campo), esquemas XSD, NT 008 (PDF) e os códigos de rejeição da SEFIN. Servem para entender um campo ou um erro, nunca para escolher ou questionar os códigos fiscais da empresa: esses vêm das notas já emitidas.
- `docs/GUIA-TECNICO.md`: as armadilhas conhecidas da API.

## Comandos

Rode da raiz do projeto.

```
python codigo/nfse.py certificado              validade do certificado e da senha (sem internet)
python codigo/nfse.py conexao restrita         testa o caminho até a SEFIN (precisa de internet)
python codigo/nfse.py adicionar pedidos/<id>.json
python codigo/nfse.py listar
python codigo/nfse.py aprovar <id> <restrita|producao>
python codigo/nfse.py recusar <id>
python codigo/nfse.py emitir <id>              precisa de internet: o app vai pedir permissão
python codigo/nfse.py verificar <id>
python codigo/nfse.py respondido <id> <enviado|rascunho>
python codigo/danfse.py --modelo <pdf do portal>
python codigo/danfse.py <nota.xml> [saida.pdf]
```
