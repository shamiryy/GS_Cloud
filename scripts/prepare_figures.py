from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
root=Path.cwd();im=Image.new('RGB',(1500,620),'white');d=ImageDraw.Draw(im);f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
d.rectangle((100,30,1400,585),outline='black',width=3);d.text((750,65),'TAREFAS',font=f,anchor='mm',fill='black')
rows=[('id','INTEGER','PK AUTOINCREMENT'),('titulo','TEXT NOT NULL','1 a 120 caracteres'),('descricao','TEXT NOT NULL','0 a 2000 caracteres'),('status','TEXT NOT NULL','pendente | em_andamento | concluida'),('data_criacao','TEXT NOT NULL','ISO 8601 em UTC')]
for i,(a,b,c) in enumerate(rows):
 y=110+i*90;d.line((100,y,1400,y),fill='black',width=2);d.text((130,y+28),a,font=f,fill='black');d.text((480,y+28),b,font=f,fill='black');d.text((820,y+28),c,font=f,fill='black')
im.save(root/'docs/diagramas/02-modelo.png')
imgs=list(sorted((root/'docs/diagramas').glob('*.png')))+list(sorted((root/'docs/evidencias').glob('0*.png')))
(root/'.private/image-sizes.json').write_text(json.dumps([{'width':Image.open(p).width,'height':Image.open(p).height} for p in imgs]))
