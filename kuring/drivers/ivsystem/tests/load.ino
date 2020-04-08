#include <Wire.h>
#include <Adafruit_MCP4725.h>

#define SERIAL_SPEED        9600          // Serial port speed
#define SERIAL_WAIT         100           // Serial port readiness waiting checkpoint
#define SERIAL_TIMEOUT      600           // timeout miliseconds; completing an approx. 1 second cycle

#define I2C_DISCOVER_WAIT   100      // ms delay after looking for I2C slaves
#define I2C_FIRST_ADDRESS   8        // address of the first slave in the I2C bus
#define I2C_MAX_SLAVES      120      // maximum number of slaves in an I2C bus
bool devices[I2C_MAX_SLAVES];        // array holding all the addresses found for the connected I2C devices

// Set this value to 9, 8, 7, 6 or 5 to adjust the resolution
#define DAC_MIN             0
#define DAC_MAX             4095
#define DAC_WAIT            3000


float adcVoltage = 0.0;

Adafruit_MCP4725 dac;


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


void setup() {

    Serial.setTimeout(SERIAL_TIMEOUT);
    Serial.begin(SERIAL_SPEED);
    while (!Serial) { delay(SERIAL_WAIT); }
    Serial.println(String("Serial port ready, working at (bps) = ") + SERIAL_SPEED);

    scanI2C();

    // For Adafruit MCP4725A1 the address is 0x62 (default) or 0x63 (ADDR pin tied to VCC)
    // For MCP4725A0 the address is 0x60 or 0x61
    // For MCP4725A2 the address is 0x64 or 0x65
    dac.begin(0x62);
    Serial.println("DAC ready");

}

void loop() {

    dac.setVoltage(DAC_MAX, false);
    delay(100);
    adcVoltage = analogRead(A3) * (5.0 / 1023.0);
    Serial.println(String("dac = ") + DAC_MAX + String(", adc = ") + adcVoltage);
    delay(DAC_WAIT);

    dac.setVoltage(DAC_MIN, false);
    delay(100);
    adcVoltage = analogRead(A3) * (5.0 / 1023.0);
    Serial.println(String("dac = ") + DAC_MIN + String(", adc = ") + adcVoltage);
    delay(DAC_WAIT);

}