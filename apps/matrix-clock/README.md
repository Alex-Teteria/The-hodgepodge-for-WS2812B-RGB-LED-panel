# LED Matrix Clock (RP2040 + DS3231)

Годинник на базі **RP2040 (Raspberry Pi Pico)** з використанням **16×16 NeoPixel (WS2812) LED-матриці** та **RTC модуля DS3231**.  
Час відображається у форматі **HH:MM**, секунди показуються на **периметрі матриці**.

---

# Основні можливості

- відображення часу у форматі **HH:MM**, цифри - пікселі 6 × 4
- **блимання двокрапки** між годинами та хвилинами
- секунди відображаються по **периметру матриці (60 пікселів)**
- **колір секунд змінюється кожну хвилину**, новий колір вибирається випадково з набору
- два режими відображення секунд

---

# Режими відображення секунд

## 1. Накопичувальна лінія

`line_sec = True`
Периметр поступово заповнюється від **0 до 59 секунди**.  
0 → 1 → 2 → ... → 59  

На початку нової хвилини колір периметра змінюється.

---

## 2. Рухома точка

`line_sec = False`  

По периметру рухається **одна точка**, що відповідає поточній секунді.

---

# Апаратна конфігурація та підключення

## Мікроконтролер

- Raspberry Pi Pico (RP2040)

## Світлодіоди

- NeoPixel / WS2812
- матриця **16×16 (256 LED)**

## Модуль RTC

- DS3231 (I2C)

## Підключення модуля DS3231

| Pico | DS3231 |
| ---- | ------ |
| GP4  | SDA    |
| GP5  | SCL    |
| 3V3  | VCC    |
| GND  | GND    |

---

## Підключення LED Matrix (NeoPixel / WS2812)

| Pico | Matrix |
| ---- | ------ |
| GP20 | DIN    |
| 5V   | VCC    |
| GND  | GND    |

---

# Алгоритм роботи

1. читається час з **DS3231**
2. якщо змінилась хвилина
   - вибирається новий колір периметра
3. якщо змінилась секунда
   - оновлюється дисплей
4. цикл повторюється

Опитування RTC: `кожні 20 ms`  
Оновлення дисплея: `1 раз на секунду`  

# Синхронізація часу

За потреби RTC DS3231 синхронізується з комп’ютера через USB порт.

Алгоритм:

1. Pico підключається до ПК
2. На ПК запускається скрипт синхронізації
3. Через **MicroPython REPL** виконується
   `ds.set_datetime(...)`
4. Виконується soft reboot
5. `main.py` запускається з новим часом  

Скрипт синхронізації:  

```python
import serial
import serial.tools.list_ports
import time
from datetime import datetime

def sync_and_reboot_pico():
    # 1. Автопошук порту
    ports = serial.tools.list_ports.comports()
    pico_port = next((p.device for p in ports if "2E8A:0005" in p.hwid.upper()), None)

    if not pico_port:
        print("Pico не знайдено!")
        return

    try:
        with serial.Serial(pico_port, 115200, timeout=1) as ser:
            print(f"Підключено до {pico_port}. Зупинка поточної програми...")

            # 2. Перериваємо виконання (Ctrl+C)
            ser.write(b'\x03') 
            time.sleep(0.5) 
            ser.write(b'\x03') # Подвійне натискання для надійності

            # 3. Формуємо команду встановлення часу
            now = datetime.now()
            day_index = now.weekday()
            cmd = (f"from machine import Pin, I2C; "
                   f"from ds3231_simple import DS3231; "
                   f"i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000);"
                   f"ds = DS3231(i2c);"
                   f"datetime = ({now.year}, {now.month}, {now.day}, {day_index}, {now.hour}, {now.minute}, {now.second}, 0);"
                   f"ds.set_datetime(datetime)\r\n")

            ser.write(cmd.encode())
            time.sleep(0.1)

            print(f"Час встановлено: {now.strftime('%H:%M:%S')}")

            # 4. М'яке перезавантаження (Ctrl+D)
            print("Перезапуск main.py з новим часом...")
            ser.write(b'\x04') 

            # Читаємо підтвердження від Pico (перші кілька рядків після ребуту)
            time.sleep(0.5)
            while ser.in_waiting:
                print("Pico:", ser.readline().decode().strip())

    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == "__main__":
    sync_and_reboot_pico()
```
> Попередньо можливо необхідно буде встановити бібліотеку:
```bash
pip install pyserial
```

## Запуск скрипта синхронізації через PowerShell
Для зручності запуск синхронізації можливий через ярлик на робочому столі. Для цього:  

1. Створити файл `monitor_pico.ps1` із таким кодом:  

```powershell
$vid = "2E8A" 
# Шукаємо Pico 
$pico = Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match "VID_$vid" }

if ($pico) {
    Write-Host "Pico знайдено! Синхронізація..."
    python "C:\<...>\sync_ds3231.py"
    Write-Host "Готово. Скрипт завершено."
} else {
    Write-Host "Pico не підключено. Спробуйте підключити і запустити знову."
}    
```
 > Переконайтеся, що шлях до файлу та ім'я файла в скрипті вказано правильно (рядок: python "C:\\<...>\sync_ds3231.py").   

2. Створити ярлик для запуску синхронізації  
   - Натисніть правою кнопкою миші на робочому столі: `Створити -> Ярлик`
   - У полі "Вкажіть розташування об'єкта" скопіюйте та вставте наступний рядок (одним рядком):  
     `powershell.exe -ExecutionPolicy Bypass -File "C:\Users\<User name>\Desktop\monitor_pico.ps1"
     `
     
     > (Переконайтеся, що шлях до файлу в лапках вказано правильно). 
   - Натисніть `Далі`, назвіть ярлик, наприклад, "Sync Pico", і натисніть `Готово`.

---

## Credits and License

- Licensed under MIT.
