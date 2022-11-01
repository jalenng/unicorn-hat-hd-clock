import os
import sys
import time
from time_system import get_time, get_time_updated
from sprite_cache import cache, import_sprite
from led import draw_frame, loop_draw, set_px
from weather import get_code
from options import clock_options

code_to_sprite = {
    -1: 'disconnected',
    0: 'loading',
    1: 'sun',
    2: 'sun',
    3: 'sun and cloud',
    4: 'sun and cloud',
    5: 'sun and haze',
    6: 'clouds',
    7: 'clouds',
    8: 'clouds',
    11: 'fog',
    12: 'rain',
    13: 'rain and cloud',
    14: 'rain and cloud',
    15: 'storm',
    16: 'storm',
    17: 'storm',
    18: 'rain and cloud',
    19: 'snow',
    20: 'snow and cloud',
    21: 'snow and cloud',
    22: 'snow',
    23: 'snow and cloud',
    24: 'snow',
    25: 'snow',
    26: 'snow',
    29: 'snow',
    30: 'hot',
    31: 'cold',
    32: 'wind',
    33: 'moon',
    34: 'moon',
    35: 'moon and cloud',
    36: 'moon and cloud',
    37: 'moon and haze',
    38: 'moon and cloud',
    39: 'rain and cloud',
    40: 'rain and cloud',
    41: 'storm',
    42: 'storm',
    43: 'snow',
    44: 'snow',
}

frame_rate = {
    'disconnected': 1,
    'loading': 10,
    'sun': 0.5,
    'sun and cloud': 0.5,
    'sun and haze': 0.5,
    'clouds': 0.25,
    'fog': 2,
    'rain': 5,
    'rain and cloud': 5,
    'storm': 10,
    'snow': 2,
    'snow and cloud': 2,
    'hot': 5,
    'cold': 5,
    'wind': 5,
    'moon': 5,
    'moon and cloud': 0.125,
    'moon and haze': 0.125,
}

TWELVE_HR_FORMAT = clock_options.get('12hrFormat', False)
OMIT_LEADING_ZERO = clock_options.get('omitLeadingZeros', False)
DEMO = clock_options.get('demo', False)
COLOR = clock_options.get('color', [255, 255, 255])

filters = [('multiply', COLOR)]


def draw_time():
    global TWELVE_HR_FORMAT, OMIT_LEADING_ZERO

    now = get_time()
    hour, minute = now.hour, now.minute

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
    hour_x_offset = 0
    if not (OMIT_LEADING_ZERO and int(hour_str[0]) == 0):
        draw_frame(cache['digits'][int(hour_str[0])],
                   9 + hour_x_offset, 5, filters)
    draw_frame(cache['digits'][int(hour_str[1])],
               13 + hour_x_offset, 5, filters)

    # Draw minute digits
    draw_frame(cache['digits'][int(minute_str[0])], 9, 11, filters)
    draw_frame(cache['digits'][int(minute_str[1])], 13, 11, filters)


def draw_weather():
    # Get sprite
    if (DEMO):
        sprite_index = int((time.time() / 5) % len(cache.keys()))
        sprite_name = list(cache.keys())[sprite_index]
    else:
        sprite_name = code_to_sprite.get(get_code(), None)

    weather_sprite = cache.get(sprite_name, None)
    if weather_sprite is None:
        return

    # Get frame
    ticks = int(time.time() * frame_rate.get(sprite_name, 1))
    frame_index = ticks % len(weather_sprite)

    draw_frame(weather_sprite[frame_index], 0, 0)


def draw_blinker():
    ticks = get_time().second % 2 == 0
    color = [0, 0, 0]
    if ticks % 2 == 0:
        if get_time_updated():
            color = [128, 128, 128]
        else:
            color = [255, 0, 0] # red
    set_px(0, 15, color, filters)


def draw():
    draw_time()
    draw_weather()
    draw_blinker()


if __name__ == '__main__':

    # Import sprites
    digits_path = os.path.join(sys.path[0], 'sprites', 'digits.png')
    import_sprite(digits_path, (3, 5), 1)

    sprites_path = os.path.join(sys.path[0], 'sprites', 'weather_icons')
    sprites_list = os.listdir(sprites_path)

    for filename in sprites_list:
        sprite_path = os.path.join(sprites_path, filename)
        import_sprite(sprite_path, (9, 9))

    # Start the draw loop
    loop_draw(draw)
