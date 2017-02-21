import argparse
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


def main(args=None):
    parser = argparse.ArgumentParser(
        "Convert LaTeX beamer slides to IPython notebooks + RISE"
    )
    parser.add_argument("input", nargs=1, help="Input file (.tex)")
    parser.add_argument("output", nargs=1, help="Output file (.ipynb)")
    args = parser.parse_args(args)
    with open(args.input[0]) as f:
        code = f.read()
    nb = tex2ipy(code)
    with open(args.output[0], 'w') as f:
        nbformat.write(nb, f)


if __name__ == '__main__':
    main()
