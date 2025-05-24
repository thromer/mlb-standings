#!/usr/bin/env python3

import requests
import subprocess
import ssl
import urllib.parse

from requests.adapters import HTTPAdapter

class HTTP11Adapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        # Force HTTP/1.1 by disabling ALPN negotiation for HTTP/2
        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(['http/1.1'])
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)


# gcloud --project=mlb-standings-001 functions deploy small --gen2 --runtime=python312 --region=us-west1 --trigger-http --no-allow-unauthenticated --timeout=1800 --service-account=mlb-standings-001-update@mlb-standings-001.iam.gserviceaccount.com && echo Deployed && curl -X POST -H "Content-Type: application/json" -H "Authorization: bearer $(gcloud --project=mlb-standings-001 auth print-identity-token)" https://us-west1-mlb-standings-001.cloudfunctions.net/small -d '{}'

def small(_request) -> str:
    url = 'https://www.baseball-reference.com'
    # result = subprocess.run(['curl', '-v', '-H', 'User-Agent: requests/2.31.0', url], capture_output=True, text=True)
    # print("CURL output:", result.stderr)

    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'requests/2.31.0')
    req.add_header('Accept', '*/*')
    try:
        response = urllib.request.urlopen(req)
        print(f"urllib.request status: {response.getcode()}")
        print("urllib.request works!")
    except Exception as e:
        print(f"urllib.request failed: {e}")
    
    
    session = requests.Session()
    session.mount('https://', HTTP11Adapter())
    session.mount('http://', HTTP11Adapter())
    resp=session.get(url, headers={
        'User-Agent': 'curl/7.88.1',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'        
    })
    resp.raise_for_status()
    print(f'partial resp={resp.content.decode(resp.encoding)[:10]}')
    return 'Done\n'

def main():
    small(None)

if __name__ == '__main__':
    main()
