"""Gera HTML/Markdown e diagramas a partir do conteúdo e evidências finais.
Word/PDF são produzidos com Microsoft Word pelo script export_report.ps1.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import html,json,re
root=Path(__file__).resolve().parents[1];docs=root/'docs';private=root/'.private';private.mkdir(exist_ok=True)
content=json.loads((docs/'conteudo-relatorio.json').read_text(encoding='utf-8'))
cloud=docs/'evidencias/nuvem';tests=json.loads((cloud/'testes-publicos.json').read_text(encoding='utf-8'));states=json.loads((cloud/'persistencia-publica.json').read_text(encoding='utf-8'))
assert len(tests)==23 and all(x['http_esperado']==x['http_recebido'] for x in tests)
assert states['antes']==states['apos_reinicio_servico']==states['apos_reinicio_vm']
di=docs/'diagramas';di.mkdir(exist_ok=True);font='C:/Windows/Fonts/arial.ttf'
def flow(name,boxes,title):
 im=Image.new('RGB',(1500,420),'white');draw=ImageDraw.Draw(im);n=len(boxes);w=(1400-(n-1)*50)//n;f=ImageFont.truetype(font,24 if n>3 else 28)
 draw.text((750,35),title,font=ImageFont.truetype(font,23),fill='black',anchor='mm')
 for i,lines in enumerate(boxes):
  x=50+i*(w+50);draw.rounded_rectangle((x,95,x+w,315),radius=12,outline='black',width=3)
  for j,line in enumerate(lines):draw.text((x+w/2,140+j*43),line,font=f,fill='black',anchor='mm')
  if i<n-1:draw.line((x+w+6,205,x+w+44,205),fill='black',width=3);draw.polygon([(x+w+44,205),(x+w+32,197),(x+w+32,213)],fill='black')
 im.save(di/name)
flow('01-arquitetura.png',[['Cliente','Swagger ou HTTP'],['VM Azure no México','Debian 12','Caddy e FastAPI'],['HDD persistente','32 GiB Standard_LRS','SQLite em /var/lib']], 'Arquitetura efetivamente implantada — HTTPS 443 e Uvicorn em loopback 8000')
flow('03-fluxo.png',[['Requisição','JSON HTTP'],['Validação','Pydantic'],['Processamento','SQL parametrizado'],['SQLite','commit ou rollback'],['Resposta','JSON e HTTP']], 'Fluxo implementado — entrada inválida 422, registro ausente 404, erro SQLite 503')
im=Image.new('RGB',(1500,620),'white');draw=ImageDraw.Draw(im);f=ImageFont.truetype(font,29);draw.rectangle((100,30,1400,585),outline='black',width=3);draw.text((750,65),'TAREFAS',font=f,fill='black',anchor='mm')
for i,(a,b,c) in enumerate([('id','INTEGER','PK AUTOINCREMENT'),('titulo','TEXT NOT NULL','1 a 120 caracteres'),('descricao','TEXT NOT NULL','0 a 2000 caracteres'),('status','TEXT NOT NULL','pendente | em_andamento | concluida'),('data_criacao','TEXT NOT NULL','ISO 8601 em UTC')]):
 y=110+i*90;draw.line((100,y,1400,y),fill='black',width=2);draw.text((130,y+28),a,font=f,fill='black');draw.text((480,y+28),b,font=f,fill='black');draw.text((820,y+28),c,font=f,fill='black')
im.save(di/'02-modelo.png')
evidence=[
('01-swagger-hospedado.png','Nuvem: documentação interativa real da API hospedada em HTTPS.'),
('02-criacao-publica.png','Nuvem: criação com HTTP 201 e Location.'),
('03-consulta-publica.png','Nuvem: consulta da tarefa criada com HTTP 200.'),
('04-atualizacao-publica.png','Nuvem: atualização para concluida com HTTP 200.'),
('05-exclusao-publica.png','Nuvem: exclusão com HTTP 204 sem corpo.'),
('06-consulta-excluida-publica.png','Nuvem: consulta após exclusão com HTTP 404.'),
('07-validacao-publica.png','Nuvem: título inválido rejeitado com HTTP 422.'),
('08-antes-reinicios.png','Nuvem: tarefa de persistência antes dos reinícios.'),
('09-apos-reinicio-servico.png','Nuvem: mesmo registro após reiniciar o serviço tarefas.'),
('10-apos-reinicio-vm.png','Nuvem: mesmo registro após reiniciar a VM Azure.'),
('11-recursos-sku-cli.png','Inventário real consultado na Azure CLI, com IDs omitidos. Captura do resultado consolidado; não é tela do portal.'),
('12-runtime-backup-cli.png','Resultado real na VM: versões, serviços, banco e backup/restauração em arquivo separado.'),
('13-testes-publicos-log.png','Log real das verificações públicas e reinícios com assertions.')]
figures=[];figure_number=0
body=['<h1>'+html.escape(content['title'])+'</h1>','<p style="text-align:center">Relatório acadêmico da implementação e hospedagem</p>'];md=['# '+content['title']]
def inline(s):
 s=html.escape(s);s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s);s=re.sub(r'`([^`]+)`',r'<span>\1</span>',s);return s

def render(text):
 result=[];code=False;table=False;first=False
 for line in text.splitlines():
  if line.startswith('```'):
   result.append('</pre>' if code else '<pre>');code=not code;continue
  if code:result.append(html.escape(line)+'\n');continue
  if line.startswith('|'):
   cells=line.strip('|').split('|')
   if all(set(c.strip())<=set('-: ') for c in cells):continue
   if not table:result.append('<table>');table=True;first=True
   tag='th' if first else 'td';first=False;result.append('<tr>'+''.join('<'+tag+'>'+inline(c)+'</'+tag+'>' for c in cells)+'</tr>');continue
  if table:result.append('</table>');table=False
  if line.startswith('### '):result.append('<h3>'+inline(line[4:])+'</h3>')
  elif line.strip():result.append('<p>'+inline(line)+'</p>')
 if table:result.append('</table>')
 return ''.join(result)
def figure(path,caption):
 global figure_number
 figure_number+=1;figures.append(str(path));caption=f'Figura {figure_number}. '+caption
 md.append('![Figura '+str(figure_number)+']('+str(path.relative_to(docs)).replace('\\','/')+')\n\n'+caption)
 return '<p class="picture"><img width="630" src="'+str(path)+'"></p><p class="caption">'+html.escape(caption)+'</p>'
for section in content['sections']:
 title=section['title'];text=section['text'];style=' style="page-break-before:always"' if title.startswith('15 ') else ''
 body.append('<h2'+style+'>'+html.escape(title)+'</h2>'+render(text));md.append('## '+title+'\n\n'+text)
 if title.startswith('4 '):body.append(figure(di/'02-modelo.png','Modelo de dados da tabela tarefas implementada.'))
 if title.startswith('5 '):body.append(figure(di/'03-fluxo.png','Fluxo de requisição e respostas implementadas.'))
 if title.startswith('9 '):body.append(figure(di/'01-arquitetura.png','Arquitetura efetivamente implantada em Mexico Central.'))
 if title.startswith('14 '):
  for i,(name,caption) in enumerate(evidence,1):body.append('<h3 style="page-break-before:always">Evidência '+str(i)+'</h3>'+figure(cloud/name,caption))
  body.append('<h3 style="page-break-before:always">Evidência local</h3>'+figure(docs/'evidencias/08-testes-locais.png','Execução local: 17 testes aprovados; caminhos pessoais omitidos.'))
  body.append('<h3 style="page-break-before:always">Repositório publicado</h3>'+figure(docs/'evidencias/09-github-publicado.png','Repositório público no GitHub, capturado em navegador após publicar a implantação.'))
styles='@page{size:A4;margin:2cm;}body{font-family:Arial;font-size:11pt;color:black;}h1{text-align:center;font-size:18pt;}h2{font-size:14pt;page-break-after:avoid;}h3{font-size:12pt;page-break-after:avoid;}p{line-height:1.15;margin:8pt 0;}table{border-collapse:collapse;width:100%;font-size:10pt;}td,th{border:1px solid #D9D9D9;padding:5pt;}th{background:#E7E6E6;text-align:left;}tr{page-break-inside:avoid;}pre{font-family:Arial;font-size:9pt;white-space:pre-wrap;}.caption{font-size:10pt;}.picture{text-align:center;}'
(private/'relatorio-final.html').write_text('<html><head><meta charset="utf-8"><style>'+styles+'</style></head><body>'+''.join(body)+'</body></html>',encoding='utf-8')
(private/'image-manifest.json').write_text(json.dumps(figures),encoding='utf-8')
(docs/'relatorio.md').write_text('\n\n'.join(md)+'\n',encoding='utf-8')
print('Relatório final preparado:',len(content['sections']),'seções e',len(figures),'imagens; 23 requisições públicas aprovadas')
