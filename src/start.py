#!/usr/bin/env python

import os
import sys
import time

print('start.py [stderr]', file=sys.stderr)
print('start.py [stdout]', file=sys.stderr)
port = os.environ.get('PORT', '8080')
cmd = [
    'gunicorn',
    f'--bind=:{port}', 
    '--workers=1', 
    '--threads=8', 
    '--timeout=0',
    '--log-level=debug',
    'main:update'
]
print(f'running gunicorn args={cmd}', file=sys.stderr)
os.execvp('gunicorn', cmd)

