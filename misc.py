import json
import logging
import logging.config
import sys

def load_config(cnfname, defcnf=None):
    """Load confiig from file at /config with name cnfname.conf,
    or return updated existing (defcnf).
    """
    if defcnf is None:
        defcnf = dict()
    res = defcnf.copy()
    try:
        f = open("config/" + str(cnfname) + ".conf", "r")
        newcnf = json.load(f)
        res.update(newcnf)
        f.close()
    except:
        pass

    return res
