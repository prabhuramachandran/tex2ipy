from io import StringIO
from textwrap import dedent

import nbformat

from tex2ipy.tex2cells import Tex2Cells
from tex2ipy.cli import tex2ipy, main, get_tex2cells_subclass


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


def test_get_tex2cells_subclass():
    # Given
    code = dedent("""
    from tex2ipy.tex2cells import Tex2Cells
    class MyConverter(Tex2Cells):
        pass
    """)
    stream = StringIO(code)

    # When
    cls = get_tex2cells_subclass(stream, 'test.py')

    # Then
    assert issubclass(cls, Tex2Cells)
    assert cls.__name__ == 'MyConverter'
    assert cls != Tex2Cells


def test_get_tex2cells_subclass_with_no_code_returns_none():
    # Given
    stream = StringIO('')

    # When
    cls = get_tex2cells_subclass(stream, 'test.py')

    # Then
    assert cls is None


def test_main_with_no_options(tmpdir):
    # Given
    src = tmpdir.join('test.tex')
    src.write(DOCUMENT)
    dest = tmpdir.join('test.ipynb')

    # When
    main(args=[str(src), str(dest)])

    # Then
    assert dest.check(file=1)


def test_main_with_options(tmpdir):
    # Given
    code = dedent("""
    from tex2ipy.tex2cells import Tex2Cells
    class Converter(Tex2Cells):
        def _handle_frame(self, node):
            super(Converter, self)._handle_frame(node)
            self.current['source'].append('## Overloaded\\n')
    """)
    convert = tmpdir.join('extra.py')
    convert.write(code)
    src = tmpdir.join('test.tex')
    src.write(DOCUMENT)
    dest = tmpdir.join('test.ipynb')

    # When
    main(args=[str(src), str(dest), '-c', str(convert)])

    # Then
    assert dest.check(file=1)
    nb = nbformat.read(str(dest), 4)

    src = nb.cells[0].source.splitlines()
    assert src[0] == '## Overloaded'
    assert src[1] == '## Foo'
