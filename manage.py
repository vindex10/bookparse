import argparse
import logging.config
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
from misc import load_config, ownLogger, exception_msg
from dbmanager import DBManager

lg = ownLogger()

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

    try:
        bookfile = open("data/book" + str(bookid) + ".pdf", "rb")
    except FileNotFoundError as e:
        exception_msg(lg, e
                        , level="ERR"
                        , text="No such book (id=%s) in data dir."\
                                 % str(bookid))
        raise

    mineparser = PDFParser(bookfile)
    document = PDFDocument(mineparser)
    if not document.is_extractable:
        lg.error("PDF text extraction is not allowed.")
        raise PDFTextExtractionNotAllowed

    db = DBManager()

    for pagenum, page in enumerate(PDFPage.create_pages(document)):
        realnum = pagenum + 1
        lg.info("Working on page %s (bookid=%s)", str(realnum), str(bookid))
        if (len(pages) > 0 and realnum not in pages)\
           or realnum in exclude:
            lg.info("Page %s (bookid=%s) excluded.", str(realnum), str(bookid))
            continue

        # Insert page entry to db, no HTML
        db.insert_page(bookid, realnum)

        lg.info("Recognizing (pagenum=%s) of book (id=%s).", str(realnum), str(bookid))
        pagetype = recognize(bookid, page)

        if pagetype == -1:
            lg.warning("Can't recognize page (pagenum=%s) in book (id=%s)."
                     , str(realnum)
                     , str(bookid))
            lg.info("Page %s (bookid=%s) skipped.", str(realnum), str(bookid))
            continue

        lg.info("Parsing (pagenum=%s) of book (id=%s). Type (pagetype=%s)."
              , str(realnum), str(bookid), str(pagetype))
        try:
            data = parse(bookid, page, pagetype)
        except Exception as e:
            exception_msg(lg, e
                            , level="WARN"
                            , text="Errors while parsing."
                                   " Skip (pagenum=%s) of book (id=%s)"\
                                    % (str(realnum), str(bookid)))
            continue
        else:
            lg.info("Inserting items to DB."
                    " (pagenum=%s) of book (id=%s). Type (pagetype=%s)."
                  , str(realnum), str(bookid), str(pagetype))
            try:
                db.bulk_insert(bookid, data, pnum=realnum)
            except Exception as e:
                exception_msg(lg, e
                                , level="ERR"
                                , text="Errors during inserting data into DB."
                                       " Maybe you should check the parser")

        # Update page entry with parsed HTML
        lg.info("Parsing to HTML (pagenum=%s) of book (id=%s)."
              , str(realnum), str(bookid))
        try:
            html = pdftohtml(page)
        except Exception as e:
            exception_msg(lg, e
                            , text="Cannot convert PDF to HTML."
                                   " (pagenum=%s) of book (id=%s)"\
                                   % (str(realnum), str(bookid)))
        else:
            lg.info("Inserting HTML to DB."
                    " (pagenum=%s) of book (id=%s). Type (pagetype=%s)."
                  , str(realnum), str(bookid), str(pagetype))
            db.insert_page(bookid, realnum, data=html)

        lg.info("Done with page."
                " (pagenum=%s) of book (id=%s). Type (pagetype=%s)."
              , str(realnum), str(bookid), str(pagetype))

if __name__ == "__main__":
    argp = argparse.ArgumentParser()

    def isbookid(string):
        try:
            int(string)
        except TypeError:
            lg.error("Wrong book id. Must be an integer")
            raise argparse.ArgumentTypeError("Book id must be integer")
        path = "data/book"+string+".pdf"
        if os.path.exists(path):
            return int(string)
        else:
            lg.error("Wrong book id. No such file: %s.pdf"
                   , str(string))
            raise argparse.ArgumentTypeError("The book with such id does not exist")
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
                lg.error("Wrong input argument format.")
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

    lg.info("Start parsing a book (id=%s). Pages: %s.", str(args["bookid"])
        , ("all" if len(args["pages"]) == 0 else str(args["pages"])))
    BookParse(**args)
