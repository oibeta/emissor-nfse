# Códigos de rejeição da SEFIN Nacional

Extraído do ANEXO_I (abas RN DPS_NFS-e e RN_RECEPCAO_DPS), leiaute v1.01.
Quando a SEFIN recusar uma emissão, o código vem na resposta.

**E1235 (falha no esquema XML)** quase sempre quer dizer que o ambiente mudou de leiaute antes da pasta. Veja "Teste e produção podem estar em leiautes diferentes" em `docs/GUIA-TECNICO.md`.

| Código | Descrição |
|---|---|
| `E0001` | O prazo de aceitação da versão do leiaute da DPS expirou. |
| `E0004` | Conteúdo do identificador informado na DPS difere da concatenação dos campos correspondentes. |
| `E0006` | Ambiente informado diverge do ambiente de recebimento para o qual o emitente enviou a DPS. |
| `E0008` | A data e hora de emissão da DPS deve ser anterior ou igual à data do seu processamento (dhProc) pelo Sistema Nacional NFS-e. |
| `E0010` | A série informada na DPS não pertence à faixa definida para o tipo de emissor utilizado para a sua emissão. |
| `E0014` | Conjunto de Série, Número, Código do Município Emissor e CNPJ/CPF informado nesta DPS já existe em uma NFS-e gerada a partir de uma DPS enviada anteriormente. |
| `E0015` | A data de competência informada na DPS não pode ser posterior à data de emissão (dhEmi) da DPS. |
| `E0016` | A data de competência deve ser igual ou posterior à data de ativação do convênio do município emissor informado na DPS, exceto quando o emitente for MEI na data de competëncia informada. |
| `E0018` | A data de competência informada na DPS deve ser igual ou posterior à data de inscrição do CNPJ do emitente no cadastro CNPJ. |
| `E0020` | A data de competência informada na DPS deve ser igual ou posterior à data de inscrição do CPF do emitente no cadastro CPF. |
| `E0023` | A data de competência informada na DPS deve ser igual ou posterior à data do indicador municipal, registrada no CNC do município correspondente ao município emissor da DPS (cLocEmi). |
| `E0025` | A data de competência informada na DPS deve ser igual ou posterior à data autorizasção de uso do emissores, registrada no CNC do município correspondente ao município emissor da DPS (cLocEmi) para o contribuinte. |
| `E0029` | O motivo da emissão não pode ser preenchido se o emitente for o prestador de serviço. |
| `E0031` | Não pode haver retenção do ISSQN pelo tomador quando o município de incidência não for o do tomador. |
| `E0032` | Não pode haver retenção do ISSQN pelo intermediário quando o município de incidência não for o do intermediário. |
| `E0034` | Somente é permitido o preenchimento do campo de chave de acesso de NFS-e rejeitada se o tipo de emitente for Tomador ou Intermediário e o motivo da emissao for por rejeição de NFS-e emitida pelo prestador. |
| `E0035` | A chave de acesso de NFS-e informada nesta DPS não possui a ela vinculada o evento de manifestação de rejeição emitido pelo mesmo emitente desta DPS. |
| `E0037` | O código do município emissor informado na DPS é inexistente no cadastro de convênio municipal do sistema nacional. |
| `E0038` | A situação do convênio do município emissor informado na DPS deve ser "ATIVO" no cadastro de convênio municipal do sistema nacional. |
| `E0039` | O município emissor informado na DPS deve estar parametrizado para utilizar os emissores públicos nacionais, conforme parametrização do município no Sistema Nacional NFS-e. |
| `E0041` | O município emissor não corresponde ao município do emitente MEI no CNPJ. |
| `E0042` | Chave de NFS-e a ser substituída é inválida. |
| `E0044` | NFS-e não existe na base de dados do autorizador de NFS-e nacional. Informe uma chave de NFS-e existente. |
| `E0046` | Uma NFS-e cancelada não pode ser substituída. Informe uma chave de NFS-e não cancelada anteriormente. |
| `E0050` | Uma NFS-e não pode ser substituída fora do prazo estabelecido pelo município emissor da NFS-e. |
| `E0056` | NFS-e não pode ser substituída pois não possui identificação do tomador. |
| `E0058` | Não poderá ocorrer a substituição de NFS-e com alteração da identificação do não emitente, conforme parametrização do município emissor da NFS-e. |
| `E0060` | Os campos data de competência, subitem da lista nacional de serviços, código complementar municipal e local da prestação não podem ser alterados quando a opção do simples nacional for Não Optante (opSimpNac = 1). |
| `E0061` | Os campos identificação do Tomador (se identificado na DPS), data de competência (dCompet), e valor do serviço (vServ), não podem ser alterados quando a opção do simples nacional for MEI (opSimpNac = 2) ou ME/EPP (opSimp |
| `E0065` | Não é possível substituição da NFS-e que tenha sido gerada em ambientes geradores diferentes. |
| `E0068` | Não é possível a substituição desta NFS-e pois a mesma possui registro de Evento de Solicitação de Análise Fiscal para Cancelamento de NFS-e aguardando resposta. Para mais informações, consultar a Administração Tributári |
| `E0070` | Não é possível a substituição desta NFS-e pois já ocorreu uma manifestação de confirmação de serviço. Para mais informações, consultar a Administração Tributária Municipal do município emissor da NFS-e. |
| `E0072` | Não é possível a substituição desta NFS-e pois já ocorreu uma manifestação tácita da NFS-e. Para mais informações, consultar a Administração Tributária Municipal do município emissor da NFS-e. |
| `E0074` | Não é permitido realizar a substituição para NFS-e que possua Evento de Tributos Recolhidos vinculado, conforme parametrização do município de incidência do ISSQN. Para mais informações, consultar a Administração Tributá |
| `E0076` | Não é permitido realizar a substituição para NFS-e que possua Evento de Bloqueio de Ofício para o Evento de Cancelamento de NFS-e por Substituição vigente. |
| `E0078` | Quando o campo cMotivo = 99, o campo xMotivo deve informado obrigatoriamente. |
| `E0080` | CNPJ do prestador informado na DPS é inválido. |
| `E0082` | CNPJ do emitente prestador não encontrado no cadastro CNPJ na data de competência. |
| `E0084` | CNPJ do emitente prestador não possui estabelecimento ou domicílio em um município correspondente ao município emissor, na data de competência informada na DPS, conforme cadastros CNPJ e CNC NFS-e. |
| `E0096` | CPF do prestador informado na DPS é inválido. |
| `E0098` | CPF do emitente prestador não encontrado no cadastro CPF na data de competência. |
| `E0099` | CPF do emitente prestador não possui estabelecimento ou domicílio em um município correspondente ao município emissor, na data de competência informada na DPS, conforme cadastro nacional complementar NFS-e (cLocEmi + CPF |
| `E0112` | O prestador de serviço, quando emitente da DPS, não pode ser identificado pelo NIF. |
| `E0113` | O NIF ou cNaoNIF do prestador deve ser informado quando o grupo de informações de endereço no exterior do prestador de serviços foi informado. |
| `E0114` | O prestador de serviço, quando emitente da DPS, somente pode ser identificado pelo CNPJ ou CPF. |
| `E0115` | Valor 0 para o motivo da não informação do NIF do prestador não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0116` | A IM deve ser informada para o emitente prestador do serviço na DPS, conforme informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0119` | IM do emitente prestador não está autorizado a emitir NFS-e, conforme informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0120` | IM do prestador não deve ser informado, pois não existem informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0121` | O nome ou razão social do prestador não deve ser informado quando o emitente da DPS for o próprio prestador. |
| `E0122` | O nome ou razão social do prestador deve ser informado quando o emitente da DPS não for o próprio prestador. |
| `E0123` | O preenchimento do nome empresarial é obrigatório quando o prestador for identificado com NIF. |
| `E0124` | O IM informado está inativo no CNC NFS-e do município emissor para a data de competência informada na DPS. |
| `E0125` | O endereço nacional do prestador do serviço deve ser informado na DPS quando for identificado pelo CNPJ ou CPF e o emitente da DPS for o tomador ou intermediário. |
| `E0128` | O endereço do prestador do serviço não deve ser informado na DPS quando o próprio prestador for o emitente da DPS. |
| `E0129` | O endereço do prestador deve ser informado na DPS quando o prestador não for o emitente da DPS. |
| `E0130` | O código do município para o endereço do prestador do serviço não existe conforme tabela de município do IBGE. |
| `E0132` | O código do município informado na DPS para o endereço do prestador do serviço, identificado pelo CNPJ, não corresponde ao município registrado em seus cadastros na data de competência informada na DPS. |
| `E0134` | O código do município informado na DPS para o endereço do prestador do serviço, identificado pelo CPF, não corresponde ao município registrado em seus cadastros na data de competência informada na DPS. |
| `E0138` | O CEP informado para o endereço nacional do prestador do serviço não existente ou não pertence ao município informado na DPS. Informe um CEP existente e que pertença ao município informado para o endereço do prestador do |
| `E0142` | O grupo de informações de endereço no exterior deve ser informado obrigatoriamente quando o prestador for identificado pelo NIF e o emitente por CNPJ. |
| `E0146` | O código de país informado para o endereço no exterior do prestador do serviço não existe ou é igual ao código do Brasil. Informe um código de país existente e diferente do codigo do Brasil (BR) para o endereço no exteri |
| `E0148` | Email inválido. |
| `E0160` | No mês de competência da NFS-e, a opção de situação perante o Simples Nacional, do prestador, informada na DPS não está de acordo com o cadastro Simples Nacional. |
| `E0161` | NFS-e cujo emitente for MEI somente poderá ser compartilhada pelo município com o ADN se a data de competência, informada na NFS-e, for menor ou igual a 31/08/2023. |
| `E0162` | Não é permitido ao não optante do Simples Nacional e o MEI preencherem o campo de indicação do regime de apuração dos tributos apurados. |
| `E0166` | É obrigatorio o preenchimento do campo de regime de apuração dos tributos do SN para o optante do Simples Nacional ME/EPP. |
| `E0172` | O Regime Especial de Tributação deve ser "Nenhum" (regEspTrib = 0) quando o serviço prestado for diferente de Tributável (tribISSQN = 1), ou seja, tribISSQN = 2, 3 ou 4. |
| `E0174` | Quando o prestador da NFS-e é MEI (opSimpNac = 2) o regime especial de tributação deve ser "Nenhum" (regEspTrib = 0). |
| `E0175` | Quando o prestador optante pelo Simples Nacional tiver o regime de apuração dos tributos ocorrendo também pelo Simples Nacional, o regime especial de tributação do ISSQN deve ser "Nenhum" (regEspTrib = 0). |
| `E0176` | É permitido informar Profissional Autônomo na DPS somente se o prestador de serviço estiver parametrizado como Profissional Autônomo, na data de competência informada na DPS, em pelo menos um dos municípios, emissor ou d |
| `E0177` | Regime especial de tributação informado na DPS não é admitido na parametrização do município de incidência do ISSQN. |
| `E0178` | Regime especial de tributação não permitido para o prestador do serviço com código de tributação na data de competência, informados na DPS, conforme parametrização do município de incidência do ISSQN. |
| `E0187` | O grupo de informações relativas ao tomador/adquirente do serviço é obrigatório para o indicador de operação informado. |
| `E0188` | CNPJ do tomador informado na DPS é inválido. |
| `E0190` | CNPJ do tomador não encontrado no cadastro CNPJ. |
| `E0194` | CNPJ do emitente tomador não possui estabelecimento ou domicílio em um município correspondente ao município emissor, na data de competência informada na DPS, conforme cadastros CNPJ e CNC NFS-e. |
| `E0202` | Na emissão da NFS-e não é permitido que o prestador do serviço seja igual ao tomador do serviço. |
| `E0204` | CNPJ ou CPF do tomador não foi informado, mas existe uma indicação para retenção do ISSQN na DPS no campo de tipo de "Retenção do ISSQN". |
| `E0206` | CPF do tomador informado na DPS é inválido. |
| `E0207` | CPF do tomador não encontrado no cadastro CPF. |
| `E0212` | CPF do emitente tomador não possui estabelecimento ou domicílio em um município correspondente ao município emissor, na data de competência informada na DPS, conforme cadastros CPF e CNC NFS-e. |
| `E0222` | O tomador de serviço, quando emitente da DPS, não pode ser identificado pelo NIF. |
| `E0223` | O NIF ou cNaoNIF do tomador deve ser informado quando o grupo de informações de endereço no exterior do tomador de serviços foi informado. |
| `E0224` | O tomador de serviço, quando emitente da DPS, somente pode ser identificado pelo CNPJ ou CPF. |
| `E0226` | Valor 0 para o motivo da não informação do NIF do tomador não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0228` | A IM deve ser informada para o emitente tomador do serviço na DPS, conforme informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0229` | O IM informado está inativo no CNC NFS-e do município emissor para a data de competência informada na DPS. |
| `E0231` | IM do emitente tomador não está autorizado a emitir NFS-e, conforme informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0232` | IM do tomador não deve ser informado, pois não existem informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0233` | O nome tomador deve ser preenchido obrigatoriamente quando o NIF do tomador for preenchido. |
| `E0234` | O endereço do tomador é obrigatório para o indicador de operação informado ou quando a incidência do ISSQN definida para o serviço prestado ocorrer no local do estabelecimento/domicílio do tomador. |
| `E0235` | O endereço nacional do tomador do serviço deve ser informado na DPS quando o tomador for identificado pelo CNPJ. |
| `E0236` | O endereço nacional do tomador do serviço não deve ser informado na DPS quando o próprio tomador do serviço for o emitente da DPS. |
| `E0237` | O endereço nacional do tomador do serviço deve ser informado na DPS quando o valor do ISSQN for retido pelo tomador, exceto se o emitente da DPS é o próprio tomador do serviço. |
| `E0238` | O código do município informado na DPS para o endereço do tomador do serviço não existe conforme tabela de município do IBGE. |
| `E0240` | O CEP informado para o endereço nacional do tomador do serviço não existe ou não pertence ao município do endereço do tomador. |
| `E0242` | O grupo de informações de endereço no exterior deve ser informado obrigatoriamente quando o tomador for identificado pelo NIF e o emitente por CNPJ. |
| `E0246` | O código de país informado para o endereço no exterior do tomador do serviço não existe ou é igual ao código do Brasil. Informe um código de país existente e diferente do codigo do Brasil (BR) para o endereço no exterior |
| `E0247` | Email inválido. |
| `E0248` | CNPJ do intermediário informado na DPS é inválido. |
| `E0250` | CNPJ do intermediário não encontrado no cadastro CNPJ. |
| `E0254` | CNPJ do emitente intermediário não possui estabelecimento ou domicílio em um município correspondente ao município emissor, na data de competência informada na DPS, conforme cadastros CNPJ e CNC NFS-e. |
| `E0262` | Na emissão da NFS-e não é permitido que o prestador do serviço seja igual ao intermediário do serviço. |
| `E0264` | CNPJ ou CPF do intermediário não foi informado, mas existe uma indicação para retenção do ISSQN na DPS no campo de tipo de "Retenção do ISSQN". |
| `E0266` | CPF do intermediário informado na DPS é inválido. |
| `E0268` | CPF do intermediário não encontrado no cadastro CPF. |
| `E0272` | CPF do emitente intermediário não possui estabelecimento ou domicílio em um município correspondente ao município emissor, na data de competência informada na DPS, conforme cadastros CPF e CNC NFS-e. |
| `E0280` | O intermediário de serviço, quando emitente da DPS, não pode ser identificado pelo NIF. |
| `E0281` | O NIF ou cNaoNIF do intermediário deve ser informado quando o grupo de informações de endereço no exterior do intermediário de serviços foi informado. |
| `E0284` | O intermediário de serviço, quando emitente da DPS, somente pode ser identificado pelo CNPJ ou CPF. |
| `E0286` | Valor 0 para o motivo da não informação do NIF do intermediário não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0287` | A IM não foi informada para o emitente intermediário do serviço na DPS. |
| `E0288` | O IM informado está inativo no CNC NFS-e do município emissor para a data de competência informada na DPS. |
| `E0289` | IM do emitente intermediário não está autorizado a emitir NFS-e, conforme informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0290` | IM do intermediário não deve ser informado, pois não existem informações complementares registradas no CNC NFS-e do município emissor informado na DPS. |
| `E0291` | O endereço nacional do intermediário do serviço não deve ser informado na DPS quando o próprio tomador do serviço for o emitente da DPS. |
| `E0292` | O nome intermediário deve ser preenchido obrigatoriamente quando o NIF do intermediário for preenchido. |
| `E0293` | O endereço nacional do intermediário do serviço deve ser informado na DPS quando o valor do ISSQN for retido pelo intermediário, exceto se o emitente da DPS é o intermediário do serviço. |
| `E0294` | O código do município informado na DPS para o endereço do intermediário do serviço não existe conforme tabela de município do IBGE. |
| `E0296` | O CEP informado para o endereço nacional do intermediário do serviço não existe ou não pertence ao município do endereço do intermediário. |
| `E0298` | O grupo de informações de endereço no exterior deve ser informado obrigatoriamente quando o intermediário for identificado pelo NIF e o emitente por CNPJ. |
| `E0299` | O código de país informado para o endereço no exterior do intermediário do serviço não existe ou é igual ao código do Brasil. Informe um código de país existente e diferente do codigo do Brasil (BR) para o endereço no ex |
| `E0300` | Email inválido. |
| `E0302` | O código do local da prestação do serviço não existe conforme a tabela de municípios IBGE disponibilizada no ANEXO_A-MUNICIPIO_IBGE-PAISES_ISO2-SNNFSe. |
| `E0304` | Informe um código de país existente e diferente de Brasil (BR), conforme tabela de país do ANEXO_A-MUNICIPIO_IBGE-PAISES_ISO2-SNNFSe-ESPEC. |
| `E0310` | O código de tributação nacional informado não existe conforme a lista de serviços nacional do Sistema Nacional NFS-e. |
| `E0312` | O código de tributação nacional informado não está administrado pelo município de incidência do ISSQN na data de competência informada na DPS, conforme a lista de serviços nacional do Sistema Nacional NFS-e. |
| `E0314` | O código de tributação municipal informado não existe ou não está administrado pelo município de incidência do ISSQN na data de competência informada na DPS, |
| `E0315` | Não é permitido informar 000 para o codigo de tributação municipal na DPS. |
| `E0316` | Código da lista NBS informado inexistente tabela de NBS do sistema. |
| `E0318` | É obrigatório informar na DPS um item da NBS para casos de exportação de serviço. |
| `E0320` | É obrigatório informar na DPS um item da NBS para casos de importação de serviço. |
| `E0322` | É obrigatório informar na DPS um item da NBS se for declarada qualquer informação de IBS/CBS. |
| `E0330` | É obrigatório prestar informações de comércio exterior para as situações de exportação de serviços. |
| `E0331` | É obrigatório prestar informações de comércio exterior para as situações de importação de serviços. |
| `E0333` | Valor 0 para o modo de prestação não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0341` | Valor 0 para o Mecanismo de apoio/fomento ao Comércio Exterior utilizado pelo prestador do serviço não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0343` | Valor 0 para o Mecanismo de apoio/fomento ao Comércio Exterior utilizado pelo tomador do serviço não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0345` | Valor 0 para o Vínculo da Operação à Movimentação Temporária de Bens não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0352` | O preenchimento do campo nDI (Número da Declaração de Importação) é obrigatório quando o campo (movTempBens) Vínculo da Operação à Movimentação Temporária de Bens for igual a 2. |
| `E0354` | O preenchimento dos campos nDI (Número da Declaração de Importação) ou do nRE (úmero do Registro de Exportação) não é permitido quando o campo (movTempBens) Vínculo da Operação à Movimentação Temporária de Bens for igual |
| `E0356` | O preenchimento do campo nRE (úmero do Registro de Exportação) é obrigatório quando o campo (movTempBens) Vínculo da Operação à Movimentação Temporária de Bens for igual a 3. |
| `E0370` | O grupo de informações de obra é obrigatório quando o código de tributação nacional pertencer a um dos subitens 07.02.01, 07.02.02, 07.04.01, 07.05,01, 07.05.02, 07.06.01, 07.06.02, 07.07.01, 07.08.01, 07.17.01, 07.19.01 |
| `E0372` | O grupo de informações de obra não é permitido quando o código de tributação nacional não pertencer a algum dos subitens 07.02.01, 07.02.02, 07.04.01, 07.05,01, 07.05.02, 07.06.01, 07.06.02, 07.07.01, 07.08.01, 07.17.01, |
| `E0373` | Código CIB inválido. |
| `E0380` | Informe um CEP correspondente ao município do local da prestação do serviço informado nesta DPS para indicar corretamente o endereço da obra. |
| `E0382` | O CEP não deve ser informado quando o endereço da obra ocorrer no exterior do país. |
| `E0384` | O grupo de informações de endereço da atividade de obra ocorrido no exterior deve ser informado quando o país do local da prestação for informado na DPS. |
| `E0386` | O grupo de informações de endereço da atividade de obra ocorrido no exterior não deve ser informado quando o município do local da prestação for informado na DPS. |
| `E0390` | O grupo de informações de Atividade/Evento é obrigatório quando o código de tributação nacional pertencer ao item 12 da lista de serviços. |
| `E0392` | O grupo de informações de Atividade/Evento não é permitido quando o código de tributação nacional não pertencer ao item 12 da lista de serviços, com exceção do código 99.01.01. |
| `E0398` | Informe um CEP correspondente ao município do local da prestação do serviço informado nesta DPS para indicar corretamente o endereço da atividade ou evento. |
| `E0400` | O CEP não deve ser informado quando o endereço da atividade de evento ocorrer no exterior do país. |
| `E0402` | O grupo de informações de endereço da atividade de evento ocorrido no exterior deve ser informado quando o país do local da prestação for informado na DPS. |
| `E0404` | O grupo de informações de endereço da atividade de evento ocorrido no exterior não deve ser informado quando o município do local da prestação for informado na DPS. |
| `E0420` | O documento de referência deve ser obrigatoriamente informado quando o emitente da DPS for o tomador ou intermediário do serviço. |
| `E0423` | O valor recebido deve ser informado na DPS quando o intermediário do serviço for o emitente da DPS. |
| `E0424` | O valor recebido não deve ser informado na DPS quando o prestador ou tomador do serviço for o emitente da DPS. |
| `E0425` | O valor recebido não pode ser menor que o valor do serviço informado na DPS. |
| `E0427` | O valor do serviço deve ser maior ou igual ao somatório dos valores informados para Desconto Incondicionado, Deduções/Reduções e Benefício Municipal. |
| `E0428` | O valor do serviço deve ser maior ou igual ao somatório dos valores informados para Desconto Incondicionado, Desconto Condicionado, Deduções/Reduções, Benefício Municipal, valores de tributos devidos CP, IRRF, CSLL e ISS |
| `E0429` | O ISSQN não pode ser objeto de redução de base de cálculo que resulte em carga tributária menor que a decorrente da aplicação da alíquota mínima de 2,0% do valor do serviço, exceto para os serviços a que se referem aos s |
| `E0431` | O valor do desconto incondicionado informado na DPS deve ser menor que o valor do serviço e maior que zero. |
| `E0432` | O valor do desconto condicionado informado na DPS deve ser menor que o valor do serviço e maior que zero. |
| `E0435` | Não é permitido o preenchimento dos campos do grupo de informações relativas à Dedução/Redução do ISSQN quando ocorrer Imunidade, Exportação do serviço ou Não incidência. |
| `E0436` | Não é permitido o preenchimento dos campos do grupo de informações relativas à Dedução/Redução do ISSQN quando o prestador de serviço é MEI. |
| `E0438` | Não é permitido o preenchimento dos campos do grupo de informações relativas à Dedução/Redução do ISSQN, quando o prestador de serviço tiver algum regime especial de tributação. |
| `E0439` | Não é permitido o preenchimento dos campos do grupo de informações relativas à Dedução/Redução do ISSQN, quando o benefício municipal informado na DPS for do tipo "Isenção". |
| `E0440` | O tipo de dedução/redução informado na DPS não é permitida pelo município de incidência do ISSQN, conforme parametrizações do código de serviço do município de incidência. |
| `E0441` | Não é permitido o preenchimento de informações relativas à Dedução/Redução para o prestador de serviço ME/EPP, apurando pelo SN conforme parametrização do código de serviço admnistrado pelo municipio de incidência do ISS |
| `E0442` | O tipo de dedução/redução informado na DPS não é permitida para o prestador de serviço ME/EPP, apurando pelo SN. |
| `E0444` | O valor percentual de dedução/redução informado na DPS não pode reduzir o valor da BC de forma que resulte no valor do ISSQN a uma alíquota efetiva menor que 2%, exceto para os códigos relativos aos subitens 042201, 0423 |
| `E0446` | Código de serviço informado na DPS não permite dedução/redução na base de cálculo do ISSQN por valor monetário. |
| `E0447` | O valor de dedução/redução informado na DPS não pode reduzir o valor da BC de forma que resulte no valor do ISSQN a uma alíquota efetiva menor que 2%, exceto para os códigos relativos aos subitens 042201, 042301, 050901, |
| `E0449` | Código de serviço informado na DPS não permite dedução/redução na base de cálculo do ISSQN por documento informado. |
| `E0453` | O valor percentual para dedução/redução deve ser maior que 0 e menor ou igual a 100%. |
| `E0454` | Código de serviço informado na DPS não permite dedução/redução na base de cálculo do ISSQN por percentual. |
| `E0455` | Informe uma chave de NFS-e válida. |
| `E0456` | NFS-e não existe na base de dados do autorizador de NFS-e nacional. Informe uma chave de NFS-e existente. |
| `E0458` | Uma NFS-e cancelada não pode ser informada para dedução/redução. |
| `E0460` | Informe uma chave de NF-e válida. |
| `E0462` | NF-e não existe na base de dados do autorizador de NF-e nacional. Informe uma chave de NF-e existente. |
| `E0464` | Uma NF-e cancelada não pode ser informada para dedução/redução. |
| `E0466` | Informe um código de município existente para o documento de nota, conforme tabela de municípios do IBGE. |
| `E0468` | Informar, obrigatoriamente, o campo de descrição no caso ideDedRed igual a 99 – Outras deduções. |
| `E0470` | Não informar o campo de descrição no caso ideDedRed diferente a 99 – Outras deduções. |
| `E0472` | A data de emissão do documento informado na DPS não pode ser posterior à data de competência da DPS. |
| `E0474` | O valor de dedução/redução não pode ser superior ao valor dedutível/redutível. |
| `E0476` | O valor de dedução/redução informado na DPS não pode ser superior ao valor do serviço. |
| `E0477` | O grupo de informações para o fornecedor deve ser informado obrigatoriamente para o tipo de documento de dedução/redução informado na DPS. |
| `E0478` | CNPJ do fornecedor informado na DPS é inválido. |
| `E0482` | CNPJ do fornecedor informado na DPS não encontrado no cadastro CNPJ. |
| `E0484` | CPF do fornecedor informado na DPS é inválido. |
| `E0488` | CPF do fornecedor informado na DPS não encontrado no cadastro CPF. |
| `E0490` | Valor 0 para o motivo da não informação do NIF do fornecedor não é permitido na Sefin do Sistema Nacional NFS-e. |
| `E0492` | O grupo de informações de endereço nacional deve ser informado obrigatoriamente quando o fornecedor for identificado pelo CPF ou CNPJ. |
| `E0494` | O código do município informado na DPS para o endereço do fornecedor do serviço não existe conforme tabela de município do IBGE. |
| `E0496` | O CEP informado para o endereço nacional do fornecedor não existe ou não pertence ao município do endereço do fornecedor. |
| `E0498` | O grupo de informações de endereço no exterior deve ser informado obrigatoriamente quando o fornecedor for identificado pelo NIF. |
| `E0499` | O código de país informado para o endereço no exterior do fornecedor não existe ou é igual ao código do Brasil. Informe um código de país existente e diferente do codigo do Brasil (BR) para o endereço no exterior do forn |
| `E0529` | O sistema considera este cenário para a prestação de serviço informada na DPS uma operação tributável. Não é permitido ao emitente da DPS informar que a prestação de serviço se trata de uma exportação de serviço. |
| `E0530` | O sistema considera este cenário para a prestação de serviço informada na DPS uma exportação de serviço. Não é permitido ao emitente da DPS informar que a prestação de serviço se trata de uma operação tributável. |
| `E0532` | O campo que informa sobre a tributação do ISSQN deve ser "4 - Não Incidência", quando houver o serviço prestado for 99.01.01 - Serviços sem a incidência de ISSQN e ICMS. |
| `E0533` | Não é permitido informar Benefício Municipal (BM deve ser nulo) quando o serviço prestado diferente de Tributável (tribISSQN = 1), ou seja, tribISSQN = 2, 3 ou 4. |
| `E0534` | Não é permitido o preenchimento de informações relativas à benefício municipal para o prestador de serviço MEI. |
| `E0535` | Não é permitido informar benefício municipal quando o prestador de serviço tiver um regime especial de tributação, ou seja, o campo que indica o regime especial de tributação é diferente de 0, (regEspTrib = 1, 2, 3, 4, 5 |
| `E0536` | Não é permitido o preenchimento de informações relativas à benefício municipal para o prestador de serviço ME/EPP, apurando pelo SN, conforme parametrização do código de serviço admnistrado pelo municipio de incidência d |
| `E0537` | Não é permitido informar benefício municipal (BM deve ser nulo) quando o município de incidência do ISSQN não está "Ativo" no Sistema Nacional NFS-e. |
| `E0539` | Não é permitido informar não incidência do ISSQN = 4 (Não Incidência) para qualquer subitem da lista nacional de serviço informado na DPS, se o subitem for incidente, conforme a parametrização do município de incidência  |
| `E0540` | Não há incidência do ISSQN (tribISSQN = 4) pois a parametrização do muncípio de incidência do ISSQN indica que o código de serviço prestado, informado na DPS, não é incidente neste município. |
| `E0541` | Não existe o código de identificação do benefício municipal informado na DPS para o municipío de incidência do ISSQN. |
| `E0544` | Período de vigência expirado para o código de identificação do Benefício Municipal no municipío de incidência do ISSQN para a data de competência informada na DPS. |
| `E0548` | O Benefício Municipal informado na DPS não permite benefício para prestadores de serviço que não estejam estabelecidos no município de incidência do ISSQN. |
| `E0550` | O código de identificação de Benefício Municipal, informada na DPS, não permite benefício para o código de tributação e/ou prestador (CPF ou CNPJ) informado na DPS, conforme parametrização do município de incidência do I |
| `E0565` | Não é permitido informar um valor monetário de redução de base de cálculo do ISSQN por benefício municipal, se o código de identificação do Benefício Municipal não corresponder ao tipo de redução por valor monetário. |
| `E0567` | É obrigatório informar vRedBCBM quando o código de identificação do Benefício Municipal (nBM) for um benefício do tipo Redução de Base de Cálculo por Valor Monetário. |
| `E0574` | O valor monetário do benefício municipal informado na DPS não pode ser superior ao valor do serviço. |
| `E0575` | O valor monetário do benefício municipal informado na DPS não pode reduzir o valor da BC de forma que resulte no valor do ISSQN a uma alíquota efetiva menor que 2%, exceto para os códigos relativos aos subitens 042201, 0 |
| `E0577` | Não é permitido informar um valor percentual de redução de base de cálculo do ISSQN por benefício municipal, se o código de identificação do Benefício Municipal não corresponder ao tipo de redução por valor percentual. |
| `E0579` | É obrigatório informar pRedBCBM quando o código de identificação do Benefício Municipal (nBM) for um benefício do tipo Redução de Base de Cálculo por percentual. |
| `E0580` | Não é permitido haver retenção quando o campo referente à tributação do ISSQN indicar imunidade, exportação ou não incidência. |
| `E0583` | Não é permitido retenção do ISSQN para o prestador do serviço que seja MEI na data de competência informada na DPS. |
| `E0585` | Somente é permitido informar suspensão de exigibilidade quando a opção da tributação do ISSQN for uma operação tributável (tribISSQN = 1). |
| `E0586` | O valor percentual para redução da base de cálculo deve ser maior que 0 e menor ou igual ao percentual parametrizado pelo município de incidência do ISSQN. |
| `E0587` | O valor percentual do benefício municipal informado na DPS não pode reduzir o valor da BC de forma que resulte no valor do ISSQN a uma alíquota efetiva menor que 2%, exceto para os códigos relativos aos subitens 042201,  |
| `E0588` | Não é permitido retenção do ISSQN para o prestador do serviço que tenha algum regime especial de tributação na data de competência informada na DPS. |
| `E0590` | É obrigatório informar o código do país onde ocorreu o resultado do serviço prestado para os cenários 2, 30, 58, 62, 72, 76, conforme a planilha "EXPORTACAO_EMISSÃO_NFS-e". |
| `E0591` | Não é permitido informar o código do país onde ocorreu o resultado do serviço prestado para os cenários diferentes de 2, 30, 58, 62, 72, 76 conforme a planilha "EXPORTACAO_EMISSÃO_NFS-e". |
| `E0592` | O tipo de imunidade é obrigatório e deve ser informado somente quando o campo referente à tributação do ISSQN for igual a "2 - Imunidade". |
| `E0593` | Não permitido o valor "0 - Imunidade (tipo não informado na nota de origem)" na DPS quando utilizado os Emissores Públicos Nacionais para emissao de NFS-e. |
| `E0594` | Não é permitido retenção do ISSQN quando houver Benefício Municipal do tipo Isenção. |
| `E0595` | Não é permitido informar alíquota superior a 5%. |
| `E0596` | Não é permitido retenção do ISSQN quando o serviço prestado corresponder ao subitem 220101 - Serviço de exploração de rodovia da lista de serviços do Sistema Nacional NFS-e. |
| `E0600` | Não é permitido informar a alíquota para prestador de serviço optante do simples nacional do tipo MEI. |
| `E0602` | Não é permitido informar alíquota quando o campo referente à tributação do ISSQN indicar imunidade, exportação ou não incidência. |
| `E0604` | Não é permitido informar alíquota quando o prestador de serviço possui algum regime especial de tributação. |
| `E0612` | Não é permitido informar alíquota quando o benefício municipal informado na DPS for do tipo "Isenção" ou "Alíquota Diferenciada". |
| `E0617` | Não é permitido informar alíquota quando o prestador de serviço não é optante do simples nacional (opSimpNac = 1) na data de competência informada na DPS, com o município de incidência do ISSQN com situação "ATIVO" no Si |
| `E0619` | É obrigatório informar alíquota quando o prestador de serviço não é optante do simples nacional (opSimpNac = 1) na data de competência informada na DPS, o município de incidência do ISSQN não está com situação "ATIVO" no |
| `E0621` | É obrigatório informar alíquota quando há indicação de retenção do ISSQN (tpRetISSQN = 2 ou 3) para o prestador de serviço ME/EPP (opSimpNac = 3) na data de competência informada na DPS, com apuração do ISSQN pelo simple |
| `E0625` | Não é permitido informar alíquota quando não há indicação de retenção do ISSQN (tpRetISSQN = 1) para o prestador de serviço ME/EPP (opSimpNac = 3) na data de competência informada na DPS, com apuração do ISSQN pelo simpl |
| `E0628` | É obrigatório informar alíquota quando o município de incidência do ISSQN não está Ativo no Sistema Nacional NFS-e, para o prestador de serviço ME/EPP (opSimpNac = 3) na data de competência informada na DPS, com apuração |
| `E0631` | Não é permitido informar alíquota quando o município de incidência do ISSQN não está Ativo no Sistema Nacional NFS-e, para o prestador de serviço ME/EPP (opSimpNac = 3) na data de competência informada na DPS, com apuraç |
| `E0635` | Não é permitido informar alíquota quando o convênio do município de incidência do ISSQN está ativo na data de competência informada na DPS, para o prestador de serviço ME/EPP (opSimpNac = 3) com a apuração do ISSQN fora  |
| `E0640` | É obrigatório informar alíquota quando o prestador de serviço ME/EPP (opSimpNac = 3) na data de competência informada na DPS, com apuração do ISSQN fora do Simples Nacional (regApTribISSQN = 2 ou 3), ou seja, pela alíquo |
| `E0650` | Em caso de importação de serviço pelo tomador, o ISSQN deve ser retido pelo tomador. |
| `E0652` | Em caso de importação de serviço pelo intermediário, o ISSQN deve ser retido pelo intermediário. |
| `E0667` | Município da incidência do ISSQN não autoriza que o CPF do tomador informado na DPS seja indicado para retenção deste imposto. |
| `E0670` | Município da incidência do ISSQN não autoriza que o CPF do intermediário informado na DPS seja indicado para retenção deste imposto. |
| `E0672` | Não pode haver retenção do ISSQN se e o tomador for o emitente da DPS e estiver estabelecido em município diferente do município de incidência do ISSQN. |
| `E0673` | Não pode haver retenção do ISSQN se e o intermediário for o emitente da DPS e estiver estabelecido em município diferente do município de incidência do ISSQN. |
| `E0675` | Não é permitido a prestação de informações relativas aos tributos federais quando o emitente da DPS for identificado por um pessoa física (CPF). |
| `E0676` | Não é permitido o preenchimento das informações relativas aos tributos federais quando o emitente for identificado como MEI na data de competência informada na DPS. |
| `E0677` | O valor da BC para Pis/Cofins deve ser menor ou igual ao valor do serviço informado na DPS. |
| `E0686` | A alíquota do Pis deve ser igual ou maior que 0 e menor ou igual a 100%. |
| `E0692` | A alíquota do Cofins deve ser igual ou maior que 0 e menor ou igual a 100%. |
| `E0694` | O valor do Pis informado não corresponde ao resultado da BC Pis/Cofins x Alíquota Pis, que foram informados na DPS. |
| `E0696` | O valor do Cofins informado não corresponde ao resultado da BC Pis/Cofins x Alíquota Cofins, que foram informados na DPS. |
| `E0699` | O valor do tributo CP deve ser maior que zero e menor que o valor do serviço informado na DPS. |
| `E0700` | O valor do tributo IRRF deve ser maior que zero e menor que o valor do serviço informado na DPS. |
| `E0701` | O valor do tributo CSLL deve ser maior que zero e menor que o valor do serviço informado na DPS. |
| `E0702` | Se o valor for informado, então deve ser igual ou maior que 0 e menor ou igual o valor do serviço. |
| `E0703` | Se o valor for informado, então deve ser igual ou maior que 0 e menor ou igual o valor do serviço. |
| `E0704` | Se o valor for informado, então deve ser igual ou maior que 0 e menor ou igual o valor do serviço. |
| `E0706` | Se a alíquota for informada, então deve ser igual ou maior que 0 e menor ou igual a 100%. |
| `E0707` | Se a alíquota for informada, então deve ser igual ou maior que 0 e menor ou igual a 100%. |
| `E0708` | Se a alíquota for informada, então deve ser igual ou maior que 0 e menor ou igual a 100%. |
| `E0710` | Para MEI pTotTribSN nunca poderá ser informado. |
| `E0712` | Para ME/EPP indTotTrib nunca poderá ser informado. |
| `E0713` | Para Não Optante do SN os campos, indicador de informação de valor total de tributos e percentual aproximado do total dos tributos da alíquota do Simples Nacional (%), não podem ser informado. |
| `E0714` | Arquivo enviado com erro na assinatura. |
| `E0715` | Certificado Digital da assinatura inválido. |
| `E0716` | Certificado Digital fora do padrão estabelecido. |
| `E0717` | A assinatura é obrigatória quando for enviado para o Web Service. |
| `E0718` | A assinatura deve ser feita com o certificado digital do emitente da DPS. |
| `E0720` | Se o tipo de retenção do PIS/COFINS for igual a "0 - PIS/COFINS/CSLL Não Retidos", então não é permitido informar o campo vRetCSLL. |
| `E0724` | Se o tipo de retenção do PIS/COFINS for diferente de "0 - PIS/COFINS/CSLL Não Retidos" ou de "2 - PIS/COFINS Não Retido", então é obrigatório informar o campo vRetCSLL. |
| `E0850` | É permitido declarar informações de IBS/CBS somente a partir da data de competência 01/01/2026. |
| `E0854` | Somente é permitio declarar informações de IBS/CBS a partir da versão 1,01 da DPS. |
| `E0901` | Código indicador da operação inexistente. |
| `E0903` | Código do tipo de Operação (tpOper) deve ser informado quando se tratar de uma compra governamental ou um dos serviços da LC 116/2003 listados: 25.05; 15.09; 17.12; 10.05. |
| `E0904` | Código do tipo de Operação (tpOper) não pode ser informado quando não se tratar de uma compra governamental ou um dos serviços da LC 116/2003 listados: 25.05; 15.09; 17.12; 10.05. |
| `E0905` | O grupo de documentos referenciados deve ser informado para o tipo de operação (tpOper). |
| `E0906` | O grupo de documentos referenciados não pode ser informado para o tipo de operação (tpOper). |
| `E0907` | NFS-e referenciada é inválida. |
| `E0910` | O destinatário não deve ser identificado para o código indicador indDest informado. |
| `E0911` | CNPJ do destinatário informado na DPS é inválido. |
| `E0912` | CNPJ do destinatário não encontrado no cadastro CNPJ na data de competência. |
| `E0913` | CPF do destinatário informado na DPS é inválido. |
| `E0914` | CPF do destinatário não encontrado no cadastro CPF na data de competência. |
| `E0920` | O código do município para o endereço do destinatário do serviço não existe conforme tabela de município do IBGE. |
| `E0921` | O código do município informado na DPS para o endereço do destinatário do serviço, identificado pelo CNPJ, não corresponde ao município registrado em seus cadastros na data de competência informada na DPS. |
| `E0922` | O código do município informado na DPS para o endereço do destinatário do serviço, identificado pelo CPF, não corresponde ao município registrado em seus cadastros na data de competência informada na DPS. |
| `E0928` | Não é permitido o grupo de informações relativo a imóvel quando o código de tributação nacional (cTribNac) não pertencer a algum dos subitens 07.02.01, 07.02.02, 07.04.01, 07.05,01, 07.05.02, 07.06.01, 07.06.02, 07.07.01 |
| `E0930` | E-mail inválido. |
| `E0931` | Não é permitido o grupo de informações relativo a imóvel quando o código de tributação nacional, relativo à construção civil, for infomado na DPS. |
| `E0932` | É obrigatório o grupo de informações relativo ao imóvel na DPS quando o código indicador da operação informado for relacionado à imóvel conforme a tabela IndOp do ANEXO_C-INDOP_IBSCBS-SNNFSe-ESPEC. |
| `E0933` | Código CIB inválido. |
| `E0934` | O grupo de informações de endereço da atividade sobre bem imóvel ocorrido no exterior deve ser informado quando o país do local da prestação for informado na DPS. |
| `E0935` | O grupo de informações de endereço da atividade sobre bem imóvel ocorrido no exterior não deve ser informado quando o município do local da prestação for informado na DPS. |
| `E0940` | Chave DF-e incorreta. |
| `E0942` | Outros documentos ficais fiscais não podem ser informados quando a data de competência for posterior a 31 de dezembro de 2025. |
| `E0943` | O código do município emissor do documento fiscal para fins de reembolso, repasse e ressarcimento que não está no repositório nacional está incorreto. |
| `E0945` | CNPJ do fornecedor de reembolso, repasse e ressarcimento informado na DPS é inválido. |
| `E0946` | CNPJ do fornecedor de reembolso, repasse e ressarcimento informado não encontrado no cadastro CNPJ na data de competência. |
| `E0947` | CPF do fornecedor de reembolso, repasse e ressarcimento informado informado na DPS é inválido. |
| `E0948` | CPF do fornecedor de reembolso, repasse e ressarcimento informado não encontrado no cadastro CPF na data de competência. |
| `E0950` | Data de emissão do documento tem que ser igual ou posterior à data de competência (dtCompDoc) |
| `E0951` | Data de competência do documento tem que ser igual ou anterior à data de emissão (dtEmiDoc) |
| `E0952` | A descrição do tipo de reembolso, repasse e ressarcimento não deve ser preenchida. |
| `E0953` | O valor reembolso, repasse e ressarcimento deve ser menor ou igual ao valor do serviço prestado. |
| `E0958` | cClassTrib para IBS/CBS incorreto para operação de prestação de serviços. |
| `E0959` | cClassTrib não pertence ao grupo CST indicado. |
| `E0964` | Grupo de tributação regular não deve ser informado. |
| `E0965` | Grupo de tributação regular deve ser informado. |
| `E0969` | cClassTribReg para IBS/CBS incorreto para operação de prestação de serviços. |
| `E0970` | cClassTribReg não pertence ao grupo CST indicado em CSTReg. |
| `E0971` | Grupo de diferimento para IBS/CBS não deve ser informado. |
| `E0972` | Grupo de diferimento para IBS/CBS deve ser informado. |

## Faixas de série da DPS, por tipo de emissor

| Faixa | Emissor |
|---|---|
| 00001 – 49999 | aplicativo próprio — **é o nosso caso** |
| 50000 – 69999 | emissor móvel |
| 70000 – 79999 | emissor Web — o portal |
| 80000 – 89999 | transcrição manual (Web) |

Série fora da faixa do emissor é recusada com `E0010`.
