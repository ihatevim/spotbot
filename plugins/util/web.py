""" web.py - handy functions for web services """

import http
import urlnorm
import json
import urllib
import yql
import requests
short_url = "http://is.gd/create.php"
paste_url = "http://hastebin.com"
yql_env = "http://datatables.org/alltables.env"

YQL = yql.Public()


class ShortenError(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def __str__(self):
        return self.text


def isgd(url):
    """ shortens a URL with the is.gd API """
    p = {'format': 'json', 'url': url}
    r = requests.get('http://is.gd/create.php', params=p)
    j = r.json()

    if 'shorturl' in j:
        return j['shorturl']
    else:
        raise ShortenError(j['errormessage'], r)


def try_isgd(url):
    try:
        out = isgd(url)
    except (ShortenError, http.HTTPError):
        out = url
    return out


def haste(text, ext='txt'):
    """ pastes text to a hastebin server """
    page = http.get(paste_url + "/documents", post_data=text)
    data = json.loads(page)
    return ("%s/%s.%s" % (paste_url, data['key'], ext))


def query(query, params={}):
    """ runs a YQL query and returns the results """
    return YQL.execute(query, params, env=yql_env)
