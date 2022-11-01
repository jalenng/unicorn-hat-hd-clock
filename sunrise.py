import time
import _thread as thread
import requests
from requests.exceptions import ConnectionError
from time_system import get_time
from datetime import datetime, timedelta, timezone
from json import loads
from json.decoder import JSONDecodeError
from options import sunrise_options

sun_times = None


def fetch_sunrise_data_thread():
    global sun_times

    # Define API call for sunrise info
    param_values = {
        'lat': sunrise_options['latitude'],
        'lng': sunrise_options['longitude'],
        'formatted': 0
    }

    # Make the GET request, generate brightness levels, then wait before repeating
    while True:

        # Update parameter values with current day info
        utc_today = datetime.utcnow()
        param_values.update({
            'date': f'{utc_today.year}-{utc_today.month}-{utc_today.day}'
        })

        # Convert to query string
        query = '&'.join(['%s=%s' % (k, v) for k, v in param_values.items()])
        resource_url = f'https://api.sunrise-sunset.org/json?{query}'

        try:
            response = requests.get(resource_url, verify=False)
            results = loads(response.text)['results']
            # Collect sunrise, sunset, and civil twilight begin and end times

            def get_time_delta(key):
                value = datetime.fromisoformat(
                    results[key]).astimezone(tz=None)
                return timedelta(hours=value.hour, minutes=value.minute)

            keys = ['civil_twilight_begin', 'sunrise',
                    'sunset', 'civil_twilight_end']
            sun_times = {key: get_time_delta(key) for key in keys}

            print('Sunrise data fetched: ')
            print('\n'.join([f'  {k}: {v}' for k, v in sun_times.items()]))

        except (ConnectionError, JSONDecodeError, KeyError) as e:
            print('Error fetching sunrise data:', e)
            sun_times = None

        # Wait for defined interval before repeating
        time.sleep(sunrise_options.get('updateInterval', 86400))


def get_brightness_level():

    # If no sunrise data is available, return the average brightness level
    if sun_times is None:
        return 0.5

    # Get the current time of day
    utc_now = get_time()
    now = timedelta(hours=utc_now.hour, minutes=utc_now.minute)

    # Compare the current time to the key times
    if now < sun_times['civil_twilight_begin']:
        # Sun is down, brightness level is 0
        return 0
    elif now < sun_times['sunrise']:
        # Sun is rising, interpolate brightness level
        t1 = sun_times['civil_twilight_begin']
        t2 = sun_times['sunrise']
        return (now - t1) / (t2 - t1)
    elif now < sun_times['sunset']:
        # Sun is up, set to full brightness
        return 1
    elif now < sun_times['civil_twilight_end']:
        # Sun is setting, interpolate brightness level between 1 and 0
        t1 = sun_times['sunset']
        t2 = sun_times['civil_twilight_end']
        return 1 - ((now - t1) / (t2 - t1))
    else:
        # Sun is down, brightness level is 0
        return 0


if sunrise_options.get('enabled', False):
    thread.start_new_thread(fetch_sunrise_data_thread, ())
