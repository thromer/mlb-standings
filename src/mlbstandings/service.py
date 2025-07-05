import os
from .app import app

from gunicorn.app.base import BaseApplication

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

def run_server(application, port: str, workers: int):
    options = {
        'bind': f':{port}',
        'workers': workers,
        # 'worker_class': 'sync',
        'threads': 8,
        'timeout': 0,
        # 'keepalive': 2,
        # 'max_requests': 1000,
        # 'max_requests_jitter': 100,
        # 'logger_class': 'debug',  # ?
    }

    StandaloneApplication(app, options).run()

def serve() -> None:
    run_server(app, os.environ.get('PORT', '8080'), 1)
