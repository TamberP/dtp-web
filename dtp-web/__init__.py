from . import _sql_utils
from . import db
from . import dtp
import os
from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for

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
                return render_template('trailer.htm', vehtype=dtp.dtp_fetch_trailtype(dbh),
                                       error = "No result found, or incorrect DTP")

            trailer["TypeStr"] = dtp.dtp_vehtype(dbh, trailer["Type"])
            return render_template('trailer_result.htm', dtpmaybe=dtpmaybe, rtrailer=trailer)
        else:
            return render_template('trailer.htm', vehtype=dtp.dtp_fetch_trailtype(dbh))

    @app.route('/traileradv', methods=['POST', 'GET'])
    def trailer_adv():
        dbh = db.get_db()
        error = None
        # advanced trailer search
        if(request.method == 'POST'):
            vehtype = None
            gvw = None
            taw = None
            if(request.form['vehtype']):
                vehtype = request.form['vehtype']
            else:
                vehtype = dtp.dtp_fetch_trailtype(dbh)
                return render_template('trailer.htm', vehtype=vehtype,
                                       error = "Invalid trailer type selected.")

            if(request.form['gvw']):
                gvw = int(request.form['gvw'])
                if(gvw < 0 or gvw > 250000):
                    return render_template('trailer.htm', vehtype=vehtype,
                                           error = "Invalid GVW given.")

            if(request.form['taw']):
                taw = int(request.form['taw'])
                if(taw < 0 or taw > 250000):
                    return render_template('trailer.htm', vehtype=vehtype,
                                           error = "Invalid TAW given.")

            numaxles = int(vehtype[0])
            if(numaxles => 5 or numaxles < 1):
                # We should never get here, but you never know.
                return render_template('trailer.htm', vehtype=vehtype,
                                       error = "Impossible axle count. Stop playing silly buggers.")


            return "{0} axles!".format(numaxles)
        else:
            return redirect(url_for('trailer'))

    ## Do the thing!
    db.init_app(app)
    return app
