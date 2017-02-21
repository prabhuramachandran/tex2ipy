import argparse

import nbformat
from nbformat.v4 import new_notebook

from .tex2cells import Tex2Cells


def get_tex2cells_subclass(fp, fname):
    """Return a subclass of Tex2Cells defined in the given file and filename.

    Parameters
    ----------

    fp: :file: Input file object.
    fname: :str: Filename of file.
    """
    ns = {}
    exec(compile(fp.read(), fname, 'exec'), ns)
    converter = None
    for k, v in ns.items():
        if type(v) is type and issubclass(v, Tex2Cells) \
           and v is not Tex2Cells:
            converter = v
            break
    return converter


def tex2ipy(code, cls=Tex2Cells):
    t2c = cls(code)
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
    parser.add_argument(
        "-c", "--converter", action="store", dest="converter", default='',
        help="Path to a Python file which defines a subclass of Tex2Cells."
    )
    args = parser.parse_args(args)
    converter = None
    if len(args.converter) > 0:
        with open(args.converter) as fp:
            converter = get_tex2cells_subclass(fp, args.converter)
    if converter is None:
        converter = Tex2Cells

    with open(args.input[0]) as f:
        code = f.read()
    nb = tex2ipy(code, converter)
    with open(args.output[0], 'w') as f:
        nbformat.write(nb, f)


if __name__ == '__main__':
    main()
