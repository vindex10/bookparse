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

    def insert_item(self, bid, pnum, data):
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

        print(query)
        self.db.commit()

    def insert_items(self, bid, pnum, data):
        """Insert items to DB.items item-by-item.
        See more in insert_item definition
        """
        if isinstance(data, dict):
            self.insert_item(bid, pnum, data)
        else:
            for item in data:
                self.insert_item(bid, pnum, item)
