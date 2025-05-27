import flask
import requests

app = flask.Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def update(path=''):
    r = requests.get('https://www.baseball-reference.com/')
    r.raise_for_status()
    print('No problem reading www.baseball-reference.com')
    return 'Done\n'
