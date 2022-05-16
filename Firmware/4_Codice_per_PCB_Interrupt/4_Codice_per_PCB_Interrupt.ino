#include <ArduinoBLE.h>
#include <math.h>
#include <MegunoLink.h>

//################# ARDUINO IOT ####################
//--------Timer Interrupt on BLE libraries---------
//#define TIMER_INTERRUPT_DEBUG         0
//#define _TIMERINTERRUPT_LOGLEVEL_     0
//#include <SAMDTimerInterrupt.h>
//#include <SAMD_ISR_Timer.h>
//
////------------DEFINE TIME VARIABLES----------------
//#define HW_TIMER_INTERVAL_MS      10
//SAMDTimer ITimer(TIMER_TC3);
//
//SAMD_ISR_Timer ISR_Timer;
//
//#define TIMER_INTERVAL_1S             1000L
//#define TIMER_INTERVAL_2S             2000L
//#define TIMER_INTERVAL_5S             5000L
//##################################################

//################ ARDUINO BLE #####################
////----------Timer Interrupt on BLE libraries----------
#define TIMER_INTERRUPT_DEBUG 0
#define _TIMERINTERRUPT_LOGLEVEL_ 0
#include <NRF52_MBED_TimerInterrupt.h>
#include <NRF52_MBED_ISR_Timer.h>

//-------------DEFINE TIME VARIABLES--------------
NRF52_MBED_Timer ITimer(NRF_TIMER_1);
NRF52_MBED_ISRTimer ISR_Timer;
#define HW_TIMER_INTERVAL_MS 1
#define TIMER_INTERVAL_1S 1000L
#define TIMER_INTERVAL_2S 2000L
#define TIMER_INTERVAL_5S 5000L
//##################################################

//----------------DEFINE STATI-----------------
#define START 0
#define CALIBRAZIONE 1
#define RISCALDAMENTO 2
#define MISURA 3
#define IDLE_S 4

//-------------DEFINE TERMICO-------------
#define RT0 100000 // Ω
#define B 4250     // K
#define VCC 3.3    // Supply voltage
#define R 100000   // R=100KΩ

//----------------PIN-----------------
const int BUTTON_PIN = 3;       // PUSH_BUTTON
const int RISCALDATORE_PIN = 5; // RISCALDAMENTO
const int VALVOLA_PIN = 8;      // VALVOLA
const int LED_PIN = 12;         // LED
const int FILO_PIN = A1;        // TERMISTORI
const int PELLE_PIN = A4;

//------------VARIABILI GENERICHE------------
int stato = 4;
int Inizializzazione = 0;
// int ButtonState=HIGH;
volatile byte ButtonState = HIGH;
byte PWM = 0;
byte ending = 0;
int j = -2;
byte i = 0;
byte k = 0;
byte ok = 0;
byte l = 0;
char mode;
float ppm_Ambientali_medio = 0;
byte quarantaperc = 0;
byte button_count = 0;
byte val = 0;

//-------------VARIABILI NTC-------------
float RT, VR, ln, TX, VRT;
float T0 = 25 + 273.15;
float Tfilo = 0;
float Tfilo_old = 0;
float Tpelle = 0;
float Tpelle_old = 0;
byte flag_temp_ok = 0;

//-------------VARIABILI CO2--------------
char buffer[8];
byte bufferCount = 0;
int digitalCo2;
float CO2Ambientale[10];
float Delta = 0;
float Ambientale = 0;
float ppm_ambientali = 0;

//-------------TIME VARIABLES-------------
unsigned long int count_time = 0;
byte seconds = 0;
byte minutes = 0;
byte hours = 0;
byte cali_seconds = 0;
byte cali_minutes = 0;
byte heating_seconds = 0;
byte heating_minutes = 0;
byte temp_seconds = 0;
byte temp_minutes = 0;
byte measure_seconds = 0;
byte measure_minutes = 0;

//---------------FLAGS-----------------
byte flag_calibration = 0;
byte flag_temperature = 0;
byte flag_measurement = 0;

//-------------GENERIC FUNCTIONS-----------------
void pressione(void);
void Startup(void);
float CalcoloTemp(float);
float Calibra(void);
void Misura(void);
void TimerHandler(void);           // Gestisce inizio e fine del timer
void InterruptTimerFunction(void); // ISR collegata al timer ogni secondo

//-------------MEGUNOLINK FUNCTIONS-----------------
TimePlot Variabile1("Ambiente"), Variabile2("Tfilo[°C]"), Variabile3("Tpelle[°C]"), Variabile4("CO2 Sangue"), Variabile5("Delta CO2");

