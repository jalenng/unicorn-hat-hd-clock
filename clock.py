#!/usr/bin/env python

""" 
A digital clock with weather status on a 16x16 Pimoroni Unicorn HAT HD for the Raspberry Pi.

This script relies on:
    - options.json to store options
    - weather-icons to store the animated icons in a single-column .png file of 10x10px frames
    - AccuWeather to retrieve weather information
    - https://sunrise-sunset.org/api for sunrise and sunset information to adjust brightness accordingly

Updated 11/29/2020
GitHub: https://github.com/jalenng/unicorn-hat-hd-clock
"""

###############################################################################
# Import modules
###############################################################################

# Built-in modules
from datetime import datetime
import json
import os
import sys
import _thread as thread
import time

# External modules
import numpy
from PIL import Image
import requests

# Unicorn HAT HD module or simulator module
try:
    import unicornhathd

    print('Unicorn HAT HD module found.')
except ImportError:
    from unicorn_hat_sim import unicornhathd

    print('Unicorn HAT HD simulator module found.')

###############################################################################
# Load options.json
###############################################################################

try:
    SYS_PATH = sys.path[0]
    options_file = open(os.path.join(SYS_PATH, 'options.json'), 'r')
    options_json = json.load(options_file)

    clock_options = options_json.get('clock')
    display_options = options_json.get('display')
    weather_options = options_json.get('weather')
    sunrise_options = options_json.get('sunrise')
except ImportError:
    print('Error decoding options.json.')
    quit()
except AttributeError:
    print('An attribute of options.json cannot be found.')
    quit()

###############################################################################
# Define constants and variables
###############################################################################

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

# From options.json
TWELVE_HR_FORMAT = clock_options.get('12hrFormat')
OMIT_LEADING_ZEROS = clock_options.get('omitLeadingZeros')
BLINKING_COLON = clock_options.get('blinkingColon')
CLOCK_COLOR = clock_options.get('color')

DISPLAY_ROTATION = display_options.get('rotation')
MIN_BRIGHTNESS = display_options.get('minBrightness')
MAX_BRIGHTNESS = display_options.get('maxBrightness')
TPF = display_options.get('animationTPF')

WEATHER_ENABLED = weather_options.get('enabled')
WEATHER_API_KEY = weather_options.get('apiKey')
LOCATION_ID = weather_options.get('locationKey')
FETCH_WEATHER_DATA_INTERVAL = weather_options.get('updateInterval')

SUNRISE_ENABLED = sunrise_options.get('enabled')
LATITUDE = sunrise_options.get('latitude')
LONGITUDE = sunrise_options.get('longitude')
FETCH_SUNRISE_DATA_INTERVAL = sunrise_options.get('updateInterval')

# Global variables
global weather_icon_num
global prev_weather_icon_num  # Used for detecting whether there is a change in weather icon number
global brightness_levels
global weather_icon_cache  # Used for saving the weather icon to RAM to minimize reads to SD card

prev_weather_icon_num = -1
weather_icon_num = 0  # 0: loading. AccuWeather icons are found here: https://developer.accuweather.com/weather-icons
brightness_levels = [MIN_BRIGHTNESS] * 288
weather_icon_cache = []

# Other variables
draw_colon = TWELVE_HR_FORMAT and OMIT_LEADING_ZEROS  # Colon only in 12-hr format and when leading zeros are omitted
clock_x_offset = -1 if draw_colon else 0
clock_y = 11
width, height = unicornhathd.get_shape()
ticks = 0  # Set ticks variable for animation


###############################################################################
# Define functions and threads
###############################################################################

# Define function to convert dictionary of parameter values to a REST query string
def convert_dict_to_query_str(param_dict):
    rtn = ''
    at_least_one = False
    for name in list(param_dict):
        if at_least_one:
            rtn += '&'
        else:
            at_least_one = True
        rtn += name + '=' + str(param_dict.get(name))
    return rtn


