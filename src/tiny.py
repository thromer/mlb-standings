import flask
import urllib3

app = flask.Flask(__name__)

from urllib3.connection import HTTPSConnection
from urllib3.poolmanager import PoolManager

class CipherInspectingHTTPSConnection(HTTPSConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher_info = None
    
    def connect(self):
        super().connect()
        if hasattr(self.sock, 'cipher') and callable(self.sock.cipher):
            self.cipher_info = self.sock.cipher()
            print(f"Cipher used: {self.cipher_info}")

            
# Create a custom pool manager
class CipherInspectingPoolManager(PoolManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace the HTTPS connection class
        self.pool_classes_by_scheme['https'].ConnectionCls = CipherInspectingHTTPSConnection


@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def update(path=''):
    http = CipherInspectingPoolManager()
    response = http.request('GET', 'https://www.baseball-reference.com/')
    print(f'{response.status=}')
    print(f'{"No p" if response.status < 400 else "P"}roblem reading www.baseball-reference.com')
    return f'Done {response.status=}\n', 200 if response.status < 400 else 500