void setup()
{
  Serial1.begin(9600);  // The one attached to the COZIR sensor
  Serial.begin(115200); // The one attached to MegunoLink
  // I/O pins setting
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  pinMode(BUTTON_PIN, INPUT); // cambiare con solo input per la PCB
  pinMode(RISCALDATORE_PIN, OUTPUT);
  pinMode(VALVOLA_PIN, OUTPUT);

  // Serial1.println(F("K 2")); //To startup the Cozir in polling mode

  /* Questa interrupt sul pin digitale BUTTON_PIN triggera una interrupt che esegue la funzione pressione()
   *  quando lo stato del bottone passa da HIGH a LOW (questo è determinato dal comando FALLING)
   */
  // attachInterrupt(digitalPinToInterrupt(BUTTON_PIN),pressione, LOW);

  ITimer.attachInterruptInterval(HW_TIMER_INTERVAL_MS * 1000, TimerHandler);
  ISR_Timer.setInterval(TIMER_INTERVAL_1S, InterruptTimerFunction);
}

void loop()
{

  val = digitalRead(BUTTON_PIN);

  if (val == HIGH)
  {
    ButtonState = HIGH;
    // digitalWrite(LED_PIN, HIGH);
  }
  else if (seconds >= 3 && val == LOW)
  { // 3s of waiting for the power on of the Arduino
    ButtonState = LOW;
    button_count++;
    // digitalWrite(LED_PIN, LOW);
  }
  switch (stato)
  {
  case IDLE_S:
    if (button_count == 1)
    {
      stato = START;
    }
    break;

  case START:
    // Cleaning calibration array
    for (i = 0; i <= 9; i++)
    {
      CO2Ambientale[i] = 0;
    }
    Startup();
    break;

  case CALIBRAZIONE:
    i = 0;
    Inizializzazione = 0;
    while (stato == CALIBRAZIONE)
    {
      if(flag_calibration)
      {
        if (ending == 0)
        {
          j++; // j non dovrebbe essere inizializzato a -1 e non -2 ??? 
          ppm_ambientali = Calibra();
          Variabile1.SendData("Ambiente ppm", ppm_ambientali, TimePlot::Green); // Sends data to MegunoLink
          CO2Ambientale[j] = ppm_ambientali;
  
          if (j == 9)
          {
            j = 8;
            /* Serial.println(CO2Ambientale[0]);
             Serial.println(CO2Ambientale[9]); */
            if (abs(CO2Ambientale[0] - CO2Ambientale[9]) <= 20)
            {
              ok = 1;
            }
            else
            {
              for (k = 0; k < 9; k++)
              {
                CO2Ambientale[k] = CO2Ambientale[k + 1];
              }
            }
          }
        }
      }

      val = digitalRead(BUTTON_PIN);

      if (val == HIGH)
      {
        ButtonState = HIGH;
      }
      else if (val == LOW && cali_minutes >= 1)
      {
        ButtonState = LOW;
        ok = 1;
      }

      if (ok)
      {
        ending = 1;
        ppm_Ambientali_medio = int((CO2Ambientale[0] + CO2Ambientale[9]) / 2);
        ok = 0;
        digitalWrite(LED_PIN, LOW);
      }

      if (ending == 1)
      {
        val = digitalRead(BUTTON_PIN);
        if (val == HIGH)
        {
        }
        else
        {
          stato = RISCALDAMENTO;
          ending = 0;
        }
      }
    }
    break;

  case RISCALDAMENTO:
    // Imposto il PWM con DC al 85%
    analogWrite(RISCALDATORE_PIN, 160);
    while (stato == RISCALDAMENTO)
    {
      if (heating_seconds >= 2)
      {
        val = digitalRead(BUTTON_PIN);

        if (val == HIGH)
        {
          ButtonState = HIGH;
        }
        else
        {
          ButtonState = LOW;
        }

        if (ButtonState == LOW)
        {
          ButtonState = HIGH;
          Serial.println(F("Stop riscaldamento"));
          analogWrite(RISCALDATORE_PIN, 0);
          stato = START;
        }
      }

      if(flag_temperature)
      {
        flag_temperature = 0;
        Tfilo = CalcoloTemp(analogRead(FILO_PIN)); // Pin analogico A4
        Variabile2.SendData("Tfilo[C]", Tfilo, TimePlot::Red);
  
        //      Tpelle=CalcoloTemp(analogRead(PELLE_PIN));
        //      Variabile3.SendData("Tpelle[C]",Tpelle,TimePlot::Blue);
  
        // DOPO 85% proviamo sul 65%
        if (Tfilo >= 41 && Tfilo <= 42)
        {
          analogWrite(RISCALDATORE_PIN, 140); // 35%
          Serial.println(F("The wire is too hot!65%"));
        }
        else if (Tfilo > 42 && Tfilo <= 47)
        {
          analogWrite(RISCALDATORE_PIN, 0);
          // analogWrite(RISCALDATORE_PIN,50);  //20%
          // Serial.println(F("The wire is too hot! 40%"));
        } // else if (Tfilo>=50){
        // analogWrite(RISCALDATORE_PIN,0);
        //}
  
        // The measurement process starts if 37.5 degrees are reached or if 9 minutes of heating has been exceeded
        //      if (Tpelle>=37.0 || heating_minutes>=9){
        //         digitalWrite(RISCALDATORE_PIN,LOW);
        //         analogWrite(RISCALDATORE_PIN,0);
        //         digitalWrite(LED_PIN,HIGH); //Switch on the LED during the measurement process
        //         Serial.println(F("Start of C02 measuring process"));
        //         Tpelle_old=Tpelle;
        //         stato=MISURA;
        //      }
  
        if (Tfilo >= 42)
        {
          flag_temp_ok = 1;
          stato = MISURA;
          analogWrite(RISCALDATORE_PIN, 0);
        }
        else
        {
          flag_temp_ok = 0;
        }
  
        if (temp_seconds >= 120 || heating_minutes >= 9)
        {
          digitalWrite(RISCALDATORE_PIN, LOW);
          analogWrite(RISCALDATORE_PIN, 0);
          digitalWrite(LED_PIN, HIGH); // Switch on the LED during the measurement process
          Serial.println(F("Start of C02 measuring process"));
          Tpelle_old = Tpelle;
          stato = MISURA;
        }
      }
    }
    break;

  case MISURA:
    Tpelle_old = Tpelle;
    // Chiudo la valvola per iniziare la misura
    digitalWrite(VALVOLA_PIN, HIGH);
    while (stato == MISURA)
    {
      if (measure_seconds > 30)
      {
        val = digitalRead(BUTTON_PIN);

        if (val == HIGH)
        {
          ButtonState = HIGH;
        }
        else
        {
          ButtonState = LOW;
        }

        if (ButtonState == LOW)
        {
          ButtonState = HIGH;
          /*Serial.println(F("Start up condition"));*/
          digitalWrite(VALVOLA_PIN, LOW);
          stato = START;
        }
      }
      if(flag_measurement)
      {
        Misura();
        // Controllo Temperatura: Se Temperatura new e Temperatura old sono diversi di piu di un grado stampa Tpelle
        Tfilo = CalcoloTemp(analogRead(FILO_PIN));
  
        // Se durante la misurazione la T pelle scende sotto i 34°C rinizio a scaldare
        if (Tfilo <= 28)
        {
          analogWrite(RISCALDATORE_PIN, 90);
        }
  
        if (Tfilo >= 34)
        {
          analogWrite(RISCALDATORE_PIN, 0);
        }
      }
    }
    break;
  }
}

