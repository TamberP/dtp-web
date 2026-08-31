import sqlite3
from . import db

def dtp_vers(dbh):
    if dbh is not None:
        return dbh.execute("SELECT * FROM Version;").fetchone()

def dtp_vehtype(dbh, vehtype):
    if dbh is not None:
        return dbh.execute("SELECT Type FROM VehType WHERE TypeId=(?)", (vehtype,)).fetchone()[0]

# Note: Specifically filters out trailer typecodes because of
# where we want to use this (on the truck specific search)

# Typecodes ending in 'D' are drawbar trailer, 'S' is semi-trailer,
# 'C' are centre-drawbar.
def dtp_fetch_vehtype(dbh):
    if dbh is not None:
        return dbh.execute("SELECT * FROM VehType WHERE TypeId NOT LIKE '_D' AND TypeID NOT LIKE '_S' AND TypeID NOT LIKE '_C' ORDER BY Type").fetchall()

# For completeness, here's the one that gives you the opposite of fetch_vehtype.
def dtp_fetch_trailtype(dbh):
    if dbh is not None:
        return dbh.execute("SELECT * FROM VehType WHERE TypeId LIKE '_D' OR TypeId LIKE '_S' OR TypeId LIKE '_C' ORDER BY Type").fetchall()

def dtp_vehmake(dbh, vehmake):
    if dbh is not None:
        return dbh.execute("SELECT Make FROM VehMake WHERE MakeId=(?)", (vehmake,)).fetchone()[0]

def dtp_fetch_vehmake(dbh):
    if dbh is not None:
        return dbh.execute("SELECT * FROM VehMake ORDER BY Make").fetchall()

def dtp_brakeroutine(dbh, routineid):
    if dbh is not None:
        return dbh.execute("SELECT \"Routine\" FROM BrakRoute WHERE RoutineId=(?)", (routineid,)).fetchone()[0]

def dtp_brakeroutine_s(dbh, routineid):
    if dbh is not None:
        result = dbh.execute("SELECT \"Routine\" FROM BrakRoute WHERE RoutineId=(?)", (routineid,)).fetchone()[0]
        return result.split(",")

def dtp_splitroutine(dbh, routineid):
    if dbh is not None:
        return dbh.execute("SELECT \"Routine\" from SplitRoutine WHERE RoutineId=(?)", (routineid,)).fetchone()

def dtp_braketype(dbh, typeid):
    if dbh is not None:
        tmp = dbh.execute("SELECT Type FROM braktype WHERE TypeId=(?)", (typeid,)).fetchone()
        if tmp is not None:
            return tmp[0]

def dtp_fetch_braketype(dbh):
    if dbh is not None:
        return dbh.execute("SELECT * FROM braktype ORDER BY Type").fetchall()

def dtp_fetch(dbh, dtp):
    if dbh is not None:
        return dbh.execute("SELECT * FROM Master WHERE DtpNumber=(?);", (dtp,)).fetchall()

def dtp_aweights(dbh, numaxles, dtp):
    if dbh is not None:
        return dbh.execute("SELECT * FROM {0}trl WHERE DTP=(?);".format(str("A"*numaxles)), (dtp,)).fetchone()

def dtp_aweights_r(dbh, numaxles, gvw, taw):
    if dbh is not None:
        return dbh.execute("SELECT * FROM {0}trl WHERE GVW=(?) AND TotalAxleWeight=(?)".format(str("A"*numaxles)),
                           (gvw, taw)).fetchone()

