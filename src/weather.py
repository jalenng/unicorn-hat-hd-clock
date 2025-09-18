import time
import _thread as thread
import requests
import traceback
from datetime import datetime, timezone
from collections import namedtuple
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError
from time_system import get_time
from options import weather_options, location_options
from sprite_enum import Sprite

forecast_items = None


ForecastItem = namedtuple('ForecastItem', ['time', 'is_day', 'temperature', 'code', 'wind_speed'])   

def fetch_weather_data_thread():
    global forecast_items

    update_interval = weather_options.get('updateInterval')
    retry_interval = weather_options.get('retryInterval')

    # Define API call for weather info
    param_values = {
        'latitude': location_options['latitude'],
        'longitude': location_options['longitude'],
        'hourly': 'wind_speed_10m,is_day,weather_code,temperature_2m'
    }

    # Convert to query string
    query = '&'.join(['%s=%s' % (k, v) for k, v in param_values.items()])
    url = f'https://api.open-meteo.com/v1/forecast?{query}'

    # Update loop
    while True:
        success = False

        try:
            print(f'[Weather] Sending request: {url}')

            response = requests.get(url)

            print(f'[Weather] Response\n{response.text}')
            
            results = response.json().get('hourly')
            zipped_lists = zip(
                map(
                    lambda iso_str: datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc), 
                    results.get('time')
                ), 
                results.get('is_day'), 
                results.get('temperature_2m'), 
                results.get('weather_code'), 
                results.get('wind_speed_10m')
            )
            forecast_items = [ForecastItem(*fields) for fields in zipped_lists]
            success = True

            print('[Weather] Retrieved forecast_items')
            print(forecast_items)
        except Exception as e:
            print('[Weather] Error fetching data')
            traceback.print_exc()

        # Wait for defined interval before repeating
        sleep_time = update_interval if success else retry_interval
        time.sleep(sleep_time)


def get_sprite_from_code(weather_code, is_day = True):
    code_to_sprite = {
        -3: Sprite.DISCONNECTED,
        -2: Sprite.LOADING,
        -1: Sprite.NOTHING,

        # Clear sky
        0: Sprite.SUN if is_day else Sprite.MOON,

        # Mainly clear
        1: Sprite.SUN if is_day else Sprite.MOON,

        # Partly cloudy
        2: Sprite.SUN_AND_CLOUD if is_day else Sprite.MOON_AND_CLOUD,

        # Overcast
        3: Sprite.CLOUDS,

        # Fog and depositing rime fog
        45: Sprite.FOG,
        48: Sprite.FOG,

        # Drizzle: Light, moderate, and dense intensity
        51: Sprite.RAIN_AND_CLOUD,
        53: Sprite.RAIN_AND_CLOUD,
        55: Sprite.RAIN_AND_CLOUD,

        # Freezing Drizzle: Light and dense intensity
        56: Sprite.RAIN_AND_CLOUD,
        57: Sprite.RAIN_AND_CLOUD,

        # Rain: Slight, moderate and heavy intensity
        61: Sprite.RAIN,
        63: Sprite.RAIN_AND_CLOUD,
        65: Sprite.RAIN_AND_CLOUD,

        # Freezing Rain: Light and heavy intensity
        66: Sprite.RAIN_AND_CLOUD,
        67: Sprite.RAIN_AND_CLOUD,

        # Snow fall: Slight, moderate, and heavy intensity
        71: Sprite.SNOW,
        73: Sprite.SNOW,
        75: Sprite.SNOW,

        # Snow grains
        77: Sprite.SNOW,

        # Rain showers: Slight, moderate, and violent
        80: Sprite.RAIN_AND_CLOUD,
        81: Sprite.RAIN_AND_CLOUD,
        82: Sprite.RAIN_AND_CLOUD,

        # Snow showers: Slight and heavy
        85: Sprite.SNOW_AND_CLOUD,
        86: Sprite.SNOW_AND_CLOUD,

        # Thunderstorm: Slight or moderate
        95: Sprite.STORM,

        # Thunderstorm with slight and heavy hail
        96: Sprite.STORM,
        99: Sprite.STORM
    }
    return code_to_sprite.get(weather_code, Sprite.NOTHING)


def get_weather_sprite():
    # If no weather data, return fallback dummy
    if forecast_items is None:
        return get_sprite_from_code(-1)
        
    # Get the current time
    utc_now = get_time()
    
    # Find forecast item matching the current time
    for item in forecast_items:
        if utc_now < item.time:
            return get_sprite_from_code(item.code, item.is_day)

    return get_sprite_from_code(-1)
    

if weather_options.get('enabled'):
    thread.start_new_thread(fetch_weather_data_thread, ())
