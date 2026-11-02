# API acadêmica de tarefas — FastAPI e SQLite

API REST simples com CRUD, validação, erros HTTP e documentação Swagger. Use somente dados fictícios.

**Estado real:** implementação e testes locais concluídos; repositório publicado. **Hospedagem pública pendente de autorização para consumo de créditos Azure.** Não há URL pública nem Swagger hospedado neste momento.

Repositório: https://github.com/shamiryy/api-tarefas-fastapi-sqlite

## Arquitetura

Cliente → FastAPI/Uvicorn → SQLite em arquivo. A proposta de nuvem acrescenta VM Linux, Caddy HTTPS e disco de SO persistente. Uma instância e um worker, evitando compartilhar o SQLite entre servidores. Veja [diagrama](docs/diagramas/01-arquitetura.png), [modelo](docs/diagramas/02-modelo.png) e [fluxo](docs/diagramas/03-fluxo.png).

## Execução local

Python 3.13. No PowerShell:

```powershell
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
$env:DATABASE_PATH="data/tarefas.db"
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8088 --workers 1
```

Abra http://127.0.0.1:8088/docs após iniciar o servidor. OpenAPI em /openapi.json e documentação alternativa em /redoc. .env.example é apenas referência: o arquivo .env não é carregado automaticamente.

## Endpoints

|Método|Caminho|Sucesso|
|---|---|---|
|GET|/health|200|
|POST|/tarefas|201 + Location|
|GET|/tarefas?limit=100&offset=0|200|
|GET|/tarefas/{task_id}|200|
|PUT|/tarefas/{task_id}|200|
|DELETE|/tarefas/{task_id}|204 sem corpo|

POST/PUT: `{"titulo":"Estudar SQLite","descricao":"Exemplo fictício","status":"pendente"}`. Título obrigatório de 1 a 120 caracteres; descrição até 2000; status pendente, em_andamento ou concluida. Campos extras são rejeitados. PUT substitui os campos editáveis e mantém ID/data. Erros: 422 para entrada inválida, 404 para registro ausente e 503 para falhas SQLite. Banco usa consultas parametrizadas e transações.

## Testes reais

```powershell
.venv/Scripts/python.exe -m pytest -v
```

17 testes aprovados, incluindo CRUD, entradas inválidas, ausentes, persistência, injeção SQL literal e OpenAPI. Veja [log real](docs/evidencias/testes-locais.txt). Há um aviso de depreciação do TestClient/httpx, sem falhas. O [registro de reinício real](docs/evidencias/reinicio-processo-local.json) comprova o mesmo registro após encerrar e iniciar Uvicorn. [Prints reais locais e GitHub](docs/evidencias/) acompanham o relatório. Testes de nuvem ainda não executados.

## Hospedagem e custos

[Procedimento integral](docs/implantacao.md). VM Azure proposta, região Canada Central, SKU Standard_B1s, SSD E4 32 GiB, IP Standard. Estimativa de varejo consultada em 02/11/2026: base US$ 14,76/mês (730 horas), mais operações/tráfego aplicáveis, antes de benefícios gratuitos. Conta Azure for Students com limite de gastos On; saldo não confirmado. **Nenhum recurso criado e nenhum SKU efetivamente utilizado para hospedagem.** Não execute scripts de criação sem autorizar consumo de créditos. Não remova o limite de gastos. Os arquivos preparados não comprovam deploy.

## Backup restauração e encerramento

`scripts/backup.py ORIGEM DESTINO_NOVO` usa SQLite backup e integrity_check. Não publique arquivos .db ou backups. Para restaurar, pare a aplicação, preserve o banco atual, copie o backup, ajuste permissões, verifique integridade e reinicie. Na nuvem, desalocar não elimina custos de disco/IP; revise os recursos e exclua o grupo exclusivo após backup para encerramento definitivo. Comandos e confirmações em docs/implantacao.md.

## Documentação e limitações

[Relatório detalhado](docs/relatorio.md), [versões](docs/versoes.json), scripts em deploy e testes em tests. [Documento Word](docs/relatorio-academico.docx) e [PDF](docs/relatorio-academico.pdf), gerados com Word e revisados por renderização. O SKU Standard_B1s retornou NotAvailableForSubscription em Canada Central; definir alternativa disponível e revisar custos continua pendente.

Demonstração sem autenticação: qualquer visitante pode alterar e apagar qualquer tarefa. HTTPS não substitui autorização. Sem alta disponibilidade, controle de usuários, rate limiting ou migrações. Use somente dados fictícios e retire a demonstração quando não for necessária.

## Pendências

Autorizar uso de créditos e confirmar saldo; criar e validar VM/HTTPS; executar CRUD e reinício públicos; capturar SKU/disco/portal; atualizar URL e inventário reais; preencher nome, matrícula, turma, disciplina e professor. A hospedagem não está concluída.
