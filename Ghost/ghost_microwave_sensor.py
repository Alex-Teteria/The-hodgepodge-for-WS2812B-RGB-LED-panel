# -----------------------------------------------------------------------
# Moving ghost body pixels for WS2816, 16x16 rgb LEDs
# The ghost's color and its speed changes depending on the distance to the person/object present
# A sensor of the HLK-LD2410 type (Microwave human/object presence sensor)
# was used to measure the distance.
# https://github.com/shabaz123/LD2410/blob/main/ld2410.py
# -----------------------------------------------------------------------
# Author: Alex Teteria
# v0.1
# 04.07.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license
import neopixel, random, time
from ghost_neo import Ghost

from machine import Pin
import ld2410
import _thread


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
np = neopixel.NeoPixel(Pin(28), n * m)
ghost = Ghost(np)
direction = ('ahead', 'up', 'down', 'right', 'left')


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
    speed = (150, 200, 250, 300, 350, 400, 500, 600, 700, 800, 900)
    for i, limit in enumerate(limits):
        if dist <= limit:
            return speed[i]
    return 200

def get_dist():
    global dist
    while True:
        meas = ld2410.read_serial_frame(print_en=False)
        if meas['moving_energy'] == 100:
            # dist = meas['moving_distance']
            dist = meas['detection_distance']
        if meas['state'] == ld2410.STATE_MOVING_TARGET or meas['state'] == ld2410.STATE_COMBINED_TARGET:
            boardled.value(1)
        else:
            boardled.value(0)
    

def main_run():
    body_color, eyes_color = get_colors()
    ghost.look(random.choice(direction), body_color, eyes_color)
    time.sleep_ms(get_speed(30))
    
def clean_up():
    # to clean the led-matrix
    for pix in range(n * m):
        np[pix] = 0, 0, 0
    np.write()

# init of the distance
dist = 30

if __name__ == '__main__':
    
    # measuring the distance in the second thread
    _thread.start_new_thread(get_dist, ())
    while True:
        main_run()

# to clean the led-matrix:
# clean_up()
    