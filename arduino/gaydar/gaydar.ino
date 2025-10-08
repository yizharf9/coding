
const int trigPin = 10;
const int echoPin = 9;
const int buzzerPin = 8;
const int buttonPin = 7;

void setup() {
  // initialize serial communication:
  Serial.begin(9600);
  pinMode(trigPin,OUTPUT);
  pinMode(buzzerPin,OUTPUT);
  pinMode(echoPin,INPUT);
  pinMode(buttonPin,INPUT);
}

void loop() {
  prompt_dist();
  int dist = prompt_dist();  
  Serial.println(dist);
  if (dist<50 && digitalRead(buttonPin)){
    noise(1);
  }
}

int prompt_dist(){
    // establish variables for duration of the ping, and the distance result
  // in inches and centimeters:
  long duration, inches, cm;

  // The PING))) is triggered by a HIGH pulse of 2 or more microseconds.
  // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // The same pin is used to read the signal from the PING))): a HIGH pulse
  // whose duration is the time (in microseconds) from the sending of the ping
  // to the reception of its echo off of an object.
  duration = pulseIn(echoPin, HIGH);

  // convert the time into a distance
  inches = microsecondsToInches(duration);
  cm = microsecondsToCentimeters(duration);

  // Serial.print(inches);
  // Serial.print("in, ");
  // Serial.print(cm);
  // Serial.print("cm");
  // Serial.println();

  delay(100);
  return cm;
}

void noise(int cycle_time){
  for (int i = 0; i<50 ; i++){
    digitalWrite(buzzerPin,HIGH);
    delay(cycle_time);
    digitalWrite(buzzerPin,LOW);
    delay(cycle_time);
  }
}


long microsecondsToInches(long microseconds) {
  // According to Parallax's datasheet for the PING))), there are 73.746
  // microseconds per inch (i.e. sound travels at 1130 feet per second).
  // This gives the distance travelled by the ping, outbound and return,
  // so we divide by 2 to get the distance of the obstacle.
  // See: https://www.parallax.com/package/ping-ultrasonic-distance-sensor-downloads/
  return microseconds / 74 / 2;
}

long microsecondsToCentimeters(long microseconds) {
  // The speed of sound is 340 m/s or 29 microseconds per centimeter.
  // The ping travels out and back, so to find the distance of the object we
  // take half of the distance travelled.
  return microseconds / 29 / 2;
}
