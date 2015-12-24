/*
  SIE558 - Final Project Arduino#2 program
The frig sensor has two magnetic door switches. Program will check door #3 and if 
status #3 changed then take pic and send to pi (doorID, pictureID, sensorValue, sensorVoltage).
It will also check door #4 and if status #4 changed then take pic and send to pi (doorID, 
pictureID, sensorValue, sensorVoltage). Pictures will be stored on SD card for now.

 The circuit:
 * magnetic door switch #3 connected to digital pin 4
 * magnetic door switch #4 connected to digital pin 5
 * camera is attached to ??
 
 */

const int doorSwitch3 = 4;    // select the input pin for the door switch #1
const int doorSwitch4 = 5;    // select the input pin for the door switch #2
int doorState3 = 1;  // variable to store the value coming from the sensor #1
int lastDoorState3 = 1;  // variable to store the last value coming from the sensor #1
int doorState4 = 1;  // variable to store the value coming from the sensor #2
int lastDoorState4 = 1;  // variable to store the last value coming from the sensor #1

void setup() {
  Serial.begin(9600);
  Serial.println("doorID, doorState");
}

void loop() {
  // delay
  delay(300);
  // read the value from the sensor:
  doorState3 = digitalRead(doorSwitch3);
  if (doorState3 != lastDoorState3) {
    // if the state has changed and door is open 
    String doorObs3 = "3," + String(doorState3);
    Serial.println(doorObs3);
    // Delay a little bit to avoid bouncing
    delay(300);
  }
  // save the current state as the last state, for next time through the loop
  lastDoorState3 = doorState3;
  
  // delay
  delay(300);
  // read the value from the sensor:
  doorState4 = digitalRead(doorSwitch4);
  if (doorState4 != lastDoorState4) {
    // if the state has changed and door is open 
    String doorObs4 = "4," + String(doorState4);
    Serial.println(doorObs4);
  }
  // save the current state as the last state, for next time through the loop
  lastDoorState4 = doorState4;
}
