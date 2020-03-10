#include "max6675.h"

int BASE = 4;     // The first relay is connected to the I / O port
int NUM = 4;      // Total number of relays
int HEATER_1 = BASE;
int HEATER_2 = BASE + 1;
int HEATER_3 = BASE + 2;
int HEATER_4 = BASE + 3;

int th_CLK = 13;
int th_SO = 12;     // Common output for all thermistors, need to check several in parallel.
int th_1_CS = 11;   // Select output from first thermistor
int th_2_CS = 10;   // Select output from second thermistor

MAX6675 th_1(th_CLK, th_1_CS, th_SO);
MAX6675 th_2(th_CLK, th_2_CS, th_SO);

int vccPin = 3;
int gndPin = 2;

// plate
int   PLT_HEATER  = HEATER_2;
float PLT_MAXTEMP = 60.0;
// camera
int   CAM_HEATER  = HEATER_2;
float CAM_MAXTEMP = 85.0;

bool heater_1_max = false;
bool heater_2_max = false;

int marker = 0x1FF1;     // Int marking the start of data transmission; the end is marked with a 'NL' character
int heater1T = 0;        // Variable reference, 0 ~ heater 1, 1 ~ heater 2
int heater2T = 1;        // Variable reference, 0 ~ heater 1, 1 ~ heater 2
int MARKER_timestamp = 0x2FF2;  // Int marking the timestamp integer in miliseconds

void dataTx(int type, float data, unsigned long timestamp) {

  Serial.print(marker);
  Serial.print(type);
  Serial.println(data);
  Serial.println(MARKER_timestamp);
  Serial.println(timestamp);

}

void setup() {

  Serial.begin(9600);

  // use Arduino pins
  pinMode(vccPin, OUTPUT);
  digitalWrite(vccPin, HIGH);
  pinMode(gndPin, OUTPUT);
  digitalWrite(gndPin, LOW);
  // wait for MAX chip to stabilize
  Serial.println("MAX6675 test");
  delay(1000);

  //Set the number I/O port to outputs
  for (int i = BASE; i < BASE + NUM; i ++) {
    pinMode(i, OUTPUT);
  }

}

void loop() {

  float th_1_in = th_1.readCelsius();
  unsigned long th_1_ts = millis();
  // dataTx(heater1T, th_1_in, th_1_ts);
  delay(250);

  float th_2_in = th_2.readCelsius();
  unsigned long th_2_ts = millis();
  // dataTx(heater2T, th_2_in, th_2_ts);
  delay(500);

  if (th_1_in > PLT_MAXTEMP) {
    Serial.print("[plate, heater] above TH > Turn OFF | "); Serial.println(th_1_in);
    digitalWrite(HEATER_2, LOW); 
  } else {
    Serial.print("[plate, heater] below TH > Turn ON | "); Serial.println(th_1_in);
    digitalWrite(HEATER_2, HIGH);
  }

  if (th_2_in > CAM_MAXTEMP) {
    Serial.print("[CAMERA, heater] above TH > Turn OFF | "); Serial.println(th_2_in);
    digitalWrite(HEATER_4, LOW);
  } else {
    Serial.print("[CAMERA, heater] below TH > Turn ON | "); Serial.println(th_1_in);
    digitalWrite(HEATER_4, HIGH);
  }

}
