import MySQLdb
import misc

class DBManager(object):
    config = {"dbuser": "user"
             ,"dbpass": "password"
             ,"dbname": "db"
             }
    def __init__(self):
        self.config = misc.load_config("dbmanager", defcnf=self.config)
        self.db = MySQLdb.connect(user=self.config["dbuser"]
                                 ,passwd=self.config["dbpass"]
                                 ,db=self.config["dbname"])

    def insert_items(self, bid, pnum, data):
        print("Bookid: "+str(bid)+"    Page: "+str(pnum))
        for i in data:
            print(i)
