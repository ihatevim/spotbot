from util import hook, http, database, formatting
import time
from util.text import capitalize_first
from bs4 import BeautifulSoup
import urllib2
import re
import requests
# Define some constants
base_url = 'https://maps.googleapis.com/maps/api/'
geocode_api = base_url + 'geocode/json'
timezone_api = base_url + 'timezone/json'

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36','Upgrade-Insecure-Requests': '1','x-runtime': '148ms'}

bias = None
def check_status(status, api):
    """ A little helper function that checks an API error code and returns a nice message.
        Returns None if no errors found """
    if status == 'REQUEST_DENIED':
        return 'The ' + api + ' API is off in the Google Developers Console.'
    elif status == 'ZERO_RESULTS':
        return 'No results found.'
    elif status == 'OVER_QUERY_LIMIT':
        return 'The ' + api + ' API quota has run out.'
    elif status == 'UNKNOWN_ERROR':
        return 'Unknown Error.'
    elif status == 'INVALID_REQUEST':
        return 'Invalid Request.'
    elif status == 'OK':
        return None
    else:
        # !!!
        return 'Unknown Demons.'
@hook.command("t", autohelp=False)
@hook.command("time", autohelp=False)
def time_command(inp, nick='', db=None, bot=None, notice=None):
    """<location> -- Gets the current time in <location>."""
    dev_key = bot.config.get("api_keys", {}).get("google_dev_key")
    if not dev_key:
        return "This command requires a Google Developers Console API key."

    save = True

    if '@' in inp:
        nick = inp.split('@')[1].strip()
        text = database.get(db,'users','location','nick',nick)
        if not text: return "No location stored for {}.".format(nick.encode('ascii', 'ignore'))
    else:
        text = database.get(db,'users','location','nick',nick)
        if not inp:
            if not text:
                notice(time.__doc__)
                return "database is empty"
        else:
            # if not location: save = True
            if " dontsave" in inp: save = False
            text = inp
    # Use the Geocoding API to get co-ordinates from the input
    params = {"address": text, "key": dev_key}
    if bias:
        params['region'] = bias

    json = requests.get(geocode_api, params=params).json()

    error = check_status(json['status'], "geocoding")
    if error:
        return error

    result = json['results'][0]

    location_name = result['formatted_address']
    location = result['geometry']['location']

    # Now we have the co-ordinates, we use the Timezone API to get the timezone
    formatted_location = "{lat},{lng}".format(**location)

    epoch = time.time()

    params = {"location": formatted_location, "timestamp": epoch, "key": dev_key}
    json = requests.get(timezone_api, params=params).json()

    error = check_status(json['status'], "timezone")
    if error:
        return error

    # Work out the current time
    offset = json['rawOffset'] + json['dstOffset']

    # I'm telling the time module to parse the data as GMT, but whatever, it doesn't matter
    # what the time module thinks the timezone is. I just need dumb time formatting here.
    raw_time = time.gmtime(epoch + offset)
    formatted_time = time.strftime('%I:%M %p, %A, %B %d, %Y', raw_time)

    timezone = json['timeZoneName']

    return "\x02{}\x02 - {} ({})".format(formatted_time, location_name, timezone)
@hook.command('time2', autohelp=False)
def timefunction2(inp, nick="", reply=None, db=None, notice=None):
    "time [location] [dontsave] | [@ nick] -- Gets time for <location>."

    save = True

    if '@' in inp:
        nick = inp.split('@')[1].strip()
        location = database.get(db,'users','location','nick',nick)
        if not location: return "No location stored for {}.".format(nick.encode('ascii', 'ignore'))
    else:
        location = database.get(db,'users','location','nick',nick)
        if not inp:
            if not location:
                notice(time.__doc__)
                return
        else:
            # if not location: save = True
            if " dontsave" in inp: save = False
            location = inp

    # now, to get the actual time
    url = "https://time.is/%s" % location.replace(' ','_').replace(' save','')
    try:
        request = urllib2.Request(url, None, headers)
        page = urllib2.urlopen(request).read()
        soup = BeautifulSoup(page, 'lxml')
        soup = soup.find('div', attrs={'id': re.compile('time_section')})
        time = filter(None, http.strip_html(soup.find('div', attrs={'id': re.compile('twd')}).renderContents().strip()))
        details = filter(None, http.strip_html(soup.find('div', attrs={'id': re.compile('dd')}).renderContents().strip()))
        prefix = filter(None, http.strip_html(soup.find('div', attrs={'id': re.compile('msgdiv')}).renderContents().strip()))
    except IndexError:
        return "Could not get time for that location."

    return formatting.output('Time', [u'{} {}, {}'.format(prefix.decode('ascii', 'ignore'), time, details)])

api_url = 'http://api.wolframalpha.com/v2/query?format=plaintext'

def watime(inp, bot=None):
    """time <area> -- Gets the time in <area>"""

    query = "current time in {}".format(inp)

    api_key = bot.config.get("api_keys", {}).get("wolframalpha", None)
    if not api_key:
        return "error: no wolfram alpha api key set"

    request = http.get_xml(api_url, input=query, appid=api_key)
    time = " ".join(request.xpath("//pod[@title='Result']/subpod/plaintext/text()"))
    time = time.replace("  |  ", ", ")

    if time:
        # nice place name for UNIX time
        if inp.lower() == "unix":
            place = "Unix Epoch"
        else:
            place = capitalize_first(" ".join(request.xpath("//pod[@"
                                                            "title='Input interpretation']/subpod/plaintext/text()"))[
                                     16:])
        return "{} - \x02{}\x02".format(time, place)
    else:
        return u"Could not get the time for '{}'.".format(inp)


@hook.command(autohelp=False)
def beats(inp):
    """beats -- Gets the current time in .beats (Swatch Internet Time). """

    if inp.lower() == "wut":
        return "Instead of hours and minutes, the mean solar day is divided " \
               "up into 1000 parts called \".beats\". Each .beat lasts 1 minute and" \
               " 26.4 seconds. Times are notated as a 3-digit number out of 1000 af" \
               "ter midnight. So, @248 would indicate a time 248 .beats after midni" \
               "ght representing 248/1000 of a day, just over 5 hours and 57 minute" \
               "s. There are no timezones."
    elif inp.lower() == "guide":
        return u"1 day = 1000 .beats, 1 hour = 41.666 .beats, 1 min = 0.6944 .beats, 1 second = 0.01157 .beats"

    t = time.gmtime()
    h, m, s = t.tm_hour, t.tm_min, t.tm_sec

    utc = 3600 * h + 60 * m + s
    bmt = utc + 3600  # Biel Mean Time (BMT)

    beat = bmt / 86.4

    if beat > 1000:
        beat -= 1000

    return formatting.output('Swatch Internet Time', ['@{0:.2f}'.format(beat)])
