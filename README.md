# API acadêmica de tarefas com FastAPI e SQLite

API REST para criar, listar, consultar, atualizar e excluir tarefas fictícias. Implementada em Python, com validação Pydantic, consultas SQL parametrizadas e documentação OpenAPI/Swagger.

- **API pública — lista de tarefas:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/tarefas
- **Swagger interativo:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/docs
- **Saúde:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/health
- **OpenAPI:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/openapi.json
- **Repositório:** https://github.com/shamiryy/api-tarefas-fastapi-sqlite

Implantação verificada em **02/11/2026**. CRUD e erros testados por HTTPS; persistência comprovada após reinício do serviço e da VM. A aplicação permanece ligada para apresentação e consome créditos até ser interrompida/excluída. O caminho raiz `/` não possui rota; use os links acima.

## Objetivo e arquitetura

Cliente → HTTPS/Caddy → FastAPI/Uvicorn em uma VM Debian 12 → SQLite no disco gerenciado persistente. Uma VM, uma instância e um worker. O banco fica em `/var/lib/tarefas/tarefas.db`, fora do código e de qualquer pasta pública, com permissão 600. Não há conta de armazenamento separada nem banco gerenciado.

[Arquitetura](docs/diagramas/01-arquitetura.png) · [Modelo de dados](docs/diagramas/02-modelo.png) · [Fluxo](docs/diagramas/03-fluxo.png).

## Estrutura

`app/`: aplicação e modelos. `tests/`: suíte isolada. `scripts/`: backup, verificação pública, capturas e relatório. `deploy/`: instalação Debian, systemd, Caddy e provisionamento Azure. `docs/`: documentação, diagramas, evidências e documentos finais. `.private/`, `.env`, chaves, bancos e backups ficam fora do Git.

## Execução local

Python 3.13 foi usado localmente; a VM executa Python 3.11.2. No PowerShell:

```powershell
git clone https://github.com/shamiryy/api-tarefas-fastapi-sqlite.git
cd api-tarefas-fastapi-sqlite
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
$env:DATABASE_PATH="data/tarefas.db"
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8088 --workers 1
```

Abra http://127.0.0.1:8088/docs após iniciar. Interrompa com Ctrl+C. O arquivo `.env.example` documenta a variável; `.env` não é carregado automaticamente. No Linux, crie o ambiente com `python3 -m venv .venv` e use `.venv/bin/python`.

## Modelo e endpoints

Campos: `id` inteiro gerado; `titulo` obrigatório de 1 a 120 caracteres; `descricao` de até 2000, padrão vazio; `status` pendente, em_andamento ou concluida; `data_criacao` UTC gerada no servidor. Campos extras são rejeitados. Espaços nas extremidades são removidos.

|Método|Caminho|Sucesso|
|---|---|---|
|GET|/health|200|
|POST|/tarefas|201 + Location|
|GET|/tarefas?limit=100&offset=0|200|
|GET|/tarefas/{task_id}|200|
|PUT|/tarefas/{task_id}|200|
|DELETE|/tarefas/{task_id}|204 sem corpo|

POST/PUT: `{"titulo":"Estudar SQLite","descricao":"Exemplo fictício","status":"pendente"}`. PUT substitui todos os campos editáveis: omitir descrição/status redefine seus padrões; ID/data permanecem. Erros: 422 para entrada inválida, 404 para registro ausente e 503 para falha SQLite. A listagem aceita limit entre 1 e 100 e offset não negativo.

## Testes executados

```powershell
.venv/Scripts/python.exe -m pytest -v
```

**17 testes locais aprovados**: CRUD, oito entradas inválidas, três operações em registro inexistente, persistência, injeção SQL literal, atualização inválida, paginação e OpenAPI. Há um aviso de depreciação TestClient/httpx, sem falhas. [Log local](docs/evidencias/testes-locais.txt).

**23 requisições públicas aprovadas**, além das operações capturadas no Swagger e verificações de HTTPS/rede. Reinícios reais do serviço e da VM mantiveram a tarefa ID 2 idêntica. [Resultados públicos](docs/evidencias/nuvem/testes-publicos.json), [persistência](docs/evidencias/nuvem/persistencia-publica.json), [prints reais](docs/evidencias/nuvem/) e [HTTPS/rede](docs/evidencias/nuvem/https-rede.json).