void InterruptTimerFunction()
{
  // Overall time counting
  seconds++;

  if (seconds == 60)
  {
    minutes++;
    seconds = 0;
  }
  if (minutes == 60)
  {
    hours++;
    minutes = 0;
  }

  if (stato == CALIBRAZIONE)
  {
    cali_seconds++;
    flag_calibration = 1;
    if (cali_seconds == 60)
    {
      cali_seconds = 0;
      cali_minutes++;
    }
  }

  if (stato != CALIBRAZIONE)
  {
    cali_seconds = 0;
    cali_minutes = 0;
  }

  // Heating phase time counting
  if (stato == RISCALDAMENTO)
  {
    heating_seconds++;
    flag_temperature = 1;
    if (heating_seconds == 60)
    {
      heating_seconds = 0;
      heating_minutes++;
    }

    if (flag_temp_ok)
    {
      temp_seconds++;
    }
  }

  if (stato != RISCALDAMENTO)
  {
    heating_seconds = 0;
    heating_minutes = 0;
    temp_seconds = 0;
    temp_minutes = 0;
  }

  if (stato == MISURA)
  {
    measure_seconds++;
    flag_measurement = 1;
    if (measure_seconds == 60)
    {
      measure_seconds = 0;
      measure_minutes++;
      // Serial.println(F("Heating minutes: "));
      // Serial.println(heating_minutes);
    }
  }

  if (stato != MISURA)
  {
    measure_seconds = 0;
    measure_minutes = 0;
  }
}

void Startup()
{
  /*Inizializzazione è una variabile che all'inizio vale 0, ma nel momento in cui c'è la connessione bluetooth
   * passa a 1 perchè la funzione Startup() viene chiamata solo quando si entra nel case START, primo case
   * dopo la connessione con la periferica
   */
  delay(1000);
  Serial1.print(F("K 2\r\n"));

  // BUTTON_PIN è LOW quando premuto
  if (ButtonState == LOW)
  {
    ButtonState = HIGH;
    digitalWrite(LED_PIN, HIGH);
    delay(1000);
    digitalWrite(LED_PIN, LOW);
    Serial.println(F("Entering calibration process"));
    stato = CALIBRAZIONE;
  }
}

