from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)


app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)

