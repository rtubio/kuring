
int SERIAL_SPEED = 9600;
int SERIAL_WAIT = 100;          // Serial port readiness waiting checkpoint
int SERIAL_TIMEOUT = 600;      // timeout miliseconds; completing an approx. 1 second cycle

int PAUSE = 3000;

void setup() {
  Serial.setTimeout(SERIAL_TIMEOUT);
  Serial.begin(SERIAL_SPEED);
  while (!Serial) { delay(SERIAL_WAIT); }
  Serial.println("Serial port ready, working at (bps) = "); Serial.println(SERIAL_SPEED);
}

void loop() {
  Serial.println("Waiting...");
  delay(PAUSE);
}
