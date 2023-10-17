'''

Ideaspark ESP8266 0.96" OLED + DHT11 Temperature and Humidity Sensor
 - connect to Wifi
 - fetch the UTC date & time from an NTP server and update the ESP8266 RTC with the correct local time (every 2 hours)
 - measure temperature and humidity (every 5 seconds)
 - show temperature, humidity, date and time on the OLED display (every 15 seconds)

'''

####################################################################################
# Modules
####################################################################################

from machine import Pin, I2C, RTC
import network
import config_ideaspark as config
import ntptime
import dht
import ssd1306
import uasyncio as asyncio
import utime
import freesans20
import freesans30
from writer_minimal import Writer


####################################################################################
# Global variables
####################################################################################

class myGlobals:
    temp = 0
    hum = 0
    

####################################################################################
# Synchronize RTC on µcontroller to local time
####################################################################################

async def updateRTC():
    ''' Update RTC after config.RTC_INTERVAL seconds :
           1) get UTC time from NTP server
           2) correct to localtime according to Timezone and Daylight Saving Time '''
    
    # loop
    while True:
        try:
            # enable STAtion mode
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            
            # not connected yet
            if not wlan.isconnected():
                
                # try to connect to WiFi network
                print('Trying to connect to wireless network...')
                wlan.connect(config.WIFI_SSID, config.WIFI_PW)
                
                # keep trying for number of times
                retries = 0
                while not wlan.isconnected() and retries < config.WIFI_RETRIES:
                    
                    # show progress
                    print('.', end='')
                    
                    # wait for 1 second
                    await asyncio.sleep_ms(1000)
                    
                    # update counter
                    retries += 1
                    
            if wlan.isconnected():
                
                # show IP address
                print('')
                print('connected to {} network with ip address {}' .format(config.WIFI_SSID, wlan.ifconfig()[0]))

                # RTC object
                rtc = RTC()
                
                # localtime tuple
                # (year, month, mday, hour, minute, second, weekday, yearday)
                #  20xx  1-12   1-31  0-23   0-59    0-59    0-6      1-366
                tm = utime.localtime()

                # debug message
                if config.DEBUG:
                    print('Current datetime: {}' .format(tm))
                    print('Synchronize with NTP server...')
                    
                # set UTC time from ntpserver into RTC
                await asyncio.sleep_ms(2000)
                ntptime.settime()

                # debug message
                if config.DEBUG:
                    print('NTP correction:   {}' .format(utime.localtime()))
                    
                # time zone correction
                # utime localtime -> (year, month, mday, hour, minute, second, weekday, yearday)
                tm = utime.localtime(utime.time() + (config.TIMEZONE * 3600))
                # rtc datetime    -> (year, month, mday, weekday, hour, minute, second, µseconds)
                rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
                
                # debug message
                if config.DEBUG:
                    print('TZ correction:    {}' .format(utime.localtime()))
                
                # Daylight Savings Time correction
                if config.DAYLIGHT_SAVING_TIME:
                        
                    # current year
                    year = utime.localtime()[0]
                    
                    # last Sunday March
                    HHMarch = utime.mktime((year, 3, (31-(int(5*year/4+4))%7), 2, 0, 0, 0, 0))
                    
                    # last Sunday October
                    HHOctober = utime.mktime((year, 10, (31-(int(5*year/4+1))%7), 3, 0, 0, 0, 0))
                    
                    # current time
                    curtime = utime.time()
                    
                    # correct local time
                    if (curtime >= HHMarch) and (curtime < HHOctober):

                        # utime localtime -> (year, month, mday, hour, minute, second, weekday, yearday)
                        tm = utime.localtime(curtime + 3600)
                        
                        # rtc datetime    -> (year, month, mday, weekday, hour, minute, second, µseconds)
                        rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
                        
                    # debug message
                    if config.DEBUG:
                        print('DST correction:   {}' .format(utime.localtime()))


                # disconnect Wifi
                wlan.disconnect()
            
            else:
                
                # not connected
                print('')
                print('Could not connect to wireless network')
            
            # wait for next RTC update
            await asyncio.sleep(config.NTP_INTERVAL)
        
        except Exception as E:
            print('Wifi error: ', E)


####################################################################################
# Get DHT11 sensor readings
####################################################################################

async def measureDHT():
    ''' do DHT measurements after config.DHT_INTERVAL seconds and save results in global variables '''

    # sensor object
    sensor = dht.DHT11(Pin(config.DHT11_GPIO))
    
    # loop
    while True:
        
        # read DHT11 sensor
        sensor.measure()
        
        # save values in global vars
        myGlobals.temp = sensor.temperature()
        myGlobals.hum = sensor.humidity()
        
        # debug output
        if config.DEBUG:
            print('Temp: {:2d}C - Hum: {:2d}%'.format(myGlobals.temp, myGlobals.hum))
        
        # wait for next measurement
        await asyncio.sleep(config.DHT_INTERVAL)
    

####################################################################################
# Update OLED display
####################################################################################

async def refreshOLED():
    ''' update OLED display after config.OLED_INTERVAL seconds '''

    # I2C object
    i2c = I2C(scl=Pin(config.SCL_GPIO), sda=Pin(config.SDA_GPIO))
    
    # check if OLED display is detected
    if 60 not in i2c.scan():
        raise RuntimeError('Cannot find OLED display')

    # OLED object
    oled = ssd1306.SSD1306_I2C(config.OLED_WIDTH, config.OLED_HEIGHT, i2c)
    
    # custom font writer object
    font_writer20 = Writer(oled, freesans20)
    font_writer30 = Writer(oled, freesans30)

    # loop
    while True:
        
        # get corrected local time
        year, month, day, hour, minute, second, dayofweek, dayofyear = utime.localtime()
        
        # clear oled
        oled.fill(0)
        
        # show date
        oled.text('{:02d}/{:02d}/{:04d}'.format(day, month, year), 20, 0)
        
        # show DOW and time
        font_writer20.set_textpos(15, 20)
        font_writer20.printstring('{} {:02d}:{:02d}'.format(config.DOW[dayofweek], hour, minute))
   
  
        # show sensor readings
        font_writer30.set_textpos(34, 0)
        font_writer30.printstring('{:2d}C {:2d}%' .format(myGlobals.temp, myGlobals.hum))
        
        # show info on oled
        oled.show()
        
        # wait for next refresh
        await asyncio.sleep(config.OLED_INTERVAL)


####################################################################################
# Main program
####################################################################################

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
   
