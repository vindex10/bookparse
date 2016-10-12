import MySQLdb
import misc

class DBManager(object):
    """DBManager class needed to communicate with DB
    """
    config = {"dbuser": "user"
             ,"dbpass": "password"
             ,"dbname": "db"
             }
    def __init__(self):
        self.config = misc.load_config("dbmanager", defcnf=self.config)
        self.db = MySQLdb.connect(user=self.config["dbuser"]
                                 ,passwd=self.config["dbpass"]
                                 ,db=self.config["dbname"])

    def insert_page(self, bid, data):
        cur = self.db.cursor()

        try:
            cur.execute("""SELECT id, isbn1, keyname
                FROM book WHERE id=%s""", (bid,))
            bdata = cur.fetchone()

            cur.execute("""SELECT MAX(pagenum)
                    FROM pages WHERE isbn1=%s""", (bdata[1],))
            try:
                pagenum = cur.fetchone()[0]
            except:
                pagenum = 1
        except:
            print("DBManager: no such book with id "+str(bid))
            raise

        query = """INSERT INTO pages (isbn1, keyname, pagedata, pagenum)
                        VALUES (%s, %s, %s, %s)"""

        # print(query % (bdata[1], bdata[2], data, pagenum))
        cur.execute(query, (bdata[1], bdata[2], data, pagenum))
        self.db.commit()

    def insert_item(self, bid, data):
        """Insert item to DB.items. Add info about book (isbn1, keyname),
        previously fetched by provided book id (bid).
        """
        item_fields = ("itemnum",\
                       "column", "itemonpage", "all", "name",\
                       "description", "other", "image",\
                       "linktoimage", "note", "address", "country",\
                       "picmisk", "pricestart", "priceend",\
                       "pricereal", "currency", "date", "auctionhouse")
        cur = self.db.cursor()

        try:
            cur.execute("""SELECT id, isbn1, keyname
                FROM book WHERE id=%s""", (bid,))
            bdata = cur.fetchone()
        except:
            print("DBManager: no such book with id "+str(bid))
            raise

        qdata = {key: data[key] for key in data.keys()
                                 if key in item_fields}
        if len(qdata) > 0:
            qdata.update({"isbn1": bdata[1]
                         ,"keyname": bdata[2]})
        else:
            return

        keylist = ",".join(qdata.keys())
        valist = qdata.values()
        paramkeys = ("%s,"*len(valist))[:-1]

        query = "INSERT INTO items (" + keylist + ")"\
                " VALUES (" + paramkeys + ")"
        cur.execute(query, tuple(valist))

        self.db.commit()

    def insert_items(self, bid, data):
        """Insert items to DB.items item-by-item.
        See more in insert_item definition
        """
        if isinstance(data, dict):
            self.insert_item(bid, data)
        else:
            for item in data:
                self.insert_item(bid, item)

    def get_imgbyhash(self, imhash):
        cur = self.db.cursor()
        cur.execute("SELECT id, image FROM items WHERE md5(image)=%s", (imhash,))
        try:
            res = cur.fetchone()[0]
        except:
            res = "undefined"

        return res
