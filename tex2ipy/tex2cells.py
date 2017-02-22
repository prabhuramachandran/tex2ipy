from glob import glob
import os
import re

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


def get_real_image_from_path(image_path):
    """Often images are provided without an extension, so we try to
    find a suitable one using glob.
    """
    formats = ('png', 'jpg', 'svg', 'gif', 'jpeg', 'bmp')
    image = image_path
    if not os.path.exists(image):
        for f in glob(image+'*'):
            if f.lower().endswith(formats):
                image = f
                break
    return image


def _replace_display_math(code):
    code = code.replace(r'\[', r'\begin{equation*}')
    return code.replace(r'\]', r'\end{equation*}')


def remove_comments(code):
    return re.sub('(?<!\\\\)%.*$', '', code, flags=re.M)


class Tex2Cells(object):
    def __init__(self, code):
        code = _replace_display_math(code)
        code = remove_comments(code)
        self.soup = TexSoup(code)
        self.listings = get_all_listings(code)
        self._listings_count = 0
        self._in_equation = False
        self.info = {}
        self.cells = []
        self.current = None

    def _parse_titlepage(self):
        nodes = ('title', 'author', 'institute', 'date', 'logo')
        for node in nodes:
            for elem in self.soup.find_all(node):
                method = getattr(self, '_handle_' + node)
                method(elem)

    def parse(self):
        """Parse the given TeX code and return suitable IPython cells.
        """
        self._parse_titlepage()
        doc = self.soup.find('document')
        self._walk(doc)
        return self.cells

    def _walk(self, node):
        if isinstance(node, TexNode):
            if self._in_equation:
                self._handle_str(node)
            else:
                name = node.name.replace('*', '_star')
                method_name = '_handle_%s' % name
                method = getattr(self, method_name, None)
                skip_children = False
                if method:
                    skip_children = method(node)
                else:
                    self._handle_unknown(node)
                if not skip_children:
                    for element in node.contents:
                        self._walk(element)
        elif isinstance(node, str):  # pragma: no branch
            if self.current is not None:  # pragma: no branch
                self._handle_str(node)

    def _make_cell(self, cell_type='markdown', slide_type='slide'):
        slideshow = dict(slide_type=slide_type)
        if cell_type == 'markdown':
            self.current = dict(
                cell_type=cell_type,
                metadata=dict(slideshow=slideshow),
                source=[]
            )
        else:
            self.current = dict(
                cell_type=cell_type,
                metadata=dict(slideshow=slideshow),
                source=[],
                outputs=[],
                execution_count=None
            )
        self.cells.append(self.current)

    def _handle_block(self, node):
        src = self.current['source']
        src.append('### %s\n' % node.args[0])
        src.append('')
        return False

    def _handle_equation(self, node):
        src = self.current['source']
        src.append('$$\n')
        src.append(''.join(str(x) for x in node.contents))
        src.append('$$\n')
        return True

    _handle_equation_star = _handle_equation
    _handle_align = _handle_equation
    _handle_align_star = _handle_equation

    def _handle_emph(self, node):
        src = self.current['source']
        if len(src) == 0:
            src.append('')
        src[-1] += '*%s* ' % node.string
        return True

    def _handle_frame(self, node):
        self._make_cell(cell_type='markdown', slide_type='slide')

    def _handle_frametitle(self, node):
        src = self.current['source']
        src.append('## ')
        for item in node.contents:
            self._walk(item)

        src[-1] += '\n'
        src.append('')

        return True

    def _handle_str(self, node):
        src = self.current['source']
        data = str(node)
        if len(src) == 0:
            src.append('')
        if self._in_equation:
            if '$' in data:
                self._in_equation = False
                src[-1] += data
            else:
                src[-1] += data
        else:
            if '$' in data:
                self._in_equation = True
                src[-1] += data
            else:
                src[-1] += data

    def _handle_item(self, node):
        src = self.current['source']
        if len(src) > 0:
            src[-1] += '\n'
        if node.parent.name == 'itemize':
            src.append('* ')
        elif node.parent.name == 'enumerate':  # pragma: no branch
            src.append('1. ')
        else:  # pragma: no cover
            print(r"\item has unknown parent node", node.parent.name)

    def _handle_itemize(self, node):
        for item in node.contents:
            self._walk(item)
        src = self.current['source']
        if len(src) > 0:  # pragma: no branch
            if not src[-1].endswith('\n'):
                src[-1] += '\n'
        return True

    _handle_enumerate = _handle_itemize

    def _handle_lstlisting(self, node):
        cell = self.current
        if cell is not None and len(cell['source']) == 0:
            # Empty cell already exists, just set its type.
            cell['cell_type'] = 'code'
            cell['execution_count'] = None
            cell['outputs'] = []
        else:
            self._make_cell(cell_type='code', slide_type='-')
        del cell
        src = []
        code = self.listings[self._listings_count]
        START = ('In []:', '...:', '....:', '.....:')
        for line in code:
            llstrip = line.lstrip()
            if llstrip.startswith(START):
                idx = line.index(':') + 2
                src.append(line[idx:])
            elif llstrip.startswith('Out[]:'):
                self.current['source'] = src
                self._make_cell(cell_type='code', slide_type='-')
                src = []
            else:
                src.append(line)
        if len(src) > 0:
            self.current['source'] = src

        self._listings_count += 1

        # If there is an itemize after the lstlisting, it will add source
        # elements into the code cell.
        siblings = list(node.parent.contents)
        s_repr = list(repr(x) for x in siblings)
        index = s_repr.index(repr(node))
        if index < (len(siblings) - 1):
            self._make_cell(slide_type='-')
        return True

    _handle_verbatim = _handle_lstlisting

    def _handle_ldots(self, node):
        self._handle_str('...')
        return True

    def _handle_pause(self, node):
        src = self.current['source']
        if len(src) == 0:
            # No content in the current cell.
            self.current['metadata']['slideshow']['slide_type'] = 'fragment'
        else:
            self._make_cell(slide_type='fragment')

    def _handle_textbf(self, node):
        src = self.current['source']
        if len(src) == 0:
            src.append('')

        src[-1] += '**%s** ' % node.string
        return True

    def _handle_texttt(self, node):
        src = self.current['source']
        if len(src) == 0:
            src.append('')
        src[-1] += '`%s` ' % node.string
        return True

    _handle_lstinline = _handle_texttt

    def _handle_title(self, node):
        self.info[node.name] = list(node.contents)[-1]
        return True

    _handle_author = _handle_title
    _handle_institute = _handle_title
    _handle_date = _handle_title
    _handle_logo = _handle_title

    def _handle_titlepage(self, node):
        src = self.current['source']
        src.append('# %s\n' % self.info.get('title', 'Title'))
        src.append('\n')
        src.append('**%s**\n' % self.info.get('author', 'Author'))
        src.append('\n')
        src.append('**%s**\n' % self.info.get('institute', 'Institute'))
        src.append('\n')
        src.append('**%s**\n' % self.info.get('date', 'Date'))
        src.append('\n')

    def _handle_pgfimage(self, node):
        src = self.current['source']
        data = list(node.contents)
        image = get_real_image_from_path(data[-1])
        src.append('<img src="%s"/>\n' % image)
        return True

    _handle_includegraphics = _handle_pgfimage

    def _handle_movie(self, node):
        src = self.current['source']
        data = list(node.contents)
        movie = data[-1]
        src.append('<div align="center">\n')
        src.append('<video loop controls src="%s"/>\n' % movie)
        src.append('</div>\n')
        return True

    def _handle_url(self, node):
        src = self.current['source']
        src.append('<%s> ' % node.string)
        return True

    def _handle_quote(self, node):
        src = self.current['source']
        for line in node.contents:
            src.append('> %s\n' % line)
        return True

    def _handle_document(self, node):
        self.cells = []
        self.current = None

    def _handle_hrule(self, node):
        self.current['source'].append('\n----\n')

    def _handle_section(self, node):
        self._make_cell()
        self.current['source'].append('## %s\n' % node.string)
        return True

    def _handle_subsection(self, node):
        self._make_cell()
        self.current['source'].append('### %s\n' % node.string)
        return True

    def _handle_subsubsection(self, node):
        self._make_cell()
        self.current['source'].append('#### %s\n' % node.string)
        return True

    def _ignore(self, node):
        return False

    _handle_center = _ignore
    _handle_figure = _ignore
    _handle_minipage = _ignore
    _handle_centering = _ignore
    _handle_tiny = _ignore
    _handle_footnotesize = _ignore
    _handle_small = _ignore
    _handle_large = _ignore
    _handle_Large = _ignore
    _handle_huge = _ignore
    _handle_Huge = _ignore

    def _ignore_children(self, node):
        return True

    _handle_vspace = _ignore_children
    _handle_hspace = _ignore_children
    _handle_vspace_star = _ignore_children
    _handle_hspace_star = _ignore_children

    def _handle_unknown(self, node):
        src = self.current['source']
        if len(src) == 0:
            src.append('')

        src[-1] += '\\%s ' % node.name
        print("No handler for ", node.name)

    ####################################################################
    # The following are not generic LaTeX commands but specific to
    # the author's macros.
    _handle_media = _handle_movie

    def _handle_BackgroundPictureWidth(self, node):
        data = list(node.contents)
        if os.path.basename(data[-1]) in ('blank', 'blank.png'):
            return True
        self._make_cell(slide_type='slide')
        src = self.current['source']
        image = get_real_image_from_path(data[-1])
        src.append('<img width="100%%" src="%s"/>\n' % image)
        return True

    def _handle_BackgroundPictureHeight(self, node):
        data = list(node.contents)
        if os.path.basename(data[-1]) in ('blank', 'blank.png'):
            return True
        self._make_cell(slide_type='slide')
        src = self.current['source']
        image = get_real_image_from_path(data[-1])
        src.append('<img height="100%%" src="%s"/>\n' % image)
        return True

    _handle_BackgroundPicture = _handle_BackgroundPictureWidth
    _handle_typ = _handle_lstinline
    _handle_kwrd = _handle_lstinline
