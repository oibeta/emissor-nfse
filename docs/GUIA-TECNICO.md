---
title: Guia técnico do emissor
description: Como o emissor fala com a API do Sistema Nacional NFS-e, e as armadilhas que custaram horas a quem escreveu o código.
date: 2026-10-24
---

# Guia técnico do emissor

Para quem quer entender, conferir ou adaptar o código. A pessoa que só usa o emissor não precisa ler isto.

## O caminho de uma nota

```
pedidos/<id>.json ──adicionar──► fila.csv (Aguardando aprovação)
                                    │  ok da pessoa no chat
                                    ▼
                                 aprovar <id> <ambiente>  ──►  Aprovado
                                    │
                                 emitir <id>
                                    ├─ confere status e ambiente
                                    ├─ CEP ─► ViaCEP (logradouro, bairro, código IBGE)
                                    ├─ número da DPS livre?  HEAD /dps/{id}
                                    ├─ monta a DPS (dps.py) e valida no XSD (validar.py)
                                    ├─ assina (assinar.py)
                                    ├─ grava "Emitindo" na fila   ◄── trava antes de enviar
                                    ├─ POST /nfse (sefin.py, mTLS)
                                    ├─ grava o XML da nota em notas/
                                    └─ gera o PDF (danfse.py)  ──►  Emitida
```

| Módulo | Faz | Dependências |
|---|---|---|
| `nfse.py` | O comando único: fila, aprovação, emissão, verificação | os outros |
| `dps.py` | Monta o XML da DPS; dias úteis e feriados nacionais | só a biblioteca padrão |
| `validar.py` | Valida contra o XSD oficial do ambiente (`schemas/` produção, `schemas_restrita/` teste) | lxml |
| `assinar.py` | Lê o `.pfx` e assina | lxml, signxml, cryptography |
| `sefin.py` | Conversa com a API por mTLS, com trava de ambiente | cryptography |
| `danfse.py` | Gera o PDF a partir do XML | pymupdf, segno, lxml |
| `senha.py` | Guarda e lê a senha no cofre do sistema | keyring |
| `testar_offline.py` | Testa montagem, XSD, assinatura e vencimento sem rede | |
| `testar_fila.py` | Testa as travas da fila e da emissão com dublês | |

## Ambientes e endereços

| | Produção restrita (teste) | Produção |
|---|---|---|
| SEFIN Nacional | `https://sefin.producaorestrita.nfse.gov.br/SefinNacional` | `https://sefin.nfse.gov.br/SefinNacional` |
| `tpAmb` no XML | `2` | `1` |

Rotas usadas: `POST /nfse` (emite; corpo `{"dpsXmlGZipB64": base64(gzip(xml assinado))}`; resposta com `chaveAcesso` e `nfseXmlGZipB64`), `HEAD /dps/{id}` e `GET /dps/{id}` (a DPS virou nota?). Mais em `docs/oficial/FONTES.md`.

## As armadilhas

### A assinatura tem três detalhes fora do padrão

Errar qualquer um dá rejeição sem mensagem que explique a causa.

1. Canonicalização **exclusiva com comentários**: `http://www.w3.org/2001/10/xml-exc-c14n#WithComments`.
2. O elemento `Signature` **sem o prefixo `ds:`**.
3. **SHA-256** na assinatura e no digest.

A assinatura é *enveloped*, referencia o `Id` do `infDPS` e entra como irmã dele, dentro de `DPS`.

### O `Id` da DPS é conferido

`"DPS"` + IBGE do emitente (7) + tipo de inscrição (1; `2` = CNPJ) + CNPJ (14) + série (5) + número (15). Divergência dá **E0004**.

### A série do portal não serve para a API (E0010)

Notas emitidas pelo portal saem com série **70000**, que é a faixa do emissor Web. Por aplicativo próprio a faixa é **00001 a 49999**.

### Número da DPS e número da NFS-e são contagens diferentes

- **Série e número da DPS:** de cada emissor. No portal o sistema numera sozinho; na API o número é seu. O `nfse.py` parte do maior número já usado na fila e pergunta à SEFIN se está livre.
- **Número da NFS-e (`nNFSe`):** sequência da empresa no município, a mesma para portal e API. Salto na sequência quer dizer que alguma nota saiu por outro caminho.

Leia o número da nota na tag `<nNFSe>` do XML devolvido, nunca nos dígitos finais da chave de acesso: ali ficam um código aleatório e o dígito verificador.

### Relógio adiantado dá E0008

