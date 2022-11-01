import time
import _thread as thread
import requests
from requests.exceptions import ConnectionError
from json import loads
from json.decoder import JSONDecodeError
from options import weather_options

weather_code = 0
weather_temp = None


def get_code():
    return weather_code


def get_temp():
    return weather_temp


def fetch_weather_data_thread():
    global weather_code, weather_temp

    # Define API call for weather info
    param_values = {
        'apikey': weather_options['apiKey'],
        'language': 'en-us',
        'details': True
    }

    # Convert to query string
    query = '&'.join(['%s=%s' % (k, v) for k, v in param_values.items()])
    locationID = weather_options['locationKey']
    url = f'http://dataservice.accuweather.com/currentconditions/v1/{locationID}?{query}'

    # Perform first GET request 10 seconds after program start
    time.sleep(10)

    # Make the GET request, update variables, then wait before repeating
    while True:
        try:
            response = requests.get(url)
            results = loads(response.text)
            weather_code = results[0].get('WeatherIcon')
            # temp_unit = 'Imperial' if weather_options['imperialSystem'] else 'Metrialue')
            print(f'Weather code fetched: {weather_code}')
            # weather_temp = results[0].get('Temperature').get(temp_unit).get('V
        except (ConnectionError, JSONDecodeError, KeyError) as e:
            print('Error fetching weather data:', e)
            weather_code = -1

        # Wait for defined interval before repeating
        time.sleep(weather_options.get('updateInterval', 1800))


if weather_options.get('enabled', False):
    thread.start_new_thread(fetch_weather_data_thread, ())
