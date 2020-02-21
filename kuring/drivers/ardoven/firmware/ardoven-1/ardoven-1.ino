#include "max6675.h"

int BASE = 4;     // The first relay is connected to the I / O port
int NUM = 4;      // Total number of relays
int HEATER_1 = BASE;
int HEATER_2 = BASE + 1;
int HEATER_3 = BASE + 2;
int HEATER_4 = BASE + 3;

bool HEATER_1__stop = false;  // Flag that marks the HEATER_1 to stop its functioning
bool HEATER_2__stop = false;  // Flag that marks the HEATER_2 to stop its functioning
bool HEATER_3__stop = false;  // Flag that marks the HEATER_3 to stop its functioning
bool HEATER_4__stop = false;  // Flag that marks the HEATER_4 to stop its functioning

int th_CLK = 13;
int th_SO = 12;     // Common output for all thermistors, need to check several in parallel.
int th_1_CS = 11;   // Select output from first thermistor
int th_2_CS = 10;   // Select output from second thermistor

MAX6675 th_1(th_CLK, th_1_CS, th_SO);
MAX6675 th_2(th_CLK, th_2_CS, th_SO);

int vccPin = 3;
int gndPin = 2;

// plate
int   PLT_HEATER      = HEATER_2;
float TARGET_T1_PLATE = 60.0;
float TARGET_T1_STOP = 30.0;
// camera
int   CAM_HEATER       = HEATER_3;
float TARGET_T2_CAMERA = 85.0;
float TARGET_T2_STOP = 30.0;

bool heater_1_max = false;
bool heater_2_max = false;

int TK_STABLE_WAIT = 250;       // miliseconds to wait after a thermocouple readout
int SERIAL_WAIT = 100;          // Serial port readiness waiting checkpoint

int MARKER = 0x1FF1;          // Int marking the start of data transmission; the end is marked with a 'NL' character
int MARKER_START = 0;
int MARKER_LEN = 4;
int MARKER_END = MARKER_START + MARKER_LEN;
int COMMAND_START = MARKER_START + MARKER_LEN;
int COMMAND_LEN = 1;
int COMMAND_END = COMMAND_START + COMMAND_LEN;

int heater1T = 0;             // Variable reference, 0 ~ heater 1, 1 ~ heater 2
int heater2T = 1;             // Variable reference, 0 ~ heater 1, 1 ~ heater 2

// COMMANDS INTERFACE
// 1 ## PAUSE command ~ stops all the actuators and leaves only the sensors on
// 2 ## RESUME command ~ reactivates the actuators
// 3 ## STOP  command ~ stops the actuators / somewhat similar to pause
// 4 ## START commmand ~ starts the execution of the control program
// 5 ## ENABLE_SERIAL command ~ enables the text output of the serial console, events are kept
// 6 ## DISABLE_SERIAL command ~ disables the text output of the serial console, only events
int COMMANDS[10] = {1, 2, 3, 4, 5, 6};

// EVENTS INTERFACE - TODO
int DATA_TYPE = 0;        // char for the data type
int EVENT_TYPE = 1;       // char for the event type
int COMMAND_TYPE = 2;     // char for the command type
int E_NOPAYLOAD = 0;      // to be used whenever there is no payload to be transmitted for the event
// -1 ##
//  0 ## DATA
int E_SYSREADY = 1;                 //  1 ## SYSTEM READY
int E_SYSWAITING = 2;               //  2 ## SYSTEM WAITING
int E_SYSPAUSED = 3;                //  3 ## SYSTEM PAUSED
int E_SYSHALTING = 4;               //  4 ## SYSTEM HALTING
int E_SYSHALTED = 5;                //  5 ## SYSTEM HALTED
int E_THERMALOFF = 6;               //  6 ## THERMAL OFF
int E_THERMALONPAUSED = 7;          //  7 ## THERMAL ON PAUSED
int E_THERMALON = 8;                //  8 ## THERMAL ON
int E_ERR_MARKERDIFFERS = 10;       // 10 ## ERR MARKER DIFFERS
int E_ERR_UNSUPPORTEDCOMMAND = 11;  // 11 ## ERR UNSUPPORTED COMMAND

int EVENTS[20] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};

bool SERIAL_ENABLED = true;

unsigned long serialSpeed = 115200;
int SERIAL_TIMEOUT = 600;      // timeout miliseconds; completing an approx. 1 second cycle

bool stopActivated = false;   // Flag that marks whether the stop has been activated or not.
bool startActivated = false;  // Flag that marks whether the task should start or not.

char PLATE_HEATER_NAME[20] = "[plate, heater]";
char CAMERA_HEATER_NAME[20] = "[camera, heater]";


void eventTxNoPayload(int eventType) { eventTx(eventType, E_NOPAYLOAD); }

void eventTx(int eventType, int eventPayload) {

  unsigned long timestamp = millis();

  Serial.print(MARKER);
  Serial.print(EVENT_TYPE);
  Serial.print(EVENTS[eventType]);
  Serial.print(eventPayload);
  Serial.println(timestamp);

}

void dataTx(int sensor, float data) {

  unsigned long timestamp = millis();

  Serial.print(MARKER);
  Serial.print(DATA_TYPE);
  Serial.print(sensor);
  Serial.print(data);
  Serial.println(timestamp);

}

