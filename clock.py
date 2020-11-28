#!/usr/bin/env python

""" 
A digital clock with weather status on a 16x16 Pimoroni Unicorn HAT HD for the Raspberry Pi.

This script relies on:
    - options.json to store options
    - weather-icons to store the animated icons in a single-column .png file of 10x10px frames.
    - AccuWeather to retrieve weather information.

Updated 11/27/2020
GitHub: https://github.com/jalenng/unicorn-hat-hd-clock
"""

# import built-in modules
import os
import sys
import time
from datetime import datetime
import json

try:
    import thread
except:
    import _thread as thread

# Import external modules
try:
    import numpy
    import requests
    from PIL import Image
except ImportError:
    print("""
Check if you have the following modules installed:
    numpy (pip install numpy)
    requests (pip install requests)
    PIL (pip install PIL)
    """)
    quit()

# Import Unicorn Hat HD module or simulator module
try:
    import unicornhathd
    print('Unicorn Hat HD module found.')
except ImportError:
    from unicorn_hat_sim import unicornhathd
    print('Unicorn Hat HD simulator module found.')

# Load options from options.json
# try:
SYS_PATH = sys.path[0]
options_file = open(os.path.join(SYS_PATH, "options.json"), 'r')
options_json = json.load(options_file)

clock_options = options_json.get('clock')
display_options = options_json.get('display')
weather_options = options_json.get('weather')
# except:
#     print('Error decoding options.json.')
#     quit()

# Constants
NUMBER_PATTERNS = [
    # 0
    [
        [0, 1, 1],
        [1, 0, 1],
        [1, 0, 1],
        [1, 0, 1],
        [1, 1, 0]
    ],
    # 1
    [
        [0, 0, 1],
        [0, 1, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 1, 1]
    ],
    # 2
    [
        [1, 1, 0],
        [0, 0, 1],
        [0, 1, 1],
        [1, 0, 0],
        [1, 1, 1]
    ],
    # 3
    [
        [1, 1, 1],
        [0, 0, 1],
        [0, 1, 1],
        [0, 0, 1],
        [1, 1, 0]
    ],
    # 4
    [
        [1, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [0, 0, 1]
    ],
    # 5
    [
        [0, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 0]
    ],
    # 6
    [
        [0, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ],
    # 7
    [
        [1, 1, 1],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0]
    ],
    # 8
    [
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ],
    # 9
    [
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 0]
    ]
]
COLON_PATTERN = [
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0]
]
CLOCK_Y = 11

BLINKING_COLON = clock_options.get('blinkingColon')
CLOCK_COLOR = clock_options.get('color')

DISPLAY_ROTATION = display_options.get('rotation')
MIN_BRIGHTNESS = display_options.get('minBrightness')
MAX_BRIGHTNESS = display_options.get('maxBrightness')
TPF = display_options.get('animationTPF')

WEATHER_ENABLED = weather_options.get('enabled')
PARAM_VALUES = weather_options.get('parameterValues')
LOCATION_ID = weather_options.get('locationKey')
FETCH_WEATHER_DATA_INTERVAL = weather_options.get('updateInterval')

# Variables
global weather_icon
weather_icon = -1  # -1: loading. AccuWeather icons are found here: https://developer.accuweather.com/weather-icons
ticks = 0  # Set ticks variable for animation

# Define brightness levels
separate_brightness_levels = [0] * 5
separate_brightness_levels[0] = numpy.linspace(MIN_BRIGHTNESS, MIN_BRIGHTNESS, 20, False, float)[0]  # 12am to 5am
separate_brightness_levels[1] = numpy.linspace(MIN_BRIGHTNESS, MAX_BRIGHTNESS, 20, False, float)[0]  # 5am to 10am
separate_brightness_levels[2] = numpy.linspace(MAX_BRIGHTNESS, MAX_BRIGHTNESS, 24, False, float)[0]  # 10am to 4pm
separate_brightness_levels[3] = numpy.linspace(MAX_BRIGHTNESS, MIN_BRIGHTNESS, 12, False, float)[0]  # 4pm to 7pm
separate_brightness_levels[4] = numpy.linspace(MIN_BRIGHTNESS, MIN_BRIGHTNESS, 20, False, float)[0]  # 7pm to 12am

# There are 96 total brightness levels to be cycled through every 15 minutes.
brightness_levels = []
for i in range(len(separate_brightness_levels)):
    brightness_levels = numpy.concatenate((brightness_levels, separate_brightness_levels[i]))
