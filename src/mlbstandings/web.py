import requests


class Web:
    @staticmethod
    def read(self, url: str) -> str:
        print(f'Web.read({url}')
        r = requests.get(url)
        r.raise_for_status()
        # TODO change everyone to bytes probably
        return r.content
