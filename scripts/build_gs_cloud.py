"""Gera a documentação acadêmica resumida GS_Cloud.pdf com evidências reais."""
from pathlib import Path
import argparse,html,json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import pymupdf
root=Path(__file__).resolve().parents[1];docs=root/'docs';ev=docs/'evidencias/entrega';private=root/'.private';private.mkdir(exist_ok=True)
args=argparse.ArgumentParser();args.add_argument('--nome',default='Shamiry França Luiz');a=args.parse_args();nome=a.nome;rm='RM567440';total_pages=16
fontroot=Path('C:/Windows/Fonts');pdfmetrics.registerFont(TTFont('Arial',str(fontroot/'arial.ttf')));pdfmetrics.registerFont(TTFont('Arial-Bold',str(fontroot/'arialbd.ttf')))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
repo='https://github.com/shamiryy/GS_Cloud';base='https://tarefas-academica-shamiryy-20261102.mexicocentral.cloudapp.azure.com'
styles={
 'body':ParagraphStyle('body',fontName='Arial',fontSize=10.5,leading=14,textColor=colors.black,spaceAfter=6),
 'small':ParagraphStyle('small',fontName='Arial',fontSize=9,leading=12,textColor=colors.black),
 'caption':ParagraphStyle('caption',fontName='Arial',fontSize=9,leading=12,textColor=colors.black),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9,leading=11.5,textColor=colors.black)
}
main=private/'gs-cloud-main.pdf';c=canvas.Canvas(str(main),pagesize=A4);W,H=A4;M=44;y=H-M;page=1;used=[]
def paragraph(text,kind='body',after=6,width=None):
 global y
 width=width or W-2*M;p=Paragraph(text,styles[kind]);_,height=p.wrap(width,H)
 if y-height<48:raise RuntimeError(f'Conteudo ultrapassou pagina {page}: {text[:60]}')
 p.drawOn(c,M,y-height);y-=height+after

def heading(text):
 global y
 c.setFont('Arial-Bold',13);c.drawString(M,y-13,text);y-=25

