#! /usr/bin/python3
import time,os,json,shutil 
from urllib.request import (
            urlopen, urlparse, urlunparse, urlretrieve, Request)
import requests
from argparse import ArgumentParser
import getopt
from sys import argv
from safari_page import SafariPage
from config import Config
from safari_page import SafariPage
from logger import Logger as log
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
class ImageExtractor:
        
    def __init__(self, soup, out_dir):
        self.__soup = soup
        self.__out_dir = out_dir

    def download_images_and_save(self):
        dir_file_list = [(img[:img.rfind('/') ],img) for img in self.__list_images()]
        tasks = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            for dir_name,image_path in dir_file_list:
                if os.path.isabs(dir_name):
                    dir_name = './' + dir_name
                joined_path = os.path.normpath( os.path.join(self.__out_dir , dir_name) )
                self.__create_dir_if_missing(joined_path)
                tasks.append(executor.submit(self.__download_and_save_image, joined_path, image_path))
            for f in as_completed(tasks):
                try:
                    f.result()
                except Exception as e:
                    print('Exception:',e)


    def __list_images(self):
        return [ img.attrs['src'] for img in self.__soup.findAll('img') ]

    def __create_dir_if_missing(self, dir_name):
        if not os.path.exists(dir_name):
            print('About to create', dir_name)
            os.makedirs(dir_name)

#image_list = ImageExtractor(open('part.html','r').read()) \
#        .list_images()

    def __download_and_save_image(self,dir_name, img_path):
        if os.path.isabs(img_path):
            img_path = '.' + img_path
        print('html image path', img_path)
        out_file = os.path.normpath( os.path.join(self.__out_dir, img_path) )        
        url = Config.SAFARI_URL + img_path
        print('downloading ', url , ' to file ', out_file)
        if not Path(out_file).is_file():
            response = requests.get(url, stream=True, verify = False)
            with open(out_file, 'wb') as out:
                shutil.copyfileobj(response.raw, out)
            del response

