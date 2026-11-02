import pytest
from fastapi.testclient import TestClient
from app.main import create_app

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path/"test.db")) as c:
        yield c

def test_crud(client):
    assert client.get("/health").status_code==200
    r=client.post("/tarefas",json={"titulo":"Estudar SQLite","descricao":"Exemplo fictício"})
    assert r.status_code==201
    item=r.json(); ident=item["id"]
    assert r.headers["location"]==f"/tarefas/{ident}"
    assert client.get("/tarefas").json()==[item]
    assert client.get(f"/tarefas/{ident}").json()==item
    r=client.put(f"/tarefas/{ident}",json={"titulo":"Revisar SQLite","status":"concluida"})
    assert r.status_code==200 and r.json()["status"]=="concluida"
    assert r.json()["data_criacao"]==item["data_criacao"]
    assert client.delete(f"/tarefas/{ident}").status_code==204
    assert client.get(f"/tarefas/{ident}").status_code==404
    assert client.get("/tarefas").json()==[]

@pytest.mark.parametrize("data",[{"titulo":""},{"titulo":"   "},{"titulo":"x"*121},{"titulo":"x","status":"errado"},{"titulo":"x","descricao":"x"*2001},{"titulo":"x","campo_extra":1},{"titulo":None},{}])
def test_invalid(client,data):
    assert client.post("/tarefas",json=data).status_code==422
    assert client.get("/tarefas").json()==[]

@pytest.mark.parametrize("method",["get","put","delete"])
def test_missing(client,method):
    kwargs={"json":{"titulo":"Exemplo"}} if method=="put" else {}
    assert getattr(client,method)("/tarefas/999999",**kwargs).status_code==404

def test_persistence(tmp_path):
    path=tmp_path/"persistent.db"
    with TestClient(create_app(path)) as first:
        item=first.post("/tarefas",json={"titulo":"Persistência fictícia"}).json()
    with TestClient(create_app(path)) as second:
        assert second.get(f"/tarefas/{item['id']}").json()==item

def test_sql_injection(client):
    title="'); DROP TABLE tarefas; --"
    r=client.post("/tarefas",json={"titulo":title})
    assert r.status_code==201 and client.get("/tarefas").json()[0]["titulo"]==title
    assert client.get("/health").status_code==200

def test_invalid_update_preserves_data(client):
    item=client.post("/tarefas",json={"titulo":"Exemplo"}).json()
    assert client.put(f"/tarefas/{item['id']}",json={"titulo":" "}).status_code==422
    assert client.get(f"/tarefas/{item['id']}").json()==item

def test_pagination(client):
    assert client.get("/tarefas?limit=101").status_code==422
    assert client.get("/tarefas?offset=-1").status_code==422

def test_openapi(client):
    assert client.get("/docs").status_code==200
    assert "/tarefas/{task_id}" in client.get("/openapi.json").json()["paths"]