def table(rows,widths):
 global y
 data=[[Paragraph(html.escape(str(v)),styles['cell']) for v in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#CCCCCC')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEEEEE')),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));_,h=t.wrap(W-2*M,H)
 if y-h<48:raise RuntimeError(f'Tabela nao cabe na pagina {page}')
 t.drawOn(c,M,y-h);y-=h+9

def image(path,width=None,maxheight=None):
 global y
 path=Path(path);reader=ImageReader(str(path));iw,ih=reader.getSize();width=width or W-2*M;h=width*ih/iw
 if maxheight and h>maxheight:width*=maxheight/h;h=maxheight
 if y-h<48:raise RuntimeError(f'Imagem nao cabe: {path.name} pagina {page}')
 c.drawImage(reader,M+(W-2*M-width)/2,y-h,width=width,height=h,mask='auto');y-=h+6;used.append(path.name)

def footer():
 c.setFont('Arial',8);c.drawString(M,25,f'{rm} - {nome}');c.drawRightString(W-M,25,f'{page} / {total_pages}')

def nextpage(wide=False):
 global W,H,y,page
 footer();c.showPage();page+=1;W,H=landscape(A4) if wide else A4;c.setPageSize((W,H));y=H-M

def diagram(boxes,height=65):
 global y
 n=len(boxes);gap=16;bw=(W-2*M-gap*(n-1))/n;bottom=y-height
 for i,lines in enumerate(boxes):
  x=M+i*(bw+gap);c.setStrokeColor(colors.black);c.roundRect(x,bottom,bw,height,5,stroke=1,fill=0)
  for j,line in enumerate(lines):c.setFont('Arial-Bold' if j==0 else 'Arial',9 if n<5 else 8);c.drawCentredString(x+bw/2,bottom+height-18-j*15,line)
  if i<n-1:
   yy=bottom+height/2;c.line(x+bw+3,yy,x+bw+gap-3,yy);c.line(x+bw+gap-7,yy+3,x+bw+gap-3,yy);c.line(x+bw+gap-7,yy-3,x+bw+gap-3,yy)
 y=bottom-8

# Página 1: identificação, objetivo, acesso, arquitetura e modelo.
c.setFont('Arial-Bold',18);c.drawCentredString(W/2,y-18,'GS Cloud - API de tarefas');y-=37
c.setFont('Arial',11);c.drawCentredString(W/2,y,f'{rm} - {nome}');y-=26
heading('1. Objetivo e acesso')
paragraph('Desenvolvi uma API básica com banco de dados e a hospedei na nuvem. Minha solução gerencia tarefas fictícias: permite criar, listar, consultar, atualizar e excluir registros. Publiquei o código no GitHub e disponibilizei a API por HTTPS.')
paragraph(f'<b>GitHub:</b> <link href="{repo}" color="black">{repo}</link>','small',5)
paragraph(f'<b>API:</b> <link href="{base}/tarefas" color="black">{base}/tarefas</link>','small',5)
paragraph(f'<b>Swagger:</b> <link href="{base}/docs" color="black">{base}/docs</link>','small',12)
heading('2. Arquitetura da solução')
diagram([['Cliente','Navegador / Swagger'],['VM Azure - Debian 12','Caddy + FastAPI'],['Disco persistente','SQLite (.db)']],65)
paragraph('Figura 1. O cliente acessa HTTPS; Caddy encaminha a requisição para FastAPI/Uvicorn, que lê ou grava o SQLite no disco da VM.','caption',10)
heading('3. Modelo de dados')
paragraph('Criei uma tabela chamada <b>tarefas</b> para armazenar os cinco campos abaixo. Configurei o servidor para gerar o ID e a data de criação.','body',6)
table([['Campo','Tipo e regra'],['id','INTEGER, chave primária e autoincremento'],['titulo','TEXT obrigatório, de 1 a 120 caracteres'],['descricao','TEXT, até 2000 caracteres; padrão vazio'],['status','pendente, em_andamento ou concluida'],['data_criacao','Data/hora UTC em formato ISO 8601']], [110,W-2*M-110])
paragraph('Figura 2. Esquema da tabela SQLite. O banco não precisa de um servidor separado: os registros são mantidos em um arquivo.','caption')
# Página 2: linguagem, rotas, fluxo e print real.
nextpage();heading('4. Linguagem e funcionamento da API')
paragraph('Usei <b>Python 3.11.2</b> na VM e <b>FastAPI 0.162.0</b> para definir os endpoints e gerar o Swagger. Utilizei Pydantic para validar os dados, <b>Uvicorn 0.54.0</b> para executar a API e sqlite3 para acessar o <b>SQLite 3.40.1</b> com consultas parametrizadas.')
table([['Método','Endpoint','Resultado'],['POST','/tarefas','Cria; HTTP 201'],['GET','/tarefas','Lista; HTTP 200'],['GET','/tarefas/{task_id}','Consulta; HTTP 200 ou 404'],['PUT','/tarefas/{task_id}','Atualiza; HTTP 200 ou 404'],['DELETE','/tarefas/{task_id}','Exclui; HTTP 204 ou 404'],['GET','/health','Verifica aplicação/banco; HTTP 200']], [60,180,W-2*M-240])
paragraph('Exemplo de JSON para criação: <b>{&quot;titulo&quot;:&quot;Estudar SQLite&quot;,&quot;status&quot;:&quot;pendente&quot;}</b>. Entradas inválidas recebem 422; registro inexistente recebe 404. PUT substitui os campos editáveis, preservando ID e data. A listagem aceita limit (1 a 100) e offset não negativo.','small',9)
diagram([['Requisição','JSON / HTTP'],['Validação','Pydantic'],['Processamento','Rota FastAPI'],['Banco','SQLite'],['Resposta','JSON + HTTP']],51)
paragraph('Figura 3. Fluxo de uma requisição, da validação até a resposta.','caption',9)
image(ev/'07-consulta-web.png',maxheight=175)
paragraph('Figura 4. Captura que realizei no navegador: GET /tarefas retorna JSON pela URL pública. Minha exportação completa do Swagger está no Anexo B.','caption')
# Página 3: elementos de nuvem e resumo da validação.
nextpage();heading('5. Elementos de nuvem utilizados')
paragraph('Hospedei minha aplicação na <b>Microsoft Azure, região Mexico Central</b>. Organizei os recursos no grupo <b>rg-api-tarefas-academica</b> e administro a VM diretamente, sem plataforma gerenciada de aplicação ou banco gerenciado.')
table([['Elemento','Configuração e finalidade'],['Máquina virtual (VM)','vm-api-tarefas; Debian GNU/Linux 12. Executa a API, o servidor Uvicorn e o proxy Caddy.'],['SKU da VM','Standard_B2ats_v2: 2 vCPUs e 1 GiB de RAM. SKU é o identificador do tamanho/plano de um recurso.'],['Armazenamento','disk-api-tarefas: disco gerenciado HDD Standard_LRS de 32 GiB. O SQLite fica em /var/lib/tarefas/tarefas.db.'],['Persistência','O disco conserva os dados ao reiniciar o serviço ou a VM. Não é armazenamento temporário; persistência não substitui backup.'],['IP e HTTPS','ip-api-tarefas: IP Standard estático com DNS público. Caddy fornece HTTPS com certificado Let’s Encrypt.'],['Rede e segurança','VNet/sub-rede conectam a VM; nsg-api-tarefas permite publicamente TCP 80 e 443. Uvicorn escuta somente em 127.0.0.1:8000.']], [115,W-2*M-115])
paragraph('Mantive <b>uma VM e um worker</b> para simplificar o uso do SQLite. Configurei systemd para manter o processo ativo e reiniciá-lo em falhas. Escolhi HDD pelo custo da demonstração; para produção com carga maior, SSD e outro banco podem ser mais adequados.','small',8)
paragraph('<b>Custo de referência:</b> base estimada de US$ 12,86/mês para 730 horas (VM, disco e IP), mais operações e eventual tráfego, antes de benefícios. Consultei os valores em 02/11/2026; não representam uma fatura. Manterei os recursos alocados para a apresentação e os excluirei após a entrega.','small',10)
heading('6. Verificação e limitações')
paragraph('Executei <b>17 testes locais</b> e registrei <b>23 requisições públicas</b>, todos aprovados, incluindo CRUD, entradas inválidas e registros inexistentes. Reiniciei o serviço e depois a VM, confirmando que o registro permaneceu idêntico. Também verifiquei backup/restauração em arquivo separado e publiquei os logs no repositório.','small',7)
paragraph('Mantive a demonstração sem autenticação e usei somente dados fictícios; qualquer visitante pode alterar/excluir tarefas. Utilizei uma única instância, sem alta disponibilidade. As cópias que mantive no mesmo disco não protegem contra sua exclusão.','small',10)
heading('7. Referências e evidências')
paragraph('FastAPI: <link href="https://fastapi.tiangolo.com/" color="black">fastapi.tiangolo.com</link> · SQLite: <link href="https://www.sqlite.org/docs.html" color="black">sqlite.org/docs.html</link> · Azure VM/SKU: <link href="https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/basv2-series" color="black">Microsoft Learn - Basv2</link> · Preços: <link href="https://prices.azure.com/api/retail/prices" color="black">Azure Retail Prices API</link>.','small',6)
paragraph('Nos anexos, apresento meus prints completos da Azure e minha exportação do Swagger, sem recortes ou censura. A exportação mostra exemplos do contrato; os logs do projeto comprovam os testes que executei.','small')
# Anexo A: um print completo por pagina em paisagem.
portal=[
 ('01-grupo.png','Recursos Azure','Figura 5. Meu grupo rg-api-tarefas-academica e seus recursos em Mexico Central.'),
 ('02-vm.png','Máquina virtual','Figura 6. Minha VM em execução, com Debian 12 e tamanho Standard_B2ats_v2.'),
 ('03-sku.png','SKU e capacidade da VM','Figura 7. Tamanho que utilizei: B2ats_v2, 2 vCPUs e 1 GiB de memória.'),
 ('04-disco.png','Armazenamento persistente','Figura 8. Disco de SO que utilizei: HDD Standard LRS de 32 GiB, associado à VM.'),
 ('05-ip-dns.png','IP público e DNS','Figura 9. Meu IP público Standard, com DNS e alocação Static.'),
 ('06-nsg.png','Regras de entrada','Figura 10. Regras que configurei para HTTP 80 e HTTPS 443, junto às regras padrão.')]
for filename,title,caption in portal:
 nextpage(True);heading('Anexo A - '+title)
 image(ev/filename,width=W-2*M,maxheight=H-2*M-78)
 paragraph(caption,'caption',8)
 paragraph('Mantive a captura original inteira, sem recortes ou censura.','caption')
footer();c.save();assert page==9
# Preserve all seven original Swagger pages, with a short appendix label and global page numbers.
final=pymupdf.open(main);swagger=pymupdf.open(ev/'swagger-ui.pdf');assert len(swagger)==7
for i in range(len(swagger)):
 p=final.new_page(width=A4[0],height=A4[1]);p.insert_font(fontname='GSArial',fontfile=str(fontroot/'arial.ttf'))
 p.insert_text((44,30),f'Anexo B - Minha exportação do Swagger ({i+1} de 7)',fontname='GSArial',fontsize=9,color=(0,0,0))
 p.show_pdf_page(pymupdf.Rect(26,50,A4[0]-26,A4[1]-40),swagger,i,keep_proportion=True)
 p.insert_text((44,A4[1]-18),f'{rm} - {nome}',fontname='GSArial',fontsize=8,color=(0,0,0))
 p.insert_text((A4[0]-70,A4[1]-18),f'{i+10} / {total_pages}',fontname='GSArial',fontsize=8,color=(0,0,0))
final.set_metadata({'title':'GS_Cloud - API de tarefas','author':f'{rm} - {nome}','subject':'Documentacao academica de API Python FastAPI SQLite na Azure','creator':'GS_Cloud'})
output=docs/'GS_Cloud.pdf';final.save(output,garbage=4,deflate=True);final.close();swagger.close()
qa=root/'qa/gs_cloud';qa.mkdir(parents=True,exist_ok=True)
d=pymupdf.open(output);assert len(d)==total_pages
for i,p in enumerate(d):p.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(str(qa/f'page-{i+1}.png'))
print('PDF gerado:',output,'| páginas:',len(d),'| identificação:',nome,rm)
