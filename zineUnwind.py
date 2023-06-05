from copy import deepcopy
from pathlib import Path
from sys import argv
#from optparse import OptionParser

from PyPDF2 import PdfFileReader, PdfFileWriter
from pdf2image import convert_from_path
import img2pdf
import PIL
# from scipy import misc


def rotate_pages(pdf_path):
    pdf_writer = PdfFileWriter()
    pdf_reader = PdfFileReader(pdf_path)
    # Rotate page 90 degrees to the right
    page_1 = pdf_reader.getPage(0).rotateClockwise(90)
    pdf_writer.addPage(page_1)
    # Rotate page 90 degrees to the left
    page_2 = pdf_reader.getPage(1).rotateCounterClockwise(90)
    pdf_writer.addPage(page_2)
    # Add a page in normal orientation
    pdf_writer.addPage(pdf_reader.getPage(2))

    with open('rotate_pages.pdf', 'wb') as fh:
        pdf_writer.write(fh)


def test(pdpath: Path):
    images = convert_from_path(pdpath.absolute())
    for i, page in enumerate(images):
        page.save(f"./out/page{str(i)}.jpg")

def splitHorizontal(page: PIL.Image):
    width, height = page.size
    width_cutoff = page.width // 2

    first = deepcopy(page.crop((0, 0, width_cutoff, height)))
    last = deepcopy(page.crop((width_cutoff, 0, width, height)))
    return(first, last)

def readzine(deckpath: Path):
    deck = convert_from_path(deckpath.absolute())
    name = deckpath.name
    fromStart = []
    fromBack = []

    first, last = splitHorizontal(deck[0])  # first page is folded different
    fromStart.append(first.rotate(90, PIL.Image.NEAREST, expand=1))
    fromBack.append(last.rotate(-90, PIL.Image.NEAREST, expand=1))
    for i, page in enumerate(deck[1:]):


        if (i % 2):
            first, last = splitHorizontal(page)
            fromStart.append(first.rotate(90, PIL.Image.NEAREST, expand=1))
            fromBack.append(last.rotate(90, PIL.Image.NEAREST, expand=1))
        else:
            first, last = splitHorizontal(page)
            fromStart.append(first.rotate(-90, PIL.Image.NEAREST, expand=1))
            fromBack.append(last.rotate(-90, PIL.Image.NEAREST, expand=1))

    fromBack.reverse()
    # orderdDeck = fromStart.extend(fromBack)  # make sure reverse is right, pages are still rotated
    fromStart.extend(fromBack)
    # pdf_bytes = img2pdf.convert(orderdDeck)

    # for i, page in enumerate(fromStart):
    #    page.save(f"./out/page{str(i)}.jpg")
    fromStart[0].save(f'{name}', save_all=True, append_images=fromStart[1:])

    # file = open(f"{name}.pdf", "wb")

    # writing pdf files with chunks
    # file.write(pdf_bytes)


if __name__ == '__main__':


    if len(argv) == 2:
        path = Path(argv[1])
    else:
        print("Program can only have one input. \nExample: python3 zineUnwind.py target")
        exit(1)

    assert path.exists()

    if path.is_dir():
        for file in path.iterdir():
            # spawn a new thread for each thing
            if file.suffix == '.pdf':
                readzine(file)

    else:
        if path.suffix == 'pdf':
            readzine(path)

# triple check zine formatting
# super slow
# add tests?
# add cli
# add auto install
# add md
