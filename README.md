# Unicorn HAT HD Clock
Digital clock with weather status on a Pimoroni Unicorn HAT HD for the Raspberry Pi
## Picture
![Picture of the clock](https://i.imgur.com/lmB21bL.gif)
## Instructions
### I. Download the required files
1. Clone this repository
    - `git clone https://github.com/jalenng/unicorn-hat-hd-clock.git`
2. Ensure you have Python installed
    - `python --version`
3. Install the required dependencies:
    - numpy (`pip install numpy`)
    - requests (`pip install requests`)
    - PIL (`pip install PIL`)
### II. Configure AccuWeather
- You will need an AccuWeather API account to get an API key: https://developer.accuweather.com/.
- Find the AccuWeather location key for your location.
### III. Configure the options
1. Open the file ``options.json`` with a text editor
2. Make the desired edits to the file
    - `clock`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `blinkingColon`   | `true`            | If `true`, the colon cycles on and off every second. If `false`, the colon is always on.
        | `color`           | `[255, 255, 0]`   | An array of values in RGB order. Determines the color of the clock.
    - `display`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `rotation`        | `180`             | Rotation of the screen
        | `minBrightness`   | `0.05`            | A float between 0.0 and 1.0 that determines the brightness of the screen during the night
        | `maxBrightness`   | `0.5`             | A float between 0.0 and 1.0 that determines the brightness of the screen during the day
        | `animationTPF`    | `6`               | The number of ticks per frame. The higher the number, the slower the animation.
    - `weather`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `enabled`         | `true`            | If `true`, shows and updates weather information
        | `locationKey`     | N/A               | **Important:** Insert your AccuWeather location key here
        | `updateInterval`  | `1800`            | Time in seconds between API calls to get weather data
        - `parameterValues` 
            | Name              | Default Value     | Description       |
            | :---------------- | :---------------- | :---------------- |
            | `apikey`          | N/A               | **Important:** Insert your AccuWeather API key here 
            | `language`        | `"en-us"`
            | `details`         | `true` 
3. Save your changes to the file
### IV. - Run the script
- Run the script to make sure everything is working as intended.
    - e.g. `python <path to clock.py>`
### V. Schedule the script to run on startup
1. Open the file `/etc/rc.local` with a text editor
    - e.g. `sudo nano /etc/rc.local`
2. Before the line that says `exit 0`, add the line `python <path to clock.py> &`
    - e.g. `python /home/pi/unicorn-hat-hd-clock/clock.py &`
    - Be sure to include the `&` at the end
3. Save your changes to the file
