import os
from textwrap import dedent

from tex2ipy.tex2cells import Tex2Cells, get_all_listings, \
    get_real_image_from_path, remove_comments


def test_get_all_listings():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{lstlisting}
    In []: 1
    Out[]: 1
    In []: print 1
    \end{lstlisting}

    \begin{itemize}
    \item blah
    \end{itemize}

    \begin{verbatim}
    In []: 2
    Out[]: 2
    In []: print 2
    \end{verbatim}

    \end{document}
    """)

    # When
    lst = get_all_listings(doc)

    # Then
    assert len(lst) == 2
    expect = ['In []: 1\n', 'Out[]: 1\n', 'In []: print 1\n']
    assert lst[0] == expect

    expect = ['In []: 2\n', 'Out[]: 2\n', 'In []: print 2\n']
    assert lst[1] == expect


def test_get_real_image_from_path(tmpdir):
    # Given a path that exists, check if that image path is given.
    img = tmpdir.join('image.png')
    img.write('')
    img_path = str(img)
    image = get_real_image_from_path(img_path)
    assert image == img_path
    img.remove()

    for ext in ('.png', '.PNG', '.jpg', '.JPEG', '.SVG', '.gif', '.BMP'):
        img = tmpdir.join('image' + ext)
        img.write('')
        img_path = str(img)
        path = os.path.splitext(img_path)[0]
        image = get_real_image_from_path(path)
        assert image == img_path
        img.remove()

    # Case when the image doesn't exist and it is not supported.
    img = tmpdir.join('image.xpm')
    img.write('')
    img_path = str(img)
    path = os.path.splitext(img_path)[0]
    image = get_real_image_from_path(path)
    assert image == path
    img.remove()


def test_remove_comments():
    # Given
    doc = dedent(r"""
    hello %world
    world % \alpha_beta
    % \item foo
    \emph{\%s} is correct
    """)

    # When
    doc = remove_comments(doc)

    # Then
    expect = '\nhello \nworld \n\n\emph{\\%s} is correct\n'
    assert doc == expect


def test_lstlisting_with_output_should_make_multiple_cells():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{lstlisting}
    In []: 1
    Out[]: 1
    In []: 1+1
    Out[]: 2
    \end{lstlisting}
    \end{document}
    """)
    t2c = Tex2Cells(doc)

    # When
    cells = t2c.parse()

    # Then
    assert len(cells) == 3
    assert cells[0]['source'] == ['1\n']
    assert cells[0]['cell_type'] == 'code'
    assert cells[0]['metadata']['slideshow']['slide_type'] == '-'
    assert cells[1]['source'] == ['1+1\n']
    assert cells[1]['cell_type'] == 'code'
    assert cells[1]['metadata']['slideshow']['slide_type'] == '-'


def test_multiple_lstlistings():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \begin{lstlisting}
    In []: 1
    \end{lstlisting}
    \begin{itemize}
    \item blah
    \end{itemize}
    \begin{verbatim}
    In []: 2
    print(2)
    >>> print('hello')
    \end{verbatim}
    \end{frame}
    \end{document}
    """)
    t2c = Tex2Cells(doc)

    # When
    cells = t2c.parse()

    # Then
    assert len(cells) == 3
    assert cells[0]['source'] == ['1\n']
    assert cells[0]['cell_type'] == 'code'
    assert cells[0]['metadata']['slideshow']['slide_type'] == 'slide'

    assert cells[1]['source'] == ['* blah\n']
    assert cells[1]['cell_type'] == 'markdown'
    assert cells[1]['metadata']['slideshow']['slide_type'] == '-'

    assert cells[2]['source'] == ['2\n', 'print(2)\n', ">>> print('hello')\n"]
    assert cells[2]['cell_type'] == 'code'
    assert cells[2]['metadata']['slideshow']['slide_type'] == '-'


def test_lstlistings_inside_itemize():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \begin{itemize}
    \item item1
    \begin{lstlisting}
    In []: 1
    \end{lstlisting}
    \item item2
    \begin{verbatim}
    print(2)
    \end{verbatim}
    \end{itemize}
    \end{frame}
    \end{document}
    """)
    t2c = Tex2Cells(doc)

    # When
    cells = t2c.parse()

    # Then
    assert len(cells) == 4
    assert cells[0]['source'] == ['* item1']
    assert cells[0]['cell_type'] == 'markdown'
    assert cells[0]['metadata']['slideshow']['slide_type'] == 'slide'

    assert cells[1]['source'] == ['1\n']
    assert cells[1]['cell_type'] == 'code'
    assert cells[1]['metadata']['slideshow']['slide_type'] == '-'

    assert cells[2]['source'] == ['* item2']
    assert cells[2]['cell_type'] == 'markdown'
    assert cells[2]['metadata']['slideshow']['slide_type'] == '-'

    assert cells[3]['source'] == ['print(2)\n']
    assert cells[3]['cell_type'] == 'code'
    assert cells[3]['metadata']['slideshow']['slide_type'] == '-'


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
    assert src[1] == "Hello world"


