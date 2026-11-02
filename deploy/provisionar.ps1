param([switch]$AutorizarConsumoDeCreditos)
$ErrorActionPreference='Stop'
if (-not $AutorizarConsumoDeCreditos) { throw 'A criação pode consumir créditos. Revise docs/implantacao.md e autorize expressamente.' }
$account=az account show -o json | ConvertFrom-Json
$all=az rest --method get --url 'https://management.azure.com/subscriptions?api-version=2022-12-01' -o json | ConvertFrom-Json
$subscription=$all.value | Where-Object subscriptionId -eq $account.id
if ($subscription.subscriptionPolicies.spendingLimit -ne 'On') { throw 'Limite de gastos deve estar On. Não o remova.' }
$rg='rg-api-tarefas-academica'
$region='canadacentral'
$dns="tarefas-$([guid]::NewGuid().ToString('N').Substring(0,10))"
$skus=az vm list-skus --location $region --size Standard_B1s --all -o json | ConvertFrom-Json
$sku=$skus | Where-Object name -eq 'Standard_B1s'
if (-not $sku -or @($sku.restrictions | Where-Object type -eq 'Location').Count -gt 0) { throw 'SKU indisponível nesta assinatura/região. Não foram criados recursos. Revise região, quota e orçamento.' }
az group create --name $rg --location $region -o none
if ($LASTEXITCODE) { throw 'Falha no grupo de recursos' }
az vm create --resource-group $rg --name vm-api-tarefas --location $region --image Ubuntu2204 --size Standard_B1s --admin-username azureuser --generate-ssh-keys --storage-sku StandardSSD_LRS --os-disk-size-gb 32 --public-ip-sku Standard --public-ip-address-dns-name $dns --nsg-rule NONE -o json
if ($LASTEXITCODE) { throw 'Falha na VM. Inspecione e remova recursos incompletos se necessário.' }
# Administração pelo Run Command autenticado do Azure. Nenhuma porta SSH pública.
az vm open-port --resource-group $rg --name vm-api-tarefas --port 80 --priority 1000 -o none
az vm open-port --resource-group $rg --name vm-api-tarefas --port 443 --priority 1010 -o none
$fqdn=az network public-ip list -g $rg --query '[0].dnsSettings.fqdn' -o tsv
Write-Host "DNS: $fqdn. Use o procedimento de instalação; a API ainda não está implantada."
