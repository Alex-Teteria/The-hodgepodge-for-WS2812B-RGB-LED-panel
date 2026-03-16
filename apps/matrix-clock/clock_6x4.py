# Author: Oleksandr Teteria
# v2.0
# 16.03.2026
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license


import neopixel, time, random
import machine
from machine import Pin, I2C
from ds3231_simple import DS3231


# Налаштування шини I2C0 для Pico
# SDA на GP4, SCL на GP5
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)

ds = DS3231(i2c)

n = 16
m = 16

np = neopixel.NeoPixel(machine.Pin(20), n * m)

green = 0, 24, 0
green_ellow = 6, 10, 0
red = 16, 0, 0
orange = 12, 4, 0
blue = 0, 0, 16
blue_light = 0, 8, 8
magenta = 8, 0, 8
yellow = 12, 8, 0
teal = 0, 5, 3
white = 12, 20, 8
nothing = 0, 0, 0

perimeter_colors = (green, red, yellow, magenta, blue)

# 6x4: rows 0..5, cols 0..3
digits_coords = {
    0: (
        (0,1), (0,2),
        (1,0), (1,3),
        (2,0), (2,3),
        (3,0), (3,3),
        (4,0), (4,3),
        (5,1), (5,2)
    ),
    1: (
        (0,2),
        (1,1), (1,2),
        (2,2),
        (3,2),
        (4,2),
        (5,1), (5,2), (5,3)
    ),
    2: (
        (0,0),(0,1),(0,2),
        (1,3),
        (2,3),
        (3,1), (3,2), (3,3),
        (4,0),
        (5,0),(5,1),(5,2),(5,3),
    ),
    3: (
        (0,0), (0,1), (0,2),
        (1,3),
        (2,1), (2,2),
        (3,3),
        (4,3),
        (5,0), (5,1), (5,2),
    ),
    4: (
        (0,0), (0,3),
        (1,0), (1,3),
        (2,1), (2,2), (2,3),
        (3,3),
        (4,3),
        (5,3)
    ),
    5: (
        (0,0), (0,1), (0,2), (0,3),
        (1,0),
        (2,0), (2,1), (2,2),
        (3,3),
        (4,3),
        (5,0), (5,1), (5,2)
    ),
    6: (
        (0,1), (0,2), (0,3),
        (1,0),
        (2,0), (2,1), (2,2),
        (3,0), (3,3),
        (4,0), (4,3),
        (5,1), (5,2)
    ),
    7: (
        (0,0), (0,1), (0,2), (0,3),
        (1,3),
        (2,2),
        (3,1),
        (4,1),
        (5,1)
    ),
    8: (
        (0,1), (0,2),
        (1,0), (1,3),
        (2,1), (2,2),
        (3,0), (3,3),
        (4,0), (4,3),
        (5,1), (5,2)
    ),
    9: (
        (0,1), (0,2),
        (1,0), (1,3),
        (2,0), (2,3),
        (3,1), (3,2), (3,3),
        (4,3),
        (5,0), (5,1), (5,2)
    )
}

positions = [
    (2, 3),  # H1
    (2, 8),  # H2
    (9, 3),  # M1
    (9, 8),  # M2
]

def coord_to_pix(i, j):
    return m * i + j if i % 2 else m - j - 1 + m * i

# clock_maps
clock_maps = []
for i_off, j_off in positions:
    pos_map = {
        dig: tuple(coord_to_pix(i + i_off, j + j_off) for i, j in coords)
        for dig, coords in digits_coords.items()
    }
    clock_maps.append(pos_map)

# colon
colon_coords = (coord_to_pix(3, 13), coord_to_pix(5, 13))
colon = 0  # init 

last_perim_pix = None  # init

# perimeter map (60)
def generate_perimeter_map():
    map_60 = []
    for j in range(16):            # top
        map_60.append(coord_to_pix(0, j))
    for i in range(1, 15):         # right
        map_60.append(coord_to_pix(i, 15))
    for j in range(15, -1, -1):    # bottom
        map_60.append(coord_to_pix(15, j))
    for i in range(14, 0, -1):     # left
        map_60.append(coord_to_pix(i, 0))
    return map_60

perimeter_map = generate_perimeter_map()

# pixels to clear each frame (digits + colon only), perimeter untouched 
clear_pixels = set(colon_coords)
for pos_map in clock_maps:
    for d in range(10):
        clear_pixels.update(pos_map[d])

def pick_new_perimeter_color(prev):
    if len(perimeter_colors) <= 1:
        return prev
    c = prev
    while c == prev:
        c = random.choice(perimeter_colors)
    return c

def draw_clock(hh, mm, ss, color_digits, color_sec, line_sec=True):
    global colon, last_perim_pix

    # clear only the dynamic interior (digits + colon)
    for pix in clear_pixels:
        np[pix] = nothing

    # digits
    digits = (hh // 10, hh % 10, mm // 10, mm % 10)
    for i in range(4):
        for pix in clock_maps[i][digits[i]]:
            np[pix] = color_digits

    # perimeter seconds
    if line_sec:
        # накопичення 0..ss 
        for s in range(ss + 1):
            if s < len(perimeter_map):
                np[perimeter_map[s]] = color_sec
        # у цьому режимі "остання точка" не потрібна
        last_perim_pix = None
    else:
        # тільки одна поточна секунда, попередню гасимо
        cur_pix = perimeter_map[ss]

        if last_perim_pix is not None and last_perim_pix != cur_pix:
            np[last_perim_pix] = nothing

        np[cur_pix] = color_sec
        last_perim_pix = cur_pix

    # blinking colon
    colon ^= 1
    for dot in colon_coords:
        np[dot] = color_digits if colon else nothing

    np.write()


def start_clock(color_digits, line_sec=True):
    # clear everything once on start
    np.fill(nothing)
    np.write()

    t0 = ds.datetime()
    last_mm = t0[5]
    last_ss = -1
    cur_color_sec = random.choice(perimeter_colors)

    while True:
        t = ds.datetime()
        hh, mm, ss = t[4], t[5], t[6]

        # нова хвилина -> новий колір периметра (без повтору попереднього)
        if mm != last_mm:
            cur_color_sec = pick_new_perimeter_color(cur_color_sec)
            last_mm = mm

        # оновлюємо дисплей тільки при зміні секунди
        if ss != last_ss:
            draw_clock(hh, mm, ss, color_digits, cur_color_sec, line_sec)
            last_ss = ss

        time.sleep_ms(20)  # перевірка раз на 20мс 

start_clock(green)
