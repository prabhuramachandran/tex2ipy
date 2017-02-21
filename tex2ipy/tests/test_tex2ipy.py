from textwrap import dedent
from tex2ipy.cli import tex2ipy, main


DOCUMENT = dedent(r"""
\documentclass[14pt, compress]{beamer}
\begin{document}
\begin{frame}
\frametitle{Foo}
Hello world
\end{frame}
\end{document}
""")


def test_tex2ipy_should_make_notebook():
    # Given
    # When
    nb = tex2ipy(DOCUMENT)

    # Then
    cells = nb['cells']
    assert len(cells) == 1
    src = cells[0]['source']
    assert src[0] == '## Foo\n'
    assert src[1] == 'Hello world'

    md = nb['metadata']
    assert sorted(md.keys()) == ['celltoolbar', 'language', 'livereveal']


def test_main(tmpdir):
    # Given
    src = tmpdir.join('test.tex')
    src.write(DOCUMENT)
    dest = tmpdir.join('test.ipynb')

    # When
    main(args=[str(src), str(dest)])

    # Then
    assert dest.check(file=1)
