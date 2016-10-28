import pdfminer.settings
pdfminer.settings.STRICT = False
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTChar, LTTextBox, LTTextLine, LTFigure, LTImage, LTPage

def parse(page):
    rsrcmgr = PDFResourceManager()
    laparams = LAParams(char_margin=4
                       ,word_margin=6
                       ,boxes_flow=1.5
                       ,line_margin=0.4)
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    def parseit(obj):
        res = [""]
        if isinstance(obj, LTChar):
            if isinstance(res[-1], str):
                res[-1] += obj.get_text()
            else:
                res.append(obj.get_text())
        elif isinstance(obj, LTTextBox) or\
                isinstance(obj, LTTextLine):
            res.append(obj.get_text())

        elif isinstance(obj, LTFigure) or isinstance(obj, LTPage):
            for subobj in obj:
                subpar = parseit(subobj)
                if isinstance(res[-1], str) and isinstance(subpar[0], str):
                    res = res[:-1] + [res[-1]+subpar[0]] + subpar[1:]
                else:
                    res = res + subpar
        elif isinstance(obj, LTImage):
            rawdata = obj.stream.get_rawdata()
            res += [("Image", obj.bbox, rawdata)]
        return res

    interpreter.process_page(page)
    layout = device.get_result()
    parsed = parseit(layout)
    parsed = list(filter(None, parsed))

    #return parsed
    itemcounter = 2

    res = {"items": list()
         , "nonitems": list()}
    images = list(filter(lambda item: item[0] is "Image",parsed))


    # treat first image as non-item
    if len(images) > 0:
        for img in images[0:1]:
            res["nonitems"].append({"image": img[2]
                                  , "name": itemcounter
                                  , "description": str(img[1])})
        itemcounter += 1

    # treat others as item-images
    if len(images) > 1:
        for img in images[1:]:
            res["items"].append({"image": img[2]
                               , "itemonpage": itemcounter
                               , "other": str(img[1])})
            itemcounter += 1


    res["items"].append({"itemonpage": 1, "other": "something"})
    return res
