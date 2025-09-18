import time
import _thread as thread
import requests
from requests.exceptions import ConnectionError
from time_system import get_time
from datetime import datetime, timedelta, timezone
from json.decoder import JSONDecodeError
from options import sunrise_options, location_options

sun_times = None


def fetch_sunrise_data_thread():
    global sun_times

    update_interval = sunrise_options.get('updateInterval')
    retry_interval = sunrise_options.get('retryInterval')

    # Define API call for sunrise info
    param_values = {
        'lat': location_options['latitude'],
        'lng': location_options['longitude'],
        'formatted': 0
    }

    # Update loop
    while True:
        success = False

        # Update parameter values with current day info
        utc_today = datetime.utcnow()
        param_values.update({
            'date': f'{utc_today.year}-{utc_today.month}-{utc_today.day}'
        })

        # Convert to query string
        query = '&'.join(['%s=%s' % (k, v) for k, v in param_values.items()])
        url = f'https://api.sunrise-sunset.org/json?{query}'

        try:
            print(f'[Sunrise] Sending request: {url}')
            
            response = requests.get(url, verify=False)
            
            print(f'[Sunrise] Response\n{response.text}')

            # Collect sunrise, sunset, and civil twilight begin and end times
            results = response.json().get('results')
            def get_time_delta(key):
                value = datetime.fromisoformat(
                    results[key]).astimezone(tz=None)
                return timedelta(hours=value.hour, minutes=value.minute)

            keys = [
                'civil_twilight_begin',
                'sunrise',
                'sunset', 
                'civil_twilight_end'
            ]
            sun_times = {key: get_time_delta(key) for key in keys}
            success = True

            print('[Sunrise] Retrieved sun_times')
            print('\n'.join([f'  {k}: {v}' for k, v in sun_times.items()]))

        except Exception as e:
            print('[Sunrise] Error fetching data')
            traceback.print_exc()

        # Wait for defined interval before repeating
        sleep_time = update_interval if success else retry_interval
        time.sleep(sleep_time)


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


if sunrise_options.get('enabled'):
    thread.start_new_thread(fetch_sunrise_data_thread, ())
