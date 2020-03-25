#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_INA219.h>
#include <Adafruit_MLX90614.h>
#include <Adafruit_MAX31865.h>

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

// The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
#define RREF      430.0
// The 'nominal' 0-degrees-C resistance of the sensor: 100.0 for PT100, 1000.0 for PT1000
#define RNOMINAL  100.0

Adafruit_SSD1306 display(128, 64);
Adafruit_INA219 ina219(I2C_INA219_ADDR);
Adafruit_MLX90614 mlx90614 = Adafruit_MLX90614();
Adafruit_MAX31865 max31865 = Adafruit_MAX31865(10, 11, 12, 13);


bool eloadEnabled     = false;                  // if 'true', eloadGain gets incremented automatically
int eloadGain         = ELOAD_GAIN_INIT;
float acs721_current  = 0.0;
float shuntVoltage_mV = 0.0, busVoltage = 0.0, loadCurrent_mA = 0.0, loadVoltage = 0.0;
double ambienceT_degC = 0.0, objectT_degC = 0.0;

uint16_t maxRTD       = 500;
float maxT_degC       = -120;



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


void setupMAX31865() {
  max31865.begin(MAX31865_2WIRE);
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


// sensor resistance wrt temperature: R(x) = R0 + R0*Ka*x + R0*Kb*x**2 + R0*Kc*x**3
// cubic polynomial:                  R0*Kc*x**3 + R0*kb*x**2 + R0*Ka*x + (R0-R(x)) = 0
// mathematical standard equation:    a*x**3 + b*x**2 + c*x + d = 0
#define Ka          5.88E-3
#define Kb          7.872E-6
#define Kc          4.71E-9
#define xPOL_d      RNOMINAL               // need to substract the readout (rtd) from MAX31865
#define POL_c       RNOMINAL * Ka
#define POL_b       RNOMINAL * Kb
#define POL_a       RNOMINAL * Kc
#define SOL_p       -1.0*POL_b / (3*POL_a)
#define SOL_p3      SOL_p * SOL_p * SOL_p
#define SOL_r       POL_c / (3*POL_a)
#define CSQ_K       1.0 / 3.0


double temp2rtd(float temp) { return RNOMINAL * (1 + Ka * temp + Kb * sq(temp) + Kc * pow(temp, 3)); }

float rtd2temp(float rtd) {
  float POL_d = xPOL_d - rtd;
  float SOL_q = SOL_p3 + ( (POL_b*POL_c - 3.0*POL_a*POL_d) / (6.0 * sq(POL_a) ) );

  // __term_1 = {q + [q2 + (r-p2)3]1/2}1/3
  float __term_1 = cbrt( (SOL_q + sqrt(sq(SOL_q) + pow( (SOL_r - sq(SOL_p)), 3) ) ) );
  // __term_2 = {q - [q2 + (r-p2)3]1/2}1/3
  float __term_2 = cbrt( (SOL_q - sqrt(sq(SOL_q) + pow( (SOL_r - sq(SOL_p)), 3) ) ));
  // return {q + [q2 + (r-p2)3]1/2}1/3   +   {q - [q2 + (r-p2)3]1/2}1/3   +   p

  return __term_1 + __term_2 + SOL_p;
}

void measureMAX31865() {

  maxRTD = max31865.readRTD();
  maxT_degC = max31865.temperature(RNOMINAL, RREF);
  uint8_t fault = max31865.readFault();

  //maxT_degC = rtd2temp(maxRTD);

  // maxT_degC = max31865.readRTD(); // max31865.temperature(RNOMINAL, RREF);
  // uint8_t fault = max31865.readFault();
  //Serial.println(String("fault = ") + fault);
  // return;

  /*
  if (fault) {
    //Serial.print("Fault 0x"); Serial.println(fault, HEX);
    return;
    if (fault & MAX31865_FAULT_HIGHTHRESH) { Serial.println("RTD High Threshold"); }
    if (fault & MAX31865_FAULT_LOWTHRESH) { Serial.println("RTD Low Threshold"); }
    if (fault & MAX31865_FAULT_REFINLOW) { Serial.println("REFIN- > 0.85 x Bias"); }
    if (fault & MAX31865_FAULT_REFINHIGH) { Serial.println("REFIN- < 0.85 x Bias - FORCE- open"); }
    if (fault & MAX31865_FAULT_RTDINLOW) { Serial.println("RTDIN- < 0.85 x Bias - FORCE- open"); }
    if (fault & MAX31865_FAULT_OVUV) { Serial.println("Under/Over voltage"); }
    max31865.clearFault();
  }
  */

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
  display.println(String("T (C) = ") + maxT_degC + ", " + maxRTD);

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
  setupMAX31865();

  pinMode(ELOAD_PIN, OUTPUT);
  analogWrite(ELOAD_PIN, eloadGain);

}


void loop() {

  Serial.println(String(" eloadGain = ") + eloadGain);

  if (eloadEnabled == true ) {analogWrite(ELOAD_PIN, eloadGain++);}

  measureINA219();
  measureMLX90614();
  // measureACS721();
  measureMAX31865();

  updateDisplay();
  delay(PAUSE);

}
