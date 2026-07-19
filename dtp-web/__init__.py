from . import _sql_utils
from . import db
from . import dtp
import os
from flask import Flask
from flask import request
from flask import render_template

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'DTP-base.sqlite'),
    )

################################################################################
###                            Default                                       ###
################################################################################

    @app.route('/', methods=['POST', 'GET'])
    def index():
        # This 'window' should have the quick dtp number search box, and a way to get to:
        # - advanced search
        # - trailer search
        # - advanced trailer search
        dbh = db.get_db()
        error = None
        dtpmaybe = None

        if(request.method == 'POST'):
            if(request.form['dtp']):
                dtpmaybe = request.form['dtp']

        else:
            dtpmaybe = request.args.get('dtp')

        if(dtpmaybe is not None):
            # todo: validate the dtp
            results = dtp.dtp_fetch(dbh, dtpmaybe)
            resultcount = len(results)
            if(resultcount == 0):
                return "No results found."

            return render_template('truck_result.htm', resultcount = resultcount, dtpmaybe=dtpmaybe, rtrucks=results)

            # blob = "<h1>Truck</h1><b>{0}</b> Result{1}:<br>".format(resultcount, 's' if (resultcount > 1) else '')
            # for result in results:
            #     blob += "<b>DTP Number:</b> {0} - <b>Make:</b> {1}<br>".format(result["DTpNumber"],
            #                                                                    dtp.dtp_vehmake(dbh, result["MakeId"]))
            #     blob += "<b>GVW:</b>{0}<br><b>GTW:</b>{1}".format(result["GVW_DesignWeight"], result["GTW_DesignWeight"])

            # return blob
        else:
            return "<form action='/' method='post'><input type='text' id='dtp' name='dtp'><br><input type='submit' value='Submit'></form>"


################################################################################
###                            Trailers                                      ###
################################################################################
    @app.route('/trailer', methods=['POST', 'GET'])
    def trailer():
        # - quick DTP search box
        # - Build-A-Bear^WDTP advanced trailer search
        dbh = db.get_db()
        error = None
        dtpmaybe = None

        if(request.method == 'POST'):
            if(request.form['dtp']):
                dtpmaybe = request.form['dtp']

        else:
            dtpmaybe = request.args.get('dtp')

        if(dtpmaybe is not None):
            trailer = dtp.dtp_t_parse(dtpmaybe)
            if(trailer is None):
                return "No results found"

            trailer["TypeStr"] = dtp.dtp_vehtype(dbh, trailer["Type"])
            return render_template('trailer_result.htm', dtpmaybe=dtpmaybe, rtrailer=trailer)
        else:
            return "<form action='/trailer' method='post'><input type='text' id='dtp' name='dtp'><br><input type='submit' value='Submit'></form>"

    ## Do the thing!
    db.init_app(app)
    return app
