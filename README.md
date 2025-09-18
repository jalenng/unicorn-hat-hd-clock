# Unicorn HAT HD Clock

Digital clock with weather status on a [Pimoroni Unicorn HAT HD](https://shop.pimoroni.com/en-us/products/unicorn-hat-hd) for the Raspberry Pi

This script relies on:

- [Open-Meteo](https://open-meteo.com) for weather data
- [Sunrise Sunset](https://sunrise-sunset.org/api) for brightness adjustment based on sunrise and sunset times

## Preview

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

## 1. Install

```bash
git clone https://github.com/jalenng/unicorn-hat-hd-clock.git
cd unicorn-hat-hd-clock
pip3 install -r requirements.txt
# for simulator support (https://github.com/jayniz/unicorn-hat-sim)
pip3 install -r requirements-sim.txt
```

## 2. Configure

Edit `config/options.json` to customize:

### `clock`

| Name               | Default         | Description                                     |
| :----------------- | :-------------- | :---------------------------------------------- |
| `12hrFormat`       | `true`          | `true` = 12-hour (AM/PM), `false` = 24-hour     |
| `demo`             | `false`         | Cycles through icons/time faster (testing mode) |
| `omitLeadingZeros` | `true`          | Drop leading zero in hours (`09 → 9`)           |
| `color`            | `[255,255,255]` | RGB values (0–255) for clock digits             |
| `retryInterval`    | `60`            | Seconds between retry attempts if API fails     |

### `led`

| Name            | Default | Description                       |
| :-------------- | :------ | :-------------------------------- |
| `fps`           | `10`    | Display refresh rate              |
| `minBrightness` | `0.1`   | Brightness at night (0.0–1.0)     |
| `maxBrightness` | `1.0`   | Brightness at day (0.0–1.0)       |
| `rotation`      | `0`     | Screen rotation (0, 90, 180, 270) |

### `weather`

| Name             | Default | Description                    |
| :--------------- | :------ | :----------------------------- |
| `enabled`        | `false` | `true` = show weather info     |
| `updateInterval` | `1800`  | Seconds between API calls      |
| `retryInterval`  | `60`    | Seconds between retry attempts |

### `sunrise`

| Name             | Default | Description                                                                                                                 |
| :--------------- | :------ | :-------------------------------------------------------------------------------------------------------------------------- |
| `enabled`        | `false` | `true` = auto-adjust brightness with sunrise/sunset, `false` = constant average between `minBrightness` and `maxBrightness` |
| `updateInterval` | `86400` | Seconds between API calls                                                                                                   |
| `retryInterval`  | `60`    | Seconds between retry attempts                                                                                              |

### `location`

| Name        | Default | Description                                              |
| :---------- | :------ | :------------------------------------------------------- |
| `latitude`  | `0`     | **Required for weather and sunrise/sunset calculations** |
| `longitude` | `0`     | **Required for weather and sunrise/sunset calculations** |

## 3. Run

```bash
python3 src/main.py
```

## 4. Run on startup

Create `/etc/systemd/clock.service`:

```ini
[Unit]
Description=Unicorn HAT HD Clock
Before=multi-user.target

[Service]
ExecStart=python3 <full path to src/main.py> # Update this path!
Type=simple
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable it:

```bash
sudo systemctl enable /etc/systemd/clock.service
```
