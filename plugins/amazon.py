from util import hook, http, database, formatting
from util.text import capitalize_first
from bs4 import BeautifulSoup
import urllib2
import re

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537a'} 

@hook.command('az')
@hook.command
def amazonsearch(inp):
    url = "http://www.amazon.com/s/url=search-alias%3Daps&field-keywords={}".format(inp.replace(" ", "%20"))
    try:
        request = urllib2.Request(url, None, headers)
        page = urllib2.urlopen(request).read()
        soup = BeautifulSoup(page, 'lxml')
        soup = soup.find('li', attrs={'id': ('result_1')})
        title = soup.find('h2')
        title = title.renderContents()
        url = soup.find('a', attrs={'class': ('a-link-normal s-access-detail-page a-text-normal')})
        url = url.get('href')
        try:
            price = soup.find('div', attrs={'class': ('a-column a-span7')})
            price = http.strip_html(price.find('span'))
        except AttributeError:
            price = soup.find('span', attrs={'class': ('a-size-medium a-color-price')})
            price = http.strip_html(price)
        azid = re.match(r'^.*\/dp\/([\w]+)\/.*',url).group(1)
    except AttributeError:
        return "Your search is too broad or I could not find any results."

    return u'(\x02{}\x02) {}, https://amzn.com/{}'.format(price, title.decode('ascii', 'ignore'), azid)