void dataRx() {

  Serial.println("[deb] Waiting for header...");
  String commandString = Serial.readString();
  Serial.print(">> readout = "); Serial.println(commandString);
  int marker__STR = commandString.substring(MARKER_START, MARKER_END).toInt();
  Serial.print("[deb] marker read = "); Serial.println(marker__STR);
  if (marker__STR == 0) { Serial.println("[deb] No marker read"); return; }
  if (marker__STR != MARKER) {
    if (SERIAL_ENABLED) {
      Serial.print("[warn] Wrong H = "); Serial.print(marker__STR);
      Serial.print(", expected = "); Serial.println(MARKER);
    }
    eventTx(E_ERR_MARKERDIFFERS, marker__STR);
    return;
  }

  int command__STR = commandString.substring(COMMAND_START, COMMAND_END).toInt();
  Serial.print("[info] Command read = "); Serial.println(command__STR);

  if (command__STR == COMMANDS[0]) { pause(); return; }
  if (command__STR == COMMANDS[1]) { resume(); return; }
  if (command__STR == COMMANDS[2]) { stop(); return; }
  if (command__STR == COMMANDS[3]) { start(); return; }

  eventTx(E_ERR_UNSUPPORTEDCOMMAND, command__STR);
  if (SERIAL_ENABLED) Serial.println("WARN!!! Unsupported command = " + command__STR);

}

void start() {
  eventTxNoPayload(E_SYSREADY);
  if (SERIAL_ENABLED) Serial.println("[INFO] Starting program...");
  startActivated = true;
}

void pause() {
  eventTxNoPayload(E_SYSPAUSED);
  if (SERIAL_ENABLED) Serial.println("[INFO] Pausing actuators functioning...");
  HEATER_2__stop = true;
  HEATER_4__stop = true;
}

void resume() {
  eventTxNoPayload(E_SYSPAUSED);
  if (SERIAL_ENABLED) Serial.println("[INFO] Resuming actuators functioning...");
  HEATER_2__stop = false;
  HEATER_4__stop = false;
  if (stopActivated == true) { stopActivated = false; }
}

void stop() {
  eventTxNoPayload(E_SYSHALTING);
  if (SERIAL_ENABLED) Serial.println("[INFO] Stopping actuators functioning...");
  HEATER_2__stop = true;
  HEATER_4__stop = true;
  stopActivated = true;
  digitalWrite(HEATER_2, LOW);
  digitalWrite(HEATER_4, LOW);
}

void controlHeater (float temperature, float threshold, int relay, bool flag, char *name) {
  if (temperature > threshold) {
    eventTx(E_THERMALOFF, relay);
    if (SERIAL_ENABLED) { Serial.print(*name); Serial.println(" above TH > Turn OFF"); }
    digitalWrite(relay, LOW);
  } else {
    if (flag == true) {
      eventTx(E_THERMALONPAUSED, relay);
      if (SERIAL_ENABLED) { Serial.print(*name); Serial.println(" below TH > but PAUSED!"); }
      digitalWrite(relay, HIGH);
    } else {
      eventTx(E_THERMALON, relay);
      if (SERIAL_ENABLED) { Serial.print(*name); Serial.println(" below TH > Turn ON"); }
      digitalWrite(relay, HIGH);
    }
  }
}

void waitStart () {
  while (startActivated == false) {
    eventTxNoPayload(E_SYSWAITING);
    if (SERIAL_ENABLED) Serial.println("Waiting for START command...");
    dataRx();
  }
}

void waitStop (float t1, float t2) {
  if (stopActivated == false) {return;}
  if ((t1 < TARGET_T1_STOP) && (t2 < TARGET_T2_STOP)) {
    eventTxNoPayload(E_SYSHALTED);
    if (SERIAL_ENABLED) Serial.println("[INFO] System Halted");
    while(true);
  }
}

void setup() {

  Serial.setTimeout(SERIAL_TIMEOUT);
  Serial.begin(serialSpeed);
  while (!Serial) { delay(SERIAL_WAIT); }

  // use Arduino pins
  pinMode(vccPin, OUTPUT);
  digitalWrite(vccPin, HIGH);
  pinMode(gndPin, OUTPUT);
  digitalWrite(gndPin, LOW);
  // wait for MAX chip to stabilize
  delay(TK_STABLE_WAIT);

  //Set the number I/O port to outputs
  for (int i = BASE; i < BASE + NUM; i ++) { pinMode(i, OUTPUT); }

}

void loop() {

  waitStart();

  float th_1_in = th_1.readCelsius();
  dataTx(heater1T, th_1_in);
  delay(TK_STABLE_WAIT);

  controlHeater(th_1_in, TARGET_T1_PLATE, HEATER_2, HEATER_2__stop, PLATE_HEATER_NAME);

  float th_2_in = th_2.readCelsius();
  dataTx(heater2T, th_2_in);
  delay(TK_STABLE_WAIT);

  controlHeater(th_2_in, TARGET_T2_CAMERA, HEATER_4, HEATER_4__stop, CAMERA_HEATER_NAME);

  dataRx();

  waitStop(th_1_in, th_2_in);

}
