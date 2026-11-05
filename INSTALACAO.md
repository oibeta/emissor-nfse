# Roteiro de instalação

Este roteiro é para **você, agente**, conduzir a instalação com a pessoa. Ela não é técnica. Leia o `AGENTS.md` antes.

**O roteiro vale para o app do ChatGPT e para o app do Claude (aba Code).** Onde a tela muda, o passo traz as duas versões. Siga só a do app em que você está rodando, e anote qual é no `progresso.md`. Os nomes de menu podem mudar com as versões dos apps: se a pessoa não achar o que o passo diz, peça um print da tela e guie por ele.

## Como conduzir

- **Um passo por vez.** Diga em que passo estão ("Passo 3 de 11: o certificado digital"), o que vai acontecer e por quê, em duas ou três frases. Espere a pessoa terminar o que é dela antes de seguir.
- **Explique termo técnico na primeira vez:** certificado digital, XML, CNPJ do tomador, ambiente de teste, Terminal.
- **Comando que a pessoa roda:** pronto para copiar, com o caminho completo da pasta do projeto, e dizendo onde colar (Terminal no Mac; PowerShell no Windows: menu Iniciar, digite "PowerShell"). Comando que você roda: rode você mesmo.
- **Quando o app pedir permissão** (internet, arquivo fora da pasta), explique à pessoa o que é antes de ela aprovar.
- **Guarde o progresso.** No começo, se `progresso.md` não existir, crie-o com o modelo abaixo. Ao fim de cada passo, marque `[x]` e anote o que importa. Se a conversa for interrompida, retome do primeiro passo sem `[x]`.
- **Não pule passo.** Se um passo falhar, resolva ou pare ali e explique o que falta.

### Modelo do `progresso.md`

```markdown
# Progresso da instalação

- [ ] 1. Pré-requisitos
- [ ] 2. Instalar o emissor
- [ ] 3. Certificado digital e senha
- [ ] 4. Teste de segurança
- [ ] 5. Nota modelo: dados da empresa e PDF
- [ ] 6. Teste de leitura com 3 emails antigos
- [ ] 7. Nota de teste completa
- [ ] 8. Mensagem padrão de resposta
- [ ] 9. Enviar direto ou deixar em rascunho
- [ ] 10. Frequência e rotina agendada
- [ ] 11. Virar para produção

## Anotações
```

---

## Passo 1. Pré-requisitos

**Objetivo:** confirmar que dá para seguir antes de instalar qualquer coisa.

Pergunte, uma de cada vez, e explique quando a pessoa não souber:

1. **A empresa já emite NFS-e pelo Emissor Nacional?** É o portal do governo em https://www.nfse.gov.br/EmissorNacional. Se ela emite pela prefeitura, num site próprio do município, este projeto não serve: o município ainda não usa o Sistema Nacional.
2. **A empresa é do Simples Nacional, como ME ou EPP?** É o caso que o projeto cobre. MEI, Lucro Presumido ou Lucro Real: avise que o código precisa de adaptação e que vocês só seguem se ela quiser testar por conta e risco.
3. **Tem certificado digital A1 da empresa?** Explique:
   > O certificado digital é a "assinatura eletrônica" da empresa. Com ele, o sistema da Receita sabe que a nota foi emitida por vocês. O tipo **A1** é um arquivo no computador (termina em `.pfx` ou `.p12`) e vem com uma senha. O tipo **A3** fica num cartão ou num token USB e pede senha a cada uso: **esse não serve para automação**.
   - Não tem certificado? Ele é comprado de uma Autoridade Certificadora (empresas que vendem "e-CNPJ A1") e vale 1 ano. Pare aqui até ela ter.
   - Tem o A1, mas não acha o arquivo? Ele pode estar instalado só no Windows. Explique como exportar com a chave privada: menu Iniciar > "Gerenciar certificados de usuário" > Pessoal > Certificados > botão direito no certificado da empresa > Todas as tarefas > Exportar > "Sim, exportar a chave privada" > formato `.pfx` > definir uma senha.
4. **Tem uma nota já emitida pelo portal**, que dê para baixar em PDF e em XML? Vai ser o modelo no passo 5.
5. **Os pedidos de nota chegam por email no Gmail?**

**Pronto quando:** as cinco respostas forem sim. Anote no `progresso.md` o regime da empresa.

## Passo 2. Instalar o emissor

**Objetivo:** deixar o Python e as bibliotecas prontos.

