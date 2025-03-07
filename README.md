# Unicorn HAT HD Clock
Digital clock with weather status on a Pimoroni Unicorn HAT HD for the Raspberry Pi

This script relies on:
- AccuWeather to retrieve weather information
- https://sunrise-sunset.org/api for sunrise and sunset information to adjust the brightness accordingly
## GIFs
![Photo of the clock](https://github.com/user-attachments/assets/63523a04-2027-4ba8-a1f9-cef3b82d814c)

![wind](https://github.com/user-attachments/assets/1e3cdf90-f307-4104-978f-d70bd5065171)
![sun](https://github.com/user-attachments/assets/d5dd5a09-81a2-40c8-a3c5-a41aafacf408)
![sun and haze](https://github.com/user-attachments/assets/745e455f-a051-4a81-9e9e-31946dee1600)
![sun and cloud](https://github.com/user-attachments/assets/800cd348-151d-4a20-bb9c-f95af148974f)
![storm](https://github.com/user-attachments/assets/56313ad1-64d2-4c0b-bec0-efe25e2d680f)
![snow](https://github.com/user-attachments/assets/2f21bfa4-db4c-4f1f-8d64-c6fe366b81c7)
![snow and cloud](https://github.com/user-attachments/assets/150a68f6-2b82-435e-a63c-084ab05e6186)
![rain](https://github.com/user-attachments/assets/bb5672d2-a7c5-493a-993c-11eb6b4e551c)
![rain and cloud](https://github.com/user-attachments/assets/d5c8da42-6f6b-4343-9fa0-5b367b99c3f1)
![moon](https://github.com/user-attachments/assets/1c1c9ec0-5c22-495e-adb9-4cc358a3063a)
![moon and haze](https://github.com/user-attachments/assets/766235b4-e0eb-4ba7-b348-f9074cf91cd5)
![moon and cloud](https://github.com/user-attachments/assets/b2953269-53ec-4d61-9bb7-bba69e12b2af)
![loading](https://github.com/user-attachments/assets/d2aa19eb-11bd-40f0-b981-f8c40b8108dc)
![hot](https://github.com/user-attachments/assets/2fbb64c5-0a72-43a7-b41a-3b48de6509de)
![fog](https://github.com/user-attachments/assets/c45ac345-1615-4db9-81d7-4184551c3c9f)
![disconnected](https://github.com/user-attachments/assets/4eb29f4f-30d7-43fc-9e17-c6c25952ff72)
![cold](https://github.com/user-attachments/assets/5fbc579d-75e7-4542-b8c9-ae6ab0c826dc)
![clouds](https://github.com/user-attachments/assets/5c29044c-39bd-4939-8cdc-ed4591a60242)

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
- You will need an AccuWeather API account to get an API key: https://developer.accuweather.com/
- Find the AccuWeather location key for your location
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
        | `retryInterval`   | `60`              | Time in seconds between retry attempts if the API call fails
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
        | `retryInterval`   | `60`              | Time in seconds between retry attempts if the API call fails
    - `sunrise`
        | Name              | Default Value     | Description       |
        | :---------------- | :---------------- | :---------------- |
        | `enabled`         | `true`            | If `true`, updates display brightness according to sunset and sunrise information. Otherwise, display brightness will constantly be at the average of `minBrightness` and `maxBrightness`
        | `latitude`        | N/A               | **Important:** Insert your latitude for sunrise/sunset data
        | `longitude`       | N/A               | **Important:** Insert your longitude for sunrise/sunset data
        | `updateInterval`  | `86400`           | Time in seconds between API calls to get sunset/sunrise data
        | `retryInterval`   | `60`              | Time in seconds between retry attempts if the API call fails
3. Save your changes to the file
### IV. Run the script
- Run the script to make sure everything is working as intended
    - `python3 main.py`
### V. Schedule the script to run on startup
We will use systemd to run this script on startup as a background process

1. Create a file called `clock.service` with a text editor in `/etc/systemd/system`
    - e.g. `sudo touch /etc/systemd/system/clock.service`
2. Open the file you just created
    - e.g. `sudo nano /etc/systemd/system/clock.service`
3. Create the service file. Use this as an example:
    ```
    [Unit]
    Description=Unicorn HAT HD Clock
    Before=multi-user.target

    [Service]
    ExecStart=python3 <path to main.py>
    Type=simple
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
3. Enable the service
    - `sudo systemctl enable /etc/systemd/system/clock.service`
