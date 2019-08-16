#include <Wire.h>
//Register locations of AD5933
//#define RK 110000
#define SLAVEADDR 0x0D // default serial bus address, 0001101 (0x0D).
#define ADDRPTR 0xB0 // address pointer, 1011 0000.
#define CTRLREG 0x80
#define CTRLREG2 0x81
#define STARTFREQ_R1 0x82
#define STARTFREQ_R2 0x83
#define STARTFREQ_R3 0x84
#define FREQINCRE_R1 0x85
#define FREQINCRE_R2 0x86
#define FREQINCRE_R3 0x87
#define NUMINCRE_R1 0x88
#define NUMINCRE_R2 0x89
#define NUMSCYCLES_R1 0x8A
#define NUMSCYCLES_R2 0x8B


#define REDATA_R1 0x94
#define REDATA_R2 0x95
#define IMGDATA_R1 0x96
#define IMGDATA_R2 0x97
#define TEMPR1 0x92
#define TEMPR2 0x93
#define STATUSREG 0x8F
const float MCLK = 16.776*pow(10,6); // AD5933 Internal Clock Speed 16.776 MHz
const float startfreq = 100*pow(10,3); // Set start freq; < 100Khz
const float increfreq = 0*pow(10,3); // Set freq increment; > 0.1 Hz
const int increnum = 95; // Set number of increments; < 511
int fsrLeftPin = 0;     // the FSR and 10K pulldown are connected to a0
int fsrCenterPin = 1;     // the FSR and 10K pulldown are connected to a1
int fsrRightPin = 2;     // the FSR and 10K pulldown are connected to a2
int fsrRefPin = 3;     // the FSR and 10K pulldown are connected to a3
int fsrReading1;  
int fsrReading2;  
int fsrReading3;  
int fsrReadingRef;  
int leftRel;
int centerRel;
int rightRel;
int count;


void setup() {
Wire.begin(); // Start I2C to 5933
Serial.begin(9600); // Start Serial to COM port to PC via USB
while (!Serial) {} // Wait for serial port to connect. Needed for native USB
Serial.println(); // Sets last data in buffer to "newline"
Serial.flush(); // Waits for the transmission of outgoing serial data to complete
}

void loop() {
delay(1000); // Wait before next loop.
programReg(); // Program Device Registers
runSweep(); // Run Sweep
delay(1000);
getPressure();
}

void programReg(){
//Set Range, PGA gain 1 (0x00 = x5, 0x01 = x1)
writeData(CTRLREG,0x01); // 2 V pk-pk and x1 gain
//writeData(CTRLREG,0x07); // 1 V pk-pk and x1 gain
//writeData(CTRLREG,0x05); // 400 mV pk-pk and x1 gain
//writeData(CTRLREG,0x03); // 200 mV pk-pk and x1 gain
// Set Start frequency
writeData(STARTFREQ_R1, getFrequency(startfreq,1));
writeData(STARTFREQ_R2, getFrequency(startfreq,2));
writeData(STARTFREQ_R3, getFrequency(startfreq,3));
// Set Increment frequency
writeData(FREQINCRE_R1, getFrequency(increfreq,1));
writeData(FREQINCRE_R2, getFrequency(increfreq,2));
writeData(FREQINCRE_R3, getFrequency(increfreq,3));
// Set Number of Points in frequency sweep, max 511
writeData(NUMINCRE_R1, (increnum & 0x001F00)>>0x08 );
writeData(NUMINCRE_R2, (increnum & 0x0000FF));
// Set settling time cycle count
writeData(NUMSCYCLES_R1, 0x07); // Max cycles x4
writeData(NUMSCYCLES_R2, 0xFF); // Max lower register for number of settling time cycles (255)



}

void runSweep() {
short re;
short img;
double freq;
int i=0;
float Vpk;
//float gain;
float impeda;
byte R1,R2;
// 1. Standby '10110000' Mask D8-10 to avoid tampering with gains and pk-pk voltage. Required for
//sweeps.
writeData(CTRLREG,(readData(CTRLREG) & 0x07) | 0xB0);
// 2. Initialize sweep
writeData(CTRLREG,(readData(CTRLREG) & 0x07) | 0x10);
// 3. Start sweep
writeData(CTRLREG,(readData(CTRLREG) & 0x07) | 0x20);
while((readData(STATUSREG) & 0x07) < 4 ) { // Check that status reg != 4, sweep not complete
delay(200); // delay between measurements
//reads imaginary and real data
int flag = readData(STATUSREG)& 2; // Check for valid real/imaginary data from status register
if (flag==2) {
R1 = readData(REDATA_R1);
R2 = readData(REDATA_R2);
re = (R1 << 8) | R2;



R1 = readData(IMGDATA_R1);
R2 = readData(IMGDATA_R2);
img = (R1 << 8) | R2;
freq = startfreq + i*increfreq;
Vpk = sqrt(pow(re,2)+pow(img,2)); // voltage pk-pk at ADC
//gain = 1/(RK*Vpk);
//impeda = 1/(gain*Vpk);
impeda = 4130000*pow(Vpk,-1.45);
//Serial.print(byte(freq/1000));
//Serial.print(" " + re);
//Serial.print(" " + img);
//Serial.print(" " + Vpk);
//Serial.print(" " + gain, 10);
Serial.print("Impedance: ");
Serial.print(impeda);
if( impeda > 1000){
  Serial.println(" - Healthy. Good Job! :-)");
} else if( impeda > 500 && impeda < 1000){
  Serial.println(" - Mild Risk");
} else{
  Serial.println(" - Major Risk. WARNING! WARNING! WARNING! WARNING!");
}
//Increment frequency, do not increment if beyond sweep
if((readData(STATUSREG) & 0x07) < 4 ){
writeData(CTRLREG,(readData(CTRLREG) & 0x07) | 0x30);
i++;
}
}
}
writeData(CTRLREG,(readData(CTRLREG) & 0x07) | 0xA0);
}

