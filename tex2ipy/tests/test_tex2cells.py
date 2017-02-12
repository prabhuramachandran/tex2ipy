from textwrap import dedent
import sys
from os.path import dirname

BASE_DIR = dirname(dirname(dirname(__file__)))
sys.path.append(BASE_DIR)

from tex2ipy.tex2cells import Tex2Cells, get_all_listings


def test_get_all_listings():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{lstlisting}
    In []: 1
    Out []: 1
    In []: print 1
    \end{lstlisting}

    \begin{itemize}
    \item blah
    \end{itemize}

    \begin{verbatim}
    In []: 2
    Out []: 2
    In []: print 2
    \end{verbatim}

    \end{document}
    """)

    # When
    lst = get_all_listings(doc)

    # Then
    assert len(lst) == 2
    expect = ['In []: 1\n', 'Out []: 1\n', 'In []: print 1\n']
    assert lst[0] == expect

    expect = ['In []: 2\n', 'Out []: 2\n', 'In []: print 2\n']
    assert lst[1] == expect


def test_lstlisting_with_output_should_make_multiple_cells():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{lstlisting}
    In []: 1
    Out []: 1
    In []: print 1
    \end{lstlisting}
    \end{document}
    """)
    t2c = Tex2Cells(doc)

    # When
    cells = t2c.parse()

    # Then
    assert len(cells) == 2
    assert cells[0]['source'] == ['1\n']
    assert cells[1]['source'] == ['print 1\n']
    assert cells[0]['metadata']['slideshow']['slide_type'] == '-'
    assert cells[1]['metadata']['slideshow']['slide_type'] == '-'


def test_titlepage_is_created():
    # Given
    doc = dedent(r"""
    \documentclass[14pt, compress]{beamer}

    \begin{document}
    \title{foo}
    \author{blah}

    \begin{frame}
    \titlepage
    \end{frame}

    \begin{frame}
    \frametitle{Foo}
    Hello world
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 2


if __name__ == '__main__':
    main()
