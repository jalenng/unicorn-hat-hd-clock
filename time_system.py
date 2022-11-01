import os
import time
import _thread as thread
from datetime import datetime
from options import clock_options

time_updated = False


def get_time_updated():
    return time_updated


def get_time():
    if (clock_options.get('demo', False)):
        # Speed up time
        modded_time = time.time() % 86400
        return datetime.fromtimestamp(modded_time * 600)
    else:
        # Use real time
        return datetime.now()


def update_time():
    global time_updated

    # Try to update the time from the NTP server
    while not time_updated:
        if (os.system('ntpdate -u pool.ntp.org') == 0):
            time_updated = True
        else:
            time.sleep(60)


thread.start_new_thread(update_time, ())