def dtp_t_parse(dtp):
    if(dtp is not None):
        dbh = db.get_db()
        trailer = {}
        aweights = {}
        # Character A: Type of trailer
        match dtp[0]:
            case '1':
                trailer["Type"] = '1S'
            case '2':
                trailer["Type"] = '2S'
            case '3':
                trailer["Type"] = '3S'
            case '4':
                trailer["Type"] = '4S'
            case '5':
                trailer["Type"] = '1C'
            case '6':
                trailer["Type"] = '2C'
            case '7':
                trailer["Type"] = '3C'
            case '8':
                trailer["Type"] = '2D'
            case '9':
                trailer["Type"] = '3D'
            case '0':
                trailer["Type"] = '4D'
            case _:
                return None # FIXME: Make this a more useful error.

        aweights = dtp_aweights(dbh, int(trailer["Type"][0]), dtp[1:4])
        # Character B, C, D
        if(trailer["Type"][1] != 'S'):
            # Drawbar trailers have all their weight on their axles,
            # so Total Axle Weight is the same as their GVW, and this
            # weight is encoded in their DTP number.
            trailer["GVW"] = str(int(dtp[1:4]) * 100)
            trailer["TAW"] = None
        else:
            # Semi-trailers are a bit more awkward, and so the number
            # encoded in their DTP is a reference into a different
            # lookup table. (TODO)
            trailer["GVW"] = aweights["GVW"]
            trailer["TAW"] = aweights["TotalAxleWeight"]

        # Character E: Which axles have park-brake.
        parkaxles = ''
        trailer["AxleCount"] = int(trailer["Type"][0])
        match dtp[4]:
            case '1': # Axle 1 only
                trailer["Park"] = [True, False, False, False]
            case '2': # Axle 2 only
                if(trailer["AxleCount"] < 2):
                    return None # FIXME: Make this more useful as an error.
                trailer["Park"] = [False, True, False, False]
            case '3': # Axles 1 + 2
                if(trailer["AxleCount"] < 2):
                    return None # FIXME
                trailer["Park"] = [True, True, False, False]
            case '4': # Axle 3 only
                if(trailer["AxleCount"] < 3):
                    return None # FIXME
                trailer["Park"] = [False, False, True, False]
            case '5': # Axles 1 + 3
                if(trailer["AxleCount"] < 3):
                    return None # FIXME
                trailer["Park"] = [True, False, True, False]
            case '6': # Axles 2 + 3
                if(trailer["AxleCount"] < 3):
                    return None # FIXME
                trailer["Park"] = [False, True, True, False]
            case '7': # Axles 1 + 2 + 3
                if(trailer["AxleCount"] < 3):
                    return None # FIXME
                trailer["Park"] = [True, True, True, False]
            case '8': # Axle 4 only
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [False, False, False, True]
            case '9': # Axles 1 + 4
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [True, False, False, True]
            case 'A': # Axles 2 + 4
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [False, True, False, True]
            case 'B': # Axles 1 + 2 + 4
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [True, True, False, True]
            case 'C': # Axles 3 + 4
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [False, False, True, True]
            case 'D': # Axles 1 + 3 + 4
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [True, False, True, True]
            case 'E': # Axles 2 + 3 + 4
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [False, True, True, True]
            case 'F': # Axles 1 + 2 + 3 + 4
                if(trailer["AxleCount"] < 4):
                    return None # FIXME
                trailer["Park"] = [True, True, True, True]
            case _:
                # Invalid character
                return None # FIXME

        # Character F: What LSV/ABS features/is trailer type approved?
        trailer["LSV"] = False
        trailer["ABS"] = False
        trailer["EBS"] = False
        trailer["TypeAppr"] = False

        match dtp[5]:
            case '0':
                # Nothing to do, but we need to do 'something'
                trailer["TypeAppr"] = False
            case '1':
                trailer["TypeAppr"] = True
            case '2':
                trailer["ABS"] = True
            case '3':
                trailer["ABS"] = True
                trailer["TypeAppr"] = True
            case '4':
                trailer["LSV"] = True
            case '5':
                trailer["LSV"] = True
                trailer["TypeAppr"] = True
            case '6':
                trailer["LSV"] = True
                trailer["ABS"] = True
            case '7':
                trailer["LSV"] = True
                trailer["ABS"] = True
                trailer["TypeAppr"] = True
            case '8':
                trailer["EBS"] = True
            case _:
                # How the fuck did you get here?
                return None


        trailer["Axle1Weight"] = aweights['Axle1Weight']
        trailer["Axle2Weight"] = aweights['Axle2Weight'] if(trailer["AxleCount"] > 1) else None
        trailer["Axle3Weight"] = aweights['Axle3Weight'] if(trailer["AxleCount"] > 2) else None
        trailer["Axle4Weight"] = aweights['Axle4Weight'] if(trailer["AxleCount"] > 3) else None
        return trailer


