from textwrap import dedent

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
    assert cells[0]['cell_type'] == 'code'
    assert cells[1]['cell_type'] == 'code'
    assert cells[0]['metadata']['slideshow']['slide_type'] == '-'
    assert cells[1]['metadata']['slideshow']['slide_type'] == '-'


def test_titlepage_is_created():
    # Given
    doc = dedent(r"""
    \documentclass[14pt, compress]{beamer}

    \begin{document}
    \title{foo}
    \author{blah}
    \date{date}
    \institute{Institute}

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
    assert cells[0]['cell_type'] == 'markdown'
    src = cells[0]['source']
    assert src[0] == '# foo\n'
    assert src[1] == '\n'
    assert src[2] == '**blah**\n'
    assert src[3] == '\n'
    assert src[4] == '**Institute**\n'
    assert src[5] == '\n'
    assert src[6] == '**date**\n'

    assert cells[1]['cell_type'] == 'markdown'
    src = cells[1]['source']
    assert src[0] == "## Foo\n"
    assert src[1] == "Hello world\n"


def test_itemize_enumerate_works():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \frametitle{Title}
       \begin{itemize}
        \item item 1
        \item item 2
       \end{itemize}
       \begin{enumerate}
        \item aa
        \item bb
       \end{enumerate}
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 1
    assert cells[0]['cell_type'] == 'markdown'
    src = cells[0]['source']
    print(src)
    assert src[0] == '## Title\n'
    assert src[1] == '* '
    assert src[2] == 'item 1\n'
    assert src[3] == '* '
    assert src[4] == 'item 2\n'
    assert src[5] == '1. '
    assert src[6] == 'aa\n'
    assert src[7] == '1. '
    assert src[8] == 'bb\n'


def test_images_should_work():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \frametitle{Title}
    \pgfimage[height=1cm,width=1cm]{images/img1.png}
    \includegraphics[height=1cm,width=1cm]{images/img2.jpg}
    \url{www.python.org}
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 1
    assert cells[0]['cell_type'] == 'markdown'
    src = cells[0]['source']
    print(src)
    assert src[0] == '## Title\n'
    assert src[1] == '<img src="images/img1.png">\n'
    assert src[2] == '<img src="images/img2.jpg">\n'
    assert src[3] == '<www.python.org>\n'


def test_space_should_be_ignored():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \frametitle{Title}
    \hspace{0.1in} hello
    \hspace*{0.1in} world
    \vspace{0.1in} hola
    \vspace*{0.1in} namaste
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 1
    assert cells[0]['cell_type'] == 'markdown'
    src = cells[0]['source']
    assert len(src) == 5
    print(src)
    assert src[0] == '## Title\n'
    assert src[1] == ' hello\n'
    assert src[2] == ' world\n'
    assert src[3] == ' hola\n'
    assert src[4] == ' namaste\n'
