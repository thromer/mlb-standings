#!/usr/bin/env python

import os
import sys
import time

print('start.py [stderr]', file=sys.stderr)
print('start.py [stdout]', file=sys.stderr)
port = os.environ.get('PORT', '8080')
cmd = [
    'functions-framework',
    f'--port={port}', 
    '--target',
    'update'
]
print(f'running functions-framework args={cmd}', file=sys.stderr)
try:
    os.execvp('functions-framework', cmd)
except e:
    print(e, file=sys.stderr)
    time.sleep(60)
    raise

