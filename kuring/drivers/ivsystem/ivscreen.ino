#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MLX90614.h>

#define SERIAL_SPEED        9600          // Serial port speed
#define SERIAL_WAIT         100           // Serial port readiness waiting checkpoint
#define SERIAL_TIMEOUT      600           // timeout miliseconds; completing an approx. 1 second cycle

#define PAUSE               100
#define ELOAD_PIN           3
#define ELOAD_GAIN_INIT     50

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
Adafruit_MLX90614 mlx90614 = Adafruit_MLX90614();


bool eloadEnabled     = false;                  // if 'true', eloadGain gets incremented automatically
int eloadGain         = ELOAD_GAIN_INIT;
float acs721_current  = 0.0;
float shuntVoltage_mV = 0.0, busVoltage = 0.0, loadCurrent_mA = 0.0, loadVoltage = 0.0;
double ambienceT_degC = 0.0, objectT_degC = 0.0;


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


void setupINA219() {
  ina219.begin();
  ina219.setCalibration_32V_1A();
}


void setupMLX90614() {
  mlx90614.begin();
}


void measureACS721() {
  int buffer = 0, read = 0;
  for (byte i = 0; i < ACS712_SAMPLES; i++) { buffer += analogRead(A7); delay(ACS712_WAIT_SAMPLE); }
  acs721_current = buffer * ACS721_FACTOR;
}


void measureINA219() {
  shuntVoltage_mV = ina219.getShuntVoltage_mV();
  busVoltage      = ina219.getBusVoltage_V();
  loadCurrent_mA  = ina219.getCurrent_mA();
  loadVoltage     = busVoltage + (shuntVoltage_mV / 1000);
}


void measureMLX90614() {
 ambienceT_degC = mlx90614.readAmbientTempC();
 objectT_degC   = mlx90614.readObjectTempC();
}


void updateDisplay() {
  display.clearDisplay();
  display.setCursor(0, 5);
  display.println("KarbonTek - IV Tracer");

  // display.println("");
  // display.println(String("V (bus ,  V): ") + busVoltage);
  // display.println(String("V (shnt, mV): ") + shuntVoltage_mV);
  display.println(String("V (load,  V): ") + loadVoltage);
  display.println(String("I (load, mA): ") + loadCurrent_mA);
  display.println(String("N (gate,  #): ") + eloadGain);
  // display.println(String("I (mosf, mA): ") + acs721_current);
  display.println(String("T (C) = ") + ambienceT_degC + String(", ") + objectT_degC);

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
  setupINA219();
  setupMLX90614();

  pinMode(ELOAD_PIN, OUTPUT);
  analogWrite(ELOAD_PIN, eloadGain);

}


void loop() {

  Serial.println(String(" eloadGain = ") + eloadGain);

  if (eloadEnabled == true ) {analogWrite(ELOAD_PIN, eloadGain++);}

  measureINA219();
  measureMLX90614();
  // measureACS721();
  updateDisplay();
  delay(PAUSE);

}
