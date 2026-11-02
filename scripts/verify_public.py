"""Verifica uma implantação real por HTTPS e registra evidências sem credenciais."""
import argparse,json,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
import httpx
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--restart-azure',action='store_true');args=p.parse_args()
base=args.base_url.rstrip('/');root=Path(__file__).resolve().parents[1];out=root/'docs/evidencias/nuvem';out.mkdir(parents=True,exist_ok=True)
records=[];log=[]
def note(s):
 line=datetime.now(timezone.utc).isoformat()+' '+s;print(line,flush=True);log.append(line)
def check(method,path,expected,payload=None):
 with httpx.Client(timeout=30) as c:r=c.request(method,base+path,json=payload) if payload is not None else c.request(method,base+path)
 body=r.json() if r.content else None
 records.append({'data_utc':datetime.now(timezone.utc).isoformat(),'metodo':method,'url':base+path,'corpo_enviado':payload,'http_esperado':expected,'http_recebido':r.status_code,'resposta':body})
 assert r.status_code==expected,(method,path,r.status_code,r.text[:200]);note(f'{method} {path} -> {expected} APROVADO');return body

def ready():
 for attempt in range(90):
  try:
   if httpx.get(base+'/health',timeout=10).status_code==200:return
  except httpx.HTTPError:pass
  if attempt%6==0:note('Aguardando retorno do HTTPS após reinicialização')
  time.sleep(5)
 raise RuntimeError('A API não retornou após reinicialização')
def azure(*cli):
 result=subprocess.run(['C:/Program Files/Microsoft SDKs/Azure/CLI2/wbin/az.cmd',*cli,'-o','json'],capture_output=True,text=True,encoding='utf-8',timeout=600)
 if result.returncode:raise RuntimeError(result.stderr[-1000:])
 return json.loads(result.stdout) if result.stdout.strip() else None
try:
 ready()
 check('GET','/health',200)
 item=check('POST','/tarefas',201,{'titulo':'Teste CRUD publico ficticio','descricao':'Evidencia automatizada','status':'pendente'});ident=item['id']
 assert any(x==item for x in check('GET','/tarefas',200))
 assert check('GET',f'/tarefas/{ident}',200)==item
 updated=check('PUT',f'/tarefas/{ident}',200,{'titulo':'Teste atualizado ficticio','descricao':'CRUD verificado','status':'concluida'})
 assert updated['data_criacao']==item['data_criacao'] and updated['status']=='concluida'
 for data in [{'titulo':''},{'titulo':'   '},{'titulo':'x','status':'invalido'},{'titulo':'x'*121},{'titulo':'x','campo_extra':True}]:check('POST','/tarefas',422,data)
 check('PUT',f'/tarefas/{ident}',422,{'titulo':' '});assert check('GET',f'/tarefas/{ident}',200)==updated
 check('GET','/tarefas/999999999',404)
 check('GET','/tarefas?limit=101',422)
 check('DELETE',f'/tarefas/{ident}',204)
 check('GET',f'/tarefas/{ident}',404)
 check('DELETE',f'/tarefas/{ident}',404)
 persistent=check('POST','/tarefas',201,{'titulo':'Persistencia na nuvem - dado ficticio','descricao':'Preservada apos reinicio do servico e da VM','status':'pendente'})
 pid=persistent['id'];states={'antes':persistent}
 with sync_playwright() as pw:
  browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1000,'height':1000})
  page.goto(base+'/docs');page.wait_for_selector('.opblock');page.screenshot(path=str(out/'01-swagger-hospedado.png'),full_page=True)
  def swagger(method,path,payload,name,task_id=None):
   page.goto(base+'/docs');page.wait_for_selector('.opblock')
   block=page.locator('.opblock-'+method).filter(has=page.locator('[data-path="'+path+'"]')).first
   block.locator('.opblock-summary').click();block.get_by_role('button',name='Try it out').click()
   if task_id is not None:block.locator('input[placeholder="task_id"]').fill(str(task_id))
   if payload is not None:block.locator('textarea').fill(json.dumps(payload))
   block.get_by_role('button',name='Execute',exact=True).click();block.locator('.live-responses-table').wait_for();page.wait_for_timeout(500)
   page.add_style_tag(content='.live-responses-table pre {font-size:22px !important;white-space:pre-wrap !important;overflow-wrap:anywhere}')
   block.locator('.live-responses-table').screenshot(path=str(out/name))
  title='Tarefa ficticia capturada '+str(int(time.time()))
  swagger('post','/tarefas',{'titulo':title},'02-criacao-publica.png')
  captured=next(x for x in check('GET','/tarefas',200) if x['titulo']==title);cid=captured['id']
  swagger('get','/tarefas/{task_id}',None,'03-consulta-publica.png',cid)
  swagger('put','/tarefas/{task_id}',{'titulo':title,'status':'concluida'},'04-atualizacao-publica.png',cid)
  assert check('GET',f'/tarefas/{cid}',200)['status']=='concluida'
  swagger('delete','/tarefas/{task_id}',None,'05-exclusao-publica.png',cid)
  check('GET',f'/tarefas/{cid}',404)
  swagger('get','/tarefas/{task_id}',None,'06-consulta-excluida-publica.png',cid)
  swagger('post','/tarefas',{'titulo':' '},'07-validacao-publica.png')
  swagger('get','/tarefas/{task_id}',None,'08-antes-reinicios.png',pid)
  if args.restart_azure:
   note('Reiniciando serviço tarefas via Azure Run Command')
   result=azure('vm','run-command','invoke','-g','rg-api-tarefas-academica','-n','vm-api-tarefas','--command-id','RunShellScript','--scripts','set -eu; systemctl restart tarefas; systemctl is-active tarefas')
   messages='\n'.join(x.get('message','') for x in result.get('value',[]))
   assert 'active' in messages and '[stderr]\n' in messages
   (out/'reinicio-servico-azure.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
   ready();after=check('GET',f'/tarefas/{pid}',200);assert after==persistent;states['apos_reinicio_servico']=after
   swagger('get','/tarefas/{task_id}',None,'09-apos-reinicio-servico.png',pid)
   note('Reiniciando VM pelo Azure CLI')
   azure('vm','restart','-g','rg-api-tarefas-academica','-n','vm-api-tarefas')
   ready();after=check('GET',f'/tarefas/{pid}',200);assert after==persistent;states['apos_reinicio_vm']=after
   swagger('get','/tarefas/{task_id}',None,'10-apos-reinicio-vm.png',pid)
   note('Persistência idêntica após reinício do serviço e da VM: APROVADO')
  browser.close()
 (out/'persistencia-publica.json').write_text(json.dumps(states,ensure_ascii=False,indent=2),encoding='utf-8')
 note(f'Verificação pública concluída: {len(records)} requisições registradas')
finally:
 (out/'testes-publicos.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'testes-publicos.txt').write_text('\n'.join(log),encoding='utf-8')
