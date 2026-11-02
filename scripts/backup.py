"""Backup consistente, inclusive com aplicação ativa. Não publica o banco."""
import argparse
import sqlite3
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("origem")
p.add_argument("destino")
a=p.parse_args()
source=Path(a.origem).resolve()
target=Path(a.destino).resolve()
if not source.is_file() or source==target or target.exists():
    p.error("Origem deve existir e destino deve ser novo e diferente")
target.parent.mkdir(parents=True,exist_ok=True)
with sqlite3.connect(source.as_uri()+"?mode=ro",uri=True) as src:
    with sqlite3.connect(target) as dst:
        src.backup(dst)
        assert dst.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
print("Backup concluído e integridade verificada")
