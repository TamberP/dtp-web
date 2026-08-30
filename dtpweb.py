#!/home/tamber/dev/dtp-web/.venv/bin/python # <-- Change this to wherever your venv python is.
import dtpweb
from wsgiref.simple_server import make_server

if __name__ == '__main__':
    theapp = dtpweb.create_app()
    with make_server('127.0.0.1', 8000, theapp) as dtpd:
        dtpd.serve_forever()

# Is this stupid? Yeah. Does it have potential godawful problems? Yeah.
# Does it work? Also yeah.
#
# If your setup works better with WSGI, then use that.
