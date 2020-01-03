import os
import re
from subprocess import call

from bs4 import NavigableString

preamble = '''
\\documentclass[a4paper]{book}
\\usepackage[english]{babel}
\\usepackage{graphicx}
\\usepackage{listings}
\\usepackage[a4paper, margin=3cm]{geometry}
\\setlength{\\parskip}{5pt}%
\\setlength{\\parindent}{0.5cm}%
\\begin{document}
\\tableofcontents
\\pagebreak
'''


def data_type(element):
    return element['data-type']


def sanitize_lstlisting(text):
    return text.replace(u'\u00A9', '\\textcopyright\\')


def sanitize(text):
    t = text.strip()
    return (t if t.startswith(',') or t.startswith('.') else ' ' + t) \
        .replace('\\', '\\textbackslash\\') \
        .replace('$', '\\$') \
        .replace(u'\u00A9', '\\textcopyright\\') \
        .replace('&', '\\&') \
        .replace('\r', ' ') \
        .replace('\n', ' ') \
        .replace('_', '\\_') \
        .replace('{', '\\{') \
        .replace('}', '\\}') \
        .replace('>', '\\gt') \
        .replace('<', '\\lt')


class TexPrinter:

    def __init__(self, out_dir, out_file_name):
        self.out_dir = out_dir
        self.out_file_name = out_file_name
        self.out = None
        self.figure_id = 1

    def preamble(self):
        try:
            a = open(os.path.join(self.out_dir, self.out_file_name + '.tex'), 'w')
            a.write(preamble)
            self.out = a
            return a
        except IOError:
            print('Can\'t open ', self.out_file_name)
            exit(1)

    def finalize(self):
        self.out.write('\\end{document}')
        self.out.close()
        # should call pdflatex twice to generate toc and use it in second run
        call(['pdflatex', self.out.name])
        call(['pdflatex', self.out.name])

    def write_content(self, content):
        self.out.write('\n')
        self.decode_children(content)

    def decode(self, element, use_mono_font=True, sanitize_listing=False, end_with_space=True):
        name = element.name
        if isinstance(element, NavigableString):
            self.write_text(element, sanitize_listing, end_with_space)
        elif 'figure' == name:
            self.handle_figure(element)
        elif 'section' == name:
            self.handle_section(element)
        elif 'p' == name:
            self.handle_paragraph(element)
        elif 'div' == name:
            self.handle_div(element)
        elif 'span' == name:
            self.decode_children(element)
        elif 'em' == name:
            self.handle_em(element)
        elif 'i' == name:
            self.handle_italic(element)
        elif 'b' == name or 'strong' == name:
            self.handle_bold(element)
        elif 'a' == name:
            self.handle_a(element)
        elif 'blockquote' == name:
            self.handle_quotation(element)
        elif 'ul' == name:
            self.handle_list(element)
        elif 'li' == name:
            self.handle_list_item(element)
        elif 'br' == name:
            self.out.write('\n\n')
        elif 'code' == name:
            self.handle_code(element, sanitize_listing, use_mono_font)
        elif 'pre' == name:
            self.handle_pre(element)
        else:
            print(name, ' doesn''t have a handler')
        # element is NormalText, sanitize and write
        pass

    def handle_div(self, element):
        self.decode_children(element)

    def handle_code(self, element, sanitize_listing, use_mono_font):
        if use_mono_font:
            self.out.write('{\\ttfamily ')
        self.decode_children(element, sanitize_listing=sanitize_listing, end_with_space=False)
        if use_mono_font:
            self.out.write('}')

    def handle_pre(self, element):
        # if element.has_attr('data-code-language'):
        # self.out.write('\n\\begin[' + element['data-code-language'] + ']{lstlisting}\n')
        # else:
        self.out.write('\\ttfamily\n')
        self.out.write('\n\\begin{lstlisting}\n')
        self.decode_children(element, use_mono_font=False, sanitize_listing=True)
        self.out.write('\n\\end{lstlisting}\n')
        self.out.write('\\rmfamily\n')

    def handle_list_item(self, element):
        self.out.write('\n\\item ')
        self.decode_children(element)

    def handle_list(self, element):
        self.out.write('\n\\begin{itemize}\n')
        self.decode_children(element)
        self.out.write('\n\\end{itemize}\n')

    def handle_quotation(self, element):
        self.out.write('\n\\begin{quotation}\n')
        self.decode_children(element)
        self.out.write('\n\\end{quotation}\n')

    def handle_figure(self, element):
        figure_id_str = str(self.figure_id)
        self.out.write('\\begin{figure}\n')
        self.out.write('\\centering\n')
        self.out.write('\\includegraphics{test/' + element.find('img')['src'] + '}\n')
        self.figure_id += 1
        caption = None
        if element.div is not None:
            caption = re.sub('Figure\ \d+-\d+\.\s+', '', element.div.h6.text.strip())
        if caption is not None:
            self.out.write('\\caption{' + caption + '}\n')
        self.out.write('\\end{figure}\n')

    def handle_em(self, element):
        self.out.write('{\\em ')
        self.decode_children(element)
        self.out.write('}')

    def handle_a(self, element):
        self.out.write(' ' + sanitize(element.text) + ' ')

    # if element.has_attr('data-type'):
    #     if 'xref' == data_type(element):
    #         self.out.write(' ' + self.sanitize(element.text) + ' ')

    def handle_italic(self, element):
        self.out.write('{\\itshape ')
        self.decode_children(element)
        self.out.write('}')

    def handle_bold(self, element):
        self.out.write('{\\bfseries ')
        self.decode_children(element)
        self.out.write('}')

    def handle_paragraph(self, element):
        if element.has_attr('data-type'):
            self.handle_special_paragraph(element)
        else:
            self.out.write('\n')
            self.decode_children(element)
            self.out.write('\n\n')

    def handle_special_paragraph(self, element):
        paragraph_type = data_type(element)
        if 'subtitle' == paragraph_type:
            self.out.write('\\section*{')
            self.decode_children(element)
            self.out.write('}')
        elif 'attribution' == paragraph_type:
            self.out.write('\n' + element.text + '\n\n')
        else:
            print('Don''t know yet how handle:', paragraph_type)

    def handle_section(self, element):
        if element.has_attr('data-type'):
            section_type = data_type(element)
        else:
            section_type = None
        if element.has_attr('data-pdf-bookmark'):
            title = element['data-pdf-bookmark']
        else:
            title = 'None title'
        if 'chapter' == section_type:
            self.handle_chapter(element, title)
        elif 'titlepage' == section_type:
            self.handle_title_page(element, title)
        elif 'sect1' == section_type:
            self.out.write('\\section{' + title + '}\\label{sec:' + title.replace(' ', '_').lower() + '}\n')
        elif 'sect2' == section_type:
            self.out.write('\\subsection{' + title + '}')
        elif 'dedication' == section_type:
            self.out.write('\\section*{' + title + '}')
        elif 'index' == section_type:
            pass

        self.decode_children(element)

    def handle_chapter(self, element, title):
        _title = re.sub('Chapter\ \\d+\.\ ', '', title.strip())
        print('Extracted chapter title:', _title)
        self.out.write('\\chapter{' + _title + '}\n')

    def handle_title_page(self, element, title):
        self.out.write('\\chapter*{' + title.strip() + '}\n')

    def decode_children(self, element, use_mono_font=True, sanitize_listing=False, end_with_space=True):
        for child in element.children:
            self.decode(child, use_mono_font, sanitize_listing, end_with_space)

    def write_text(self, element, sanitize_listing=False, end_with_space=True):
        trimmed_text = sanitize_lstlisting(element) if sanitize_listing else sanitize(element)
        if len(trimmed_text) > 0:
            self.out.write(trimmed_text)
            if end_with_space and not sanitize_listing:
                self.out.write(' ')
