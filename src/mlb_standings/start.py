#!/usr/bin/env python

import os
import sys
import time

port = os.environ.get('PORT', '8080')
cmd = [
    'gunicorn',
    f'--bind=:{port}',
    '--workers=1',
    '--threads=8',
    '--timeout=0',
#    '--log-level=debug',
    'main:app'
]
os.execvp('gunicorn', cmd)

