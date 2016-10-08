from importlib import import_module


def recognize(bookid, page):
    try:
        int(bookid)
    except:
        raise ValueError("Bookid must be numeric")
    try:
        bookrec = import_module("recognizers.book" + str(bookid))
    except:
        print("No such recognizer for book with id " + str(bookid))
        raise

    for (t, func) in bookrec.pagetypes.items():
        rec = getattr(bookrec, func)
        if rec(page):
            return t

def parse(bookid, page, pagetype):
    try:
        int(bookid)
    except:
        raise ValueError("Bookid must be numeric")
    try:
        bookpar = import_module("parsers.book" + str(bookid))
    except:
        print("No such parser for book with id " + str(bookid))
        raise

    func = getattr(bookpar, bookpar.pagetypes[pagetype])
    return func(page)