1. Rode `python --version` (no Mac, tente também `python3 --version`). Precisa ser 3.10 ou mais novo.
2. Se não houver Python, guie a pessoa:
   - **Windows:** baixar em https://www.python.org/downloads/ e, na primeira tela do instalador, **marcar "Add python.exe to PATH"**. Depois, fechar e abrir de novo o app (ChatGPT ou Claude).
   - **Mac:** baixar em https://www.python.org/downloads/ e instalar.
3. Instale as dependências: `python -m pip install -r requirements.txt`. O app vai pedir permissão de internet: explique que é para baixar as bibliotecas.
4. Confira: `python -c "import lxml, signxml, cryptography, keyring, pymupdf, segno; print('ok')"`.

**Pronto quando:** o último comando imprimir `ok`.

## Passo 3. Certificado digital e senha

**Objetivo:** o certificado numa pasta segura e a senha no cofre do computador, sem passar pelo chat.

1. Explique por que isso importa:
   > Com o arquivo do certificado e a senha, qualquer pessoa emite nota em nome da sua empresa. Por isso o arquivo vai ficar numa pasta só sua, fora deste projeto e fora de pastas que sincronizam com a nuvem. E a senha vai para o cofre do computador, que só a sua conta abre. **Nunca me mande a senha aqui no chat.**
