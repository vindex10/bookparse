import argparse
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

from parser import Parser
from recognizer import Recognizer
from dbmanager import DBManager


class BookParser(object):
    laparams = {"char_margin": 4,
                "word_margin": 6,
                "boxes_flow": 1.5,
                "line_margin": 0.4
               }

    def __init__(self, file=None, pages=set()\
                 , exclude=set(), laparams=dict()):
        self.file = file
        self.pages = pages
        self.exclude = exclude
        self.laparams.update(laparams)

    def run(self):
        mineparser = PDFParser(self.file)
        document = PDFDocument(mineparser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rec = Recognizer()
        par = Parser()
        db = DBManager()

        for pagenum, page in enumerate(PDFPage.create_pages(document)):
            realnum = pagenum + 1
            if len(self.pages) > 0\
               and realnum in self.pages\
               and realnum not in self.exclude:
                pagetype = rec.get_pagetype(page)
                data = par.parse(page, pagetype)
                db.insert_items(data)





if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("-f", "--file"
                      , type=argparse.FileType("rb")
                      , help="Path to file to process")

    def numrange(string):
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
                      , type=numrange
                      , help="Range of pages to process")
    argp.add_argument("-e", "--exclude"
                      , type=numrange
                      , help="Range of pages to exclude")

    pargs = argp.parse_args()
    args = vars(pargs)
    if len(args["pages"]) > 0:
        args["pages"] = args["pages"] - args["exclude"]
