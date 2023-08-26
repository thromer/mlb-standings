import requests


class Web:
    @staticmethod
    def read(url: str) -> str:
        print(f'Web.read({url}')
        r = requests.get(url)
        r.raise_for_status()
        if r.encoding is None:
            raise ValueError(f'Missing encoding in esponse to GET {url}')
        return r.content.decode(r.encoding)
