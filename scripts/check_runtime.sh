#!/bin/sh
set -eu
/opt/tarefas/.venv/bin/python - <<'PY'
import json,sys,sqlite3,platform,subprocess,importlib.metadata as meta,os
from pathlib import Path
from datetime import datetime,timezone
from contextlib import closing
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
folder=Path('/var/lib/tarefas/backups');folder.mkdir(mode=0o700,exist_ok=True)
backup=folder/f'backup-{stamp}.db';restored=folder/f'restaurado-{stamp}.db'
subprocess.run(['/opt/tarefas/.venv/bin/python','/opt/tarefas/scripts/backup.py','/var/lib/tarefas/tarefas.db',str(backup)],check=True,stdout=subprocess.PIPE)
with closing(sqlite3.connect(backup)) as src,closing(sqlite3.connect(restored)) as dst:
 src.backup(dst)
 original=src.execute('SELECT * FROM tarefas ORDER BY id').fetchall()
 restored_rows=dst.execute('SELECT * FROM tarefas ORDER BY id').fetchall()
 integrity=dst.execute('PRAGMA integrity_check').fetchone()[0]
 assert original==restored_rows and integrity=='ok'
for path in [backup,restored]:
 os.chmod(path,0o600)
 import pwd
 info=pwd.getpwnam('tarefas');os.chown(path,info.pw_uid,info.pw_gid)
os.chown(folder,info.pw_uid,info.pw_gid)
info={
 'data_utc':datetime.now(timezone.utc).isoformat(),
 'os':platform.freedesktop_os_release().get('PRETTY_NAME'),
 'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,
 'bibliotecas':{p:meta.version(p) for p in ['fastapi','uvicorn','pydantic','starlette']},
 'caddy':subprocess.check_output(['caddy','version'],text=True).strip(),
 'servicos':{s:subprocess.check_output(['systemctl','is-active',s],text=True).strip() for s in ['tarefas','caddy']},
 'banco':{'caminho':'/var/lib/tarefas/tarefas.db','permissao_octal':oct(Path('/var/lib/tarefas/tarefas.db').stat().st_mode & 0o777),'proprietario':pwd.getpwuid(Path('/var/lib/tarefas/tarefas.db').stat().st_uid).pw_name},
 'backup_restauracao':{'ambiente':'VM Azure','backup':str(backup),'restauracao_em_arquivo_separado':str(restored),'registros_comparados':len(original),'integridade':integrity,'dados_identicos':original==restored_rows,'limite':'Ambos no mesmo disco; n?o h? c?pia externa autom?tica'},
 'disco_montado':subprocess.check_output(['findmnt','-T','/var/lib/tarefas','-n','-o','SOURCE,FSTYPE,TARGET'],text=True).strip(),
 'portas_em_escuta':subprocess.check_output(['ss','-lnt'],text=True).strip(),
 'commit_codigo':subprocess.check_output(['git','-C','/opt/tarefas','rev-parse','HEAD'],text=True).strip()
}
print('TAREFAS_JSON_BEGIN')
print(json.dumps(info,ensure_ascii=True))
print('TAREFAS_JSON_END')
PY
