# Unicorn HAT HD Clock
Digital clock with weather status on a Pimoroni Unicorn HAT HD for the Raspberry Pi

This script relies on:
- `options.json` to store options
- weather-icons to store the animated icons in a single-column .png file of 10x10px frames
- AccuWeather to retrieve weather information
- https://sunrise-sunset.org/api for sunrise and sunset information to adjust the brightness accordingly
## GIF
![GIF of the clock](https://i.imgur.com/lmB21bL.gif)
## Instructions
### I. Download the required files
1. Clone this repository
    - `git clone https://github.com/jalenng/unicorn-hat-hd-clock.git`
2. Ensure you have Python 3 installed
    - `python3 --version`
3. Install the required dependencies:
    - numpy (`pip install numpy`)
    - requests (`pip install requests`)
    - PIL (`pip install PIL`)
### II. Configure AccuWeather
- You will need an AccuWeather API account to get an API key: https://developer.accuweather.com/.
- Find the AccuWeather location key for your location.
### III. Configure the options
1. Open the file `options.json` with a text editor
2. Make the desired edits to the file
    - `clock`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `12hrFormat`      | `true`            | If `true`, clock displays in 12-hour time. Otherwise, clock displays in 24-hour time.
        | `omitLeadingZeros`| `true`            | If `true`, the leading zeroes of the hour are dropped. Otherwise, include the leading zeros
        | `blinkingColon`   | `true`            | If `true`, the colon cycles on and off every second. Otherwise, the colon is always on. This attribute is effective only if both `12hrFormat` and `omitLeadingZeros` are `true`.
        | `color`           | `[255, 255, 0]`   | An array of values in RGB order. Determines the color of the clock.
    - `display`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `rotation`        | `180`             | Rotation of the screen
        | `minBrightness`   | `0.004`           | A float between 0.0 and 1.0 that determines the brightness of the screen during the night
        | `maxBrightness`   | `0.5`             | A float between 0.0 and 1.0 that determines the brightness of the screen during the day
        | `secondsPerFrame` | `0.1`             | The duration of each frame. The higher the number, the slower the animation.
    - `weather`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `enabled`         | `true`            | If `true`, shows and updates weather information
        | `apiKey`          | N/A               | **Important:** Insert your AccuWeather API key here 
        | `locationKey`     | N/A               | **Important:** Insert your AccuWeather location key here
        | `updateInterval`  | `1800`            | Time in seconds between API calls to get weather data
        | `showTemperature` | `true`            | If `true`, the clock will cycle between the time and temperature. This attribute is effective only if `enabled` is `true`.
        | `temperatureColor`| `[255, 128, 0]`   | An array of values in RGB order. Determines the color of the temperature.
        | `imperialSystem`  | `true`            | If `true`, the temperature is displayed in Fahrenheit. Otherwise, the temperature is displayed in Celsius.
    - `sunrise`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `enabled`         | `true`            | If `true`, updates display brightness according to sunset and sunrise information. Otherwise, display brightness will be constantly at `minBrightness`
        | `latitude`        | N/A               | **Important:** Insert your latitude for sunrise/sunset data
        | `longitude`       | N/A               | **Important:** Insert your longitude for sunrise/sunset data
        | `updateInterval`  | `86400`           | Time in seconds between API calls to get sunset/sunrise data
3. Save your changes to the file
### IV. Run the script
- Run the script to make sure everything is working as intended.
    - e.g. `python3 <path to clock.py>`
### V. Schedule the script to run on startup
1. Open the file `/etc/rc.local` with a text editor
    - e.g. `sudo nano /etc/rc.local`
2. Before the line that says `exit 0`, add the line `python3 <path to clock.py> &`
    - e.g. `python3 /home/pi/unicorn-hat-hd-clock/clock.py &`
    - Be sure to include the `&` at the end
3. Save your changes to the file