void writeData(int addr, int data) {



Wire.beginTransmission(SLAVEADDR);
Wire.write(addr);
Wire.write(data);
Wire.endTransmission();
delay(1);
}

int readData(int addr){
int data;
Wire.beginTransmission(SLAVEADDR);
Wire.write(ADDRPTR);
Wire.write(addr);
Wire.endTransmission();
delay(1);
Wire.requestFrom(SLAVEADDR,1);
if (Wire.available() >= 1){
data = Wire.read();
}
else {
data = -1;
}
delay(1);
return data;



}

byte getFrequency(float freq, int n){
long val = long((freq/(MCLK/4)) * pow(2,27)); // AD5933 Start frequency code.
byte code; // Frequency code for each register.
switch (n) {
case 1:
code = (val & 0xFF0000) >> 0x10;
break;
case 2:
code = (val & 0x00FF00) >> 0x08;
break;
case 3:
code = (val & 0x0000FF);
break;
default:
code = 0;
}
return code;
}

int getPressure(){
  count = 0;
  while(count < 10){
    fsrReading1 = analogRead(fsrLeftPin); 
    fsrReading2 = analogRead(fsrCenterPin);
    fsrReading3 = analogRead(fsrRightPin);  
    fsrReadingRef = analogRead(fsrRefPin);
    leftRel = fsrReading1 - fsrReadingRef;
    centerRel = fsrReading2 - fsrReadingRef;
    rightRel = fsrReading3 - fsrReadingRef;
    
   
    //Serial.print("Left Pressure Sensor raw reading = ");
    //Serial.print(fsrReading1);     // the raw analog reading
    Serial.print("Left Pressure Sensor reading = ");
    Serial.print(leftRel);     // the relative reading compared to reference pressure sensor
  
    if(fsrReading1 > 950){
      Serial.println(" - Left Sensor pressure maxed - DANGER");
    }
    // We'll have a few threshholds, qualitatively determined
    if (leftRel < 10) {
      Serial.println(" - No pressure");
    } else if (leftRel < 200) {
      Serial.println(" - Light pressure");
    } else if (leftRel < 500) {
      Serial.println(" - Medium Pressure");
    } else if (leftRel < 800) {
      Serial.println(" - Large Pressure");
    } else {
      Serial.println(" - Dangerous Pressure");
    }
    
    //Serial.print("Center Pressure Sensor raw reading = ");
    //Serial.print(fsrReading2);     // the raw analog reading
    Serial.print("Center Pressure Sensor reading = ");
    Serial.print(centerRel);     // the relative reading compared to reference pressure sensor
  
    if(fsrReading2 > 950){
      Serial.println(" - Center Sensor pressure maxed - DANGER");
    }
    // We'll have a few threshholds, qualitatively determined
    if (centerRel < 10) {
      Serial.println(" - No pressure");
    } else if (centerRel < 200) {
      Serial.println(" - Light pressure");
    } else if (centerRel < 500) {
      Serial.println(" - Medium Pressure");
    } else if (centerRel < 800) {
      Serial.println(" - Large Pressure");
    } else {
      Serial.println(" - Dangerous Pressure");
    }
    
    //Serial.print("Right Pressure Sensor raw reading = ");
    //Serial.print(fsrReading3);     // the raw analog reading
    Serial.print("Right Pressure Sensor reading = ");
    Serial.print(rightRel);     // the relative reading compared to reference pressure sensor
  
    if(fsrReading1 > 950){
      Serial.println("3- Right Sensor pressure maxed - DANGER");
    }
    // We'll have a few threshholds, qualitatively determined
    if (rightRel < 10) {
      Serial.println(" - No pressure");
    } else if (rightRel < 200) {
      Serial.println(" - Light pressure");
    } else if (rightRel < 500) {
      Serial.println(" - Medium Pressure");
    } else if (rightRel < 800) {
      Serial.println(" - Large Pressure");
    } else {
      Serial.println(" - Dangerous Pressure");
    }
  
    if((1.2 * leftRel) < centerRel || (1.2 * rightRel)){
      Serial.println("Force being applied on spinal column");
    } else if( leftRel > (1.2 * rightRel)){
      Serial.println("Patient favoring force towards left side");
    } else if( rightRel > (1.2 * leftRel)){
      Serial.println("Patient favoring force towards right side");
    } else{
      Serial.println("Good force distribution :)");
    }
    count++;
    delay(3000);
  }
}
