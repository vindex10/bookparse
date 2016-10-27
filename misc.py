import json
import logging
import sys
import traceback

lg = logging.getLogger(__name__)

def load_config(cnfname, defcnf=None):
    """Load confiig from file at /config with name cnfname.conf,
    or return updated existing (defcnf).
    """
    if defcnf is None:
        defcnf = dict()
    res = defcnf.copy()

    try:
        f = open("config/" + str(cnfname) + ".conf", "r")
    except FileNotFoundError as e:
        exception_msg(lg, e
            , text="There is no config for (%s). Using default." % str(cnfname)
            , notb=True)
    else:
        try:
            newcnf = json.load(f)
        # In Python 3.5 should be changed to json.JSONDecodeError
        except ValueError as e:
            exception_msg(lg, e, text="Wrong format of config (%s). Should be JSON." % str(cnfname))
        else:
            res.update(newcnf)
        f.close()

    return res

def exception_msg(logger, e, level=None, text=None, notb=False):
    """ Print exception message, and write traceback to DEBUG if needed"""
    level_funcs = {"ERR": logger.error
                 , "WARN": logger.warning
                 , "INFO": logger.info
                 , "DEBUG": logger.debug}

    if level is None or level not in level_funcs.keys():
        level = "INFO"

    func = level_funcs[level]
    text = str(text)+"\n" if text is not None else ""
    func(text + str(e))

    if not notb:
        logger.debug(traceback.format_exc())
