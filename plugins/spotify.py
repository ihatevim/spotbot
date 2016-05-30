import re

from util import hook, http, web
from urllib import urlencode

def sptfy(inp, sptfy=False):
    shortenurl = "http://sptfy.com/index.php"
    data = urlencode({'longUrl': inp, 'shortUrlDomain': 1, 'submitted': 1, "shortUrlFolder": 6, "customUrl": "",
                      "shortUrlPassword": "", "shortUrlExpiryDate": "", "shortUrlUses": 0, "shortUrlType": 0})
    try:
        soup = http.get_soup(shortenurl, post_data=data, cookies=True)
    except:
        return inp
    try:
        link = soup.find('div', {'class': 'resultLink'}).text.strip()
        return link
    #if we can't shorten the url explain why and use isgd instead
    except:
        message = "Unable to shorten URL: %s" % \
                  soup.find('div', {'class': 'messagebox_text'}).find('p').text.split("<br/>")[0]
        print message
        return web.try_isgd(inp)

@hook.command('sp')
@hook.command
def spotify(inp):
    """spotify <song> -- Search Spotify for <song>"""
    try:
        data = http.get_json("http://api.spotify.com/v1/search?q=foo&type=track", q=inp.strip())
    except Exception as e:
        return "Could not get track information: {}".format(e)

    try:
        track = data["tracks"]["items"][0]["external_urls"]["spotify"]
    except IndexError:
        return "Could not find track."
    url = sptfy(track)
    uri = data["tracks"]["items"][0]["uri"]
    return u"\x02{}\x02 by \x02{}\x02 - \x02{}\x02, {}".format(data["tracks"]["items"][0]["name"],
                                                           data["tracks"]["items"][0]["artists"][0]["name"], url, uri)


@hook.command
def spalbum(inp):
    """spalbum <album> -- Search Spotify for <album>"""
    try:
        data = http.get_json("http://api.spotify.com/v1/search?q=foo&type=album", q=inp.strip())
    except Exception as e:
        return "Could not get album information: {}".format(e)

    try:
        albumurl = data["albums"]["items"][0]["external_urls"]["spotify"]
    except IndexError:
        return "Could not find album."
    url = sptfy(albumurl)
    uri = data["albums"]["items"][0]["uri"]
    return u"\x02{}\x02 - \x02{}\x02 - \x02{}\x02".format(data["albums"]["items"][0]["name"], url, uri)


@hook.command
def spartist(inp):
    """spartist <artist> -- Search Spotify for <artist>"""
    try:
        data = http.get_json("http://api.spotify.com/v1/search?q=foo&type=artist", q=inp.strip())
    except Exception as e:
        return "Could not get artist information: {}".format(e)

    try:
        artisturl = data["artists"]["items"][0]["external_urls"]["spotify"]
    except IndexError:
        return "Could not find artist."
    url = sptfy(artisturl)
    uri = data["artists"]["items"][0]["uri"]
    return u"\x02{}\x02 - \x02{}\x02 - \x02{}\x02".format(data["artists"]["items"][0]["name"], url, uri)