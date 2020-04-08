#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_MLX90614.h>
#include <max6675.h>

#define SERIAL_SPEED        9600          // Serial port speed
#define SERIAL_WAIT         100           // Serial port readiness waiting checkpoint
#define SERIAL_TIMEOUT      600           // timeout miliseconds; completing an approx. 1 second cycle

#define PAUSE               100

#define I2C_DISCOVER_WAIT   100      // ms delay after looking for I2C slaves
#define I2C_FIRST_ADDRESS   8        // address of the first slave in the I2C bus
#define I2C_MAX_SLAVES      120      // maximum number of slaves in an I2C bus
bool devices[I2C_MAX_SLAVES];        // array holding all the addresses found for the connected I2C devices

#define I2C_LCD_WAIT        100       // ms to wait for LCD to initialize
#define I2C_LCD_ADDR        0x3C      // LCD crystal screen
#define I2C_INA219_ADDR     0x40      // INA219 current sensor


int th_CLK = 13;
int th_SO = 12;     // Common data output
int th_1_CS = 11;   // Select output from first thermistor
int th_2_CS = 10;   // Select output from second thermistor


MAX6675 th_1(th_CLK, th_1_CS, th_SO);
MAX6675 th_2(th_CLK, th_2_CS, th_SO);

Adafruit_SSD1306 display(128, 64);
Adafruit_MLX90614 mlx90614 = Adafruit_MLX90614();


double ambienceT_degC = 0.0, objectT_degC = 0.0, plastic_degC = 0.0, metal_degC = 0.0;


void scanI2C() {
  byte count = 0;
  Wire.begin();

  for (byte i = I2C_FIRST_ADDRESS; i < I2C_MAX_SLAVES; i++) {
    Wire.beginTransmission (i);

    if (Wire.endTransmission () == 0) {
      Serial.print ("[info] Found address: "); Serial.print (i, DEC); Serial.print (" (0x"); Serial.print (i, HEX); Serial.println (")");
      devices[i] = true;
      count++;
      delay (I2C_DISCOVER_WAIT);
    }

  }

  Serial.print("Found "); Serial.print(count); Serial.println(" device(s)");

}


void setupLCD() {
  delay(I2C_LCD_WAIT);
  display.begin(SSD1306_SWITCHCAPVCC, I2C_LCD_ADDR);
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setRotation(0);
  display.setTextWrap(false);
  display.dim(0);
}


void setupMLX90614() {
  mlx90614.begin();
}



void measureThermoK() {
  plastic_degC = th_1.readCelsius();
  metal_degC = th_2.readCelsius();
}


void measureMLX90614() {
 ambienceT_degC = mlx90614.readAmbientTempC();
 objectT_degC   = mlx90614.readObjectTempC();
}


void updateDisplay() {

  display.clearDisplay();
  display.setCursor(0, 5);
  display.println("KarbonTek - Cold Point Manager");

  display.println(String("T (sur, C) = ") + ambienceT_degC);
  display.println(String("T (obj, C) = ") + objectT_degC);
  display.println(String("T (pls, C) = ") + plastic_degC);
  display.println(String("T (met, C) = ") + metal_degC);

  display.display();

}


void setupSerial() {
  Serial.setTimeout(SERIAL_TIMEOUT);
  Serial.begin(SERIAL_SPEED);
  while (!Serial) { delay(SERIAL_WAIT); }
  Serial.println(String("Serial port ready, working at (bps) = ") + SERIAL_SPEED);
}


void setupI2C() {
  // Find I2C devices, only to be executed once to find the addresses of the devices
  // This function should not be used dynamically, since the addresses for the devices should be static
  for (int i = 0; i < I2C_MAX_SLAVES; i++) { devices[i] = false; }
  scanI2C();
}

void setup() {

  setupSerial();
  setupI2C();

  setupLCD();
  setupMLX90614();

}


void loop() {

  measureThermoK();
  measureMLX90614();

  updateDisplay();
  delay(PAUSE);

}
