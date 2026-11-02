# GS_Cloud

API acadêmica de gerenciamento de tarefas, desenvolvida em Python com FastAPI e SQLite e hospedada em uma VM Debian 12 na Microsoft Azure.

## Entrega

- **[Documentação acadêmica - GS_Cloud.pdf](docs/GS_Cloud.pdf)**: explicação resumida, esquemas visuais e minhas capturas completas.
- **Repositório público:** https://github.com/shamiryy/GS_Cloud
- **API:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/tarefas
- **Swagger:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/docs
- **Saúde:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/health
- **OpenAPI:** https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com/openapi.json

A raiz `/` não possui rota; abra `/docs` ou `/tarefas`. A aplicação permanece ligada para apresentação e pode consumir créditos.

## Estrutura e arquitetura

```text
app/          Aplicação FastAPI e modelos
tests/       Testes isolados com bancos temporários
 deploy/      Instalação Debian, Caddy, systemd e provisionamento Azure
 scripts/     Backup, verificações e geração do PDF
 docs/        GS_Cloud.pdf, diagramas, versões e evidências
```

Cliente → HTTPS/Caddy → FastAPI/Uvicorn → SQLite em disco persistente. Na VM, o banco fica em `/var/lib/tarefas/tarefas.db`, com permissão 600, fora do código. Há uma VM e um worker. Consultas SQL usam parâmetros; validação é feita pelo Pydantic. .env, chaves, bancos, backups e .private não são publicados.

## Execução local

No PowerShell, com Python 3.13 e Git:

```powershell
git clone https://github.com/shamiryy/GS_Cloud.git
cd GS_Cloud
py -3.13 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
$env:DATABASE_PATH="data/tarefas.db"
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8088 --workers 1
```

Abra http://127.0.0.1:8088/docs após iniciar. No Linux use `python3` e `.venv/bin/python`. `.env.example` documenta a variável; o aplicativo não carrega `.env` automaticamente. Dependências de produção estão em requirements.txt; versões locais e da nuvem em [docs/versoes.json](docs/versoes.json).

## Dados e endpoints

Cada tarefa tem ID, título, descrição, status e data de criação UTC. Título: 1 a 120 caracteres; descrição: até 2000. Status: pendente, em_andamento ou concluida. ID/data são gerados no servidor; campos extras são rejeitados.

|Método|Endpoint|Resultado|
|---|---|---|
|POST|/tarefas|Cria, 201 + Location|
|GET|/tarefas|Lista, 200|
|GET|/tarefas/{task_id}|Consulta, 200 ou 404|
|PUT|/tarefas/{task_id}|Atualiza, 200 ou 404|
|DELETE|/tarefas/{task_id}|Exclui, 204 ou 404|
|GET|/health|Verifica API/banco, 200|

JSON de POST/PUT: `{"titulo":"Estudar SQLite","descricao":"Dado fictício","status":"pendente"}`. PUT substitui os campos editáveis e preserva ID/data. Omitir descrição/status redefine seus padrões. Paginação: limit entre 1 e 100 (padrão 100), offset não negativo. Erros: 422 para entrada inválida, 404 para registro inexistente e 503 para falha SQLite durante a requisição.

## Testes e evidências

```powershell
.venv/Scripts/python.exe -m pytest -v
```

17 testes locais aprovados, com um aviso de depreciação TestClient/httpx sem falhas. Foram registradas 23 requisições públicas aprovadas, além das operações capturadas no Swagger. O registro ID 2 foi preservado após reiniciar serviço e VM. Backup/restauração em arquivo separado também foram verificados.

- [Log local](docs/evidencias/testes-locais.txt)
- [Requisições públicas](docs/evidencias/nuvem/testes-publicos.json)
- [Persistência](docs/evidencias/nuvem/persistencia-publica.json)
- [Infraestrutura real](docs/evidencias/nuvem/recursos-azure.json)
- [Backup e runtime](docs/evidencias/nuvem/runtime-backup.json)
- [Prints fornecidos para a entrega](docs/evidencias/entrega/)

O PDF exportado do Swagger mostra exemplos do contrato, não um log de CRUD executado. Os testes executados estão nos registros acima. As capturas usadas na entrega são os arquivos originais integrais, sem recortes ou censura, conforme a versão final solicitada.

## Hospedagem e operação

Azure Mexico Central; VM `vm-api-tarefas`; SKU `Standard_B2ats_v2` (2 vCPUs, 1 GiB); Debian 12; HDD `Standard_LRS` de 32 GiB; IP Standard estático. O NSG libera publicamente somente 80/443; Uvicorn fica em loopback. Administração por Azure Run Command.

[Comandos de implantação, backup e encerramento](deploy/README.md). Referência de varejo de 02/11/2026: base US$ 12,86/mês para 730 horas, mais operações e eventual tráfego, antes de benefícios. [Preços consultados](docs/evidencias/nuvem/precos-verificados.json). Não é fatura nem promessa de gratuidade.

## Limitações

Demonstração sem autenticação: qualquer visitante pode alterar e excluir tarefas. Use somente dados fictícios. Não há alta disponibilidade, rate limiting ou migrações automáticas. As cópias no mesmo disco não protegem contra sua exclusão. Após a apresentação, exclua o grupo exclusivo para encerrar o consumo; desalocar a VM não elimina necessariamente custos de disco/IP.

## Gerar o documento

Com as evidências já incluídas, Python e fontes Arial disponíveis no Windows:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-docs.txt
.venv/Scripts/python.exe scripts/build_gs_cloud.py
```

Saída: `docs/GS_Cloud.pdf`. O gerador verifica o total de 16 páginas e renderiza imagens em qa para revisão. Os relatórios extensos anteriores foram substituídos por essa documentação.
