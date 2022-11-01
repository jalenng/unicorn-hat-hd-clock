# Unicorn HAT HD Clock
Digital clock with weather status on a Pimoroni Unicorn HAT HD for the Raspberry Pi

This script relies on:
- AccuWeather to retrieve weather information
- https://sunrise-sunset.org/api for sunrise and sunset information to adjust the brightness accordingly
## GIFs
![GIF of the clock](https://user-images.githubusercontent.com/42555186/199179508-c477e8ba-bc36-42db-8626-b16badf9cce3.gif)

![sun](https://user-images.githubusercontent.com/42555186/199180158-473950e8-c768-409e-b6e2-1d3ade414937.gif)
![sun and cloud](https://user-images.githubusercontent.com/42555186/199180157-f90b5b6f-f507-46f1-b067-a293b8da0c1d.gif)
![clouds](https://user-images.githubusercontent.com/42555186/199180140-f91f2515-b1ab-449a-9f8a-f64a8f65c585.gif)
![fog](https://user-images.githubusercontent.com/42555186/199180143-5308898e-13d8-49e8-ae47-844d671205cf.gif)

![rain](https://user-images.githubusercontent.com/42555186/199181173-a0a867d2-9467-4707-90b6-c2b8b24f3dc0.gif)
![rain and cloud](https://user-images.githubusercontent.com/42555186/199180153-8236f758-2eba-4114-a35e-90b9b8658366.gif)
![storm](https://user-images.githubusercontent.com/42555186/199180156-16c4ccbc-7ae6-421d-b07d-8632c265a1ae.gif)
![snow](https://user-images.githubusercontent.com/42555186/199181172-3094c16e-c484-46c7-98a2-91471df33923.gif)

![snow and cloud](https://user-images.githubusercontent.com/42555186/199180154-aa802605-3d4f-425a-861b-2b44486a0f13.gif)
![hot](https://user-images.githubusercontent.com/42555186/199180144-f32f8954-738c-4e5a-a583-e600b7d0bf30.gif)
![cold](https://user-images.githubusercontent.com/42555186/199187852-03e96545-953c-44c5-8e05-5bcfe106581d.png)
![wind](https://user-images.githubusercontent.com/42555186/199180136-f6d820ad-29f4-4870-92c9-745b2c409eab.gif)

![moon](https://user-images.githubusercontent.com/42555186/199187848-6083a6fb-1cfc-48cf-abca-75338f910156.png)
![moon and cloud](https://user-images.githubusercontent.com/42555186/199187842-43ee1913-e857-4e8c-af0b-c2e6068faf5a.gif)
![loading](https://user-images.githubusercontent.com/42555186/199180147-481e3ec5-8e48-4521-807d-4b488770900e.gif)
![disconnected](https://user-images.githubusercontent.com/42555186/199188347-52d12ed5-3178-4f85-be34-b1087ac828ad.gif)

## Instructions
### I. Download the required files
1. Clone this repository
    - `git clone https://github.com/jalenng/unicorn-hat-hd-clock.git`
2. Ensure you have Python 3 installed
    - `python3 --version`
3. Install the required dependencies:
    - `pip install -r requirements.txt`
    - `pip install -r requirements-sim.txt` (if using the [simulator](https://github.com/jayniz/unicorn-hat-sim))
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
        | `demo`            | `false`           | If `true`, the time is sped up, and the screen cycles through the various icons
        | `omitLeadingZeros`| `true`            | If `true`, the leading zeroes of the hour are dropped. Otherwise, include the leading zeros.
        | `color`           | `[255, 255, 255]` | An array of values in RGB order. Determines the color of the clock.
    - `led`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `fps`             | `10`              | Desired framerate of the screen
        | `minBrightness`   | `0.004`           | A float between 0.0 and 1.0 that determines the brightness of the screen during the night
        | `maxBrightness`   | `0.5`             | A float between 0.0 and 1.0 that determines the brightness of the screen during the day
        | `rotation`        | `180`             | Rotation of the screen
    - `weather`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `enabled`         | `true`            | If `true`, shows and updates weather information
        | `apiKey`          | N/A               | **Important:** Insert your AccuWeather API key here 
        | `locationKey`     | N/A               | **Important:** Insert your AccuWeather location key here
        | `updateInterval`  | `1800`            | Time in seconds between API calls to get weather data
    - `sunrise`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `enabled`         | `true`            | If `true`, updates display brightness according to sunset and sunrise information. Otherwise, display brightness will constantly be at the average of `minBrightness` and `maxBrightness`
        | `latitude`        | N/A               | **Important:** Insert your latitude for sunrise/sunset data
        | `longitude`       | N/A               | **Important:** Insert your longitude for sunrise/sunset data
        | `updateInterval`  | `86400`           | Time in seconds between API calls to get sunset/sunrise data
3. Save your changes to the file
### IV. Run the script
- Run the script to make sure everything is working as intended.
    - e.g. `python3 main.py`
### V. Schedule the script to run on startup
1. Open the file `/etc/rc.local` with a text editor
    - e.g. `sudo nano /etc/rc.local`
2. Before the line that says `exit 0`, add the line `python3 <path to main.py> &`
    - e.g. `python3 /home/pi/unicorn-hat-hd-clock/main.py &`
    - Be sure to include the `&` at the end
3. Save your changes to the file
