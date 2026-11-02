# Implantação e operação da API na Azure

## 1. Configuração efetivamente implantada

Verificada em 02/11/2026. Grupo exclusivo `rg-api-tarefas-academica`, região **Mexico Central**, VM `vm-api-tarefas`, SKU **Standard_B2ats_v2** (2 vCPUs, 1 GiB), imagem oficial `Debian:debian-12:12-gen2:0.20261026.2643`. Disco de SO `disk-api-tarefas`, **Standard_LRS/HDD, 32 GiB**, persistente; IP `ip-api-tarefas`, **Standard estático**. A VM está ligada e foi mantida assim para apresentação.

URL base: https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com

- Lista pública: https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/tarefas
- Swagger: https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/docs
- Saúde: https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/health

O caminho raiz `/` não tem rota. Use `/docs` ou `/tarefas` para abrir a aplicação.

## 2. Disponibilidade e preços

A assinatura restringe regiões a Canada Central, Central US, Mexico Central, Chile Central e South Africa North. Consultas autenticadas encontraram B1s indisponível; B2ats_v2 sem bloqueio regional nas três últimas. Isso foi seguido da criação bem-sucedida em Mexico Central. Imagem Debian sem plano adicional de Marketplace (plan null).

Preços de varejo oficiais em Mexico Central, consultados em 02/11/2026:

|Item|Valor|Condição|
|---|---|---|
|B2ats v2 Linux|US$ 0,0103/h|Computação em funcionamento|
|IP Standard IPv4|US$ 0,005/h|Recurso alocado|
|HDD S4 LRS 32 GiB|US$ 1,6896/mês|Disco gerenciado persistente|
|Operações HDD|US$ 0,00055/10 mil|Dependem do uso|

Base de 730 horas: **US$ 12,8586/mês**, aproximadamente US$ 0,42 por 24 horas. Mais operações e eventual tráfego, tributos/câmbio aplicáveis, antes de franquias ou benefícios. São preços de referência e não uma fatura apurada. Fonte: https://prices.azure.com/api/retail/prices, arquivo `docs/evidencias/nuvem/precos-verificados.json`. VNet/sub-rede e NSG não têm tarifa básica de criação; a NIC padrão não adicionou um serviço tarifado separado nesta implantação. Não há Bastion, balanceador, conta Storage, Log Analytics ou backup externo contratado por este projeto.

O consumo de créditos acadêmicos foi autorizado. O limite de gastos da assinatura foi mantido. Saldo e identificadores de assinatura não são publicados. Não foi presumida gratuidade de VM/disco/IP.

O HDD foi escolhido pelo menor custo para a demonstração pequena e passou nos testes. A Microsoft recomenda SSD para sistemas operacionais e bancos transacionais em produção; não se trata de uma recomendação de HDD para produção.

## 3. Provisionamento reproduzível

Os recursos já existem; **não execute o provisionador novamente para atualizar a API**. Para reproduzir em outra implantação autorizada, tenha Azure CLI autenticado e Git. Confirme assinatura, região permitida, disponibilidade, quota e preços. O DNS global deverá ser único. Na raiz:

```powershell
./deploy/provisionar.ps1 -AutorizarConsumoDeCreditos -Regiao mexicocentral -Tamanho Standard_B2ats_v2 -Dns NOME_DNS_UNICO
```

O script protege contra nova criação quando a VM já existe, verifica spendingLimit On, cria grupo exclusivo e VM, gera chave SSH local sem publicá-la e configura somente 80/443. Os comandos executados nesta implantação usaram uma chave exclusiva na pasta privada local. A porta SSH pública permaneceu fechada; a administração usa Azure Run Command autenticado.

A imagem foi fixada à versão verificada. Em uma implantação futura, confirme se a imagem continua disponível e se o SKU ainda possui capacidade. Uma falha deve ser inspecionada; recursos incompletos do projeto devem ser removidos antes de tentar outra região. Não altere outros grupos.

## 4. Instalação do código e HTTPS

```powershell
./deploy/instalar-azure.ps1
```

