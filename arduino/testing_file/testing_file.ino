const int big_delay = 300; 
const int Vout = 13;
const int Vin = 9;
bool toggle = false;
int count = 3;

void setup() {
  pinMode(Vout,OUTPUT);
  pinMode(Vin,INPUT);
}

void loop() {
  
  if (digitalRead(Vin)==HIGH){   
    toggle = !toggle;
    delay(500);
  }
  if (toggle){
     blink(count);
  }

  // if(digitalRead(Vin)==HIGH){
  //   // blink();
  //   digitalWrite(Vout,HIGH);
  // }
  // else if(digitalRead(Vin)==LOW){
  //   // blink();
  //   digitalWrite(Vout,LOW);
  // }
  // else{
  //   digitalWrite(Vout,LOW);
  // }
}

void blink(int count){ // a function that makes the LED's connected to blink
  for(int i=0 ; i<count ; i++)
  digitalWrite(13,HIGH);
    delay(big_delay + 200);
    digitalWrite(13,LOW);
    delay(big_delay);
}


