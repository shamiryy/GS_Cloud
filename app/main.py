import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException, Response, Query
from pydantic import BaseModel, ConfigDict, Field

Status = Literal["pendente", "em_andamento", "concluida"]
class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    titulo: str = Field(min_length=1, max_length=120)
    descricao: str = Field(default="", max_length=2000)
    status: Status = "pendente"
class Task(TaskInput):
    id: int
    data_criacao: datetime

def create_app(db_path=None):
    path = Path(db_path or os.getenv("DATABASE_PATH", "data/tarefas.db"))
    @contextmanager
    def connection():
        db = sqlite3.connect(path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()
    @asynccontextmanager
    async def lifespan(app):
        path.parent.mkdir(parents=True, exist_ok=True)
        with connection() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL CHECK(length(titulo) BETWEEN 1 AND 120),
                descricao TEXT NOT NULL DEFAULT '' CHECK(length(descricao)<=2000),
                status TEXT NOT NULL CHECK(status IN ('pendente','em_andamento','concluida')),
                data_criacao TEXT NOT NULL)""")
        yield
    api = FastAPI(title="API acadêmica de tarefas", version="1.0.0", lifespan=lifespan,
                  description="Demonstração pública sem autenticação. Use apenas dados fictícios.")
    def find(db, task_id):
        row = db.execute("SELECT * FROM tarefas WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise HTTPException(404, "Tarefa não encontrada")
        return dict(row)
    @api.exception_handler(sqlite3.Error)
    async def database_error(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"detail":"Banco de dados temporariamente indisponível"})
    @api.get("/health", tags=["Saúde"])
    def health():
        with connection() as db:
            db.execute("SELECT COUNT(*) FROM tarefas").fetchone()
        return {"status":"ok"}
    @api.post("/tarefas", response_model=Task, status_code=201, tags=["Tarefas"])
    def create(task: TaskInput, response: Response):
        with connection() as db:
            cursor=db.execute("INSERT INTO tarefas (titulo,descricao,status,data_criacao) VALUES (?,?,?,?)",
                (task.titulo,task.descricao,task.status,datetime.now(timezone.utc).isoformat()))
            result=find(db,cursor.lastrowid)
        response.headers["Location"]=f"/tarefas/{result['id']}"
        return result
    @api.get("/tarefas", response_model=list[Task], tags=["Tarefas"])
    def list_tasks(limit: int=Query(100,ge=1,le=100), offset: int=Query(0,ge=0)):
        with connection() as db:
            return [dict(r) for r in db.execute("SELECT * FROM tarefas ORDER BY id LIMIT ? OFFSET ?",(limit,offset))]
    @api.get("/tarefas/{task_id}", response_model=Task, tags=["Tarefas"])
    def get(task_id:int):
        with connection() as db:
            return find(db,task_id)
    @api.put("/tarefas/{task_id}", response_model=Task, tags=["Tarefas"])
    def update(task_id:int, task:TaskInput):
        with connection() as db:
            find(db,task_id)
            db.execute("UPDATE tarefas SET titulo=?,descricao=?,status=? WHERE id=?",(task.titulo,task.descricao,task.status,task_id))
            return find(db,task_id)
    @api.delete("/tarefas/{task_id}", status_code=204, tags=["Tarefas"])
    def delete(task_id:int):
        with connection() as db:
            find(db,task_id)
            db.execute("DELETE FROM tarefas WHERE id=?",(task_id,))
        return Response(status_code=204)
    return api
app=create_app()
