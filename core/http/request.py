'''
Created on 03/ott/2011

@author: emilio
'''

import urllib
from random import choice

agents = (
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)",
    "Opera/9.20 (Windows NT 6.0; U; en)",
    "Opera/9.00 (Windows NT 5.1; U; en)",
    "Googlebot/2.1 ( http://www.googlebot.com/bot.html)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/20100101 Firefox/17.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11",
    "Mozilla/5.0 (Linux; U; Android 2.2; fr-fr; Desire_A8181 Build/FRF91)",
)

class URLOpener(urllib.FancyURLopener):

    version = choice(agents)

    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass


class Request:

    def __init__(self, url, proxy={}):
        self.url = url
        self.data = {}

        self.opener = URLOpener(proxies = proxy)

    def __setitem__(self, key, value):
        self.opener.addheader(key, value)

    def read(self, bytes= -1):
        if self.data:
            handle = self.opener.open(self.url, data=urllib.urlencode(self.data))
        else:
            handle = self.opener.open(self.url)

        if bytes > 0:
            return handle.read(bytes)
        else:
            return handle.read()