/*
  SIE558 - Final Project Arduino#1 program
The entry sensor has two magnetic door switches and a camera. Program will check door #1 and if 
status #1 changed then send to pi (doorID, sensorValue).
It will also check door #2 and if status #2 changed then send to pi (doorID,sensorValue).

 The circuit:
 * magnetic door switch #1 connected to digital pin 4
 * magnetic door switch #2 connected to digital pin 5
 * camera is attached to ??
 */

const int doorSwitch1 = 4;    // select the input pin for the door switch #1
const int doorSwitch2 = 5;    // select the input pin for the door switch #2
int doorState1 = 1;  // variable to store the value coming from the sensor #1
int lastDoorState1 = 1;  // variable to store the last value coming from the sensor #1
int doorState2 = 1;  // variable to store the value coming from the sensor #2
int lastDoorState2 = 1;  // variable to store the last value coming from the sensor #1

void setup() {
  Serial.begin(9600);
  Serial.println("doorID, doorState");
}

void loop() {
  // delay
  delay(300);
  // read the value from the sensor:
  doorState1 = digitalRead(doorSwitch1);
  if (doorState1 != lastDoorState1) {
    // if the state has changed and door is open 
    String doorObs1 = "1," + String(doorState1);
    Serial.println(doorObs1);
    // Delay a little bit to avoid bouncing
    delay(300);
  }
  // save the current state as the last state, for next time through the loop
  lastDoorState1 = doorState1;
  
  // delay
  delay(300);
  // read the value from the sensor:
  doorState2 = digitalRead(doorSwitch2);
  if (doorState2 != lastDoorState2) {
    // if the state has changed and door is open 
    String doorObs2 = "2," + String(doorState2);
    Serial.println(doorObs2);
  }
  // save the current state as the last state, for next time through the loop
  lastDoorState2 = doorState2;
}
