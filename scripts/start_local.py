"""Start the local capstone stack; stop all children on Ctrl+C."""
from pathlib import Path
import os,signal,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
PYTHON=sys.executable
children=[]
def run(args,cwd):
    subprocess.run(args,cwd=cwd,check=True)
def start(args,cwd):
    children.append(subprocess.Popen(args,cwd=cwd))
try:
    run([PYTHON,'manage.py','migrate','--noinput'],ROOT/'server')
    run([PYTHON,'manage.py','seed_cars'],ROOT/'server')
    run([PYTHON,'manage.py','collectstatic','--noinput'],ROOT/'server')
    start(['npm','run','local'],ROOT/'server/database')
    start([PYTHON,'-m','gunicorn','app:app','--bind','127.0.0.1:5050'],ROOT/'server/djangoapp/microservices')
    start([PYTHON,'manage.py','runserver','127.0.0.1:8000','--noreload'],ROOT/'server')
    print('Open http://127.0.0.1:8000. Press Ctrl+C to stop.',flush=True)
    while all(child.poll() is None for child in children):time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    for child in children:
        if child.poll() is None:child.terminate()
    for child in children:
        try:child.wait(timeout=10)
        except subprocess.TimeoutExpired:child.kill()