/* Interrupt sulla pressione del tasto */
void pressione()
{
  ButtonState = LOW;
  button_count++;
}

float Calibra()
{
  flag_calibration = 0;
  // Inserisco range in cui è possibile compiere la misura
  /* Serial1 è la seriale associata al sensore di CO2 che fornisce valori a 8 bit. Z\r\n ritorna il
   *  valore più recente di CO2 che viene misurato già filtrato digitalmente.
   */
  digitalWrite(LED_PIN, !digitalRead(LED_PIN));
  Serial1.println(F("Z")); // request co2
  delay(50);               // Campiona a 1 s;
  bool foundValues = false;
  // foundValues è vero fino a che non ho stampato info
  while (!foundValues)
  {
    if (Serial1.available())
    {
      char input = Serial1.read();

      /* \n indicates the end of one measurement, while 32 is the ASCII character used to separate different
       *  responses from the sensor, including measurements. Ancora da chiarire perchè 8 e non 5 bit
       */
      if (input != '\n' && input != 32 && bufferCount < 8) // get response from COZIR
      {
        buffer[bufferCount] = input;
        bufferCount++;
      }
      else if (input == '\n')
      { // sort Serial data once we have received the \n(carattere terminatore)
        bufferCount = 0;
        // Serial.println(buffer);
        for (byte i = 0; i < 7; i++)
        {
          // shuffle array back one position to get rid of the capital letter
          buffer[i] = buffer[i + 1];
        }
        digitalCo2 = atoi(buffer);
        Ambientale = digitalCo2;
        foundValues = true;

        for (byte i = 0; i < 8; i++) // clear the entire buffer array
        {
          buffer[i] = 0;
        }
      }
    }
  }

  // Ritorno il delta ad ogni valore ricevuto
  return Ambientale;
}

float CalcoloTemp(float RawADC)
{
  VR = RawADC; // RawADC è il valore che arriva dal pin analogico con analogRead() in bit
  // Acquisizione valore analogico di VRT
  VR = (VCC / 1023.00) * VR; // Conversione in voltaggio
  VRT = VCC - VR;            // Sottraggo VR a VCC perchè nel partitore resistivo l'NTC è sopra e io campiono il valore di tensione sulla
                             // resistenza sotto
  RT = VRT / (VR / R);       // Resistenza di RT

  ln = log(RT / RT0);
  TX = (1 / ((ln / B) + (1 / T0))); // Temperatura dal termistore

  TX = TX - 273.15; // Conversione in Celsius

  // Serial.print(TX + 273.15);        //Conversion to Kelvin
  // Serial.print("K\t\t");
  // Serial.print((TX * 1.8) + 32);    //Conversion to Fahrenheit
  // Serial.println("F");
  return TX;
}

void Misura()
{
  flag_measurement = 0;

  // Inserisco range in cui è possibile compiere la misura
  Serial1.println(F("Z")); // request co2
  delay(50);               // Campiona a 1 s;
  bool foundValues = false;
  // foundValues è vero fino a che non ho stampato info
  while (!foundValues)
  {
    char input = Serial1.read();

    if (input > 0)
    {
      if (input != '\n' && input != 32 && bufferCount < 8) // get response from COZIR
      {
        buffer[bufferCount] = input;
        bufferCount++;
      }
      else if (input == '\n')
      { // sort Serial data once we have received the \n(carattere terminatore)
        bufferCount = 0;
        // Serial.println(buffer);
        for (byte i = 0; i < 7; i++)
        {
          // shuffle array back one position to get rid of the capital letter
          buffer[i] = buffer[i + 1];
        }

        // converte stringa in int
        digitalCo2 = atoi(buffer);
        // Serial.print(F("\nValore Co2 ppm: ")); Serial.println(digitalCo2);
        // Serial.print(F("\nValore Co2 mmHg: ")); Serial.println(digitalCo2 * 0.077521636);
        Variabile4.SendData("CO2Sangue", digitalCo2, TimePlot::Black);
        Delta = digitalCo2 - ppm_Ambientali_medio;
        Variabile5.SendData("DeltaCO2", Delta, TimePlot::Blue);

        // Invio continuo
        Serial.print(F("\nValore Co2 ppm: "));
        Serial.println(digitalCo2);
        // Serial.print(F("\nValore Co2 mmHg: "));Serial.println(digitalCo2*0.077521636);

        foundValues = true;

        for (byte i = 0; i < 8; i++) // clear the entire buffer array
        {
          buffer[i] = 0;
        }
      }
    }
  }
}

/* Timer settings */
void TimerHandler()
{
  ISR_Timer.run();
}
