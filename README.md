# Tex2IPython Notebook

[![Build Status](https://travis-ci.org/prabhuramachandran/tex2ipy.svg?branch=master)](https://travis-ci.org/prabhuramachandran/tex2ipy)
[![codecov](https://codecov.io/gh/prabhuramachandran/tex2ipy/branch/master/graph/badge.svg)](https://codecov.io/gh/prabhuramachandran/tex2ipy)


This package makes it easy to convert a LaTeX file (currently) typically using
the beamer package into an IPython notebook with
[RISE](https://github.com/damianavila/RISE).

To use the package, simply run:

    $ tex2ipy talk.tex talk.ipynb


This does not attempt to completely cover all TeX macros. Bulk of the basics
should work hopefully covering 90% of the basic macros.

## Customization

If you wish to support more macros or your own, you can subclass `Tex2Cells`
and add any handlers for your own macros. Let us say you add additional
methods to your subclass and in a file called `customize.py` you can use this
file as follows:

    $ tex2ipy -c customize.py talk.tex talk.ipynb

This will use your customizations for the conversion.
