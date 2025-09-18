from enum import Enum

class Sprite(Enum):
    NOTHING = "nothing"
    DISCONNECTED = "disconnected" # currently unused
    LOADING = "loading" # currently unused
    SUN = "sun"
    SUN_AND_CLOUD = "sun and cloud"
    SUN_AND_HAZE = "sun and haze" # currently unused
    CLOUDS = "clouds"
    FOG = "fog"
    RAIN = "rain"
    RAIN_AND_CLOUD = "rain and cloud"
    STORM = "storm"
    SNOW = "snow"
    SNOW_AND_CLOUD = "snow and cloud"
    HOT = "hot" # currently unused
    COLD = "cold" # currently unused
    WIND = "wind" # currently unused
    MOON = "moon"
    MOON_AND_CLOUD = "moon and cloud"
    MOON_AND_HAZE = "moon and haze" # currently unused