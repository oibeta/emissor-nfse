---
name: emissao-nfse
description: Acha pedidos de nota fiscal de serviço no Gmail, põe na fila, mostra o resumo para aprovação e, com o ok da pessoa, emite a NFS-e pelo Sistema Nacional, gera o PDF e responde ao cliente. Use quando a rotina agendada de NFS-e rodar, ou quando a pessoa disser "tem pedido de nota?", "emitir", "emitir a nota", "fila de notas", "responder o cliente". Não use para nota de produto (NF-e) nem antes de a instalação terminar (ver INSTALACAO.md).
---

# Emissão de NFS-e: o dia a dia

Antes de tudo: leia o `AGENTS.md`, o `empresa.json` e o `rotina.md`. Se o `progresso.md` tiver passo sem `[x]`, pare e siga `INSTALACAO.md`.

São três partes. **A Rotina nunca aprova nem emite.**

---

## Parte 1: Rotina (rodada agendada)

1. `python codigo/nfse.py certificado`. Se faltar menos de 45 dias para vencer, inclua o aviso no relatório.
2. Busque no Gmail com a busca do `rotina.md`.
3. Para cada thread, pule se o pedido já está na fila (`python codigo/nfse.py listar`). Para cada pedido novo:
   - leia **a thread inteira**, com os anexos; vale o valor **mais recente**, porque correções chegam em resposta;
   - leia os dados do **tomador** só da parte que fala do tomador, nunca do bloco do prestador (a própria empresa);
   - siga o que o `rotina.md` diz sobre o formato daquele remetente;
   - monte `pedidos/<id_pedido>.json` no formato de `modelos/pedido.exemplo.json`. O `id_pedido` é o identificador do pedido no email; sem um, use `aaaa-mm-dd-<remetente>`. Vencimento em dias: `prazo_dias`, com `{vencimento}` na descrição onde a data deve aparecer. Data fechada: `vencimento` (aaaa-mm-dd).
   - `python codigo/nfse.py adicionar pedidos/<id_pedido>.json`
4. Relate **um resumo por pedido**, no formato abaixo, e peça o ok. Termine a rodada aí.

```
Pedido PED-2026-0001 · nota de TESTE, sem valor fiscal     (ou: nota REAL, com valor fiscal)
Cliente: CLIENTE EXEMPLO S.A. (CNPJ 11.222.333/0001-81)
Valor: R$ 1.500,00 · Competência: 10/2026 · Vencimento: 30 dias após a emissão
Descrição: Prestação de serviço conforme proposta 0001. Vencimento: <data>.
Alertas: nenhum

Para emitir, responda: emitir PED-2026-0001
Se algo estiver errado, me diga o que corrigir.
```

Se não houver pedido novo nem aviso, termine sem relatar nada.

---

## Parte 2: Emitir (quando a pessoa responde)

Só com o ok explícito da pessoa, nesta conversa, para aquele pedido.

1. **Correção:** se a pessoa corrigir algum dado, rode `python codigo/nfse.py recusar <id>`, corrija o JSON, troque o `id_pedido` (acrescente `-2`), adicione de novo e mostre o resumo novo. Só emita depois do ok no resumo corrigido.
2. **Ok:** `python codigo/nfse.py aprovar <id> <ambiente do empresa.json>`.
3. `python codigo/nfse.py emitir <id>`. O app pede internet: diga que é o envio para a Receita.
4. Leia a saída:
   - **"EMITIDA"**: siga para a Parte 3.
   - **"PAROU: SEFIN recusou ..."**: explique o erro em linguagem simples, usando `docs/oficial/codigos-rejeicao.md`, e o que corrigir. Não tente de novo sozinho.
   - **"PAROU: a conexão caiu ..."** ou status "Emitindo": rode `python codigo/nfse.py verificar <id>` e siga o que ele disser. **Nunca reenvie** uma DPS que virou nota.
   - **"A NOTA FOI EMITIDA, mas o PDF falhou"**: a nota existe. O PDF sai da consulta pública (https://www.nfse.gov.br/consultapublica), pela chave de acesso. Avise a pessoa.

---

## Parte 3: Responder ao cliente

1. Monte a resposta **na thread do pedido**, com a mensagem padrão do `rotina.md`, e anexe o PDF (`arquivo_pdf` da fila). Anexe também o XML se o `rotina.md` disser que sim.
2. Siga o modo do `rotina.md`:
   - **rascunho:** crie o rascunho e diga à pessoa que ele está pronto para conferir e enviar.
   - **enviar:** envie e confirme para quem foi enviado.
   - Se o anexo não funciona (anotado no `rotina.md`): sempre rascunho, e diga qual arquivo da pasta `notas/` ela anexa.
3. `python codigo/nfse.py respondido <id> <enviado|rascunho>`.
4. Feche com uma linha: número da nota, cliente, valor e se a resposta foi enviada ou ficou em rascunho.
