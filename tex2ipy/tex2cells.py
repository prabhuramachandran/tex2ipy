from glob import glob
import os

from TexSoup import TexSoup, TexNode


def get_all_listings(code):
    result = []
    start = (r'\begin{lstlisting}', r'\begin{verbatim}')
    end = (r'\end{lstlisting}', r'\end{verbatim}')
    in_listing = False
    for line in code.splitlines():
        llstrip = line.lstrip()
        if llstrip.startswith(start):
            in_listing = True
            block = []
            continue
        elif llstrip.endswith(end):
            in_listing = False
            result.append(block)
            continue
        elif in_listing:
            block.append(line + '\n')

    return result


class Tex2Cells(object):
    def __init__(self, code):
        self.soup = TexSoup(code)
        self.listings = get_all_listings(code)
        self._listings_count = 0
        self.info = {}
        self.cells = []
        self.current = None

    def parse(self):
        """Parse the given TeX code and return suitable IPython cells.
        """
        doc = self.soup.find('document')
        self._walk(doc)
        return self.cells

    def _walk(self, node):
        if isinstance(node, TexNode):
            name = node.name.replace('*', '_star')
            method_name = '_handle_%s' % name
            method = getattr(self, method_name, None)
            skip_children = False
            if method:
                skip_children = method(node)
            else:
                print("No handler for ", node.name)
            if not skip_children:
                for element in node.contents:
                    self._walk(element)
        elif isinstance(node, str):
            if self.current is not None:
                self._handle_str(node)

    def _make_cell(self, cell_type='markdown', slide_type='slide'):
        slideshow = dict(slide_type=slide_type)
        if cell_type == 'markdown':
            self.current = dict(
                cell_type=cell_type,
                metadata=dict(slideshow=slideshow),
                source=[]
            )
        elif cell_type == 'code':
            self.current = dict(
                cell_type=cell_type,
                metadata=dict(slideshow=slideshow),
                source=[],
                outputs=[],
                execution_count=None
            )
            pass
        self.cells.append(self.current)

    def _handle_frame(self, node):
        self._make_cell(cell_type='markdown', slide_type='slide')

    def _handle_frametitle(self, node):
        self.current['source'].append(
            '## %s\n' % node.string
        )
        return True

    def _handle_str(self, node):
        src = self.current['source']
        src.append(node + '\n')

    def _handle_itemize(self, node):
        pass

    def _handle_enumerate(self, node):
        pass

    def _handle_item(self, node):
        src = self.current['source']
        if node.parent.name == 'itemize':
            src.append('* ')
        elif node.parent.name == 'enumerate':
            src.append('1. ')
        else:
            print("\item has Unknown parent node", node.parent.name)

    def _handle_lstlisting(self, node):
        self._make_cell(cell_type='code', slide_type='-')
        src = []
        code = self.listings[self._listings_count]
        START = ('In []:', '...:', '....:', '.....:')
        for line in code:
            llstrip = line.lstrip()
            if llstrip.startswith(START):
                idx = line.index(':') + 2
                src.append(line[idx:])
            elif llstrip.startswith('Out []:'):
                self.current['source'] = src
                self._make_cell(cell_type='code', slide_type='-')
                src = []
        if len(src) > 0:
            self.current['source'] = src

        self._listings_count += 1

        siblings = list(node.parent.contents)
        s_repr = list(repr(x) for x in siblings)
        index = s_repr.index(repr(node))
        if index != len(siblings) - 1:
            self._handle_frame(node)
            self.current['metadata']['slideshow']['slide_type'] = '-'
            for item in siblings[index+1:]:
                self._walk(item)
        return True

    _handle_verbatim = _handle_lstlisting

    def _handle_title(self, node):
        self.info[node.name] = list(node.contents)[-1]
        return True

    _handle_author = _handle_title
    _handle_institute = _handle_title
    _handle_date = _handle_title
    _handle_logo = _handle_title

    def _handle_titlepage(self, node):
        src = self.current['source']
        src.append('# %s' % self.info.get('title', 'Title'))
        src.append('\n')
        src.append('**%s**' % self.info.get('author', 'Author'))
        src.append('\n')
        src.append('**%s**' % self.info.get('date', 'Date'))
        src.append('\n')

    def _handle_pgfimage(self, node):
        src = self.current['source']
        data = list(node.contents)
        image = data[-1]
        formats = ('png', 'jpg', 'svg', 'gif', 'jpeg', 'bmp')
        if not os.path.exists(image):
            for f in glob(image+'*'):
                if f.lower().endswith(formats):
                    image = f
                    break
        src.append('<img src="%s">\n' % image)
        return True

    _handle_includegraphics = _handle_pgfimage

    def _handle_url(self, node):
        src = self.current['source']
        src.append('%s \n' % node.string)

    def _handle_document(self, node):
        self.cells = []
        self.current = None

    def _ignore(self, node):
        return True

    _handle_vspace = _ignore
    _handle_hspace = _ignore
    _handle_vspace_star = _ignore
    _handle_hspace_star = _ignore