Para reproduzir as verificações públicas: instale requirements-docs.txt, execute `.venv/Scripts/python.exe -m playwright install chromium` e depois:

```powershell
.venv/Scripts/python.exe scripts/verify_public.py --base-url https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com --restart-azure
```

O parâmetro de reinício usa Azure CLI autenticado e reinicia a VM real. Use apenas na demonstração; sem o parâmetro não há reinicialização. Ele cria e exclui somente suas tarefas de teste, mantendo uma tarefa fictícia para persistência.

## Hospedagem e custo

**Microsoft Azure / Mexico Central / vm-api-tarefas / Standard_B2ats_v2 / 2 vCPUs / 1 GiB / Debian 12.** Disco `disk-api-tarefas`, HDD `Standard_LRS` de 32 GiB (faixa S4); IP `ip-api-tarefas`, SKU Standard estático; grupo `rg-api-tarefas-academica`. Apenas 80/443 liberadas ao público; SSH e porta 8000 bloqueados no NSG. Administração por Azure Run Command.

Consulta oficial de varejo de 02/11/2026: VM US$ 0,0103/h, IP US$ 0,005/h, disco US$ 1,6896/mês. **Base estimada US$ 12,86/mês para 730 horas**, mais operações HDD (US$ 0,00055 por 10 mil) e eventual tráfego, antes de benefícios, câmbio ou tributos. Não é a cobrança efetivamente apurada. Consumo de créditos acadêmicos autorizado; limite de gastos mantido. [Preços verificados](docs/evidencias/nuvem/precos-verificados.json) e [inventário real](docs/evidencias/nuvem/recursos-azure.json).

[Implantação detalhada, manutenção e remoção](docs/implantacao.md). Os scripts estão configurados para a combinação que funcionou. Não crie uma segunda VM para apenas atualizar o código.

## Backup e restauração

`scripts/backup.py ORIGEM DESTINO_NOVO` usa a API de backup SQLite e integrity_check. Backup/restauração local e em arquivo separado na VM foram testados com dados idênticos. [Evidência na VM](docs/evidencias/nuvem/runtime-backup.json). As cópias atuais ficam no mesmo disco e não protegem contra sua exclusão; não há backup externo automático. Nunca publique bancos ou backups no GitHub.

Para restaurar o banco da API, pare o serviço, preserve o banco atual, copie uma cópia verificada para o caminho configurado, ajuste proprietário/permissões, verifique integridade e reinicie. O teste executado restaurou em arquivo separado, sem substituir o banco público. Procedimento completo em docs/implantacao.md.

## Documentação e evidências

[Relatório detalhado](docs/relatorio.md) · [Word](docs/relatorio-academico.docx) · [PDF](docs/relatorio-academico.pdf). Os documentos finais foram refeitos após a implantação: 28 páginas, três diagramas e 15 capturas selecionadas, com revisão visual de todas as páginas. Evidências de infraestrutura foram coletadas da CLI autenticada, com identificadores da assinatura omitidos; não são telas do portal Azure.

## Limitações e encerramento

Demonstração **sem autenticação**: qualquer visitante pode consultar, alterar e excluir qualquer tarefa. Use somente dados fictícios. Sem alta disponibilidade, controle de usuários, rate limiting ou migrações. SQLite serializa escritas; uma instância simplifica o uso do arquivo. O HDD prioriza custo nesta demonstração pequena; para produção, a recomendação da Microsoft é SSD para SO e bancos transacionais.

Para encerrar temporariamente: `az vm deallocate -g rg-api-tarefas-academica -n vm-api-tarefas` — disco/IP podem continuar sendo cobrados. Após backup privado e conferência de que o grupo contém somente este trabalho, exclua o grupo pelo portal ou `az group delete -n rg-api-tarefas-academica --yes`. Confirme `az group exists -n rg-api-tarefas-academica` retornando false e confira custos finais no portal. **Não foram excluídos nem desligados os recursos após os testes.**

Nome, matrícula, turma, disciplina e professor ainda precisam ser preenchidos pela estudante. As demais evidências técnicas estão publicadas; capturas adicionais do portal são orientadas no relatório.
