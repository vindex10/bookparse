import argparse
import logging
import os
import sys
import re

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams


from tools import recognize, parse, pdftohtml
from misc import load_config
from dbmanager import DBManager

lg = logging.getLogger(__name__)

logconf = load_config("logging", defcnf={
     "version": 1
    ,"disable_existing_loggers": False
})
logging.config.dictConfig(logconf)

handler = [h for h in lg.handlers if h._name == "file"]
if len(handler) is not 0:
    handler[0].doRollover()

def BookParse(bookid, pages=None, exclude=None):
    """ Takes id of book to parse. Id of book is one from DB,
    and should correspond to filename as book12.pdf,
    for id of the book in DB is 12. Also function accepts
    optional argument "pages", it defines pages to parse, and
    optional argument "exclude", to define pages to exclude.
    Range format accepted: 1,2,3-8,15
    """
    if pages is None:
        pages = set()
    if exclude is None:
        exclude = set()

    bookpath = "data/book" + str(bookid) + ".pdf"
    if os.path.exists(bookpath):
        bookfile = open("data/book" + str(bookid) + ".pdf", "rb")
    else:
        raise IOError("No such book with id " + str(bookid) + " in data dir")
    mineparser = PDFParser(bookfile)
    document = PDFDocument(mineparser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed

    db = DBManager()

    for pagenum, page in enumerate(PDFPage.create_pages(document)):
        realnum = pagenum + 1
        if (len(pages) > 0 and realnum not in pages)\
           or realnum in exclude:
            continue

        # Insert page entry to db, no HTML
        db.insert_page(bookid, realnum)

        pagetype = recognize(bookid, page)
        data = parse(bookid, page, pagetype)
        db.insert_items(bookid, data, pnum=realnum)

        # Update page entry with parsed HTML
        html = pdftohtml(page)
        db.insert_page(bookid, realnum, data=html)

if __name__ == "__main__":
    argp = argparse.ArgumentParser()

    def isbookid(string):
        try:
            int(string)
        except:
            raise argparse.ArgumentTypeError("Book id must be integer")
        path = "data/book"+string+".pdf"
        if os.path.exists(path):
            return int(string)
        else:
            argparse.ArgumentError("bookid", "The book with such id does not exist")
    argp.add_argument("bookid"
                     ,type=isbookid
                     ,help="Book id. The file should be named like book123.pdf"
                     )

    def isnumrange(string):
        string = string.replace(" ", "")
        parts = string.split(",")
        parts = filter(None, parts)

        single = re.compile(r"^\d+$")
        ranged = re.compile(r"^\d+-\d+$")

        res = set()

        for part in parts:
            if single.match(part):
                res = res|set([int(part)])
            elif ranged.match(part):
                first, last = part.split("-")
                res = res|set(range(int(first), int(last)+1))
            else:
                raise argparse.ArgumentTypeError("Wrong argument format")

        return res
    argp.add_argument("-p", "--pages"
                     ,type=isnumrange
                     ,default=set()
                     ,help="Range of pages to process. Format: 1,2,3-8,10")
    argp.add_argument("-e", "--exclude"
                     ,type=isnumrange
                     ,default=set()
                     ,help="Range of pages to exclude. Format: 1,2,3-8,10")

    pargs = argp.parse_args()
    args = vars(pargs)
    if len(args["pages"]) > 0:
        args["pages"] = args["pages"] - args["exclude"]

    BookParse(**args)