def test_titlepage_is_created_when_title_is_outside_document():
    # Given
    doc = dedent(r"""
    \documentclass[14pt, compress]{beamer}
    \title{foo}
    \author{blah}
    \date{date}
    \begin{document}
    \begin{frame}
    \titlepage
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
    assert src[0] == '# foo\n'
    assert src[1] == '\n'
    assert src[2] == '**blah**\n'
    assert src[3] == '\n'
    assert src[4] == '**Institute**\n'
    assert src[5] == '\n'
    assert src[6] == '**date**\n'


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
    hello
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
    assert src[1] == '\n'
    assert src[2] == '* item 1\n'
    assert src[3] == '* item 2\n\n'
    assert src[4] == '1. aa\n'
    assert src[5] == '1. bb\nhello'


def test_images_should_work_figure_ignored():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \frametitle{Title}
    \begin{figure}
    \pgfimage[height=1cm,width=1cm]{images/img1.png}
    \end{figure}
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
    assert src[1] == ''
    assert src[2] == '<img src="images/img1.png"/>\n'
    assert src[3] == '<img src="images/img2.jpg"/>\n'
    assert src[4] == '<www.python.org> '


def test_movie_env_works():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \movie[width=9cm, height=5cm]{}{movies/movie.mp4}
    \media{poster.png}{movies/movie.mp4}
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
    assert src[0] == '<div align="center">\n'
    assert src[1] == '<video loop controls src="movies/movie.mp4"/>\n'
    assert src[2] == '</div>\n'
    assert src[3] == '<div align="center">\n'
    assert src[4] == '<video loop controls src="movies/movie.mp4"/>\n'
    assert src[5] == '</div>\n'


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
    assert len(src) == 2
    print(src)
    assert src[0] == '## Title\n'
    assert src[1] == ' hello world hola namaste'


def test_quote_works_center_ignored_hrule_works():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \begin{center}
    \begin{quote}
    To do
    or not to do.
    \end{quote}
    \hrule
    \end{center}
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
    assert len(src) == 3
    print(src)
    assert src[0] == '> To do\n'
    assert src[1] == '> or not to do.\n'
    assert src[2] == '\n----\n'


def test_document_sections():
    # Given
    doc = dedent(r"""
    \begin{document}
    \section{Introduction}
    \subsection{Motivation}
    \subsubsection{Blah}
    \section{Methods}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 4
    assert cells[0]['cell_type'] == 'markdown'
    assert cells[0]['source'] == ['## Introduction\n']
    assert cells[1]['cell_type'] == 'markdown'
    assert cells[1]['source'] == ['### Motivation\n']
    assert cells[2]['cell_type'] == 'markdown'
    assert cells[2]['source'] == ['#### Blah\n']
    assert cells[3]['cell_type'] == 'markdown'
    assert cells[3]['source'] == ['## Methods\n']


def test_minipage_is_ignored():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \begin{minipage}
    hello world
    \end{minipage}
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 1
    assert cells[0]['cell_type'] == 'markdown'
    assert cells[0]['source'] == ['hello world']


def test_inline_equations():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    $\int f(x) dx$
    \begin{itemize}
    \item hello $\alpha + \frac{1}{2} \beta_{\gamma}$ world
    \end{itemize}
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
    expect = [
        r'$\int f(x) dx$' + '\n',
        r'* hello $\alpha + \frac{1}{2}\beta_{\gamma}$ world' + '\n'
    ]
    assert src == expect


def test_equations():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \begin{equation}
    \alpha + \frac{1}{2} \beta_1
    \end{equation}
    \begin{equation*}
    \beta = \gamma
    \end{equation*}
    \begin{align}
    \beta = \gamma
    \end{align}
    \begin{align*}
    \beta = \gamma
    \end{align*}
    \[v_\theta = \frac{\Gamma}{2\pi r}\]
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
    assert src[0] == '$$\n'
    assert src[1] == r'\alpha + \frac{1}{2}\beta_1'
    assert src[2] == '$$\n'
    assert src[3] == '$$\n'
    assert src[4] == r'\beta = \gamma'
    assert src[5] == '$$\n'
    assert src[6] == '$$\n'
    assert src[7] == r'\beta = \gamma'
    assert src[8] == '$$\n'
    assert src[9] == '$$\n'
    assert src[10] == r'\beta = \gamma'
    assert src[11] == '$$\n'
    assert src[12] == '$$\n'
    assert src[13] == r'v_\theta = \frac{\Gamma}{2\pi r}'
    assert src[14] == '$$\n'


def test_pause_should_add_new_fragment():
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \begin{itemize}
    \item item 1
    \pause
    \item item 2
    \end{itemize}
    \begin{lstlisting}
    print 1
    \end{lstlisting}
    \pause
    \begin{lstlisting}
    print 2
    \end{lstlisting}
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    print(cells)
    assert len(cells) == 4
    assert cells[0]['cell_type'] == 'markdown'
    assert cells[0]['metadata']['slideshow']['slide_type'] == 'slide'
    src = cells[0]['source']
    assert src[0] == '* item 1'

    assert cells[1]['cell_type'] == 'markdown'
    assert cells[1]['metadata']['slideshow']['slide_type'] == 'fragment'
    src = cells[1]['source']
    assert src[0] == '* item 2\n'

    assert cells[2]['cell_type'] == 'code'
    assert cells[2]['metadata']['slideshow']['slide_type'] == '-'
    src = cells[2]['source']
    assert src[0] == 'print 1\n'

    assert cells[3]['cell_type'] == 'code'
    assert cells[3]['metadata']['slideshow']['slide_type'] == 'fragment'
    src = cells[3]['source']
    assert src[0] == 'print 2\n'


def test_background_picture():
    # Given
    doc = dedent(r"""
    \begin{document}
    \BackgroundPicture{images/img1.png}
    \BackgroundPicture{images/blank}
    \BackgroundPictureWidth{images/img2.jpg}
    \BackgroundPictureWidth{images/blank}
    \BackgroundPictureHeight{images/img3.jpg}
    \BackgroundPictureHeight{images/blank}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 3

    assert cells[0]['cell_type'] == 'markdown'
    src = cells[0]['source']
    assert len(src) == 1
    assert src[0] == '<img width="100%" src="images/img1.png"/>\n'

    assert cells[1]['cell_type'] == 'markdown'
    src = cells[1]['source']
    assert len(src) == 1
    assert src[0] == '<img width="100%" src="images/img2.jpg"/>\n'

    assert cells[2]['cell_type'] == 'markdown'
    src = cells[2]['source']
    assert len(src) == 1
    assert src[0] == '<img height="100%" src="images/img3.jpg"/>\n'


def test_text_embellishments():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \textbf{bold} \emph{emph} \texttt{texttt} \lstinline{code}
    \typ{code} \kwrd{for} hello \ldots
    \end{frame}
    \begin{frame}
    \emph{emph}
    \end{frame}
    \begin{frame}
    \texttt{texttt}
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 3
    src = cells[0]['source']
    assert src[0] == '**bold** *emph* `texttt` `code` `code` `for`  hello ...'
    src = cells[1]['source']
    assert src[0] == '*emph* '
    src = cells[2]['source']
    assert src[0] == '`texttt` '


def test_unknown_macro_should_be_in_source():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \something
    \other{hello}
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 1
    src = cells[0]['source']
    assert src == ['\\something \\other hello']


def test_block_is_handled():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \begin{block}{Test block}
    Hello world
    \end{block}
    \end{frame}
    \end{document}
    """)

    # When
    t2c = Tex2Cells(doc)
    cells = t2c.parse()

    # Then
    assert len(cells) == 1
    src = cells[0]['source']
    assert src[0] == '### Test block\n'
    assert src[1] == 'Hello world'


def test_title_can_have_text_embellishments():
    # Given
    doc = dedent(r"""
    \begin{document}
    \begin{frame}
    \frametitle{\emph{emph} \textbf{bold} $\alpha$  \lstinline{print}}
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
    assert src[0] == '## *emph*  **bold**  $\\alpha$  `print` \n'
