import sys
import nbformat
from nbformat.v4 import new_notebook

from .tex2cells import Tex2Cells


def tex2ipy(code):
    t2c = Tex2Cells(code)
    cells = t2c.parse()
    livereveal = dict(
        transition='none',
        scroll=True,
        controls=True,
        slideNumber=True,
        help=True
    )
    md = dict(
        language='python',
        celltoolbar='Slideshow',
        livereveal=livereveal
    )
    nb = new_notebook(
        metadata=md,
        cells=cells
    )
    return nb


def main():
    code = open(sys.argv[1]).read()
    nb = tex2ipy(code)
    nbformat.write(nb, open(sys.argv[2], 'w'))


if __name__ == '__main__':
    main()
