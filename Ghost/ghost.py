# -----------------------------------------------------------------------
# Moving ghost body pixels for WS2816, 16x16 rgb LEDs
# The ghost's color changes depending on the ambient temperature,
# and its speed of movement depends on pressure.
# A BME280 type sensor was used to measure temperature and pressure
# -----------------------------------------------------------------------
# Author: Alex Teteria
# v0.2
# 10.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license
import neopixel, random, time
from ghost_neo import Ghost

from machine import Pin, I2C
import bme280_float as bme280


n = 16 # number of row
m = 16 # number of col

green = 0, 24, 0
green_yellow = 6, 10, 0
red = 16, 0, 0
orange = 12, 4, 0
blue = 0, 0, 16
blue_light = 0, 8, 8
magenta = 8, 0, 8
yellow = 12, 8, 0
teal = 0, 5, 3
white = 12, 20, 8
nothing = 0, 0, 0

bus = I2C(0, scl=Pin(21, Pin.PULL_UP), sda=Pin(20, Pin.PULL_UP), freq=400_000)
bme = bme280.BME280(i2c=bus)

np = neopixel.NeoPixel(Pin(28), n * m)
ghost = Ghost(np)
direction = ('ahead', 'up', 'down', 'right', 'left')
sensor = [0, 0, 0] # ініциалізація сенсора

def get_colors(temperature):
    # temperature limits in °C
    limits = (34, 30, 28, 26, 24, 22, 20)
    colors_1 = (red, orange, yellow, green_yellow, green, blue_light, blue)
    colors_2 = (blue, blue, red, red, red, red, red)
    for i, limit in enumerate(limits):
        if temperature > limit:
            return colors_1[i], colors_2[i]
    return magenta, nothing   

def get_speed(pressure):
    # pressure in mmHg: 760, 755, 750, 745, 740, 738, 736, 734, 732, 730, 725
    limits = (101325, 100658, 99992, 99325, 98659, 98392, 98125, 97858, 97592, 97325, 96659)
    speed = (100, 150, 200, 250, 300, 350, 400, 500, 600, 700, 800)
    for i, limit in enumerate(limits):
        if pressure > limit:
            return speed[i]
    return 1000   

def main_run():
    bme.read_compensated_data(sensor)
    body_color, eyes_color = get_colors(sensor[0])
    ghost.look(random.choice(direction), body_color, eyes_color)
    time.sleep_ms(get_speed(sensor[1]))
    
def clean_up():
    # to clean the led-matrix
    for pix in range(n * m):
        np[pix] = 0, 0, 0
    np.write()


if __name__ == '__main__':
    
    while True:
        main_run()

# to clean the led-matrix:
# clean_up()
    