#!/home/tamber/dev/dtp-web/.venv/bin/python
from flup.server.fcgi import WSGIServer
import dtpweb

theapp = dtpweb.create_app()
WSGIServer(theapp, bindAddress='/var/run/lighttpd/fastcgi-dtp.socket').run()
