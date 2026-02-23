# LD2410 MicroPython Driver

Цей драйвер призначений для сенсора присутності HLK-LD2410 (LD2410) під MicroPython, зокрема на RP2040 (Raspberry Pi Pico / Pico W). Драйвер читає Basic report-кадри з UART та надає просту перевірку підключення сенсора через probe().

Підтримується:

- читання Basic report (стан, дистанції, “енергії”)
- ін’єкція UART (UART налаштовується у вашому застосунку, а не в драйвері)
- опційне керування LED (наприклад, GPIO25)
- probe() через команду читання firmware (спрощена перевірка “сенсор відповідає”)

Не підтримується (у поточній версії):

- розбір Engineering mode (кадри з payload_len != 0x0d повертаються як None)

--------------------------------------------

1. Підключення (RP2040)

--------------------------------------------

Типова схема:

- Pico UART TX -> LD2410 RX
- Pico UART RX -> LD2410 TX
- GND Pico -> GND LD2410 (обов’язково спільна земля)
- Живлення сенсора — згідно характеристик модуля

Приклад пінів:

- UART1 TX: GP8
- UART1 RX: GP9
- LED індикатор: GP25 (вбудований LED Pico)

--------------------------------------------

2. Ініціалізація UART і драйвера

--------------------------------------------

Приклад використання:

from machine import UART, Pin
from ld2410 import LD2410
import time

uart = UART(1, baudrate=256000, tx=Pin(8), rx=Pin(9), timeout=20)
sensor = LD2410(uart, led_pin=25, flush_on_read=False)

while True:
    meas = sensor.read_report(print_hex=False)
    if meas:
        print(meas)
    time.sleep_ms(50)

Пояснення:

- UART створюється в основному коді, тому легко міняти піни/номер UART/baudrate, не лізучи у драйвер.
- led_pin (опційно): якщо заданий, драйвер вмикає LED при стані MOVING або COMBINED.
- flush_on_read: якщо True, драйвер перед читанням кадру чистить буфер UART (може бути корисно, але інколи шкодить).

--------------------------------------------

3. probe() — проста перевірка “сенсор підключено”

--------------------------------------------

Метод probe() робить:

- очищення UART буфера
- відправляє команду “read firmware”: A0 00 у форматі командного кадру
- чекає sleep_ms
- читає доступні байти і перевіряє, що там є CMD_HEADER і CMD_TERMINATOR

Використання:

if sensor.probe(sleep_ms=80):
    print("LD2410 підключено")
else:
    print("LD2410 не знайдено")

Рекомендації:

- якщо драйвер використовується в другому потоці (який постійно читає read_report()), то probe() викликати ДО запуску другого потоку, щоб потік не “з’їв” відповідь firmware.
- якщо інколи probe() повертає False, збільшіть sleep_ms до 120..150.

--------------------------------------------

4. read_report() — читання Basic report

--------------------------------------------

read_report(print_hex=False) читає один report-кадр:

- шукає REPORT_HEADER (f4 f3 f2 f1)
- читає 2 байти length (little-endian)
- дочитує payload і 4 байти REPORT_TERMINATOR (f8 f7 f6 f5)
- якщо payload_len == 0x0d (Basic), парсить поля і повертає словник meas
- якщо payload_len інший (наприклад 0x23 для Engineering), повертає None

Параметр:

- print_hex=True: друкує весь кадр у hex (для діагностики)

--------------------------------------------

5. Поля словника meas

--------------------------------------------

meas має ключі:

- state:
  0 = no target
  1 = moving target
  2 = stationary target
  3 = combined target

- moving_distance: відстань до рухомої цілі, сантиметри

- moving_energy: інтенсивність сигналу для рухомої компоненти, шкала 0…100 “схожа на відсотки”, бо має 100 як верхню межу. Але це не калібрований відсоток чогось фізичного; це умовна величина, нормована сенсором

- stationary_distance: відстань до нерухомої цілі, сантиметри

- stationary_energy: інтенсивність сигналу для нерухомої компоненти (шкала 0…100, умовні одиниці)

- detection_distance: підсумкова дистанція виявлення, сантиметри

Примітка:
detection_distance - це загальна/підсумкова дистанція, на якій сенсор вважає, що ціль присутня (часто близько до moving_distance або stationary_distance, залежно від того, який тип цілі зараз домінує).

Практика (Як правильно інтерпретувати на практиці):

- Для логіки “є людина/об’єкт чи ні” перш за все дивляться state.
- Для відстані — беруть:
  - moving_distance, якщо state = moving/combined
  - stationary_distance, якщо state = stationary
  - або detection_distance, якщо хочете “єдину” відстань без розділення по типу

--------------------------------------------

6. Приклад запуску потоку лише якщо сенсор знайдено

--------------------------------------------

import _thread, time
from machine import UART, Pin
from ld2410 import LD2410

uart = UART(1, baudrate=256000, tx=Pin(8), rx=Pin(9), timeout=20)
sensor = LD2410(uart, led_pin=25, flush_on_read=False)

dist = 30
ENERGY_TRIGGER = 80  # підберіть 

def get_dist(sensor):
    global dist
    while True:
        meas = sensor.read_report(print_hex=False)
        if meas is None:
            time.sleep_ms(20)
            continue
        if meas.get("moving_energy", 0) >= ENERGY_TRIGGER:
            dist = meas.get("detection_distance", dist)
        time.sleep_ms(20)

if sensor.probe(sleep_ms=80):
    _thread.start_new_thread(get_dist, (sensor,))
    print("LD2410 знайдено -> потік дистанції запущено")
else:
    print("LD2410 не знайдено -> працюємо без сенсора")

while True:
    # основний цикл, в якому використовується значення dist
    # ....
    time.sleep_ms(100)

--------------------------------------------


7. Troubleshooting

--------------------------------------------

probe() завжди False:

- перевірте TX/RX (часто переплутані)
- перевірте GND (спільна земля обов’язкова)
- перевірте, що ви використовуєте правильний UART і правильні піни 
- збільшіть sleep_ms у probe() до 120..150
- переконайтесь у правильному baudrate (часто 256000)

read_report() часто None:

- збільшіть UART timeout (наприклад 20..50)
- не вмикайте flush_on_read без потреби (інколи він викидає корисні байти)
- переконайтесь, що сенсор шле Basic report (інакше потрібен Engineering парсер)

--------------------------------------------

## License
- Licensed under MIT.

