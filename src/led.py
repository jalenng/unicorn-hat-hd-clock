from copy import deepcopy
import time
from sunrise import get_brightness_level
from options import led_options

try:
    import unicornhathd as hat
    print('[LED] Unicorn HAT HD module found.')
except ImportError:
    from unicorn_hat_sim import unicornhathd as hat
    print('[LED] Unicorn HAT HD simulator module found.')

width, height = hat.get_shape()

buffer = []
old_buffer = []


def map_coords(x, y):
    return (width - x - 1, y)


def setup():
    global buffer, old_buffer
    clear()
    old_buffer = deepcopy(buffer)


def draw_frame(frame, x, y, filters=[]):
    for y2 in range(len(frame)):
        for x2 in range(len(frame[y2])):

            # Check for out of bounds
            xx2, yy2 = x + x2, y + y2
            if not in_bounds(xx2, yy2):
                continue

            old_px = buffer[yy2][xx2]

            in_rgb = apply_filters(frame[y2][x2][:3], filters)
            in_alpha = frame[y2][x2][3]

            if in_alpha == 0:
                continue
            elif in_alpha == 255:
                add_px = in_rgb
                old_px = [0, 0, 0]
            else:
                in_alpha_decimal = float(in_alpha_decimal) / 255
                add_px = [int(val * in_alpha_decimal) for val in in_rgb]
                old_px = [int(val * (1 - in_alpha_decimal)) for val in old_px]

            new_px = [old + new for old, new in zip(old_px, add_px)]
            new_px = [min(max(val, 0), 255) for val in new_px]

            buffer[yy2][xx2] = new_px


def apply_filters(in_rgb, filters):
    for blend_mode, f_rgb in filters:
        if blend_mode == 'multiply':
            in_rgb = [int(x * (y / 255)) for x, y in zip(in_rgb, f_rgb)]
    return in_rgb


def set_px(x, y, color, filters=[]):
    if in_bounds(x, y):
        buffer[y][x] = apply_filters(color, filters)


def in_bounds(x, y):
    return not (x < 0 or x >= width or y < 0 or y >= height)


def clear():
    global buffer
    buffer = [[[0, 0, 0] for _ in range(width)] for y in range(height)]
    hat.clear()


def show():
    global old_buffer
    for y in range(height):
        for x in range(width):
            px = [(int((buffer[y][x][i] + old_buffer[y][x][i])) / 2)
                for i in range(3)]
            hat.set_pixel(*map_coords(x, y), *px)

    hat.show()

    old_buffer = deepcopy(buffer)


def off():
    hat.off()


def set_brightness(level):
    min_val = led_options.get('minBrightness')
    max_val = led_options.get('maxBrightness')
    brightness = min_val + ((max_val - min_val) * level)
    hat.brightness(brightness)


time_behind = 0
time_behind_max = 0.5


def loop_draw(draw_func):
    global time_behind

    secs_per_frame = 1 / led_options.get('fps')
    try:
        while True:
            loop_start_time = time.time()

            clear()
            set_brightness(get_brightness_level())
            draw_func()
            show()

            # Calculate how long we have left in the loop to sleep
            loop_finish_time = time.time()
            loop_duration = loop_finish_time - loop_start_time
            sleep_duration = secs_per_frame - loop_duration

            # Ensure consistent frame rate
            if sleep_duration >= time_behind:
                sleep_duration -= time_behind
                time_behind = 0
            else:
                time_behind -= sleep_duration
                time_behind = min(time_behind, time_behind_max)
                sleep_duration = 0

            time.sleep(sleep_duration)

    except KeyboardInterrupt:
        off()


hat.rotation(led_options.get('rotation'))
setup()
