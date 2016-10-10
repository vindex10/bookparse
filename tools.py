from importlib import import_module


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
    except:
        print("No such parser found for book with id " + str(bookid)+\
            ". Please name your parser as book" + str(bookid) + ".py")
        raise

    func = getattr(bookpar, bookpar.pagetypes[pagetype])
    return func(page)
