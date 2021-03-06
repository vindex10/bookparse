import MySQLdb

import misc
from misc import ownLogger, exception_msg

lg = ownLogger(__name__)

class DBManager(object):
    """DBManager class needed to communicate with DB
    """
    config = {"dbuser": "user"
             ,"dbpass": "password"
             ,"dbname": "db"
             }
    def __init__(self):
        self.config = misc.load_config("dbmanager", defcnf=self.config)

        try:
            self.db = MySQLdb.connect(user=self.config["dbuser"]
                                 ,passwd=self.config["dbpass"]
                                 ,db=self.config["dbname"])
        except MySQLdb.Error as e:
            exception_msg(lg, e, level="ERR"
                               , text="Can't connect to mysql db.")
            raise

        self.db.set_character_set('utf8')

    def insert_page(self, bid, pagenum, data=None):
        cur = self.db.cursor()

        try:
            cur.execute("""SELECT id, isbn1, keyname
                FROM book WHERE id=%s""", (bid,))
            bdata = cur.fetchone()
        except MySQLdb.Error as e:
            exception_msg(lg, e, level="ERR"
                               , text="No such book with id "+str(bid))
            raise

        query = """INSERT INTO pages (isbn1, keyname, pagedata, pagenum)
                    VALUES (%s, %s, %s, %s) ON DUPLICATE KEY
                    UPDATE pagedata=%s"""

        # print(query % (bdata[1], bdata[2], data, pagenum))
        try:
            cur.execute(query, (bdata[1], bdata[2], data, pagenum, data))
            self.db.commit()
        except MySQLdb.Error as e:
            exception_msg(lg, e, level="ERR"
                               , text="Can't insert page to DB")
            raise

    def insert_item(self, bid, data, pnum=None):
        """Insert item to DB.items. Add info about book (isbn1, keyname),
        previously fetched by provided book id (bid).
        """
        item_fields = ("itemnum",\
                       "column", "pagenum", "itemonpage", "all", "name",\
                       "description", "other", "image",\
                       "linktoimage", "note", "address", "country",\
                       "picmisk", "pricestart", "priceend",\
                       "pricereal", "currency", "date", "auctionhouse")
        cur = self.db.cursor()

        try:
            cur.execute("""SELECT id, isbn1, keyname
                FROM book WHERE id=%s""", (bid,))
            bdata = cur.fetchone()
        except MySQLdb.Error as e:
            exception_msg(lg, e, level="ERR"
                               , text="No such book with id "+str(bid))
            raise

        qdata = {key: data[key] for key in data.keys()
                                 if key in item_fields}
        if len(qdata) > 0:
            qdata.update({"isbn1": bdata[1]
                         ,"keyname": bdata[2]})
            if pnum is not None:
                qdata.update({"pagenum": pnum})
        else:
            lg.info("No items in book (id=%s) on page (pagenum=%s) found."
                  , str(bid), pnum if pnum is not None else -1)
            return

        keylist = list()
        valist = list()
        for key,val in qdata.items():
            keylist.append(key)
            valist.append(val)

        paramkeys = ("%s,"*len(valist))[:-1]
        updkeys = [key for key in keylist if key
            not in ("id", "isbn1", "pagenum", "itemonpage", "keyname")]
        updvals = [qdata[key] for key in updkeys]
        updkeys = [str(key) + "=%s" for key in updkeys]

        query = "INSERT INTO items (" + ",".join(keylist) + ")"\
                " VALUES (" + paramkeys + ") ON DUPLICATE KEY"\
                " UPDATE " + ",".join(updkeys)

        try:
            cur.execute(query, tuple(valist + updvals))
            self.db.commit()
        except MySQLdb.Error as e:
            exception_msg(lg, e, level="ERR"
                               , text="Can't insert item to DB")
            raise

    def insert_nonitem(self, bid, data, pnum=None):
        """Insert non-item into DB.`nonitems`.
        Add info about book (isbn1, keyname),
        previously fetched by provided book id (bid).
        """
        item_fields = ("pagenum", "name", "description", "image")
        cur = self.db.cursor()

        try:
            cur.execute("""SELECT id, keyname
                FROM book WHERE id=%s""", (bid,))
            bdata = cur.fetchone()
        except MySQLdb.Error as e:
            exception_msg(lg, e, level="ERR"
                               , text="No such book with id "+str(bid))
            raise

        qdata = {key: data[key] for key in data.keys()
                                 if key in item_fields}
        if len(qdata) > 0:
            qdata.update({"keyname": bdata[1]})
            if pnum is not None:
                qdata.update({"pagenum": pnum})
        else:
            lg.info("No non-items in book (id=%s) on page (pagenum=%s) found."
                  , str(bid), pnum if pnum is not None else -1)
            return

        keylist = list()
        valist = list()
        for key,val in qdata.items():
            keylist.append(key)
            valist.append(val)

        paramkeys = ("%s,"*len(valist))[:-1]
        updkeys = [key for key in keylist if key
            not in ("id", "pagenum", "keyname")]
        updvals = [qdata[key] for key in updkeys]
        updkeys = [str(key) + "=%s" for key in updkeys]

        query = "INSERT INTO nonitems (" + ",".join(keylist) + ")"\
                " VALUES (" + paramkeys + ") ON DUPLICATE KEY"\
                " UPDATE " + ",".join(updkeys)

        try:
            cur.execute(query, tuple(valist + updvals))
            self.db.commit()
        except MySQLdb.Error as e:
            exception_msg(lg, e, level="ERR"
                               , text="Can't insert item to DB")
            raise

    def bulk_insert(self, bid, data, pnum=None, entrytype=None):
        """Insert items to DB.items item-by-item.
        See more in insert_item definition
        """

        funcs = {"items": self.insert_item
               , "nonitems": self.insert_nonitem}

        if entrytype is None:
            for key in funcs.keys():
                if key in data.keys():
                    self.bulk_insert(bid, data[key], pnum, entrytype=key)
            return

        thefunc = funcs[entrytype]

        if isinstance(data, dict):
            thefunc(bid, data, pnum)
        else:
            for item in data:
                thefunc(bid, item, pnum)

    def get_imgbyhash(self, imhash):
        cur = self.db.cursor()
        cur.execute(\
            "SELECT id, MD5(image) AS imhash, \"items\" AS tabname FROM items HAVING imhash=%s"
            " UNION ALL "
            "SELECT id, MD5(image) AS imhash, \"nonitems\" AS tabname FROM nonitems HAVING imhash=%s;", (imhash, imhash))
        try:
            res = cur.fetchone()
            res = {"id": res[0], "tabname": res[2]}
        except (MySQLdb.Error, TypeError):
            res = "undefined"

        return res
