# -----------------------------------------------------------------------
# Contains the Ghost class - ghost body pixels for WS2816, 16x16 rgb LEDs
# -----------------------------------------------------------------------
# Author: Alex Teteria
# v0.1
# 09.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import neopixel, random, time

n = 16 # number of row
m = 16 # number of col

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

# figure = ((i1, j1), (i2, j2), ...) coordinates of the points of the figure on the matrix (row, column)
body_pos = ((7,1), (8,1), (9,1), (10,1), (11,1), (12,1), (13,1),
        (4,2), (5,2), (6,2), (7,2), (8,2), (9,2), (10,2), (11,2), (12,2), (13,2), (14,2),
        (3,3), (4,3), (5,3), (6,3), (7,3), (8,3), (9,3), (10,3), (11,3), (12,3), (13,3), (14,3),
        (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (8,4), (9,4), (10,4), (11,4), (12,4), (13,4),
        (2,5), (3,5), (4,5), (5,5), (6,5), (7,5), (8,5), (9,5), (10,5), (11,5), (12,5),
        (1,6), (2,6), (3,6), (4,6), (5,6), (6,6), (7,6), (8,6), (9,6), (10,6), (11,6), (12,6), (13,6),
        (1,7), (2,7), (3,7), (4,7), (5,7), (6,7), (7,7), (8,7), (9,7), (10,7), (11,7), (12,7), (13,7), (14,7),
        (1,8), (2,8), (3,8), (4,8), (5,8), (6,8), (7,8), (8,8), (9,8), (10,8), (11,8), (12,8), (13,8), (14,8),
        (1,9), (2,9), (3,9), (4,9), (5,9), (6,9), (7,9), (8,9), (9,9), (10,9), (11,9), (12,9), (13,9),
        (2,10), (3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10), (10,10), (11,10), (12,10),
        (2,11), (3,11), (4,11), (5,11), (6,11), (7,11), (8,11), (9,11), (10,11), (11,11), (12,11), (13,11),
        (3,12), (4,12), (5,12), (6,12), (7,12), (8,12), (9,12), (10,12), (11,12), (12,12), (13,12), (14,12),
        (4,13), (5,13), (6,13), (7,13), (8,13), (9,13), (10,13), (11,13), (12,13), (13,13), (14,13),
        (7,14), (8,14), (9,14), (10,14), (11,14), (12,14), (13,14))

eyes_pos_ahead = ((6,3), (7,3), (8,3), (5,4), (6,4), (7,4), (8,4), (9,4),
        (6,6), (7,6), (8,6), (5,5), (6,5), (7,5), (8,5), (9,5),
        (6,9), (7,9), (8,9), (5,10), (6,10), (7,10), (8,10), (9,10),
        (6,12), (7,12), (8,12), (5,11), (6,11), (7,11), (8,11), (9,11))

eyes_pos_up = ((3,3), (4,3), (5,3), (2,4), (3,4), (4,4), (5,4), (6,4),
        (3,6), (4,6), (5,6), (2,5), (3,5), (4,5), (5,5), (6,5),
        (3,9), (4,9), (5,9), (2,10), (3,10), (4,10), (5,10), (6,10),
        (3,12), (4,12), (5,12), (2,11), (3,11), (4,11), (5,11), (6,11))

eyes_pos_right = ((5,4), (6,4), (7,4), (4,5), (5,5), (6,5), (7,5), (8,5),
        (5,7), (6,7), (7,7), (4,6), (5,6), (6,6), (7,6), (8,6),
        (5,10), (6,10), (7,10), (4,11), (5,11), (6,11), (7,11), (8,11),
        (5,13), (6,13), (7,13), (4,12), (5,12), (6,12), (7,12), (8,12))
        
eyes_pos_left = ((5,2), (6,2), (7,2), (4,3), (5,3), (6,3), (7,3), (8,3),
        (5,5), (6,5), (7,5), (4,4), (5,4), (6,4), (7,4), (8,4),
        (5,8), (6,8), (7,8), (4,9), (5,9), (6,9), (7,9), (8,9),
        (5,11), (6,11), (7,11), (4,10), (5,10), (6,10), (7,10), (8,10))

pupils_pos_ahead = (7,4), (8,4), (7,5), (8,5), (7,10), (8,10), (7,11), (8,11)
pupils_pos_up = (2,4), (3,4), (2,5), (3,5), (2,10), (3,10), (2,11), (3,11)
pupils_pos_down = (8,4), (9,4), (8,5), (9,5), (8,10), (9,10), (8,11), (9,11)
pupils_pos_right = (6,6), (7,6), (6,7), (7,7), (6,12), (7,12), (6,13), (7,13)
pupils_pos_left = (6,2), (7,2), (6,3), (7,3), (6,8), (7,8), (6,9), (7,9)

def coord_to_pix(i, j):
    '''отримує координати матриці (row x col) row = i, col =  j
       вертає neopixel-значення LED-матриці
    '''
    return m * i + j if i % 2 else m-j-1 + m * i

# create pixels for NeoPixel matrix
body_pix = {coord_to_pix(i, j) for i, j in body_pos}
eyes_ahead_pix = {coord_to_pix(i, j) for i, j in eyes_pos_ahead}
eyes_up_pix = {coord_to_pix(i, j) for i, j in eyes_pos_up}
eyes_right_pix = {coord_to_pix(i, j) for i, j in eyes_pos_right}
eyes_left_pix = {coord_to_pix(i, j) for i, j in eyes_pos_left}
pupils_ahead_pix = {coord_to_pix(i, j) for i, j in pupils_pos_ahead}
pupils_up_pix = {coord_to_pix(i, j) for i, j in pupils_pos_up}
pupils_down_pix = {coord_to_pix(i, j) for i, j in pupils_pos_down}
pupils_right_pix = {coord_to_pix(i, j) for i, j in pupils_pos_right}
pupils_left_pix = {coord_to_pix(i, j) for i, j in pupils_pos_left}


class Ghost:

    def __init__(self, neopixel):
        self.np = neopixel  # instance of neopixel.NeoPixel class
        self.body_pix = body_pix
        self.eyes_ahead_pix = eyes_ahead_pix
        self.eyes_up_pix = eyes_up_pix
        self.eyes_right_pix = eyes_right_pix
        self.eyes_left_pix = eyes_left_pix
        self.pupils_ahead_pix = pupils_ahead_pix
        self.pupils_up_pix = pupils_up_pix
        self.pupils_down_pix = pupils_down_pix
        self.pupils_right_pix = pupils_right_pix
        self.pupils_left_pix = pupils_left_pix
        self.dir_eyes = {'up': self.eyes_up_pix, 'ahead': self.eyes_ahead_pix,
                        'down': self.eyes_ahead_pix, 'right': self.eyes_right_pix,
                        'left': self.eyes_left_pix}
        self.dir_pupils = {'up': self.pupils_up_pix, 'ahead': self.pupils_ahead_pix,
                          'down': self.pupils_down_pix, 'right': self.pupils_right_pix,
                          'left': self.pupils_left_pix}
                
    def look(self, direction, color, pupils_color):
        # paint the body
        for pix in self.body_pix:
            self.np[pix] = color
        # paint the eyes    
        for pix in self.dir_eyes[direction]:
            self.np[pix] = white
        # paint the pupils               
        for pix in self.dir_pupils[direction]:
            self.np[pix] = pupils_color
        self.np.write()
            

if __name__ == '__main__':
    
    np = neopixel.NeoPixel(machine.Pin(28), n * m)
    direction = ('ahead', 'up', 'down', 'right', 'left')
    ghost = Ghost(np)

    while True:
        ghost.look(random.choice(direction), blue, red)
        time.sleep_ms(200)
    
    # to clean the led-matrix:
    '''
    for pix in range(n * m):
        np[pix] = 0, 0, 0
    np.write()        
    '''
    