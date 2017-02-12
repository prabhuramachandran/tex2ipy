from textwrap import dedent
from tex2ipy.cli import tex2ipy


def test_tex2ipy_should_make_notebook():
    # Given
    doc = dedent(r"""
    \documentclass[14pt, compress]{beamer}
    \begin{document}
    \begin{frame}
    \frametitle{Foo}
    Hello world
    \end{frame}
    \end{document}
    """)

    # When
    nb = tex2ipy(doc)

    # Then
    cells = nb['cells']
    assert len(cells) == 1
    src = cells[0]['source']
    assert src[0] == '## Foo\n'
    assert src[1] == 'Hello world\n'

    md = nb['metadata']
    assert sorted(md.keys()) == ['celltoolbar', 'language', 'livereveal']
