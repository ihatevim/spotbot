# weather.py
# Rewritten by ScottSteiner to use Weather Underground instead of Yahoo 
from util import hook, database, http, web

base_url = "http://api.wunderground.com/api/{}/{}/q/{}.json"

def format_coordinates(latitude, longitude):
	"Formats coordinates into one string"
	latitude = round(float(latitude), 2)
	longitude = round(float(longitude), 2)
	if latitude > 0: latitude_direction = "N"
	else: latitude_direction = "S"
	if longitude > 0: longitude_direction = "E"
	else: longitude_direction = "W"
	return "{}{} {}{}".format(roundnum(abs(latitude)), latitude_direction, roundnum(abs(longitude)), longitude_direction)

def get_weather(location, api_key):
	"Gets weather information from weather underground"

	weather_url = base_url.format(api_key, "geolookup/conditions", location)
	weather_data = http.get_json(weather_url)
	if 'results' in weather_data['response']:
		location = "zmw:{}".format(weather_data['response']['results'][0]['zmw'])
		weather_url = base_url.format(api_key, "geolookup/conditions", location)
		weather_data = http.get_json(weather_url)
	alerts_url = base_url.format(api_key, "alerts", location)
	forecast_url = base_url.format(api_key, "forecast", location)

	alerts = http.get_json(alerts_url)['alerts']
	forecast = http.get_json(forecast_url)['forecast']
	current_observation = weather_data['current_observation']

	return (current_observation, alerts, forecast)

@hook.command('w', autohelp=False)
@hook.command('we', autohelp=False)
@hook.command('wu', autohelp=False)
@hook.command('wz', autohelp=False)
@hook.command('weather', autohelp=False)
def weatherunderground(inp, nick=None, reply=None, db=None, notice=None, bot=None):
	"weather | <location> [save] | <@ user> -- Gets weather data for <location>."
	save = False

	api_key = bot.config.get("api_keys", {}).get("wunderground", None)
	if not api_key: return "error: missing api key"

	if '@' in inp:
		nick = inp.split('@')[1].strip()
		loc = database.get(db,'users','location','nick',nick)
		if not loc: return "No location stored for {}.".format(nick.encode('ascii', 'ignore'))
	else:
		if not inp:
			loc = database.get(db,'users','location','nick',nick)
			if not loc:
				notice(weather.__doc__)
				return
		else:
			if " save" in inp: 
				inp = inp.replace(' save','')
				database.set(db,'users','location',inp,'nick',nick)

			loc = inp

	location = http.quote_plus(loc.replace(' ', '_'))
	# now, to get the actual weather
	try:
		(data, alerts, forecast) = get_weather(location, api_key)
	except KeyError:	
		return "Could not get weather for that location ({}).".format(location)

	# put all the stuff we want to use in a dictionary for easy formatting of the output
	tomorrow = forecast['simpleforecast']['forecastday'][1]
	weather_data = {
		"city": data['display_location']['full'],
		"zip": data['display_location']['zip'],
		"coordinates": format_coordinates(data['display_location']['latitude'],data['display_location']['longitude']),
		"conditions": data['weather'],
		"temp_f": roundnum(float(data['temp_f']),0),
		"temp_c": roundnum(float(data['temp_c']),0),
		"humidity": data['relative_humidity'],
		"wind_kph": roundnum(data['wind_kph']),
		"wind_mph": roundnum(data['wind_mph']),
		"wind_direction": data['wind_dir'],
		"wind_text": data['wind_string'],
		"tomorrow_conditions": tomorrow['conditions'],
		"tomorrow_high_f": roundnum(float(tomorrow['high']['fahrenheit']),0),
		"tomorrow_high_c": roundnum(float(tomorrow['high']['celsius']),0),
		"tomorrow_low_f": tomorrow['low']['fahrenheit'],
		"tomorrow_low_c": tomorrow['low']['celsius'],
		"alerts": ""
	}
	if weather_data['zip'] == "00000": weather_data['zip'] = ""
	else:
		if alerts:
			desc = [x['description'] for x in alerts]
			url = "http://www.accuweather.com/us/nothing/finer/{}/watches-warnings.asp".format(weather_data['zip'])
			weather_data['alerts'] = " \x034,8\x02{}\x02 \x0312\037{}\037\x03".format(", ".join(desc), web.isgd(url))
		weather_data['zip'] = " (\x02{}\x02)".format(weather_data['zip'])

	reply(u"\x02{city}{zip} (\x02{coordinates}\x02) " \
	"Current\x02: {conditions}, " \
	"{temp_f}F/{temp_c}C, " \
	"{wind_mph}mph/{wind_kph}kph ({wind_direction}) Wind, " \
	"{humidity} Humidity "\
	"\x02Tomorrow\x02: {tomorrow_conditions}, "\
	"High {tomorrow_high_f}F/{tomorrow_high_c}C, "\
	"Low {tomorrow_low_f}F/{tomorrow_low_c}C"\
	"{alerts}".format(**weather_data))

def roundnum(num, digits=2):
	return "{:g}".format(round(num,digits))