2. Peça para **a pessoa** criar a pasta e mover o arquivo `.pfx` para lá. **Você não move o arquivo.**
   - Windows: `C:\Users\<nome do usuário>\Certificados\`
   - Mac: a pasta `Certificados` dentro da pasta pessoal (a da casinha no Finder), **não** em Documentos nem na Mesa, que podem sincronizar com o iCloud.
   - Se o arquivo veio por email ou está em Downloads, peça para apagar as cópias que sobraram depois de mover.
3. Peça o **caminho completo** do arquivo e o **CNPJ** da empresa. Para achar o caminho: no Windows, botão direito no arquivo > "Copiar como caminho"; no Mac, botão direito com a tecla Option > "Copiar ... como Nome do Caminho".
4. Crie o `empresa.json` na raiz, copiando `modelos/empresa.exemplo.json`. Preencha agora só `cnpj` (só números) e `certificado_pfx` (use barras `/`). O resto fica para o passo 5.
5. Dê à pessoa o comando para guardar a senha, com o caminho completo da pasta do projeto. Exemplo no Windows:
   ```
   cd "C:\Users\<nome>\Documents\Emissor NFS-e"; python codigo\senha.py
   ```
   Explique: ela abre o PowerShell (ou o Terminal), cola, aperta Enter e digita a senha. **A senha não aparece enquanto ela digita, e isso é normal.** O programa confere se a senha abre o certificado antes de guardar.
6. Quando ela disser que guardou, rode `python codigo/nfse.py certificado`.
7. **Confira o titular.** O comando mostra o titular do certificado. Ele tem que ter a razão social e o CNPJ da empresa do `empresa.json`. Se aparecer o nome de uma pessoa (e-CPF) ou outro CNPJ, o certificado é o errado: pare e peça o e-CNPJ A1 da empresa.

**Pronto quando:** o comando mostrar "Certificado ok", o titular for a empresa e a data de vencimento aparecer. Anote a data no `progresso.md`. Se faltar menos de 45 dias, avise que é hora de renovar.

## Passo 4. Teste de segurança

**Objetivo:** provar que o emissor funciona e que o caminho até a Receita está aberto, sem emitir nada.

1. `python codigo/testar_offline.py`: confere a montagem da nota, a validação contra o esquema oficial e a assinatura, com dados fictícios e um certificado descartável.
2. `python codigo/testar_fila.py`: confere as travas, ou seja, que não se emite sem aprovação, nem duas vezes, nem no ambiente errado.
3. `python codigo/nfse.py conexao restrita`: conecta ao **ambiente de teste** da Receita com o certificado de verdade. O app vai pedir permissão de internet. Explique:
   > A Receita tem dois ambientes: o de **teste** (produção restrita), onde a nota não vale nada, e o de **produção**, onde a nota é real. Vamos fazer tudo no de teste até o último passo.
4. **Confira se o leiaute mudou.** A Receita publica versões novas do XML, primeiro no teste e depois na produção. Abra as duas páginas e compare a data no nome do pacote de esquemas XSD com a dos pacotes em `docs/oficial/esquemas-xsd/`:
   - produção: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/documentacao-atual (no pacote: `20260209`);
   - teste: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica/producao-restrita (no pacote: `prodrest-20261020`).
   Mesma data nos dois: siga. Data mais nova em algum: **pare**. Explique à pessoa que o governo mudou o formato da nota e que o código precisa ser adaptado antes de emitir naquele ambiente (ver "Teste e produção podem estar em leiautes diferentes" em `docs/GUIA-TECNICO.md`). Anote as datas no `progresso.md`.

**Pronto quando:** os dois testes terminarem com `ok`, a conexão mostrar `"mtls": "ok"` e as datas dos esquemas baterem. Se a conexão falhar, a mensagem diz o motivo: internet bloqueada, certificado errado ou certificado vencido.

## Passo 5. Nota modelo: dados da empresa e PDF

**Objetivo:** tirar os dados fixos de uma nota real e preparar o PDF.

1. Peça para a pessoa baixar, de uma nota que ela já emitiu pelo portal, **o PDF e o XML**. No Emissor Nacional: Notas emitidas > na nota, os botões de download. O PDF também sai da consulta pública (https://www.nfse.gov.br/consultapublica), pela chave de acesso. Peça para salvar os dois na pasta `amostras/` do projeto.
2. **Leia o XML** e preencha o `empresa.json`:
   | Campo do `empresa.json` | Tag no XML |
   |---|---|
   | `razao_social` | `emit/xNome` |
   | `cloc_emi` | `emit/enderNac/cMun` |
   | `cloc_prestacao` | `DPS/infDPS/serv/locPrest/cLocPrestacao` |
   | `ctrib_nac` | `DPS/infDPS/serv/cServ/cTribNac` |
   | `ctrib_mun` | `DPS/infDPS/serv/cServ/cTribMun` (vazio se não houver) |
   | `op_simp_nac`, `reg_ap_trib_sn`, `reg_esp_trib` | `DPS/infDPS/prest/regTrib/...` |
   | `aliq_simples_nacional` | `DPS/infDPS/valores/trib/totTrib/pTotTribSN` |
   | `texto_fixo_descricao` | o trecho final de `xDescServ` que se repete em toda nota (dados bancários, por exemplo). Confirme com a pessoa. |
   - **Não copie a série** do XML (`serie`, normalmente 70000): essa faixa é do portal e dá erro E0010 na API. Mantenha `00001`.
   - Os códigos e a alíquota vêm **só do XML**. Não consulte os anexos oficiais para conferir, escolher ou questionar um código: a classificação fiscal é da pessoa e da contabilidade, e a nota aceita pela Receita já mostra a que ela usa. Se uma nota antiga (passo 6) tiver um código diferente do da nota modelo, não interprete: mostre as duas notas e pergunte qual código vale para os próximos pedidos.
   - Mostre à pessoa a tabela preenchida, em linguagem simples ("código do serviço", com o número lido do XML), e peça para ela confirmar. Pergunte se a alíquota do Simples ainda é a mesma, porque ela muda com o faturamento.
3. **Crie o molde do PDF:** `python codigo/danfse.py --modelo "amostras/<pdf da nota>"`. Abra o `codigo/danfse_modelo.pdf` e confira que não sobrou nenhum dado da nota (só linhas, títulos e o logo).
4. **Teste o PDF:** `python codigo/danfse.py "amostras/<xml da nota>" amostras/teste-pdf.pdf`. Peça para a pessoa abrir o `teste-pdf.pdf` e o PDF do portal lado a lado e conferir se estão iguais.
   - Se o comando parar dizendo que "o molde não cobre" algum grupo, a nota tem algo fora do caso coberto (intermediário, retenção, IBS/CBS). Explique e combine que o PDF dessas notas sai pelo portal.

**Pronto quando:** o `empresa.json` estiver completo e confirmado, e a pessoa disser que os PDFs batem.

## Passo 6. Teste de leitura com 3 emails antigos

**Objetivo:** ensinar e provar a leitura dos pedidos, usando pedidos que já viraram nota.

1. **Conecte o Gmail**, se ainda não estiver:
   - **ChatGPT:** Customize > Plugins > Gmail.
   - **Claude:** Configurações > Conectores > Gmail. Depois de conectar, abra uma sessão nova nesta pasta para o conector aparecer.
   - Confira que você consegue buscar emails e criar rascunho. Se o conector não aparecer nas suas ferramentas, pare e peça para a pessoa conectar.
2. Peça **3 pedidos de nota antigos que já foram emitidos**. Explique:
   > Se os pedidos chegam em formatos diferentes, por exemplo às vezes com os dados no corpo do email e às vezes num PDF anexo, ou com uma correção numa resposta depois, escolha um exemplo de cada formato. É assim que eu aprendo a ler todos.
   Pergunte também como achar os pedidos: o assunto costuma ter alguma palavra fixa? Vêm sempre do mesmo remetente?
3. Para cada pedido, **leia a thread inteira**, inclusive anexos, e monte o JSON no formato de `modelos/pedido.exemplo.json`, em `pedidos/amostra-1.json` etc. Regras:
   - vale o valor **mais recente** da thread (correções chegam depois);
   - os dados do **tomador** (o cliente que recebe a nota) saem só da parte do email que fala do tomador, nunca de um bloco do prestador, que é a própria empresa;
   - o vencimento: se o email diz "N dias após a emissão", use `prazo_dias` e escreva `{vencimento}` na descrição, no lugar onde a data deve aparecer; se diz uma data, use `vencimento` (aaaa-mm-dd);
   - `valor` como está no email; o programa normaliza.
   - Se o anexo não puder ser lido pelo Gmail, peça para a pessoa salvar o anexo em `amostras/`, e anote no `rotina.md` que pedidos nesse formato precisam desse passo manual.
4. **Compare com a nota que foi emitida para cada pedido.** Peça o PDF ou o número da nota, ou ache a resposta enviada com o PDF no Gmail. Mostre uma tabela por pedido, com o campo, o que você leu e o que está na nota, para tomador, CNPJ, valor, competência e descrição. Toda diferença é discutida com a pessoa até a regra ficar clara.
5. Crie o `rotina.md` a partir de `modelos/rotina.exemplo.md`: a busca do Gmail que acha os pedidos e a lista dos formatos, com o que aprendeu de cada um.
6. Guarde uma cópia fiel de cada email (texto como veio, sem reescrever) em `amostras/email-1.txt` etc. Eles servem de teste se a leitura mudar um dia.

**Pronto quando:** os 3 pedidos forem lidos sem diferença em relação às notas emitidas, e o `rotina.md` tiver a busca e os formatos.

## Passo 7. Nota de teste completa

**Objetivo:** fazer o caminho inteiro, do pedido ao email com o PDF, no ambiente de teste.

1. Copie `pedidos/amostra-1.json` para `pedidos/TESTE-1.json`, troque o `id_pedido` para `TESTE-1` e rode `python codigo/nfse.py adicionar pedidos/TESTE-1.json`.
2. Mostre o resumo como a rotina vai mostrar no dia a dia (ver o skill `emissao-nfse`), deixando claro que é **nota de TESTE, sem valor fiscal**, e peça o ok.
3. Com o ok: `python codigo/nfse.py aprovar TESTE-1 restrita` e `python codigo/nfse.py emitir TESTE-1`. O app pode pedir internet duas vezes: uma para o ViaCEP (`viacep.com.br`), que completa o endereço do cliente pelo CEP, e outra para o envio ao ambiente de teste da Receita. Explique as duas antes.
4. Confira com a pessoa:
   - o PDF em `notas/`, com a faixa "NFS-e SEM VALIDADE JURÍDICA" (é o certo para teste);
   - o XML em `notas/` contra o XML da nota modelo, campo a campo: municípios, códigos de serviço, regime, alíquota. Só o tomador, o valor, as datas e a descrição podem mudar.
     - **Diferença esperada:** enquanto o teste estiver num leiaute mais novo que a produção, o XML de teste traz o campo `finNFSe` (finalidade da nota, valor `0`), que a nota modelo não tem. Isso é certo e não é erro. O mesmo vale para a série (`00001` no teste, `70000` na nota do portal).
5. **Teste o anexo no Gmail:** crie um email **para a própria pessoa** (nunca para o cliente), com o PDF da nota de teste anexado. Peça para ela conferir que chegou com o anexo.
   - Funcionou: anote no `rotina.md` que o anexo funciona.
   - Não funcionou: anote que a resposta será sempre em rascunho e que a pessoa anexa o PDF à mão. Explique isso a ela.

**Pronto quando:** a nota de teste tiver chave de acesso, o PDF estiver certo, o XML bater com o modelo, e o teste do anexo estiver anotado.

## Passo 8. Mensagem padrão de resposta

Peça para a pessoa escrever a mensagem que vai junto com a nota quando ela responde ao pedido. Ofereça um ponto de partida curto:

> Olá,
>
> Segue em anexo a nota fiscal referente ao pedido.
>
> Obrigado!

Pergunte se o cliente costuma pedir o XML junto com o PDF. Grave a mensagem e a resposta no `rotina.md`.

**Pronto quando:** a mensagem estiver no `rotina.md`, nas palavras da pessoa.

## Passo 9. Enviar direto ou deixar em rascunho

Pergunte:

> Depois que você confirmar os dados e a nota sair, prefere que eu **envie a resposta direto** para o cliente, ou que eu **deixe em rascunho** no Gmail para você conferir e enviar?

- Se o anexo não funcionou no passo 7, a única opção é rascunho.
- Recomende rascunho nas primeiras semanas. Dá para mudar depois: é só pedir.

**Pronto quando:** o modo estiver no `rotina.md`.

## Passo 10. Frequência e rotina agendada

1. Pergunte com que frequência olhar a caixa de entrada. Sugira **duas vezes por dia útil** (10h e 16h). Lembre que **o computador precisa estar ligado e o app aberto** nesses horários.
2. Grave a frequência no `rotina.md`.
3. Crie a tarefa agendada neste projeto local, com essa frequência e com o prompt:
   ```
   Use o skill emissao-nfse, parte "Rotina". Siga o AGENTS.md.
   Nesta rodada, nunca aprove nem emita: só ache pedidos novos, ponha na fila e me mostre o resumo pedindo o ok.
   Se não houver pedido novo nem aviso, termine sem relatar nada.
   ```
   - **ChatGPT:** crie em **Scheduled**, neste projeto local.
   - **Claude:** crie você mesmo, com a sua ferramenta de tarefas agendadas, apontando para esta pasta. Ela aparece na lista de tarefas agendadas do app.
4. Rode a tarefa uma vez agora e veja o resultado com a pessoa:
   - **ChatGPT:** **Run now**, e o resultado em **Scheduled**.
   - **Claude:** rode pela ferramenta de tarefas agendadas; o resultado abre como uma sessão nova na barra lateral.
5. Explique o dia a dia: quando houver pedido, o resumo aparece na conversa que a tarefa abriu (em **Scheduled** no ChatGPT, na barra lateral no Claude). Ela responde naquela conversa com `emitir` (ou o que estiver errado), e você segue o skill.

**Pronto quando:** a tarefa existir e a primeira rodada tiver terminado sem erro.

## Passo 11. Virar para produção

Até aqui, nada teve valor fiscal. Explique:

> A partir de agora, as notas são **reais**: vão para a Receita, valem como documento fiscal, e erro só se corrige cancelando ou substituindo a nota no portal.

1. Confira que os passos 1 a 10 estão com `[x]`.
2. **Confira de novo a página da produção** (passo 4, item 4). Se o pacote de esquemas XSD da produção tiver data mais nova que `20260209`, pare: a primeira nota real seria recusada com o erro E1235. O código precisa da adaptação descrita em `docs/GUIA-TECNICO.md` antes.
3. Peça para a pessoa digitar exatamente: **`QUERO EMITIR NOTAS REAIS`**. Sem essa frase, não siga.
4. Troque `ambiente` para `producao` no `empresa.json`.
5. Rode `python codigo/nfse.py conexao producao`.
6. Combine que a **primeira nota real** será acompanhada: quando chegar o próximo pedido, vocês conferem juntos, ela abre o PDF e confere no portal (Notas emitidas) se a nota apareceu.
7. Lembre: o número da nota segue a sequência da empresa no município, a mesma das notas do portal. Se pular um número, alguma nota saiu por outro caminho.

**Pronto quando:** o `empresa.json` estiver em `producao` e a conexão de produção der `"mtls": "ok"`. Marque o último `[x]` e parabenize a pessoa.

---

## Depois da instalação

- **Mudou a alíquota do Simples?** Atualize `aliq_simples_nacional` no `empresa.json`.
- **Certificado renovado?** A pessoa coloca o novo `.pfx` na mesma pasta, você ajusta `certificado_pfx` se o nome mudou, e ela roda `python codigo/senha.py` de novo.
- **Pedido num formato novo?** Leia com a pessoa, compare com o resultado esperado e acrescente o formato ao `rotina.md`.