# Define thread for fetching weather data
def fetch_weather_data_thread():
    global weather_icon_num

    # Define API call for weather info
    param_values = {
        'apikey': WEATHER_API_KEY,
        'language': 'en-us',
        'details': True
    }
    queries = convert_dict_to_query_str(param_values)
    resource_url = 'http://dataservice.accuweather.com/currentconditions/v1/' + LOCATION_ID + '?' + queries

    # Perform first GET request 3.5 seconds after program start
    time.sleep(3.5)

    # Make the GET request, update variables, then wait before repeating
    while True:
        request_text = requests.get(resource_url).text
        request_results = json.loads(request_text)
        weather_icon_num = request_results[0].get('WeatherIcon')

        # Wait for defined interval before repeating
        time.sleep(FETCH_WEATHER_DATA_INTERVAL)


# Define thread for fetching sunrise and sunset data
def fetch_sunrise_data_thread():
    global brightness_levels

    # Define API call for sunrise info
    param_values = {
        'lat': LATITUDE,
        'lng': LONGITUDE,
        'formatted': 0
    }

    # Perform first GET request 3.5 seconds after program start
    time.sleep(3.5)

    # Make the GET request, generate brightness levels, then wait before repeating
    while True:
        # Update parameter values with current day info
        utc_today = datetime.utcnow()
        param_values.update({
            'date': str(utc_today.year) + '-' + str(utc_today.month) + '-' + str(utc_today.day)
        })

        queries = convert_dict_to_query_str(param_values)
        resource_url = 'https://api.sunrise-sunset.org/json?' + queries

        request_text = requests.get(resource_url).text
        request_results = json.loads(request_text).get('results')

        # Collect sunrise, sunset, and civil twilight begin and end times
        sun_times = [
            datetime.fromisoformat(request_results.get('civil_twilight_begin')).astimezone(tz=None),
            datetime.fromisoformat(request_results.get('sunrise')).astimezone(tz=None),
            datetime.fromisoformat(request_results.get('sunset')).astimezone(tz=None),
            datetime.fromisoformat(request_results.get('civil_twilight_end')).astimezone(tz=None)
        ]

        # Calculate the ending indices for each section.
        # Each index marks five minutes, and each hour occupies 12 indices
        for i in range(len(sun_times)):
            sun_times[i] = int((12 * sun_times[i].hour) + (sun_times[i].minute / 5))
        sun_times.append(288)

        # Define the starts and ends of each sections' range
        brightness_levels_section_start = \
            [MIN_BRIGHTNESS, MIN_BRIGHTNESS, MAX_BRIGHTNESS, MAX_BRIGHTNESS, MIN_BRIGHTNESS]
        brightness_levels_section_end = \
            [MIN_BRIGHTNESS, MAX_BRIGHTNESS, MAX_BRIGHTNESS, MIN_BRIGHTNESS, MIN_BRIGHTNESS]

        # Define the brightness levels by calculating and appending each section
        brightness_levels = []
        for (start, end, index) in zip(brightness_levels_section_start, brightness_levels_section_end, sun_times):
            brightness_levels_section = numpy.linspace(start, end, index - len(brightness_levels), False)
            brightness_levels = numpy.concatenate((brightness_levels, brightness_levels_section))

        # Wait for defined interval before repeating
        time.sleep(FETCH_SUNRISE_DATA_INTERVAL)


# Define function to draw a pattern defined as a 2D array
def draw_pattern(x, y, pattern, color=CLOCK_COLOR):
    pattern_rows = len(pattern)
    pattern_columns = len(pattern[0])
    for i in range(pattern_rows):
        for j in range(pattern_columns):
            converted_x = y + i
            converted_y = x + j
            if converted_x in range(width) and converted_y in range(height):
                if pattern[i][j] == 1:
                    unicornhathd.set_pixel(y + i, x + j, color[0], color[1], color[2])


