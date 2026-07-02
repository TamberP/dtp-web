from . import _sql_utils
from . import db
from . import dtp
import os
from flask import Flask
from flask import request

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'DTP-base.sqlite'),
    )


    @app.route('/', methods=['POST', 'GET'])
    def index():
        # This 'window' should have the quick dtp number search box, and a way to get to:
        # - advanced search
        # - trailer search
        # - advanced trailer search
        dbh = db.get_db()

        error = None
        if(request.method == 'POST'):
            if(request.form['dtp']):
                # todo: validate the dtp
                results = dtp.dtp_fetch(dbh, request.form['dtp'])
                resultcount = len(results)
                if(resultcount == 0):
                    return "No results found."

                blob = "<h1>Truck</h1><b>{0}</b> Result{1}:<br>".format(resultcount, 's' if (resultcount > 1) else '')
                for result in results:
                    blob += "<b>DTP Number:</b> {0} - <b>Make:</b> {1}<br>".format(result["DTpNumber"], result["MakeId"])
                    blob += "<b>GVW:</b>{0}<br><b>GTW:</b>{1}".format(result["GVW_DesignWeight"], result["GTW_DesignWeight"])

                return blob
        else:
            dtpmaybe = request.args.get('dtp')
            if(dtpmaybe is not None):
                return "So this is crazy, but dtpmaybe: {0}".format(dtpmaybe)
            else:
                return "<form action='/' method='post'><input type='text' id='dtp' name='dtp'><br><input type='submit' value='Submit'></form>"

    @app.route('/trailer', methods=['POST', 'GET'])
    def trailer():
        # - quick DTP search box
        # - Build-A-Bear^WDTP advanced trailer search
        dbh = db.get_db()
        error = None

        if(request.method == 'POST'):
            if(request.form['dtp']):
                dtpmaybe = request.form['dtp']
                trailer = dtp.dtp_t_parse(dtpmaybe)
                if(trailer is None):
                    return "No results found"
                blob = "<h1>{0}</h1><b>DTP</b>: {1}<br>".format(dtp.dtp_vehtype(dbh, trailer["Type"])[0], dtpmaybe)
                for x in range(1, (trailer["AxleCount"]+1)):
                    blob += "<b>Axle {0}</b>: {1}kg<br>".format(x, trailer["Axle{0}Weight".format(x)])
                blob += "<b>Total Axle Weight:</b> {0}kg<br>".format(trailer["TAW"])
                blob += "<b>Kingpin Weight:</b> {0}kg<br>".format(trailer["GVW"] - trailer["TAW"])
                blob += "<b>GVW:</b> {0} kg".format(trailer["GVW"])

                return blob
        else:
            dtpmaybe = request.args.get('dtp')
            if(dtpmaybe is not None):
                return "So this is crazy, but dtpmaybe: {0}".format(dtpmaybe)
            else:
                return "<form action='/trailer' method='post'><input type='text' id='dtp' name='dtp'><br><input type='submit' value='Submit'></form>"

    db.init_app(app)
    return app
