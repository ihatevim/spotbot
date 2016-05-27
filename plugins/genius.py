import re
from util import hook, http, text, database, web
import urllib2
import json
import requests
base_url = "http://api.genius.com/search?q=foo&access_token={}"
	
@hook.command('lyr')
@hook.command
def lyrics(inp,db=None,chan=None,bot=None):
	"""lyrics <song> -- Search genius for a specific song"""
	access_token = bot.config.get("api_keys", {}).get("genius_access_token", None)
	if not access_token:
		return "An API key is needed to use this application."
	try:
		data = http.get_json((base_url.format(access_token)), q=inp.strip())
	except Exception as e:
		return "Could not find song: {}".format(e)
	try:
		song = data["response"]["hits"][0]["index"]
	except IndexError:
		return "Could not find song"
	return u"{} by {} - {}".format(data["response"]["hits"][0]["result"]["title"], data["response"]["hits"][0]["result"]["primary_artist"]["name"], data["response"]["hits"][0]["result"]["url"])