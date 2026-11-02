import json, os, subprocess, sys, time, socket
from pathlib import Path
import httpx
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
os.chdir(root)
out=root/"docs/evidencias"; out.mkdir(exist_ok=True)
private=root/".private";private.mkdir(exist_ok=True)
env=os.environ.copy();env["DATABASE_PATH"]=str(private/"evidence.db")
log=open(private/"server.log","w")
sock=socket.socket();sock.bind(("127.0.0.1",0));port=sock.getsockname()[1];sock.close()
def start():
    p=subprocess.Popen([sys.executable,"-m","uvicorn","app.main:app","--host","127.0.0.1","--port",str(port)],env=env,stdout=log,stderr=log)
    for i in range(100):
        try:
            if httpx.get(f"http://127.0.0.1:{port}/health",trust_env=False).status_code==200:return p
        except httpx.HTTPError:pass
        time.sleep(.1)
    raise RuntimeError("Servidor n?o iniciou")
proc=start();results=[]
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page(viewport={"width":1000,"height":1000})
        base=f"http://127.0.0.1:{port}"
        page.goto(base+"/docs");page.wait_for_selector(".opblock");page.screenshot(path=str(out/"01-swagger-local.png"),full_page=True)
        def swagger(method,path,payload,name):
            page.goto(base+"/docs");page.wait_for_selector(".opblock")
            block=page.locator(".opblock-"+method).filter(has=page.locator('[data-path="'+path+'"]')).first
            block.locator(".opblock-summary").click()
            block.get_by_role("button",name="Try it out").click()
            if "{task_id}" in path:block.locator('input[placeholder="task_id"]').fill(str(ident))
            if payload is not None:block.locator("textarea").fill(json.dumps(payload,ensure_ascii=False))
            block.get_by_role("button",name="Execute",exact=True).click()
            block.locator(".responses-wrapper .response-col_status").last.wait_for()
            page.wait_for_timeout(900)
            page.add_style_tag(content=".live-responses-table pre {font-size:22px !important;white-space:pre-wrap !important;overflow-wrap:anywhere}")
            block.locator(".live-responses-table").screenshot(path=str(out/name))
        swagger("post","/tarefas",{"titulo":"Apresentacao ficticia","descricao":"Preparar slides de demonstracao"},"02-criacao-local.png")
        rows=httpx.get(base+"/tarefas").json();assert rows
        item=rows[-1];ident=item["id"]
        swagger("get","/tarefas/{task_id}",None,"03-consulta-local.png")
        swagger("put","/tarefas/{task_id}",{"titulo":"Apresentacao ficticia revisada","status":"concluida"},"04-atualizacao-local.png")
        before=httpx.get(base+f"/tarefas/{ident}").json();assert before["status"]=="concluida"
        proc.terminate();proc.wait(timeout=15);proc=start()
        after=httpx.get(base+f"/tarefas/{ident}").json();assert after==before
        results.append({"teste":"reinicio real do processo Uvicorn","antes":before,"depois":after,"resultado":"aprovado"})
        swagger("get","/tarefas/{task_id}",None,"05-apos-reinicio-local.png")
        swagger("delete","/tarefas/{task_id}",None,"06-exclusao-local.png")
        r=httpx.get(base+f"/tarefas/{ident}");assert r.status_code==404
        swagger("get","/tarefas/{task_id}",None,"07-consulta-excluida-local.png")
        results.append({"teste":"consulta apos exclusao","http":r.status_code,"resposta":r.json(),"resultado":"aprovado"})
        page.goto((out/"testes-locais.txt").as_uri());page.add_style_tag(content="pre {font-size:18px;white-space:pre-wrap;overflow-wrap:anywhere}");page.locator("pre").screenshot(path=str(out/"08-testes-locais.png"))
        page.goto("https://github.com/shamiryy/GS_Cloud");page.wait_for_timeout(1500);page.screenshot(path=str(out/"09-github-publicado.png"),full_page=False)
        browser.close()
finally:
    proc.terminate();proc.wait(timeout=15);log.close()
(out/"reinicio-processo-local.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
print("CRUD Swagger e reinicio real verificados; prints locais salvos")
