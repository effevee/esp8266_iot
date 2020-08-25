'''

Geekcreit® ESP8266 IoT Development Board + DHT11 Temperature and Humidity Sensor + Yellow Blue OLED Display
 - connect to Wifi
 - fetch the UTC date & time from an NTP server every 6 hours
 - update the ESP8266 RTC with the correct local time
 - measure temperature and humidity every 5 seconds
 - show temperature, humidity, date and time on the OLED display every second

'''

# modules
from machine import Pin, I2C
import network
import secrets
import ntptime
import dht
import ssd1306
import uasyncio as asyncio
import utime

# constants
DHT11_GPIO = 5
SCL_GPIO = 14
SDA_GPIO = 2
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_ADDR = 0x3C
GMT_DST = 2     # localtime = GMT + GMT_DST hours (ex. GMT+2)
DOW = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
DEBUG = True


# global variables
class myGlobals:
    now = None
    temp = 0
    hum = 0
    

# coroutine to update RTC with UTC time from ntp server
async def updateRTC():
    ntp_interval = 6 * 60 * 60 # seconds
    wlan = None
    # loop
    while True:
        try:
            # connect to Wifi
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            if not wlan.isconnected():
                retries = 0
                print('Trying to connect to wireless network...')
                wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PW)
                while not wlan.isconnected():
                    retries += 1
                    await asyncio.sleep_ms(500)
                    if retries < secrets.WIFI_RETRIES:
                        pass
                    else:
                        break
            if wlan.isconnected():
                print('network config:', wlan.ifconfig())
                # set UTC time from ntpserver into RTC
                await asyncio.sleep_ms(500)
                ntptime.settime()
                # disconnect Wifi
                wlan.disconnect()
            else:
                print('Could not connect to wireless network')
            # wait for next RTC update
            await asyncio.sleep(ntp_interval)
        
        except Exception as E:
            print('Wifi error: ', E)


# coroutine DHT11 measurement
async def measureDHT():
    dht_interval = 5 # seconds
    # loop
    while True:
        # read DHT11 sensor
        sensor.measure()
        # save values in global vars
        myGlobals.temp = sensor.temperature()
        myGlobals.hum = sensor.humidity()
        # debug output
        if DEBUG:
            print('Temp: {:2d}C - Hum: {:2d}%'.format(myGlobals.temp, myGlobals.hum))
        # wait for next measurement
        await asyncio.sleep(dht_interval)
    

# coroutine refresh OLED display
async def refreshOLED():
    oled_interval = 1 # second
    # loop
    while True:
        # get local time corrected with Daylight Savings Time/Summer Time
        lt = utime.localtime(utime.mktime(utime.localtime()) + GMT_DST*3600)
        # save localtime in global vars
        myGlobals.now = lt
        # format strings to be displayed
        line1 = 'Temp {:2d}C Hum {:2d}%'.format(myGlobals.temp, myGlobals.hum)
        line2 = DOW[int(lt[6])] + ' {:02d}/{:02d}/{:04d}'.format(lt[2], lt[1], lt[0])
        line3 = '    {:02d}:{:02d}:{:02d}'.format(lt[3], lt[4], lt[5])
        # show info on oled
        oled.fill(0)
        oled.text(line1, 0, 0)
        oled.text(line2, 0, 20)
        oled.text(line3, 0, 30)
        oled.show()
        # wait for next refresh
        await asyncio.sleep(oled_interval)


# instantiate objects
sensor = dht.DHT11(Pin(DHT11_GPIO))
i2c = I2C(scl=Pin(SCL_GPIO), sda=Pin(SDA_GPIO))
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr = OLED_ADDR)
    
try:
    # init event loop scheduler
    loop = asyncio.get_event_loop()
    # put tasks on event loop queue
    loop.create_task(updateRTC())
    loop.create_task(measureDHT())
    loop.create_task(refreshOLED())
    # execute tasks
    loop.run_forever()
    
except KeyboardInterrupt:
    print('Program halted')
    
except Exception as E:
    print('asyncio error: ', E)
    
finally:
    loop.close()
    oled.poweroff()
   