if len(brightness_levels) != 96:
    print('96 brightness levels expected, but ' + str(len(brightness_levels)) + ' were found.')
    quit()

# Get shape and set rotation of Unicorn HAT HD
width, height = unicornhathd.get_shape()
unicornhathd.rotation(DISPLAY_ROTATION)

# Define API call for weather info
queries = ''
at_least_one = False;
for name in list(PARAM_VALUES):
    if at_least_one:
        queries = queries + '&'
    else:
        at_least_one = True
    queries = queries + name + '=' + PARAM_VALUES.get(name)

resource_url = 'http://dataservice.accuweather.com/currentconditions/v1/' + LOCATION_ID + '?' + queries


# Define function to get weather data
def fetch_weather_data():
    global weather_icon
    time.sleep(3)
    while True:
        request_text = requests.get(resource_url).text
        loaded_request = json.loads(request_text)
        weather_icon = loaded_request[0].get('WeatherIcon')
        time.sleep(FETCH_WEATHER_DATA_INTERVAL)


# Define function to draw a pattern
def draw_pattern(x, y, pattern, color=CLOCK_COLOR, brightness=1.0):
    pattern_rows = len(pattern)
    pattern_columns = len(pattern[0])
    for i in range(pattern_rows):
        for j in range(pattern_columns):
            converted_x = y + i
            converted_y = x + j
            if converted_x in range(width) and converted_y in range(height):
                if pattern[i][j] == 1:
                    unicornhathd.set_pixel(y + i, x + j,
                                           color[0] * brightness,
                                           color[1] * brightness,
                                           color[2] * brightness)


# Define function to draw an animated image
def draw_animated_image(x, y, image_path, frame_height):
    try:
        image = Image.open(image_path)
        image_width = image.width
        image_height = image.height

        if image_height % frame_height == 0:
            number_of_frames = image_height / frame_height
            frame_index = int(ticks / TPF) % number_of_frames
            frame_starting_y = frame_index * frame_height

            for px in range(image_width):
                for py in range(frame_height):
                    pixel = image.getpixel((px, frame_starting_y + py))
                    r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])

                    converted_x = y + py
                    converted_y = x + px
                    if converted_x in range(width) and converted_y in range(height):
                        unicornhathd.set_pixel(converted_x, converted_y, r, g, b)

    except IOError:
        print(image_path + ' cannot be found.')
        quit()


# Start a thread to manage fetching weather data
if WEATHER_ENABLED:
    thread.start_new_thread(fetch_weather_data, ())

# Draw and update loop
try:
    while True:
        # Clear hat
        unicornhathd.clear()

        # Get the time
        current = datetime.now()
        hour = current.hour
        minute = current.minute
        second = current.second
        microsecond = current.microsecond

        # Calculate brightness index
        brightness_index = int((hour * 4) + (minute / 15))

        if brightness_index in range(len(brightness_levels)):
            unicornhathd.brightness(brightness_levels[brightness_index])

        # Cast time values to strings
        hour_str = str(hour % 12).zfill(2)
        if hour_str == '00':
            hour_str = '12'
        minute_str = str(minute).zfill(2)

        # Draw clock digits
        if int(hour_str[0]) != 0:
            draw_pattern(-1, CLOCK_Y, NUMBER_PATTERNS[int(hour_str[0])])
        draw_pattern(3, CLOCK_Y, NUMBER_PATTERNS[int(hour_str[1])])
        draw_pattern(9, CLOCK_Y, NUMBER_PATTERNS[int(minute_str[0])])
        draw_pattern(13, CLOCK_Y, NUMBER_PATTERNS[int(minute_str[1])])

        # Draw colon
        if BLINKING_COLON:
            if second % 2 == 0:
                draw_pattern(6, CLOCK_Y, COLON_PATTERN)
        else:
            draw_pattern(6, CLOCK_Y, COLON_PATTERN)

        # Draw weather image
        if WEATHER_ENABLED:
            image_filename = 'weather-icons/' + str(weather_icon) + '.png'
            draw_animated_image(3, 0, os.path.join(SYS_PATH, image_filename), 10)
            ticks = ticks + 1

        # Send buffer to hat to show
        unicornhathd.show()

except KeyboardInterrupt:
    unicornhathd.off()
