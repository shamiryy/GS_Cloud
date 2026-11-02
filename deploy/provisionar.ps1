param(
 [switch]$AutorizarConsumoDeCreditos,
 [string]$Regiao='mexicocentral',
 [string]$Tamanho='Standard_B2ats_v2',
 [string]$Dns='tarefas-academica-shamiryy-20261102'
)
$ErrorActionPreference='Stop'
if(-not $AutorizarConsumoDeCreditos){throw 'Revise os custos e autorize explicitamente o consumo de creditos.'}
$rg='rg-api-tarefas-academica'
$existing=az vm list -g $rg --query "[?name=='vm-api-tarefas'].name" -o tsv 2>$null
if($existing){throw 'A VM ja existe. Nao execute novamente para atualizar; siga o procedimento de atualizacao.'}
$account=az account show -o json | ConvertFrom-Json
$all=az rest --method get --url 'https://management.azure.com/subscriptions?api-version=2022-12-01' -o json | ConvertFrom-Json
$subscription=$all.value | Where-Object subscriptionId -eq $account.id
if($subscription.subscriptionPolicies.spendingLimit -ne 'On'){throw 'Mantenha o limite de gastos ativo.'}
az group create -n $rg -l $Regiao --tags projeto=api-tarefas-academica finalidade=demonstracao-academica -o none
if($LASTEXITCODE){throw 'Falha ao criar grupo exclusivo'}
az vm create -g $rg -n vm-api-tarefas -l $Regiao --image Debian:debian-12:12-gen2:0.20261026.2643 --size $Tamanho --admin-username azureuser --generate-ssh-keys --storage-sku Standard_LRS --os-disk-size-gb 32 --os-disk-name disk-api-tarefas --public-ip-sku Standard --public-ip-address ip-api-tarefas --public-ip-address-dns-name $Dns --nsg nsg-api-tarefas --nsg-rule NONE --vnet-name vnet-api-tarefas --subnet subnet-api --nic-delete-option Delete --os-disk-delete-option Delete --security-type Standard --tags projeto=api-tarefas-academica -o json
if($LASTEXITCODE){throw 'Criacao nao concluida. Inspecione e remova somente os recursos incompletos deste projeto antes de tentar outra regiao.'}
foreach($port in @(80,443)){
 $priority=if($port -eq 80){1000}else{1010}
 az network nsg rule create -g $rg --nsg-name nsg-api-tarefas -n "permitir-$port" --priority $priority --direction Inbound --access Allow --protocol Tcp --source-address-prefixes '*' --source-port-ranges '*' --destination-address-prefixes '*' --destination-port-ranges $port -o none
 if($LASTEXITCODE){throw 'Falha ao configurar NSG'}
}
az disk update -g $rg -n disk-api-tarefas --network-access-policy DenyAll --public-network-access Disabled -o none
if($LASTEXITCODE){throw 'Falha ao proteger exportacao do disco'}
Write-Host 'Infraestrutura criada. Execute deploy/instalar-azure.ps1 e valide o CRUD publico.'
