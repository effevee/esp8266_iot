//------------------------------------------------------------------------------------------------------------
// Geekcreit® ESP8266 IoT Development Board + DHT11 Temperature and Humidity Sensor + Yellow Blue OLED Display
// - connect to Wifi
// - fetch the UTC date & time from an NTP server every 2 hours
// - update the ESP8266 RTC with the correct local time
// - measure temperature and humidity every 5 seconds
// - show temperature, humidity, date and time on the OLED display every second
//------------------------------------------------------------------------------------------------------------

// libraries
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <ESP8266WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <TimeLib.h>

// My secret stuff (eg network credentials)
// #define "YOUR_SSID";
// #define "YOUR_PASSWORD";
#include "secrets.h"

// constants
#define DHTTYPE DHT11
#define DHT11_GPIO 5
#define SCL_GPIO 14
#define SDA_GPIO 2
#define OLED_WIDTH 128
#define OLED_HEIGHT 64
#define OLED_ADDR 0x3C

#define INTERVAL_RTC 7200*1000   // 2 hours
#define INTERVAL_DHT 5*1000      // 5 seconds
#define INTERVAL_OLED 1*1000     // 1 second

String DOW[7] = {"Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"};


// variables
unsigned long time_RTC = -INTERVAL_RTC;
unsigned long time_DHT = 0;
unsigned long time_OLED = 0;
int temp = 0;
int hum = 0;
time_t cdt = 0;     // current date time in built-in RTC


// instantiate objects
// ** NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "europe.pool.ntp.org");
// ** DHT sensor
DHT dht(DHT11_GPIO, DHTTYPE);
// ** OLED display
Adafruit_SSD1306 display(OLED_WIDTH, OLED_HEIGHT, &Wire, -1);


//------------------------------------------------------------------------------------------------------------
// setup code to run once
//------------------------------------------------------------------------------------------------------------

void setup() {
  
  // Initialise Serial Monitor
  Serial.begin(115200);
  
  // Initialise DHT11 sensor
  dht.begin();
  
  // Initialize I2C
  Wire.begin(SDA_GPIO, SCL_GPIO);

  // Initialise OLED display
  if(!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  delay(2000);
  display.clearDisplay();
  display.setTextColor(WHITE);

  // Connect to Wi-Fi network
  Serial.print("Connecting to ");
  Serial.println(_ssid);
  WiFi.begin(_ssid, _password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }

  // Initialize a NTPClient to get time
  timeClient.begin();

  // Set offset time in seconds to adjust for your timezone, for example: GMT +1 = 3600, GMT +8 = 28800, GMT -1 = -3600
  timeClient.setTimeOffset(3600);
}


//------------------------------------------------------------------------------------------------------------
// main code to be run repeatedly
//------------------------------------------------------------------------------------------------------------

void loop() {
  
  // schedule update RTC
  if (millis() >= time_RTC + INTERVAL_RTC) {
    time_RTC += INTERVAL_RTC;
    updateRTC();
  }
  
  // schedule DHT11 measurement
  if (millis() >= time_DHT + INTERVAL_DHT) {
    time_DHT += INTERVAL_DHT;
    measureDHT();
  }

  // schedule OLED display refresh
  if (millis() >= time_OLED + INTERVAL_OLED) {
    time_OLED += INTERVAL_OLED;
    refreshOLED();
  }

}


//------------------------------------------------------------------------------------------------------------
// update internal RTC with Daylight Saving Time
//------------------------------------------------------------------------------------------------------------

void updateRTC() {
  Serial.println("Updating RTC with Daylight Saving Time"); 

  // get time from ntp server
  timeClient.update();

  // get Epoch Time (seconds since 1 Jan 1900)
  unsigned long epochTime = timeClient.getEpochTime();

  // overlay with time structure
  struct tm *ptm = gmtime ((time_t *)&epochTime);

  // extract components
  int Hour = ptm->tm_hour;
  int Minute = ptm->tm_min;
  int Second = ptm->tm_sec;
  int Day = ptm->tm_mday;
  int Month = ptm->tm_mon+1;
  int Year = ptm->tm_year+1900;
  // int dayofweek = ptm->tm_wday;
  
  // set system date and time in RTC
  setTime(Hour, Minute, Second, Day, Month, Year);
}


//------------------------------------------------------------------------------------------------------------
// Measure temperature and humidity with DHT11
//------------------------------------------------------------------------------------------------------------

void measureDHT() {
  Serial.println("Measuring Temperature and Humidity"); 

  // read temperature and humidity
  temp = dht.readTemperature() + 0.5;
  hum = dht.readHumidity() + 0.5;
  if (isnan(hum) || isnan(temp)) {
    Serial.println("Failed to read from DHT sensor!");
  }
}


//------------------------------------------------------------------------------------------------------------
// Refresh the OLED display
//------------------------------------------------------------------------------------------------------------

void refreshOLED() {
  Serial.println("Refreshing OLED display");
  
  // get current date and time from RTC
  time_t cdt = now();
  
  // format date and time strings
  String currentDate = DOW[weekday(cdt)-1] + " " + twoDigits(day(cdt)) + "/" + twoDigits(month(cdt)) + "/" + year(cdt);
  String currentTime = twoDigits(hour(cdt)) + ":" + twoDigits(minute(cdt)) + ":" + twoDigits(second(cdt));
    
  // clear display
  display.clearDisplay();
  
  // display current date
  display.setTextSize(1);
  display.setCursor(0, 8);
  display.print(currentDate);   

  // display current time
  display.setTextSize(2);
  display.setCursor(0, 20);
  display.print(currentTime);   

  // display temperature and humidity
  display.setTextSize(3);
  display.setCursor(0, 43);
  display.print(temp);
  display.print("C ");
  display.print(hum);
  display.print("%"); 
  
  // show display
  display.display();
}


// helper function to insert leading zero for date/time strings
String twoDigits(int digits) {
  if (digits < 10) {
    return "0" + String(digits);
  }
  else {
    return String(digits);
  }
}