# Define function to draw an animated image
def draw_animated_image(x, y, image_path, frame_height):
    global prev_weather_icon_num
    global weather_icon_cache

    # If there is a change in the weather icon number
    if weather_icon_num != prev_weather_icon_num:

        # Clear the weather icon cache
        prev_weather_icon_num = weather_icon_num
        weather_icon_cache = []

        # Try to read and cache the new weather icon image file
        try:
            image = Image.open(image_path)
            image_width = image.width
            image_height = image.height

            if image_height % frame_height == 0:
                number_of_frames = int(image_height / frame_height)
                weather_icon_cache = [[[(0, 0, 0) for k in range(frame_height)] for j in range(image_width)]
                                      for i in range(number_of_frames)]

                for i in range(number_of_frames):
                    frame_starting_y = i * frame_height

                    for px in range(image_width):
                        for py in range(frame_height):
                            pixel = image.getpixel((px, frame_starting_y + py))
                            r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                            weather_icon_cache[i][px][py] = (r, g, b)

        except IOError:
            print(image_path + ' cannot be found.')
            quit()

    # Read from the cache and update the Unicorn HAT HD pixels accordingly
    frame_index = int(ticks / TPF) % len(weather_icon_cache)
    weather_icon_cache_frame = weather_icon_cache[frame_index]

    for px in range(len(weather_icon_cache_frame)):
        for py in range(len(weather_icon_cache_frame[px])):

            pixel = weather_icon_cache_frame[px][py]
            r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])

            converted_x = y + py
            converted_y = x + px

            if converted_x in range(width) and converted_y in range(height):
                unicornhathd.set_pixel(converted_x, converted_y, r, g, b)


###############################################################################
# Execute functions
###############################################################################

# Set display rotation
unicornhathd.rotation(DISPLAY_ROTATION)

# Start thread to manage fetching data
if WEATHER_ENABLED:
    thread.start_new_thread(fetch_weather_data_thread, ())
if SUNRISE_ENABLED:
    thread.start_new_thread(fetch_sunrise_data_thread, ())

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

        # Calculate brightness index
        brightness_index = int((hour * 12) + (minute / 5))

        if brightness_index in range(len(brightness_levels)):
            unicornhathd.brightness(brightness_levels[brightness_index])

        # Cast time values to strings
        if TWELVE_HR_FORMAT:
            twelve_hour = hour % 12
            if twelve_hour == 0:
                hour_str = '12'
            else:
                hour_str = str(twelve_hour).zfill(2)
        else:
            hour_str = str(hour).zfill(2)
        minute_str = str(minute).zfill(2)

        # Draw hour digits
        if OMIT_LEADING_ZEROS:
            if int(hour_str[0]) != 0:
                draw_pattern(0 + clock_x_offset, clock_y, NUMBER_PATTERNS[int(hour_str[0])])
        else:
            draw_pattern(0 + clock_x_offset, clock_y, NUMBER_PATTERNS[int(hour_str[0])])
        draw_pattern(4 + clock_x_offset, clock_y, NUMBER_PATTERNS[int(hour_str[1])])

        # Draw minute digits
        draw_pattern(9, clock_y, NUMBER_PATTERNS[int(minute_str[0])])
        draw_pattern(13, clock_y, NUMBER_PATTERNS[int(minute_str[1])])

        # Draw colon
        if draw_colon:
            if not BLINKING_COLON or second % 2 == 0:
                draw_pattern(6, clock_y, COLON_PATTERN)

        # Draw weather image
        if WEATHER_ENABLED:
            image_filename = 'weather-icons/' + str(weather_icon_num) + '.png'
            draw_animated_image(3, 0, os.path.join(SYS_PATH, image_filename), 10)
            ticks += 1

        # Send buffer to the Unicorn HAT HD for showing
        unicornhathd.show()

# Ctrl-C
except KeyboardInterrupt:
    unicornhathd.off()
