#! /usr/bin/python3
import getpass
import os
from argparse import ArgumentParser, ArgumentTypeError
from sys import argv

from bs4 import BeautifulSoup

from config import Config
from html_printer import HtmlPrinter
from image_extractor import ImageExtractor
from safari_page import SafariPage
from tex_printer import TexPrinter


class Main:

    def __init__(self, url, out_file_name, email, password, verbose, tex):
        self.url = url
        Config.verbose = verbose
        self.out_dir = os.path.join('out/' + out_file_name)
        self.output_printer = TexPrinter(self.out_dir, out_file_name) if tex else HtmlPrinter(self.out_dir,
                                                                                              out_file_name)
        self.out = self._init_io()
        self.out_file_name = out_file_name
        self.login_page = SafariPage(url, email, password)

    def _init_io(self):
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        return self.output_printer.preamble()

    def read_content(self, url):
        return self.login_page.read_content(url)

    def write_content(self, content):
        self.output_printer.write_content(content)

    def extract_chapter(self, soup):
        return soup.find('div', id='sbo-rt-content').prettify()

    def find_nexturl(self, soup):
        try:
            return soup.findAll('a', class_='next')[0].attrs['href']
        except:
            return None

    def download_content(self, url_to_check):
        content = self.read_content(url_to_check)
        soup = BeautifulSoup(content, 'lxml')
        ImageExtractor(soup, self.out_dir).download_images_and_save()
        self.write_content(self.extract_chapter(soup))
        next_url = self.find_nexturl(soup)
        print('Next page:', next_url)
        if next_url is not None:
            self.download_content(Config.SAFARI_URL + next_url)

    def start(self):
        self.download_content(self.url)

    def finalize(self):
        self.output_printer.finalize()

    def init_safari(self):
        self.login_page.log_in()


def init():
    p = ArgumentParser()
    p.add_argument('-v', '--verbose', nargs='?', type=str2bool, default=False, const=True,
                   help='print a lot of diagnostics')
    p.add_argument('-o', '--out', required=True, help='out file name')
    p.add_argument('-u', '--url', required=True, help='url to safari book')
    p.add_argument('-e', '--email', required=True, help='Your safari login')
    p.add_argument('-t', '--tex', nargs='?', type=str2bool, default=False, const=True, help='use tex to generate book')
    a = p.parse_args()
    return Main(a.url, a.out, a.email, getpass.getpass(), a.verbose, a.tex)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


def usage():
    print('usage:\n', argv[0], " -u url_to_safari_book\n -o out_file\n [-v]")


def main():
    m = init()
    m.init_safari()
    m.start()
    m.finalize()


main()