Esse script lê o FQDN do IP real, prepara payload para **Bash** e chama Azure Run Command. No Debian, Run Command usa `/bin/sh`; por isso o wrapper chama Bash explicitamente antes de usar `set -euo pipefail`. O instalador instala Python/venv, Git, Caddy e curl, clona o repositório em `/opt/tarefas`, instala requirements.txt e cria usuário de serviço `tarefas`.

O SQLite fica em `/var/lib/tarefas/tarefas.db`, com pasta privada e arquivo 600. O disco é `/dev/sda1`, ext4 montado em `/`, confirmado por findmnt. Não se usa armazenamento temporário. A exportação pública do disco está bloqueada (networkAccessPolicy DenyAll e publicNetworkAccess Disabled). Isso não é um endpoint do banco.

A unidade `tarefas.service` usa um worker, reinício em falhas, usuário sem shell, NoNewPrivileges, ProtectSystem e escrita permitida em /var/lib/tarefas. Caddy encaminha HTTPS para `127.0.0.1:8000`, sem servir arquivos. Sua configuração local de produção usa o FQDN real; deploy/Caddyfile é um modelo com domínio de exemplo explicitamente inválido.

O certificado Let's Encrypt foi obtido e validado sem desativar verificação TLS. Foi observado TLS 1.3 e redirect HTTP 308. Detalhes e validade no arquivo `https-rede.json`. A renovação é administrada pelo Caddy enquanto a VM, o DNS e a conectividade estiverem disponíveis.

Não considere o texto `Provisioning succeeded` do Run Command como sucesso suficiente: confira stdout/stderr, serviços, HTTPS e CRUD. A primeira tentativa encontrou diferença de shell e foi corrigida; a implantação bem-sucedida foi comprovada pelos testes públicos posteriores.

## 5. Testes públicos executados

Foram registradas 23 requisições com assertions, além de operações capturadas no Swagger. Incluem POST 201, GET 200, PUT 200, DELETE 204, consulta após exclusão 404, entradas inválidas 422, atualização inválida preservando dados, listagem e registro ausente. Uma tarefa ID 2 foi consultada antes, depois de reiniciar o serviço e depois de reiniciar a VM: todos os campos permaneceram iguais. Veja `testes-publicos.json`, `testes-publicos.txt`, `persistencia-publica.json` e prints `08`, `09` e `10` em docs/evidencias/nuvem.

