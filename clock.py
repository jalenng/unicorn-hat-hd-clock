#!/usr/bin/env python

"""
A digital clock with weather status on a 16x16 Pimoroni Unicorn HAT HD for the Raspberry Pi.

This script relies on:
    - options.json to store options
    - weather-icons to store the animated icons in a single-column .png file of 10x10px frames
    - AccuWeather to retrieve weather information
    - https://sunrise-sunset.org/api for sunrise and sunset information to adjust brightness accordingly

Updated 1/23/2021
GitHub: https://github.com/jalenng/unicorn-hat-hd-clock
"""

###############################################################################
# Import modules
###############################################################################
from datetime import datetime
import json
import os
import sys
import _thread as thread
import time

import numpy
from PIL import Image
import requests

from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError

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
except ImportError as err:
    print('Error decoding options.json: ' + str(err))
    quit()
except AttributeError as err:
    print('An attribute of options.json cannot be found: ' + str(err))
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

DEGREE_PATTERN = [
    [1, 1, 0],
    [1, 1, 0],
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
]

HYPHEN_PATTERN = [
    [0, 0, 0],
    [0, 0, 0],
    [1, 1, 1],
    [0, 0, 0],
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
SPF = display_options.get('secondsPerFrame')

WEATHER_ENABLED = weather_options.get('enabled')
WEATHER_API_KEY = weather_options.get('apiKey')
LOCATION_ID = weather_options.get('locationKey')
FETCH_WEATHER_DATA_INTERVAL = weather_options.get('updateInterval')
SHOW_TEMPERATURE = weather_options.get('showTemperature')
TEMPERATURE_COLOR = weather_options.get('temperatureColor')
IMPERIAL_SYSTEM = weather_options.get('imperialSystem')

SUNRISE_ENABLED = sunrise_options.get('enabled')
LATITUDE = sunrise_options.get('latitude')
LONGITUDE = sunrise_options.get('longitude')
FETCH_SUNRISE_DATA_INTERVAL = sunrise_options.get('updateInterval')

# Global variables
# 0: loading; 1: network error; AccuWeather icons are found here: https://developer.accuweather.com/weather-icons
global weather_icon_num
global weather_temp
global brightness_levels

# Other variables
draw_colon = TWELVE_HR_FORMAT and OMIT_LEADING_ZEROS  # Colon only in 12-hr format and when leading zeros are omitted
clock_hour_x_offset = -1 if draw_colon else 0  # If colon is drawn, need to shift hours to the left to make room
clock_y = 11
width, height = unicornhathd.get_shape()
ticks = 0


###############################################################################
# Define functions and threads
###############################################################################
# Define function to load images into RAM by returning dictionary of (r, g, b) tuples. Goal: minimize SD card reads.
# Returns a dictionary such that dict[icon_number][frame][x][y] returns the r, g, b value of the pixel at x, y.
def load_images(relative_path):
    rtn = {}
    images_path = os.path.join(SYS_PATH, relative_path)
    images_list = os.listdir(images_path)

    # Iterate through each file in ./weather-icons
    for filename in images_list:
        split_filename = os.path.splitext(filename)
        file_path = os.path.join(images_path, filename)
        try:
            image = Image.open(file_path)
            image_width = image.width
            image_height = image.height
            image_num = int(split_filename[0])

            # If dimensions are suitable, turn image to a 2D array of (r, g, b) tuples
            if image_height % image_width == 0:
                number_of_frames = int(image_height / image_width)
                rtn[image_num] = [
                    [[(0, 0, 0) for k in range(image_width)] for j in range(image_width)]
                    for i in range(number_of_frames)]

                for frame_num in range(number_of_frames):
                    frame_starting_y = frame_num * image_width

                    for px in range(image_width):
                        for py in range(image_width):
                            pixel = image.getpixel((px, frame_starting_y + py))
                            r, g, b, a = int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3])
                            rtn[image_num][frame_num][px][py] = (r, g, b, a)

        except ValueError:
            print(file_path + ' does not correspond to an icon number.')
        except IOError:
            print(file_path + ' could not be read.')

    return rtn


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


# Thread for fetching weather data
def fetch_weather_data_thread():
    global weather_icon_num
    global weather_temp

    # Define API call for weather info
    param_values = {
        'apikey': WEATHER_API_KEY,
        'language': 'en-us',
        'details': True
    }
    queries = convert_dict_to_query_str(param_values)
    resource_url = 'http://dataservice.accuweather.com/currentconditions/v1/' + LOCATION_ID + '?' + queries

    # Perform first GET request 10 seconds after program start
    time.sleep(10)

    # Make the GET request, update variables, then wait before repeating
    while True:
        try:
            response = requests.get(resource_url)
            results = json.loads(response.text)
            weather_icon_num = results[0].get('WeatherIcon')
            weather_temp = results[0].get('Temperature').get('Imperial').get('Value') if IMPERIAL_SYSTEM else results[0].get('Temperature').get('Metric').get('Value')
        except (ConnectionError, JSONDecodeError, KeyError) as ex:
            print(ex)
            weather_icon_num = -1

        # Wait for defined interval before repeating
        time.sleep(FETCH_WEATHER_DATA_INTERVAL)


