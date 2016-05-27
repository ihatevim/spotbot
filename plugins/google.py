import random
import json as j
import urllib2
from googleapiclient.discovery import build
from util import hook, http, text, database, web
import re

def api_get(query):
    """Use the RESTful Google Search API"""
    service = build("customsearch", "v1",
    developerKey = dev_key)
    json = service.cse().list(
        q=query,
        cx = cse_key,
    ).execute()
    return json

@hook.command('search')
@hook.command('g')
@hook.command
def google(inp,db=None,chan=None,bot=None):
    """google <query> -- Returns first google search result for <query>."""
    trimlength = database.get(db,'channels','trimlength','chan',chan)
    global dev_key 
    global cse_key
    dev_key = bot.config.get("api_keys", {}).get("google_dev_key", None)
    cse_key = bot.config.get("api_keys", {}).get("google_cse_key", None)
    if not trimlength: trimlength = 9999 
    json = api_get(inp)
    totalresults = json['queries']['request'][0]['totalResults']
    if totalresults == "0":
        return 'No results found.'

    result = json['items'][0]['link']
    title = json['items'][0]['title']
    content = json['items'][0]['snippet']

    if not content: content = "No description available."
    else: content = http.html.fromstring(content.replace('\n', '')).text_content()

    return u'{} -- \x02{}\x02: "{}"'.format(result, title, content)

	
# @hook.command('image')
@hook.command('gis')
@hook.command('gi')
@hook.command('image')
@hook.command
def googleimage(inp):
    """gis <query> -- Returns first Google Image result for <query>."""

    json = api_get(inp)
    totalresults = json['queries']['request'][0]['totalResults']
    if totalresults == "0":
        return 'No images; sorry :C'
    imgurl=json['items'][0]['pagemap']['cse_image'][0]['src']
    return '{}'.format(imgurl)

@hook.command('nym')
@hook.command('littleanon')
@hook.command('gfy')
@hook.command
def lmgtfy(inp, bot=None):
    "lmgtfy [phrase] - Posts a google link for the specified phrase"

    link = "http://lmgtfy.com/?q=%s" % http.quote_plus(inp)

    try:
        return web.isgd(link)
    except (web.ShortenError, http.HTTPError):
        return link

