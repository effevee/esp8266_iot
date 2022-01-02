# Pins
DHT11_GPIO = 2
SCL_GPIO = 5
SDA_GPIO = 4

# OLED
OLED_WIDTH = 64
OLED_HEIGHT = 48

# Localtime
DOW = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
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
