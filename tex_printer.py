import os
import re
from subprocess import call

from bs4 import NavigableString


class TexPrinter:

    def __init__(self, out_dir, out_file_name):
        self.out_dir = out_dir
        self.out_file_name = out_file_name
        self.out = None
        self.figure_id = 1

    def preamble(self):
        try:
            a = open(os.path.join(self.out_dir, self.out_file_name + '.tex'), 'w')
            a.write(
                '''
                \\documentclass[a4paper]{book}
                \\usepackage{graphicx}
                \\usepackage[a4paper, inner=1.5cm, outer=3cm, top=2cm, bottom=3cm, bindingoffset=1cm]{geometry}
                \\begin{document}
                ''')
            self.out = a
            return a
        except IOError:
            print('Can\'t open ', self.out_file_name)
            exit(1)

    def finalize(self):
        self.out.write('\\end{document}')
        self.out.close()
        call(['pdflatex', self.out.name])

    def write_content(self, content):
        self.out.write('\n')
        self.decode_children(content)

    def decode(self, element):
        name = element.name
        if 'figure' == name:
            self.handle_figure(element)
        elif 'section' == name:
            self.handle_section(element)
        elif 'p' == name:
            self.handle_paragraph(element)
        elif 'div' == name:
            self.decode_children(element)
        elif 'span' == name:
            self.decode_children(element)
        elif 'em' == name:
            self.handle_em(element)
        elif 'i' == name:
            self.handle_italic(element)
        elif 'b' == name:
            self.handle_bold(element)
        elif 'a' == name:
            pass
        elif isinstance(element, NavigableString):
            self.write_text(element)
        else:
            print(name,' doesn''t have a handler')
        # element is NormalText, sanitize and write
        pass

    def handle_figure(self, element):
        figure_id_str = str(self.figure_id)
        self.out.write('\\begin{figure}\n')
        self.out.write('\\centering\n')
        self.out.write('\\includegraphics{' + element.find('img')['src'] + '}\n')
        self.figure_id += 1
        caption = None
        if element.div is not None:
            caption = re.sub('Figure\ \d+-\d+\.\s+','', element.div.h6.text.strip())
        if caption is not None:
            self.out.write('\\caption{' + caption + '}\n')
        self.out.write('\\end{figure}\n')

    def handle_em(self, element):
        self.out.write('{\\em ')
        self.decode_children(element)
        self.out.write('}')

    def handle_italic(self, element):
        self.out.write('{\\itshape ')
        self.decode_children(element)
        self.out.write('}')

    def handle_bold(self, element):
        self.out.write('{\\bfseries ')
        self.decode_children(element)
        self.out.write('}')

    def handle_paragraph(self, element):
        self.out.write('\n\n')
        self.decode_children(element)
        self.out.write('\n')

    def handle_section(self, element):
        if element.has_attr('data-type'):
            section_type = element['data-type']
        else:
            section_type = None

        title = element['data-pdf-bookmark']
        if 'chapter' == section_type:
            self.handle_chapter(element, title)
        elif 'sect1' == section_type:
            self.out.write('\\section{' + title + '}\\label{sec:' + title.replace(' ', '_').lower() + '}\n')
        elif 'sect2' == section_type:
            self.out.write('\\subsection{'+ title +'}')

        self.decode_children(element)

    def handle_chapter(self,element, title):
        _title = re.sub('Chapter\ \\d+\.\ ','',title.strip()) 
        print( 'Extracted chapter title:' , _title)
        self.out.write('\\chapter{' + _title +'}\n')

    def decode_children(self, element):
        for child in element.children:
            self.decode(child)

    def write_text(self, element):
        trimmed_text = self.sanitize(element)
        if len(trimmed_text) > 0:
            self.out.write(trimmed_text)
            self.out.write(' ')

    def sanitize(self, text):
        return text.strip().replace('$', '\\$').replace(u'\u00A9', '\\textcopyright').replace('&', '\\&'). \
            replace('\r', ' ').replace('\n', ' ')
