#include <SPI.h>
#include <MFRC522.h>
#define PERIOD 30000

#define SS_PIN 10
#define RST_PIN 9
MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance.

#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 16, 2); // Устанавливаем дисплей

unsigned long my_timer; //время работы
//uint32_t timer = 0;


void setup() {
  lcd.init();
  lcd.backlight();// Включаем подсветку дисплея
  lcd.setCursor(0, 0);
  lcd.print("Press Your Card");


  Serial.begin(9600); // Initialize serial communications with the PC
  SPI.begin();   // Init SPI bus
  mfrc522.PCD_Init(); // Init MFRC522 card
  Serial.println("Scan PICC to see UID and type...");

  my_timer =  millis();

}
void loop() {
  //  if (millis() - timer >= PERIOD) {
  //    // ваше действие
  //    lcd.clear(); //очистить
  //    lcd.setCursor(0, 0);
  //    lcd.print("Press Your Card");
  //    do {
  //      timer += PERIOD;
  //      if (timer < PERIOD) break;  // переполнение uint32_t
  //    } while (timer < millis() - PERIOD); // защита от пропуска шага
  //  }
  
  //переполнение my_timer примерно 50 дней
  if (millis() - my_timer < 0) {
  my_timer =  millis();
  }


  // очистка экрана
  if (millis() - my_timer >= PERIOD) {
    my_timer = millis();   // "сбросить" таймер
    // дейтвия, которые хотим выполнить один раз за период
    lcd.clear(); //очистить
    lcd.setCursor(0, 0);
    lcd.print("Press Your Card");

    Serial.println("Скинул " + String(my_timer));
  }


  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  String UID_string;
  Serial.print("Card UID:");
  for (byte i = 0; i < mfrc522.uid.size; i++)
  {
    Serial.print(mfrc522.uid.uidByte[i], HEX);
    String byte_uid = String(mfrc522.uid.uidByte[i], HEX);

    if (byte_uid.length() == 1)
    {
      byte_uid = "0" + byte_uid;
    }
    UID_string += byte_uid;
  }

  Serial.println();
  Serial.println("Полный код:");
  Serial.println(UID_string);


  unsigned long UID_DEC = str_to_long(UID_string);

  Serial.println("UID_DEC:");
  Serial.println(UID_DEC);

  lcd.clear(); //очистить
  //первая строка
  lcd.setCursor(0, 0);
  lcd.print("ReadOK." + UID_string);

  //Вторая строка
  lcd.setCursor(0, 1);
  // Выводим на экран
  lcd.print("UID:" + String(UID_DEC, 10));

  my_timer = millis();   // "сбросить" таймер

}
//перевод из string в unsigned long
unsigned long str_to_long(String str) {
  unsigned long ansver = 0;
  for (byte n = 0; n < str.length(); n++) {
    if ((byte(str.charAt(n) ) >= 0x30) && (byte(str.charAt(n) ) <= 0x39)) { //цифры ASCII 0 - 9
      ansver |= ((byte(str.charAt(n) ) - 0x30));
    }
    if ((byte(str.charAt(n) ) >= 0x41) && (byte(str.charAt(n) ) <= 0x46)) { //символы ASCII A - F
      ansver |= ((byte(str.charAt(n) ) - 0x41 + 10));
    }
    if ((byte(str.charAt(n) ) >= 0x61) && (byte(str.charAt(n) ) <= 0x66)) { //символы ASCII a - f
      ansver |= ((byte(str.charAt(n) ) - 0x61 + 10));
    }

    if (n < (str.length() - 1) ) {
      ansver = ansver << 4;
    }

  }

  return ansver;

}
