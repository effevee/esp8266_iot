# Pins
DHT11_GPIO = 5
SCL_GPIO = 14
SDA_GPIO = 2

# OLED
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Localtime
DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
TIMEZONE = 1                    # UTC+1 hour
DAYLIGHT_SAVING_TIME = True     # +1 hour between last sunday of March 2AM and last sunday of October 3AM

# intervals (seconds)
NTP_INTERVAL = 7200      # 2 hours
DHT_INTERVAL = 5
OLED_INTERVAL = 15

# Debug
DEBUG = True

# WLAN credentials
WIFI_SSID = "<your wifi ssid>"
WIFI_PW = "<your wifi password>"
WIFI_RETRIES = 10
