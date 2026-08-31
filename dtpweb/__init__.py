from . import _sql_utils as sql
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
            if(request.form.get('dtp') != None):
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

    @app.route('/truckadv', methods=['POST', 'GET'])
    def truck_adv():
        dbh = db.get_db()
        error = None
        # advanced truck search!
        if(request.method == 'POST'):
            query = sql.Query()

            query.FROM('Master').SELECT('*')

            srch_make = request.form.get('make')
            if(srch_make is not None and srch_make != "*"):
                query.WHERE(str('MakeId="' + srch_make + '"'))
#                srch_make = dtp.dtp_vehmake(dbh, srch_make)

            srch_type = request.form.get('vehtype')
            if(srch_type is not None and srch_type != "*"):
                query.WHERE(str('TypeId="' + srch_type + '"'))
#                srch_type = dtp.dtp_vehtype(dbh, srch_type)

            srch_gvw  = request.form.get('gvw')
            if(srch_gvw is not None and srch_gvw != ""):
                query.WHERE(str('GVW_DesignWeight=' + str(int(srch_gvw)/10)))

            srch_gtw  = request.form.get('gtw')
            if(srch_gtw is not None and srch_gtw != ""):
                query.WHERE(str('GTW_DesignWeight=' + str(int(srch_gtw)/10)))

            srch_braketype_serv = request.form.get('braketype_serv')
            if(srch_braketype_serv is not None and srch_braketype_serv != "*"):
                srch_braketype_serv = dtp.dtp_braketype(dbh, srch_braketype_serv)

            srch_braketype_sec  = request.form.get('braketype_sec')
            srch_braketype_park = request.form.get('braketype_park')

            tmp = dbh.execute(str(query)).fetchall()
            results = []
            for row in tmp:
                results.append("A")

            return "{0} results".format(len(results))
        else:
            vehtype = dtp.dtp_fetch_vehtype(dbh)
            vehmake = dtp.dtp_fetch_vehmake(dbh)
            braketype = dtp.dtp_fetch_braketype(dbh)
            return render_template('truck.htm',
                                   vehtype = vehtype,
                                   vehmake = vehmake,
                                   braketype = braketype )


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

            numaxles = int(vehtype[0])
            if(numaxles >= 5 or numaxles < 1):
                # We should never get here, but you never know.
                return render_template('trailer.htm', vehtype=vehtype,
                                       error = "Impossible axle count. Stop playing silly buggers.")

            if(request.form['gvw']):
                gvw = int(request.form['gvw'])
                if(gvw < 0 or gvw > 250000):
                    return render_template('trailer.htm', vehtype=dtp.dtp_fetch_trailtype(dbh),
                                           error = "Invalid GVW given.")

            if(request.form['taw']):
                taw = int(request.form['taw'])
                if(taw < 0 or taw > 250000):
                    return render_template('trailer.htm', vehtype=dtp.dtp_fetch_trailtype(dbh),
                                           error = "Invalid TAW given.")
            else:
                taw = 0
                # Sum up given axle weights to get a TAW
                if(request.form['ax1weight']):
                    taw += int(request.form['ax1weight'])
                if(request.form['ax2weight'] and (numaxles > 1)):
                    taw += int(request.form['ax2weight'])
                if(request.form['ax3weight'] and (numaxles > 2)):
                    taw += int(request.form['ax3weight'])
                if(request.form['ax4weight'] and (numaxles > 3)):
                    taw += int(request.form['ax4weight'])


            # Calculate DTP digits
            dtp_a = numaxles
            match vehtype[1]:
                case 'S':
                    # dtp_bcd requires some lookup, here.
                    lookup_result = dtp.dtp_aweights_r(dbh, numaxles, gvw, taw)
                    if(lookup_result is not None):
                        dtp_bcd = lookup_result['DTP']
                    else:
                        dtp_bcd = 'XXX'
                case 'C':
                    # Centre drawbar
                    # 1 axle becomes 5, 2 becomes 6, 3 becomes 7, 4C isn't permitted
                    if(numaxles > 3):
                        return render_template('trailer.htm', vehtype=dtp.dtp_fetch_trailtype(dbh),
                                               error = "4-axle centre drawbar trailer? How? {0} - {1}".format(numaxles,
                                                                                                              vehtype))
                    dtp_a += 4
                    dtp_bcd = (gvw / 100)
                    taw = gvw
                case 'D':
                    # Full drawbar style (i.e. dolly-style)
                    match numaxles:
                        case 1:
                            return render_template('trailer.htm', vehtype=dtp.dtp_fetch_trailtype(dbh),
                                                   error = "Single-axle D type trailer? How? {0} - {1}".format(numaxles,
                                                                                                               vehtype))
                        case 2:
                            dtp_a += 6
                        case 3:
                            dtp_a += 6
                        case 4:
                            dtp_a = 0
                    dtp_bcd = (gvw / 100)
                    taw = gvw

            # DTP E, which axles have park brake, comes from manual input
            scrundle = list("0000")
            if(request.form.get('ax1park') != None):
                scrundle[0] = "1"
            if(request.form.get('ax2park') != None):
                scrundle[1] = "1"
            if(request.form.get('ax3park') != None):
                scrundle[2] = "1"
            if(request.form.get('ax4park') != None):
                scrundle[3] = "1"

            scrundle = "".join(scrundle)

            match scrundle:
                case '1000':
                    dtp_e = '1'
                case '0100':
                    dtp_e = '2'
                case '1100':
                    dtp_e = '3'
                case '0010':
                    dtp_e = '4'
                case '1010':
                    dtp_e = '5'
                case '0110':
                    dtp_e = '6'
                case '1110':
                    dtp_e = '7'
                case '0001':
                    dtp_e = '8'
                case '1001':
                    dtp_e = '9'
                case '0101':
                    dtp_e = 'A'
                case '1101':
                    dtp_e = 'B'
                case '0011':
                    dtp_e = 'C'
                case '1011':
                    dtp_e = 'D'
                case '0111':
                    dtp_e = 'E'
                case '1111':
                    dtp_e = 'F'
                case _:
                    dtp_e = 'X'

            # DTP F also comes from manual input (TODO)
            dtp_f = 'X'
            scrundle = list("0000")
            if(request.form.get('typeappr') != None):
                scrundle[0] = "1"
            if(request.form.get('abs') != None):
                scrundle[1] = "1"
            if(request.form.get('lsv') != None):
                scrundle[2] = "1"
            if(request.form.get('ebs') != None):
                scrundle[3] = "1"
            scrundle = "".join(scrundle)

            match scrundle:
                case '0000':
                    dtp_f = '0'
                case '1000': # Type Approved
                    dtp_f = '1'
                case '0100': # ABS
                    dtp_f = '2'
                case '1100': # Type Approved & ABS
                    dtp_f = '3'
                case '0010': # LSV
                    dtp_f = '4'
                case '1010': # Type Approved & LSV
                    dtp_f = '5'
                case '0110': # ABS & LSV
                    dtp_f = '6'
                case '1110': # Type Approved & ABS & LSV
                    dtp_f = '7'
                case '0001': # EBS
                    dtp_f = '8'
                case _: # Not a valid combo, because EBS includes ABS & LSV
                    dtp_f = 'X'


            calculated_dtp = "{0}{1}{2}{3}".format(dtp_a, dtp_bcd, dtp_e, dtp_f)
            return render_template('trailer_result_adv.htm', dtp=calculated_dtp, vehtype=vehtype, gvw=gvw, taw=taw)
        else:
            return redirect(url_for('trailer'))

    @app.route('/psv', methods=['POST', 'GET'])
    def psv():
        return "<html><body><h1>Not Implemented</h1><a href='/'>Main Menu</a></body></html>"

    @app.route('/help')
    def show_da_help():
        return render_template('help.htm')

    ## Do the thing!
    db.init_app(app)
    return app
