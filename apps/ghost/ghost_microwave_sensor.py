# -----------------------------------------------------------------------
# Moving ghost body pixels for WS2816, 16x16 rgb LEDs
# The ghost's color and its speed changes depending on the distance to the person/object present
# A sensor of the HLK-LD2410 type (Microwave human/object presence sensor)
# was used to measure the distance.
# -----------------------------------------------------------------------
# Author: Alex Teteria
# v2.0
# 23.02.2026
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license
import neopixel, random, time
from ghost_neo import Ghost
from machine import UART, Pin
from ld2410 import LD2410
import _thread


uart = UART(1, baudrate=256000, tx=Pin(8), rx=Pin(9), timeout=20)
sensor = LD2410(uart, led_pin=25, flush_on_read=False)

n = 16 # number of row
m = 16 # number of col

red = 16, 0, 0
blue = 0, 0, 24

# colors from red (min dist) to blue (max dist)
colors = ((16, 0, 0), (15, 1, 0), (14, 2, 0), (13, 3, 0),
          (12, 4, 0), (12, 5, 0), (12, 6, 0), (12, 7, 0),
          (12, 8, 0), (11, 9, 0), (10, 10, 0), (9, 11, 0),
          (9, 12, 0), (8, 13, 0), (8, 14, 0), (7, 15, 0),
          (6, 16, 0), (5, 17, 0), (4, 18, 0), (3, 19, 0),
          (2, 20, 0), (1, 22, 0), (0, 24, 0), (0, 22, 2),
          (0, 20, 4), (0, 18, 6), (0, 16, 8), (0, 14, 10),
          (0, 12, 12), (0, 10, 14), (0, 8, 16), (0, 6, 18),
          (0, 4, 20), (0, 2, 22), (0, 0, 24)
          )

boardled = Pin(25, Pin.OUT)
np = neopixel.NeoPixel(Pin(20), n * m)
ghost = Ghost(np)
direction = ('ahead', 'up', 'down', 'right', 'left')

# init of the distance
if not sensor.probe():
    dist = 800
else:
    dist = 30

# при необхідності — замінити поріг 100 на 60..80
ENERGY_TRIGGER = 100

def get_colors():
    # distance limits in sm
    limits = (30, 39, 40, 42, 44, 46, 50, 56,
              64, 66, 69, 73, 78, 86, 95, 97,
              100, 104, 109, 115, 122, 130,
              139, 147, 155, 165, 175, 188,
              204, 214, 226, 240, 256, 276, 300
              )

    for i, limit in enumerate(limits):
        if dist <= limit:
            color_2 = blue if i < 7 else red
            return colors[i], color_2
    return blue, red   

def get_speed(dist):
    # distance limits in sm
    limits = (30, 44, 64, 78, 100, 122, 155, 175, 204, 226, 300)
    speed = (80, 150, 200, 250, 300, 350, 400, 500, 600, 700, 800)
    for i, limit in enumerate(limits):
        if dist <= limit:
            return speed[i]
    return 200

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

def main_run():
    body_color, eyes_color = get_colors()
    ghost.look(random.choice(direction), body_color, eyes_color)
    time.sleep_ms(get_speed(dist))
    
def clean_up():
    # to clean the led-matrix
    for pix in range(n * m):
        np[pix] = 0, 0, 0
    np.write()


if __name__ == '__main__':
    
    # measuring the distance in the second thread
    if sensor.probe():
        _thread.start_new_thread(get_dist, (sensor,))
    
    while True:
        main_run()

