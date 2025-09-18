import os
import sys
import json

# Default settings
DEFAULTS = {
    "clock": {
        "12hrFormat": True,
        "demo": False,
        "omitLeadingZeros": True,
        "color": [255, 255, 255],
        "retryInterval": 60,
    },
    "led": {
        "fps": 10,
        "minBrightness": 0.1,
        "maxBrightness": 1.0,
        "rotation": 0,
    },
    "weather": {
        "enabled": False,
        "updateInterval": 1800,
        "retryInterval": 60,
    },
    "sunrise": {
        "enabled": False,
        "updateInterval": 86400,
        "retryInterval": 60,
    },
    "location": {
        "latitude": 0,
        "longitude": 0,
    }
}

options = {}
clock_options = {}
led_options = {}
weather_options = {}
sunrise_options = {}
location_options = {}


def deep_update(defaults, overrides):
    result = defaults.copy()
    for key, value in overrides.items():
        if isinstance(value, dict) and key in result:
            result[key] = deep_update(result[key], value)
        else:
            result[key] = value
    return result


def load_options():
    global options
    global clock_options, led_options, weather_options, sunrise_options, location_options

    options_path = os.path.join(sys.path[0], "..", "config", "options.json")

    if os.path.exists(options_path):
        with open(options_path, "r") as options_file:
            try:
                user_options = json.load(options_file)
                options = deep_update(DEFAULTS, user_options)
            except json.JSONDecodeError:
                print("[Options] Error parsing options.json, using defaults")
                options = DEFAULTS.copy()
    else:
        print("[Options] options.json not found, using defaults")
        options = DEFAULTS.copy()

    clock_options = options.get('clock')
    led_options = options.get('led')
    weather_options = options.get('weather')
    sunrise_options = options.get('sunrise')
    location_options = options.get('location')

    print("[Options] Loaded")


load_options()
