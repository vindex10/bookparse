from io import BytesIO
from importlib import import_module
from hashlib import md5
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

from dbmanager import DBManager
db = DBManager()

def recognize(bookid, page):
    """Gets bookid and page(instance of pdfminer.PDFPage), loads a collection
    of recognizers which correspond to the book, and maps them one by one
    on page until one returns True. Returns corresponding page type.
    """
    try:
        int(bookid)
    except:
        raise ValueError("Bookid must be integer")
    try:
        bookrec = import_module("recognizers.book" + str(bookid))
    except:
        print("No such recognizer found for book with id " + str(bookid)+\
            ". Please name your recognizer as book" + str(bookid) + ".py")
        raise

    for (t, func) in bookrec.pagetypes.items():
        rec = getattr(bookrec, func)
        if rec(page):
            return t

def parse(bookid, page, pagetype):
    """Gets id of the book, page(instnce of pdfminer.PDFPage) an type
    of page, then loads parsers for book and applies needed for page.
    Returns parsed data in form of collection of dictionaries
    (1 dict per item), with keys correspond to DB fields.
    """
    try:
        int(bookid)
    except:
        raise ValueError("Bookid must be integer")
    try:
        bookpar = import_module("parsers.book" + str(bookid))
        pagepar = import_module(bookpar.__name__ + "."\
                                + str(bookpar.pagetypes[pagetype]))
    except:
        print("No such parser found for book with id " + str(bookid)+\
            ". Please name your parser as book" + str(bookid) + ".py")
        raise

    return pagepar.parse(page)

def pdftohtml(page):
    output = BytesIO()
    manager = PDFResourceManager()

    class imagewriter(object):
        @staticmethod
        def export_image(img):
            if img.stream:
                fstream = img.stream.get_rawdata()
            else:
                return "undefined"

            imhash = md5(fstream).hexdigest()
            imgid = db.get_imgbyhash(imhash)

            if imgid is not "undefined":
                return "items."+str(imgid)
            else:
                return "undefined"

    converter = HTMLConverter(manager
                             ,output
                             ,laparams=LAParams()
                             ,imagewriter=imagewriter)
    interpreter = PDFPageInterpreter(manager, converter)

    interpreter.process_page(page)
    converter.close()
    text = output.getvalue().decode("utf-8")
    output.close()

    return text
