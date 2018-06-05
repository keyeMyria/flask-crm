
from werkzeug.contrib.fixers import ProxyFix
from crm import crm


def main():
    crm.app.wsgi_app = ProxyFix(crm.app.wsgi_app)
    crm.app.run(host="0.0.0.0", port=4990, debug=True)


if __name__ == '__main__':
    main()