def master_rowparse(raw):
    if(raw is not None):
        dbh = db.get_db()
        testdata = {}
        testdata["DTpNumber"] = raw["DTpNumber"]
        testdata["MakeId"] = raw["MakeId"]
        testdata["MakeStr"] = dtp_vehmake(dbh, raw["MakeId"])
        testdata["TypeId"] = raw["TypeId"]
        testdata["TypeStr"] = dtp_vehtype(dbh, raw["TypeId"])
        testdata["AxleCount"] = int(raw["TypeId"][0])
        testdata["Suffixes"] = raw["DuplicateID"] if (raw["DuplicateID"] is not None) else ''
        testdata["Second_Front_Axle_Steer"] = 'Yes' if(raw["SecFrontAxleSteered"] == 1) else 'No'
        testdata["Trans_Sec_Park_Brake"] = 'Yes' if(raw["TransSecParkBrake"] == 1) else 'No'
        testdata["Secondary_only_Tractor"] = 'Yes' if(raw["SecBrakeOnlyOnTrac"] == 1) else 'No'
        testdata["PrePriorPost68"] = 'Yes' if(raw["PPPSelector"] == 1) else 'No'
        testdata["GVWDesign"] = (raw["GVW_DesignWeight"] * 10)
        testdata["GTWDesign"] = (raw["GTW_DesignWeight"] * 10)
        testdata["Axle1DesignWeight"] = (raw["Axle1DesignWeight"] * 10)
        testdata["Axle2DesignWeight"] = (raw["Axle2DesignWeight"] * 10)
        testdata["Axle3DesignWeight"] = (raw["Axle3DesignWeight"] * 10)
        testdata["Axle4DesignWeight"] = (raw["Axle4DesignWeight"] * 10)
        testdata["Axle5DesignWeight"] = (raw["Axle5DesignWeight"] * 10)
        testdata["Axle1Modulation"] = 'Yes' if(raw["ModAxle1Affect"] == 1) else 'No'
        testdata["Axle2Modulation"] = 'Yes' if(raw["ModAxle2Affect"] == 1) else 'No'
        testdata["Axle3Modulation"] = 'Yes' if(raw["ModAxle3Affect"] == 1) else 'No'
        testdata["Axle4Modulation"] = 'Yes' if(raw["ModAxle4Affect"] == 1) else 'No'
        testdata["Axle5Modulation"] = 'Yes' if(raw["ModAxle5Affect"] == 1) else 'No'
        testdata["ABSFitted"] = 'Yes' if(raw["ABSFitted"] == 1) else 'No'
        testdata["ABSOption"] = 'Yes' if(raw["ABSOption"] == 1) else 'No'
        testdata["LSVFitted"] = 'Yes' if(raw["LSVFitted"] == 1) else 'No'
        testdata["LSVOption"] = 'Yes' if(raw["LSVOption"] == 1) else 'No'
        testdata["DoubleDrive"] = 'Yes' if(raw["DoubleDriveFitted"] == 1) else 'No'
        testdata["ThirdDiff"] = 'Yes' if(raw["AskThirdDiffFitted"] == 1) else 'No'
        testdata["ParkOnDiff"] = 'Yes' if(raw["SecParkBrakeOnDiffAxle"] == 1) else 'No'
        testdata["ServBrakeDist"] = raw["ServiceBrakeDestrib"]
        testdata["SecBrakeDist"] = (raw["SecBrakeDestrib"]) if(raw["SecBrakeDestrib"] != 99) else 100
        testdata["ServiceType"] = dtp_braketype(dbh, raw["FoundServBrake"])
        testdata["SecondaryType"] = dtp_braketype(dbh, raw["FoundSecBrake"])
        testdata["ParkType"] = dtp_braketype(dbh, raw["FoundParkBrake"])
        testdata["BrakeRoutine"] = dtp_brakeroutine_s(dbh, raw["BrakeRoutine"])
        # break out brake routine strings
        testdata["BrakeRoutineServ"] = testdata["BrakeRoutine"][0]
        testdata["BrakeRoutineSec"]  = testdata["BrakeRoutine"][1]
        testdata["BrakeRoutinePark"] = testdata["BrakeRoutine"][2]

        testdata["SplitRoutine"] = dtp_splitroutine(dbh, raw["SplitRoutine"])
        return testdata
    else:
        return None