Para reproduzir:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-docs.txt
.venv/Scripts/python.exe -m playwright install chromium
.venv/Scripts/python.exe scripts/verify_public.py --base-url https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com --restart-azure
```

O script usa o Azure CLI autenticado para `systemctl restart tarefas` e `az vm restart`, aguardando o retorno do HTTPS. Não execute durante outra apresentação. Para testar apenas HTTP/Swagger sem reiniciar, omita `--restart-azure`.

Verificações adicionais: /docs, /redoc e /openapi.json 200; arquivos de banco/.env 404; portas 22/8000 não acessíveis da origem de teste; 80/443 abertas. O /health foi apenas uma das verificações.

## 6. Operação e atualização

No portal Azure: VM → Executar comando → RunShellScript. Exemplos:

```sh
systemctl is-active tarefas caddy
systemctl status tarefas --no-pager
journalctl -u tarefas -n 50 --no-pager
journalctl -u caddy -n 50 --no-pager
```

Para atualizar o código, primeiro faça backup. Em Run Command, use `set -eu`, `git -C /opt/tarefas pull --ff-only`, `/opt/tarefas/.venv/bin/pip install -r /opt/tarefas/requirements.txt` e `systemctl restart tarefas`. Não remova /var/lib/tarefas. Confirme a versão e refaça o CRUD e a consulta de um ID anterior. Mudanças futuras de esquema exigem migração; este projeto cria a tabela inicial, mas não tem migrações automáticas.

As versões efetivas na VM foram Python 3.11.2, SQLite 3.40.1, FastAPI 0.162.0, Uvicorn 0.54.0, Pydantic 2.14.2, Starlette 1.10.0 e Caddy 2.6.2. Veja runtime-backup.json. O código da aplicação testado corresponde ao commit registrado nesse arquivo; os commits seguintes também incluem documentação e ferramentas de implantação.

## 7. Backup e restauração

O script usa a Online Backup API do SQLite e integrity_check. Crie destino novo, nunca publique o banco:

```sh
install -d -m 700 -o tarefas -g tarefas /var/lib/tarefas/backups
runuser -u tarefas -- /opt/tarefas/.venv/bin/python /opt/tarefas/scripts/backup.py /var/lib/tarefas/tarefas.db /var/lib/tarefas/backups/backup-NOME_UNICO.db
```

Backup e restauração em arquivo separado **foram executados na VM**: um registro fictício comparado, dados idênticos e integridade ok. O banco público não foi substituído durante esse teste. O script de verificação está em scripts/check_runtime.sh e o resultado em runtime-backup.json.

As cópias estão no mesmo disco, sem agendamento e sem armazenamento externo: não protegem contra exclusão/perda desse disco. Antes de excluir o grupo, transfira uma cópia para local privado fora dele, se precisar dos dados. A chave privada local não deve ser publicada nem enviada pelo chat. Armazenamento externo adicional não foi contratado.

Para restaurar no banco da API, via Run Command, adaptando BACKUP_EXISTENTE e nomes novos:

```sh
set -eu
systemctl stop tarefas
# Preserve a cópia atual antes de substituir qualquer arquivo.
cp -p /var/lib/tarefas/tarefas.db /var/lib/tarefas/backups/antes-restauracao-NOME_UNICO.db
cp BACKUP_EXISTENTE /var/lib/tarefas/tarefas.db
chown tarefas:tarefas /var/lib/tarefas/tarefas.db
chmod 600 /var/lib/tarefas/tarefas.db
/opt/tarefas/.venv/bin/python -c 'import sqlite3; c=sqlite3.connect("/var/lib/tarefas/tarefas.db"); assert c.execute("PRAGMA integrity_check").fetchone()[0]=="ok"; c.close()'
systemctl start tarefas
```

Depois consulte registros conhecidos pela URL pública. Não execute a substituição com a aplicação ativa. Se a integridade falhar, mantenha o serviço parado e recupere a cópia preservada. O procedimento de substituição do banco ativo está documentado; o teste real usou arquivo separado.

## 8. Prints adicionais do portal

As evidências obrigatórias de CRUD, testes, persistência e repositório foram capturadas. A infraestrutura tem capturas identificadas de **saídas reais da CLI**, não de um painel simulado. Para complementar com telas do portal autenticado:

1. Azure → Grupos de recursos → rg-api-tarefas-academica → Visão geral: mostre os recursos e a região.
2. VM vm-api-tarefas → Visão geral ou Tamanho: nome, Linux, Mexico Central, Standard_B2ats_v2, 2 vCPUs e 1 GiB.
3. VM → Discos e depois disk-api-tarefas → Visão geral: Standard HDD LRS, 32 GiB, disco de SO gerenciado.
4. ip-api-tarefas → Visão geral/Configuração: SKU Standard, estático e DNS; NSG → regras de entrada: somente regras públicas 80/443.

Oculte nome pessoal, email, ID da assinatura, tenant e informações financeiras. Não é necessário mostrar saldo dos créditos. Confirme que cada imagem está legível e corresponda aos nomes reais. Essas telas complementam o inventário já comprovado pela CLI; não precisam ser inventadas para concluir os testes técnicos.

## 9. Interromper e excluir para evitar consumo posterior

Os recursos permanecem ligados para apresentação. Para pausa temporária:

```powershell
az vm deallocate -g rg-api-tarefas-academica -n vm-api-tarefas
```

Desalocar para a computação, mas disco e IP alocados podem continuar consumindo créditos. Desligar apenas dentro do Linux não equivale a desalocar. Não remova o limite de gastos.

Para encerrar definitivamente após a entrega, salve o material e eventual backup privado e confira o grupo exclusivo:

```powershell
az resource list -g rg-api-tarefas-academica -o table
az group delete -n rg-api-tarefas-academica --yes
az group exists -n rg-api-tarefas-academica
```

A confirmação final deve ser `false`. Confira também o custo final no portal, que pode aparecer com atraso. A exclusão é irreversível e remove VM, disco/banco, IP e rede deste grupo. O repositório e os relatórios publicados no GitHub permanecem. **Nenhuma exclusão foi executada após os testes.**
