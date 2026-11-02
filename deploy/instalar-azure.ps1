$ErrorActionPreference='Stop'
$project=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$rg='rg-api-tarefas-academica'
$domain=az network public-ip show -g $rg -n ip-api-tarefas --query dnsSettings.fqdn -o tsv
if($LASTEXITCODE -or -not $domain){throw 'DNS publico nao encontrado'}
$source=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'instalar.sh'))
$payload="#!/bin/sh`nexport API_DOMAIN=$domain`nbash <<'TAREFAS_INSTALL'`n$source`nTAREFAS_INSTALL`n"
$tempDir=Join-Path $project '.private'
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
$scriptFile=Join-Path $tempDir 'install-cloud.sh'
[IO.File]::WriteAllText($scriptFile,$payload,(New-Object Text.UTF8Encoding($false)))
$result=az vm run-command invoke -g $rg -n vm-api-tarefas --command-id RunShellScript --scripts "@$scriptFile" -o json
if($LASTEXITCODE){throw 'Falha na execucao remota'}
$result
Write-Host 'Confirme stdout/stderr e valide HTTPS e CRUD; Provisioning succeeded sozinho nao comprova sucesso do instalador.'
