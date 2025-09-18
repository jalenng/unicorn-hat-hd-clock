import os
import sys
import time
from time_system import get_time, get_time_updated
from sprite_cache import cache, import_sprite
from led import draw_frame, loop_draw, set_px
from weather import get_weather_sprite
from options import clock_options
from sprite_enum import Sprite

frame_rate = {
    Sprite.DISCONNECTED: 1,
    Sprite.LOADING: 6,
    Sprite.SUN: 0.5,
    Sprite.SUN_AND_CLOUD: 0.5,
    Sprite.SUN_AND_HAZE: 0.5,
    Sprite.CLOUDS: 0.5,
    Sprite.FOG: 0.5,
    Sprite.RAIN: 6,
    Sprite.RAIN_AND_CLOUD: 6,
    Sprite.STORM: 6,
    Sprite.SNOW: 2,
    Sprite.SNOW_AND_CLOUD: 2,
    Sprite.HOT: 6,
    Sprite.COLD: 12,
    Sprite.WIND: 6,
    Sprite.MOON: 0,
    Sprite.MOON_AND_CLOUD: 0.5,
    Sprite.MOON_AND_HAZE: 0,
}

TWELVE_HR_FORMAT = clock_options.get('12hrFormat')
OMIT_LEADING_ZERO = clock_options.get('omitLeadingZeros')
DEMO = clock_options.get('demo')
COLOR = clock_options.get('color')

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
    origin = (2, 3)
    if not (OMIT_LEADING_ZERO and int(hour_str[0]) == 0):
        draw_frame(cache['digits'][int(hour_str[0])], origin[0], origin[1], filters)
    draw_frame(cache['digits'][int(hour_str[1])], origin[0] + 6, origin[1], filters)

    # Draw minute digits
    draw_frame(cache['digits'][int(minute_str[0])], origin[0], origin[1] + 6, filters)
    draw_frame(cache['digits'][int(minute_str[1])], origin[0] + 6, origin[1] + 6, filters)


def draw_weather():
    # Get sprite
    if (DEMO):
        sprite_index = int((time.time() / 5) % len(cache.keys()))
        sprite_name_value = list(cache.keys())[sprite_index]
        sprite_name = Sprite(sprite_name_value)
    else:
        sprite_name = get_weather_sprite()

    weather_sprite = cache.get(sprite_name.value, None)
    if weather_sprite is None or len(weather_sprite) == 0:
        return

    # Get frame
    ticks = int(time.time() * frame_rate.get(sprite_name, 1))
    frame_index = ticks % len(weather_sprite)

    draw_frame(weather_sprite[frame_index], 0, 0)


def draw_blinker():
    ticks = get_time().second % 2 == 0
    if ticks % 2 == 0:
        if get_time_updated():
            color = [128, 128, 128]
        else:
            color = [128, 0, 0] # red

        filters = [('multiply', color)]
        draw_frame(cache['digits'][10], -2, 9, filters)


def draw():
    draw_weather()
    draw_blinker()
    draw_time()


if __name__ == '__main__':

    # Import sprites
    digits_path = os.path.join(sys.path[0], '..', 'sprites', 'digits.png')
    import_sprite(digits_path, (8, 8), 1)

    sprites_path = os.path.join(sys.path[0], '..', 'sprites', 'weather_icons')
    sprites_list = os.listdir(sprites_path)

    for filename in sprites_list:
        sprite_path = os.path.join(sprites_path, filename)
        import_sprite(sprite_path, (9, 9))

    # Start the draw loop
    loop_draw(draw)
