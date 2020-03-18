#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_INA219.h>

#define SERIAL_SPEED    9600          // Serial port speed
#define SERIAL_WAIT     100           // Serial port readiness waiting checkpoint
#define SERIAL_TIMEOUT  600           // timeout miliseconds; completing an approx. 1 second cycle

#define PAUSE 100

#define I2C_DISCOVER_WAIT   100      // ms delay after looking for I2C slaves
#define I2C_FIRST_ADDRESS   8        // address of the first slave in the I2C bus
#define I2C_MAX_SLAVES      120      // maximum number of slaves in an I2C bus
bool devices[I2C_MAX_SLAVES];        // array holding all the addresses found for the connected I2C devices

#define I2C_LCD_WAIT        100       // ms to wait for LCD to initialize
#define I2C_LCD_ADDR        0x3C      // LCD crystal screen
#define I2C_INA219_ADDR     0x40      // INA219 current sensor

#define ADC_STEPS           1024
#define ADC_RANGE           5.0

#define ACS712_MVAMP        100       // use 185 for 5A, 100 for 20A Module and 66 for 30A Module
#define ACS712_SAMPLES      10        // samples to take for measuring 1 value
#define ACS712_WAIT_SAMPLE  10        // ms to wait in between samples

const float ACS721_FACTOR   = ( ADC_RANGE * ACS712_MVAMP ) / ( ACS712_SAMPLES * ADC_STEPS );

Adafruit_SSD1306 display(128, 64);
Adafruit_INA219 ina219(I2C_INA219_ADDR);


float acs721_current = 0.0;
float shuntVoltage_mV = 0.0, busVoltage = 0.0, loadCurrent_mA = 0.0, loadVoltage = 0.0;


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


void setup_I2CLCD(){
  delay(I2C_LCD_WAIT);
  display.begin(SSD1306_SWITCHCAPVCC, I2C_LCD_ADDR);
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setRotation(0);
  display.setTextWrap(false);
  display.dim(0);
}


void ACS721_measure() {
  int buffer = 0, read = 0;
  for (byte i = 0; i < ACS712_SAMPLES; i++) { buffer += analogRead(A1); delay(ACS712_WAIT_SAMPLE); }
  acs721_current = buffer * ACS721_FACTOR;
}


void INA219_measure() {
  shuntVoltage_mV = ina219.getShuntVoltage_mV();
  busVoltage      = ina219.getBusVoltage_V();
  loadCurrent_mA  = ina219.getCurrent_mA();
  loadVoltage     = busVoltage + (shuntVoltage_mV / 1000);
}


void updateDisplay() {
  display.clearDisplay();
  display.setCursor(0, 5);
  display.println("KarbonTek - IV Tracer");
  display.println("");
  display.println(String("V (bus ,  V): ") + busVoltage);
  display.println(String("V (shnt, mV): ") + shuntVoltage_mV);
  display.println(String("V (load,  V): ") + loadVoltage);
  display.println(String("I (load, mA): ") + loadCurrent_mA);
  display.println(String("7 (load, mA): ") + acs721_current);
  display.display();
}


void setup() {

  Serial.setTimeout(SERIAL_TIMEOUT);
  Serial.begin(SERIAL_SPEED);
  while (!Serial) { delay(SERIAL_WAIT); }
  Serial.println(String("Serial port ready, working at (bps) = ") + SERIAL_SPEED);

  // Find I2C devices, only to be executed once to find the addresses of the devices
  // This function should not be used dynamically, since the addresses for the devices should be static
  // for (int i = 0; i < I2C_MAX_SLAVES; i++) { devices[i] = false; }
  // scanI2C();

  setup_I2CLCD();

  ina219.begin();
  ina219.setCalibration_32V_1A();

}


void loop() {

  Serial.println("Measuring");
  INA219_measure();
  // ACS721_measure();
  Serial.println(String("> ACS721, I = ") + acs721_current);
  updateDisplay();
  delay(PAUSE);

}