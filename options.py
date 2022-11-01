import os
import sys
from json import loads

options = {}

clock_options = {}
led_options = {}
weather_options = {}
sunrise_options = {}


def load_options():
    global options
    global clock_options, led_options, weather_options, sunrise_options

    options_path = os.path.join(sys.path[0], 'options.json')
    with open(options_path, 'r') as options_file:
        options = loads(options_file.read())

    clock_options = options.get('clock')
    led_options = options.get('led')
    weather_options = options.get('weather')
    sunrise_options = options.get('sunrise')

    print('Options loaded.')


load_options()