A `dhEmi` não pode ser posterior à hora de processamento da SEFIN. O `dps.py` usa a hora de Brasília menos 30 segundos. Se ainda assim vier E0008, o `nfse.py` lê `dataHoraProcessamento` na resposta, refaz a DPS com essa hora e reenvia uma vez.

### Ambiente no XML e no endereço têm que bater (E0006)

O `sefin.py` recusa enviar quando o `tpAmb` do XML não corresponde ao ambiente escolhido. Uma camada acima, o `nfse.py` recusa emitir quando o ambiente aprovado na fila não é o do `empresa.json`.

### Teste e produção podem estar em leiautes diferentes (E1235)

A Receita muda primeiro a produção restrita e só depois a produção, e as duas continuam dizendo "versão 1.01". Em 20/10/2026 a produção restrita passou para os esquemas da **NT 009**, que exigem o campo `finNFSe` (finalidade da nota, `0` = regular) dentro de `infDPS`, entre `cMotivoEmisTI` e `chNFSeRej`. Sem ele, a SEFIN recusa com **E1235** ("invalid child element 'cLocEmi'"). A produção ainda usa os esquemas de 09/02/2026 e não aceita o campo.

Por isso o código tem dois pacotes: `codigo/schemas/` (produção) e `codigo/schemas_restrita/` (produção restrita). O `validar.py` escolhe pelo `tpAmb` da DPS, e o `dps.py` só põe `finNFSe` quando o ambiente é a restrita.

**Quando a produção adotar a NT 009** (veja o cronograma em https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/documentacao-atual):
1. baixe o pacote XSD novo da produção para `codigo/schemas/`;
2. no `dps.py`, tire o `if` e envie `finNFSe` sempre;
3. rode os dois testes. O `testar_offline.py` vai falhar no ponto que confere que a produção não leva `finNFSe`: troque essa conferência.

E1235 em outro campo é o mesmo tipo de problema: compare o pacote XSD do ambiente com o da pasta antes de mexer no XML.

### O XSD oficial da produção tem um defeito

No pacote da produção, o tipo `TSSerieDPS` traz o pattern `^0{0,4}\d{1,5}$`. Em XML Schema o pattern já é ancorado, e `^` e `$` viram caracteres literais: nenhuma série real passa. A SEFIN não valida por esse pattern. O `validar.py` ignora esse erro, e só esse. O pacote da produção restrita de 20/10/2026 já corrigiu o pattern.

### Endereço do tomador

A SEFIN aceita a DPS sem endereço do tomador, e a nota sai sem ele: a API não completa pelo CNPJ (o portal completa). Por isso o `nfse.py` monta o endereço pelo CEP (ViaCEP, que também dá o código IBGE do município) e só leva do email o número e o complemento.

### O PDF não vem da API

O endpoint de DANFSe foi suspenso em 03/08/2026 pela **NT 008/2026** (`docs/oficial/notas-tecnicas/`). O `danfse.py` escreve os valores do XML num molde do modelo oficial DANFSe v2.0, criado a partir de um PDF do portal com `--modelo`, e desenha o QR Code da consulta pública. Notas de teste levam a faixa "NFS-e SEM VALIDADE JURÍDICA" (item 2.4.3 da NT). O plano B é a consulta pública pela chave: https://www.nfse.gov.br/consultapublica.

## Nunca emitir duas vezes

Nota duplicada não tem desfazer. Três camadas:

1. Só se emite linha com status `Aprovado`. Depois de emitida, ela não volta para `Aprovado`.
2. O status `Emitindo` e o número da DPS são gravados **antes** do envio. Se o processo morrer no meio, a linha fica travada até alguém rodar `verificar`.
3. Linha com número de DPS de uma tentativa anterior: antes de qualquer coisa, a SEFIN é consultada (`HEAD /dps/{id}`). Se a DPS virou nota, a emissão para.

## Adaptar para outro caso

O `dps.py` cobre Simples Nacional ME/EPP, ISSQN tributável e não retido, sem retenções federais e sem IBS/CBS. Para outro caso:

1. Ache os grupos no Anexo I (`docs/oficial/anexos/anexo_i-...xlsx`): cada linha é um campo, com tipo, tamanho, obrigatoriedade e regras.
2. Acrescente os grupos em `monta_dps()`, na ordem do XSD.
3. Valide contra o XSD e emita em produção restrita até a SEFIN aceitar.
4. O `danfse.py` recusa os grupos que ele não sabe desenhar. Amplie a lista `NAO_COBERTO` e as posições seguindo a NT 008.
5. Rode `testar_offline.py` e `testar_fila.py`.
