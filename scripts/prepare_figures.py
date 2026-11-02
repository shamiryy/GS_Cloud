"""Obtém as dimensões na ordem exata das imagens no relatório."""
from pathlib import Path
from PIL import Image
import json
root=Path(__file__).resolve().parents[1]
paths=json.loads((root/'.private/image-manifest.json').read_text(encoding='utf-8'))
(root/'.private/image-sizes.json').write_text(json.dumps([{'width':Image.open(p).width,'height':Image.open(p).height} for p in paths]),encoding='utf-8')
print('Dimensões verificadas:',len(paths))