# Thread for fetching sunrise and sunset data
def fetch_sunrise_data_thread():
    global brightness_levels

    # Define API call for sunrise info
    param_values = {
        'lat': LATITUDE,
        'lng': LONGITUDE,
        'formatted': 0
    }

    # Make the GET request, generate brightness levels, then wait before repeating
    while True:
        # Update parameter values with current day info
        utc_today = datetime.utcnow()
        param_values.update({
            'date': str(utc_today.year) + '-' + str(utc_today.month) + '-' + str(utc_today.day)
        })

        queries = convert_dict_to_query_str(param_values)
        resource_url = 'https://api.sunrise-sunset.org/json?' + queries

        try:
            response = requests.get(resource_url)
            results = json.loads(response.text).get('results')

            # Collect sunrise, sunset, and civil twilight begin and end times
            sun_times = [
                datetime.fromisoformat(results.get('civil_twilight_begin')).astimezone(tz=None),
                datetime.fromisoformat(results.get('sunrise')).astimezone(tz=None),
                datetime.fromisoformat(results.get('sunset')).astimezone(tz=None),
                datetime.fromisoformat(results.get('civil_twilight_end')).astimezone(tz=None)
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
        except (ConnectionError, JSONDecodeError, KeyError) as ex:
            print(ex)

        # Wait for defined interval before repeating
        time.sleep(FETCH_SUNRISE_DATA_INTERVAL)


# Function that draws a pattern defined in a 2D array
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


# Define function to draw the temperature
def draw_temperature():
    
    # Cast temperature value to a string
    if weather_temp is None:
        temp_string = "-"
        temp_starting_x = int((width - 6) / 2)

        # Draw hyphen
        draw_pattern(temp_starting_x, clock_y, HYPHEN_PATTERN, TEMPERATURE_COLOR)
    else:
        temp_string = str(int(weather_temp))
        temp_starting_x = int((width - ((len(temp_string) * 4) + 2)) / 2)

        # Draw temperature digits
        for i in range(len(temp_string)): 
            draw_pattern(temp_starting_x + (i * 4), clock_y, NUMBER_PATTERNS[int(temp_string[i])], TEMPERATURE_COLOR)

    # Draw degree symbol
    draw_pattern(temp_starting_x + ((len(temp_string)) * 4), clock_y, DEGREE_PATTERN, TEMPERATURE_COLOR)

# Define function to draw the clock
def draw_clock():
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
            draw_pattern(0 + clock_hour_x_offset, clock_y, NUMBER_PATTERNS[int(hour_str[0])])
    else:
        draw_pattern(0 + clock_hour_x_offset, clock_y, NUMBER_PATTERNS[int(hour_str[0])])
    draw_pattern(4 + clock_hour_x_offset, clock_y, NUMBER_PATTERNS[int(hour_str[1])])

    # Draw minute digits
    draw_pattern(9, clock_y, NUMBER_PATTERNS[int(minute_str[0])])
    draw_pattern(13, clock_y, NUMBER_PATTERNS[int(minute_str[1])])

    # Draw colon
    if draw_colon:
        if not BLINKING_COLON or second % 2 == 0:
            draw_pattern(6, clock_y, COLON_PATTERN)


# Define function to draw weather icon
def draw_weather_icon(x, y):
    image_array = weather_icon_dict[weather_icon_num]
    frame_index = ticks % len(image_array)
    frame_array = image_array[frame_index]

    for px in range(len(frame_array)):
        for py in range(len(frame_array[px])):
            pixel = frame_array[px][py]
            r, g, b, a = int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3])

            if a != 0:
                converted_x = y + py
                converted_y = x + px

                if converted_x in range(width) and converted_y in range(height):
                    unicornhathd.set_pixel(converted_x, converted_y, r, g, b)


###############################################################################
# Execute functions
###############################################################################
try:
    # Set display rotation
    unicornhathd.rotation(DISPLAY_ROTATION)

    # Start thread to manage fetching data
    brightness_levels = [MIN_BRIGHTNESS] * 288
    if WEATHER_ENABLED:
        weather_icon_dict = load_images('weather-icons')
        weather_icon_num = 0
        weather_temp = None
        thread.start_new_thread(fetch_weather_data_thread, ())
    if SUNRISE_ENABLED:
        thread.start_new_thread(fetch_sunrise_data_thread, ())

    # Draw and update loop
    while True:
        # Clear hat
        unicornhathd.clear()

        # Get the time
        current = datetime.now()
        hour = current.hour
        minute = current.minute
        second = current.second

        # Calculate brightness index and set brightness
        brightness_index = int((hour * 12) + (minute / 5))
        if brightness_index in range(len(brightness_levels)):
            unicornhathd.brightness(brightness_levels[brightness_index])

        # Draw clock or temperature
        if WEATHER_ENABLED and SHOW_TEMPERATURE and ticks % 50 < 25:
            draw_temperature()
        else:
            draw_clock()

        # Draw weather image
        if WEATHER_ENABLED:
            draw_weather_icon(3, 0)

        # Send buffer to the Unicorn HAT HD for showing
        unicornhathd.show()

        ticks += 1
        time.sleep(SPF)

# Ctrl-C
except KeyboardInterrupt:
    print('Keyboard interrupt detected. Turning off Unicorn HAT HD.')
    unicornhathd.off()
except BaseException:
    print('Unknown error. Restarting.')
    os.execv(sys.executable, ['python'] + sys.argv)
