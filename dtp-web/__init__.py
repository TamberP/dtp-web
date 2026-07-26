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
    @app.route('/')
    def index():
        # Links to truck search, trailer search, and PSV search
        return render_template('index.htm')


    ################################################################################
    ###                            Truck                                         ###
    ################################################################################
    @app.route('/truck', methods=['POST', 'GET'])
    def truck():
        # This 'window' should have the quick dtp number search box,
        # and a way to do an advanced search.
        dbh = db.get_db()
        error = None
        dtpmaybe = None

        if(request.method == 'POST'):
            if(request.form['dtp']):
                dtpmaybe = request.form['dtp']

        else:
            dtpmaybe = request.args.get('dtp')

        try:
            if(dtpmaybe is not None):
                # todo: validate the dtp
                results = dtp.dtp_fetch(dbh, dtpmaybe)
                aresults = []
                resultcount = len(results)
                if(resultcount == 0):
                    return render_template('truck.htm', error = "No results found")

                for i in results:
                    tmp = dict(i)

                    tmp["MakeStr"] = dtp.dtp_vehmake(dbh, tmp["MakeId"])
                    tmp["TypeStr"] = dtp.dtp_vehtype(dbh, tmp["TypeId"])
                    woem = dtp.dtp_brakeroutine(dbh, tmp["BrakeRoutine"])[0].split(",")
                    tmp["BrakeRoutineServ"] = woem[0]
                    tmp["BrakeRoutineSec"]  = woem[1]
                    tmp["BrakeRoutinePark"] = woem[2]
                    tmp["FoundServStr"] = dtp.dtp_braketype(dbh, tmp["FoundServBrake"])
                    tmp["FoundSecStr"] = dtp.dtp_braketype(dbh, tmp["FoundSecBrake"])
                    tmp["FoundParkStr"] = dtp.dtp_braketype(dbh, tmp["FoundParkBrake"])
                    tmp["AxleCount"] = int(tmp["TypeId"][0])
                    aresults.append(tmp)

                    return render_template('truck_result.htm', resultcount = resultcount, dtpmaybe=dtpmaybe, rtrucks=aresults)
            else:
                vehtype = dtp.dtp_fetch_vehtype(dbh)
                vehmake = dtp.dtp_fetch_vehmake(dbh)
                braketype = dtp.dtp_fetch_braketype(dbh)
                return render_template('truck.htm',
                                       vehtype = vehtype,
                                       vehmake = vehmake,
                                       braketype = braketype )
        except:
            return render_template('truck.htm', error = "Code exception! Beat the dev!"), 500


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
