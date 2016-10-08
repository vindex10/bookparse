import json

def load_config(cnfname, defcnf=None):
    if defcnf is None:
        defcnf = dict()
    res = defcnf.copy()
    try:
        f = open("config/"+str(cnfname)+".conf", "r")
        newcnf = json.load(f)
        res.update(newcnf)
        f.close()
    except:
        pass

    return res
