---
title: Fontes da documentação oficial
description: De onde veio cada arquivo desta pasta e os links das APIs do Sistema Nacional NFS-e.
date: 2026-10-24
---

# Fontes da documentação oficial

Os arquivos foram baixados do gov.br em 23/10/2026; os da produção restrita (NT 009), em 24/10/2026. **A produção e a produção restrita podem estar em leiautes diferentes**, mesmo com o mesmo número de versão. Antes de começar, confira se saiu versão nova para cada ambiente:

- Documentação atual (produção): https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/documentacao-atual
- Documentação de homologação (testes): https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/producao-restrita
- Reforma Tributária (RTC) e notas técnicas: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/rtc
- Logos da NFS-e: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/logos-da-nfs-e

## O que é cada arquivo

| Arquivo | O que é | Quando usar |
|---|---|---|
| `manuais/manual-contribuintes-emissor-publico-api-sistema-nacional-nfs-e-v1-2-out2025.pdf` | Manual do contribuinte da API de emissão (SEFIN Nacional): autenticação, endpoints, fluxo | **Leia primeiro.** |
| `manuais/manual-contribuintes-apis-adn-sistema-nacional-nfse.pdf` | Manual das APIs do ADN (Ambiente de Dados Nacional): consulta e distribuição de documentos | Para baixar notas emitidas e eventos |
| `manuais/guia-emissorpubliconacionalweb_snnfse-ern-v12.pdf` | Guia do portal Web (Emissor Nacional) | Para entender os campos pela tela |
| `anexos/anexo_i-sefin_adn-dps_nfse-snnfse-v1-01-...xlsx` | **Leiaute da DPS e da NFS-e campo a campo, e as regras de validação** | Para montar o XML |
| `anexos/anexo_ii-sefin_adn-pedregevt_evt-...xlsx` | Leiaute dos eventos (cancelamento, substituição etc.) | Para cancelar nota |
| `anexos/anexo_a-municipio_ibge-paises_iso2-...xlsx` | Códigos IBGE dos municípios e ISO dos países | `cloc_emi`, `cloc_prestacao` |
| `anexos/anexo_b-nbs2-lista_servico_nacional-...xlsx` | Lista de serviços nacional e NBS | `ctrib_nac` |
| `anexos/anexo-c-indop-ibscbs-...xlsx` | Indicadores de operação do IBS/CBS (Reforma Tributária) | Quando o IBS/CBS for obrigatório para você |
| `esquemas-xsd/nfse-esquemas_xsd-v1-01-20260209.zip` | Esquemas XSD da **produção** (09/02/2026), os mesmos de `codigo/schemas/` | Validar o XML de produção |
| `esquemas-xsd/nfse-esquemas_xsd-prodrest-v1-01-20261020.zip` | Esquemas XSD da **produção restrita** (20/10/2026, NT 009), os mesmos de `codigo/schemas_restrita/` | Validar o XML de teste |
| `anexos/anexo_i-sefin_adn-dps_nfse-snnfse_prodrest-...xlsx` | Anexo I da produção restrita (20/10/2026) | Montar o XML de teste |
| `notas-tecnicas/nt-008-se-cgnfse-danfse-20260714-v1-02.pdf` | NT 008/2026: suspensão da API do PDF e o modelo DANFSe v2.0 | Gerar o PDF |
| `notas-tecnicas/nt-009-se-cgnfse-rtc-20260911-v1-01.pdf` | NT 009/2026: mudanças de leiaute da Reforma Tributária (entre elas, `finNFSe` em `infDPS`), já em vigor na produção restrita | Entender E1235 e o que muda na produção |
| `logos/logo-nfse-horizontal.png` | Logo oficial | Cabeçalho do DANFSe |
| `codigos-rejeicao.md` | Os códigos de rejeição da SEFIN, extraídos do Anexo I (abas RN DPS_NFS-e e RN_RECEPCAO_DPS) | Entender um erro |

## Endereços das APIs

| | Produção restrita (testes) | Produção |
|---|---|---|
| SEFIN Nacional (emissão) | `https://sefin.producaorestrita.nfse.gov.br/SefinNacional` | `https://sefin.nfse.gov.br/SefinNacional` |
| Documentação Swagger da SEFIN | https://sefin.producaorestrita.nfse.gov.br/API/SefinNacional/docs/index | https://sefin.nfse.gov.br/SefinNacional/docs/index |
| ADN (contribuintes) | `https://adn.producaorestrita.nfse.gov.br/contribuintes` | `https://adn.nfse.gov.br/contribuintes` |
| Documentação Swagger do ADN | https://adn.producaorestrita.nfse.gov.br/contribuintes/docs/index.html | https://adn.nfse.gov.br/contribuintes/docs/index.html |

As páginas Swagger exigem o certificado digital instalado no navegador (mTLS). Sem ele, respondem `403`.

Rotas usadas na emissão (detalhes no manual):

- `POST /nfse`: envia a DPS assinada. Corpo: `{"dpsXmlGZipB64": "..."}`. Resposta com `chaveAcesso` e `nfseXmlGZipB64`.
- `GET /nfse/{chaveAcesso}`: consulta a nota.
- `HEAD /dps/{id}` e `GET /dps/{id}`: diz se a DPS já virou nota. Use antes de enviar, para não emitir duas vezes.
- Eventos (cancelamento etc.): ver manual e Anexo II.

## Outros links úteis

- Emissor Nacional (portal Web): https://www.nfse.gov.br/EmissorNacional
- Consulta pública por chave de acesso (baixa o PDF, sem login): https://www.nfse.gov.br/consultapublica
- Alíquotas de ISSQN por município: https://www.gov.br/nfse/pt-br/biblioteca/aliquotas
- Códigos de tributação nacional e NBS: https://www.gov.br/nfse/pt-br/mei-e-demais-empresas/codigos-de-tributacao-nacional-nbs
