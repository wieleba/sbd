#! /usr/bin/python3
import time
import json
import os
import re
from shutil import copyfile
from bs4 import BeautifulSoup
from urllib.request import (
            urlopen, urlparse, urlunparse, urlretrieve, Request)
import requests
from argparse import ArgumentParser
import getopt
from sys import argv
from safari_page import SafariPage
from config import Config
from image_extractor import ImageExtractor
from logger import Logger as log
import getpass

class Main:
        
    def __init__(self, url, out_file_name, email, password, verbose):
        self.url = url
        Config.verbose = verbose
        self.out_dir = os.path.join('out/' + out_file_name)
        self.out = self._init_io(out_file_name)
        self.out_file_name = out_file_name
        self.login_page = SafariPage(url, email, password)

    def _init_io(self,out_file_name):
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        copyfile('style.css',self.out_dir + '/style.css')
        copyfile('style2.css',self.out_dir + '/style2.css')

        try:
           a = open(os.path.join(self.out_dir,out_file_name + '.html'),'w')
           a.write(
                   '''<html>
                            <head>
                               <meta charset="utf-8"/>
                               <link rel="stylesheet" href="style.css" /> 
                               <link rel="stylesheet" href="style2.css" />
                            </head>
                            <body>''')
           return a
        except IOError:
            print ('Can\'t open ',out_file_name)
            exit(1)

    def read_content(self,url):
        return self.login_page.read_content(url)

    def write_content(self,content):
        self.out.write('\n')
        if(content is not None):
            self.out.write('<div class="page">')
            self.out.write(re.sub(r'href=".*\.xhtml',r'href="'+ self.out_file_name + '.html', content.replace('src="/','src="./')))
            self.out.write('</div>')

    def extract_chapter(self,soup):
        return soup.find('div',id='sbo-rt-content').prettify()

    def find_nexturl(self,soup):
        try:
           return soup.findAll('a',class_='next')[0].attrs['href']
        except:
            return  None

    def download_content(self,url_to_check):
        content = self.read_content(url_to_check)
        soup = BeautifulSoup(content,'lxml')
        ImageExtractor(soup, self.out_dir).download_images_and_save()
        self.write_content(self.extract_chapter(soup))
        nexturl = self.find_nexturl(soup)
        print('Next page:', nexturl)
        if nexturl != None:
            self.download_content(Config.SAFARI_URL + nexturl)
    
    def start(self):
        self.download_content(self.url)

    def finalize(self):
        self.out.write('</body></html>')
        self.out.close()

    def init_safari(self):
        self.login_page.log_in()

def init():
    p = ArgumentParser()
    p.add_argument('-v','--verbose', nargs='?', type=str2bool, default=False,const=True, help='print a lot of diagnostics')
    p.add_argument('-o','--out',required=True, help='out file name')
    p.add_argument('-u','--url',required=True, help='url to safari book')
    p.add_argument('-e','--email', required=True, help='Your safari login')
    a = p.parse_args()
    return Main(a.url, a.out, a.email, getpass.getpass(), a.verbose)

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def usage():
    print ('usage:\n',argv[0], " -u url_to_safari_book\n -o out_file\n [-v]")

def main():    
    m = init()
    m.init_safari()
    m.start()
    m.finalize()

main()

