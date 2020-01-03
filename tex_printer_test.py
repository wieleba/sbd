#! /usr/bin/python3
import os

from bs4 import BeautifulSoup

from tex_printer import TexPrinter


def extract_chapters(soup):
    return soup.find_all('div', class_='page')


class Main:

    def __init__(self, input_file):
        self.out_dir = os.path.join('test')
        self.input_file = input_file

        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        self.output_printer = TexPrinter(self.out_dir, 'test_output')
        self.out = self._init_io()

    def _init_io(self):
        return self.output_printer.preamble()

    def write_content(self, content):
        self.output_printer.write_content(content)

    def write_chapters(self):
        in_file = open(self.input_file, 'r')

        content = in_file.read()
        soup = BeautifulSoup(content, 'lxml')
        for chapter in extract_chapters(soup):
            self.write_content(chapter)

    def finalize(self):
        self.output_printer.finalize()


def main():
    m = Main('test.html')
#    m = Main('optimizing_java_full.html')
    m.write_chapters()
    m.finalize()


main()
