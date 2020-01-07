import requests
from config import Config
from logger import log_response
import time


def _get_login_page_headers():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Host': 'learning.oreilly.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
    }


class SafariPage:
    """
    """

    def __init__(self, url, email, password):
        self.__cookies = {}
        self.__url = url
        self.__email = email
        self.__password = password
        self.__session = requests.Session()

    def __post_login_page_headers(self):
        headers = dict(_get_login_page_headers())
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        headers['Referer'] = 'https://learning.oreilly.com/accounts/login/'
        return headers

    def __get_log_in_page(self):
        r = requests.get(Config.LOGIN_URL, headers=_get_login_page_headers(), allow_redirects=False)
        log_response(r, 'GET', Config.verbose)
        return r

    def log_in(self):
        log_in_page_response = self.__get_log_in_page()
        self.__update_cookies(log_in_page_response)
        csrf_token = self.__cookies.get('csrfsafari')
        print('TOKEN:', csrf_token)
        fd = self.__form_data(csrf_token)
        r = requests.post(Config.LOGIN_URL, headers=self.__post_login_page_headers(), \
                          data=fd, cookies=self.__cookies, allow_redirects=False)
        log_response(r, 'POST', Config.verbose)
        self.__update_cookies(r)
        if r.status_code == 403:
            raise Exception('CSRF error')
        self.__new_cookies = r.headers.get('Cookie', '')
        return self.__new_cookies

    def read_content(self, url):
        r = requests.get(url, headers=_get_login_page_headers(), cookies=self.__cookies)
        log_response(r, 'GET', Config.verbose)
        return r.text

    def __update_cookies(self, r):
        c = self.__find_cookies_to_set(r)
        if len(c) > 0:
            self.__cookies.update(c)

    def __form_data(self, csrf_token):
        data = {'email': self.__email, 'password1': self.__password, 'login': 'Sign+In', \
                'csrfmiddlewaretoken': csrf_token, 'next': ''}
        return data

    def __find_cookies_to_set(self, r):
        cookies_to_set = r.headers.get('Set-Cookie', '')
        separate_cookies = cookies_to_set.split(',')
        raw_cookies = [s[:s.find(';')] for s in [c.lstrip() for c in separate_cookies if c.lstrip()] if s[0].isalpha()]
        d = {}
        for r in raw_cookies:
            v = r.split('=')
            d[v[0]] = v[1]
        return d
