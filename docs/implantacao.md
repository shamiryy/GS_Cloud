# Implantação em VM Azure — preparada, ainda não executada

Nenhum recurso de nuvem deste projeto foi criado. A consulta de SKU retornou NotAvailableForSubscription para Standard_B1s em Canada Central e Central US. Não tente criar essa combinação; confirme uma região/SKU disponível e atualize o orçamento antes da autorização. A autorização para uso de créditos está pendente. Não execute a criação sem revisar custos e saldo.

## 1. Condições verificadas em 02/11/2026

Assinatura Azure for Students ativa e spendingLimit On. Essa proteção não foi removida. Não foi confirmado saldo nem prazo dos créditos. Regiões permitidas: Canada Central, Central US, Mexico Central, South Africa North e Chile Central. East US foi excluída da proposta por restrição da assinatura.

Em Canada Central, a API oficial de preços de varejo retornou B1s Linux US$ 0,0116/h; E4 LRS SSD 32 GiB US$ 2,64/mês; IPv4 Standard US$ 0,005/h. Base para 730 horas: US$ 14,758/mês. Operações de disco: US$ 0,002/10 mil. Tráfego, impostos, câmbio e condições contratuais podem alterar o valor. Benefícios gratuitos e créditos não foram abatidos dessa estimativa. O medidor Disk Mount, retornado na pesquisa, não foi incluído na estimativa de um disco de SO convencional; confirme a cotação no portal antes da criação. Fonte: https://prices.azure.com/api/retail/prices e docs/evidencias/precos-azure-canadacentral.json. Preço não equivale a cobrança efetivamente ocorrida.

## 2. Antes de criar

Abra https://portal.azure.com → Assinaturas → Azure for Students → Visão geral e Custo + Cobrança. Confirme saldo, vencimento dos créditos e limite de gastos. Consulte também https://www.microsoftazuresponsorships.com/Balance. Não envie credenciais pelo chat. Autorize o consumo de créditos ou confirme uma oferta gratuita que cubra VM, disco e IP. Não migre a assinatura para pagamento por uso.

## 3. Provisionar

No PowerShell autenticado, na raiz do repositório, execute somente após autorização:

```powershell
./deploy/provisionar.ps1 -AutorizarConsumoDeCreditos
```

A criação pode falhar por capacidade ou quota. Não substitua automaticamente o SKU por outro pago. O script cria exclusivamente rg-api-tarefas-academica, VM, disco, IP, VNet, sub-rede, NIC e NSG associados. Não abra a porta 22; a administração usa Azure Run Command com a autenticação do Azure CLI. As portas públicas permitidas são 80 e 443. O Uvicorn escuta apenas 127.0.0.1:8000.

## 4. Instalar e ativar HTTPS

O script informa o DNS público real. Na VM → Executar comando → RunShellScript, cole o conteúdo de deploy/instalar.sh precedido de `export API_DOMAIN=DNS_REAL`. Como alternativa, no Azure CLI, crie um arquivo local temporário com essa primeira linha e o script e execute:

```powershell
az vm run-command invoke -g rg-api-tarefas-academica -n vm-api-tarefas --command-id RunShellScript --scripts @arquivo-temporario.sh
```

O script instala Python, Caddy e dependências. Se o Ubuntu da imagem não disponibilizar uma versão compatível com os pins, interrompa, registre o erro e escolha uma imagem Python compatível; não declare implantação bem-sucedida sem testes. Caddy obtém certificado público pelo DNS real e renova automaticamente. Confirme que o DNS resolve para o IP da VM, as portas 80/443 estão acessíveis e não há erro nos logs `journalctl -u tarefas -u caddy`. O arquivo do banco fica em /var/lib/tarefas/tarefas.db, no disco de SO persistente, e não na pasta pública nem no disco temporário. Caddy atua apenas como proxy; não há file_server.

## 5. Validar publicamente

Abra https://DNS_REAL/docs. Execute POST /tarefas, GET /tarefas, GET /tarefas/ID, PUT /tarefas/ID, DELETE /tarefas/ID e GET /tarefas/ID, esperando 201, 200, 200, 200, 204 e 404. Execute também POST com título vazio e status inválido (422), e consulta por ID inexistente (404). Salve requisições e respostas com data. Não use /health como única evidência.

Crie outra tarefa fictícia, registre ID e todos os campos e execute `az vm restart -g rg-api-tarefas-academica -n vm-api-tarefas`. Aguarde o HTTPS voltar e consulte o mesmo ID: os campos devem permanecer idênticos. Capture antes/depois e a reinicialização. Teste também `systemctl restart tarefas` via Run Command. Atualize o README, relatório e tabela de recursos apenas com valores reais retornados pelo Azure.

## 6. Capturas pendentes da nuvem

VM → Visão geral: nome, região, sistema operacional e tamanho. VM → Tamanho: SKU, vCPU e memória. VM → Discos: tipo, capacidade e persistência. IP público → Configuração: SKU e DNS. Assinatura → Créditos/Serviços gratuitos: condição e validade, ocultando nome pessoal, IDs de assinatura, email e dados financeiros. Abra /docs e capture cada operação e código, além da consulta antes/depois da reinicialização. Não publique tokens nem telas com credenciais.

## 7. Backup e restauração

Na VM, execute como usuário tarefas ou root: `/opt/tarefas/.venv/bin/python /opt/tarefas/scripts/backup.py /var/lib/tarefas/tarefas.db /var/lib/tarefas/backup-data.db`. O script exige destino novo e usa a API de backup do SQLite, verificando integridade. Copie para outro local privado para sobreviver à exclusão do disco; isso não está provisionado automaticamente. Planeje retenção e custo antes de contratar armazenamento adicional. Não publique backups no GitHub.

Para restaurar, pare `systemctl stop tarefas`, preserve o banco atual em um nome novo, copie o backup para /var/lib/tarefas/tarefas.db, ajuste proprietário tarefas:tarefas e permissão 600, verifique `PRAGMA integrity_check` com sqlite3 em Python, inicie `systemctl start tarefas` e consulte os registros esperados. A restauração na nuvem está pendente; o procedimento local está documentado e pode ser exercitado sem custos.

## 8. Interromper e remover

Para interrupção temporária: `az vm deallocate -g rg-api-tarefas-academica -n vm-api-tarefas`. Isso interrompe a cobrança de computação da VM desalocada, mas disco e IP podem continuar consumindo créditos. Para encerrar, faça backup privado, confirme que o grupo contém somente este projeto com `az resource list -g rg-api-tarefas-academica -o table`, e execute `az group delete -n rg-api-tarefas-academica --yes`. Confirme `az group exists -n rg-api-tarefas-academica` retornando false e confira custos finais no portal. Exclusão é irreversível; não execute antes da apresentação e sem preservar os dados necessários.
