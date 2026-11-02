# Comandos de implantação e operação

A VM deste projeto já existe. Não rode o provisionamento para apenas atualizar o código.

## Reproduzir em uma nova implantação autorizada

Confirme assinatura, região/SKU disponíveis, quota e custo. O DNS deve ser único.

```powershell
./deploy/provisionar.ps1 -AutorizarConsumoDeCreditos -Regiao mexicocentral -Tamanho Standard_B2ats_v2 -Dns NOME_DNS_UNICO
./deploy/instalar-azure.ps1
```

O instalador usa Bash explicitamente no Azure Run Command, instala Python/Caddy e configura tarefas.service. Banco: /var/lib/tarefas/tarefas.db, usuário tarefas, permissão 600. Deploy/Caddyfile é um modelo; a configuração de produção usa o DNS real. Confirme stdout/stderr, serviços, HTTPS e CRUD: Provisioning succeeded sozinho não basta.

## Verificações

Na VM, por Run Command: `systemctl is-active tarefas caddy` e `journalctl -u tarefas -n 50 --no-pager`.

Para repetir HTTP/Swagger e reinícios reais, com Azure CLI autenticado e Chromium instalado:

```powershell
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe scripts/verify_public.py --base-url https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com --restart-azure
```

Omitir --restart-azure evita os reinícios. Não execute durante apresentação.

## Atualizar código

Faça backup; use `git -C /opt/tarefas pull --ff-only`, instale requirements.txt com /opt/tarefas/.venv/bin/pip e execute `systemctl restart tarefas`. Preserve /var/lib/tarefas e refaça CRUD/consulta de um ID anterior. Mudanças de esquema exigem migração manual.

## Backup e restauração

`scripts/backup.py ORIGEM DESTINO_NOVO` usa SQLite backup e integrity_check. Na VM execute como tarefas ou root; guarde cópias privadas. Para restaurar o banco ativo: pare tarefas, preserve o arquivo atual, copie um backup verificado, ajuste proprietário tarefas:tarefas/permissão 600, verifique integridade, inicie e consulte registros. O teste real restaurou em arquivo separado; não substituiu o banco público. As cópias atuais estão no mesmo disco, sem backup externo automático.

## Encerramento após a entrega

Pausa temporária: `az vm deallocate -g rg-api-tarefas-academica -n vm-api-tarefas`. Disco/IP podem continuar consumindo créditos.

Após preservar o material necessário e conferir que o grupo contém somente este projeto:

```powershell
az resource list -g rg-api-tarefas-academica -o table
az group delete -n rg-api-tarefas-academica --yes
az group exists -n rg-api-tarefas-academica
```

Confirme false e confira custos finais no portal. A exclusão é irreversível, incluindo banco/disco. Nenhuma exclusão de nuvem foi executada durante a atualização da documentação.
