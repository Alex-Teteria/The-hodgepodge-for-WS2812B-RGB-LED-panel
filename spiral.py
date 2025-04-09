# ----------------------------------------------------------------------------
# Spiral effect on LED matrix
# Implementing pathfinding on an LED matrix from edges to center in a circle
# Result output on an LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------------------
# Author: Alex Teteria
# v0.2
# 08.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import time, random
import collections
from neopixel import NeoPixel as np


n = 16         # number of row
m = 16         # number of col
neo_pin = 28   # output to LED panel 
speed = 20

green = 0, 24, 0
low_green = 0, 1, 0
green_ellow = 6, 10, 0
red = 24, 0, 0
orange = 12, 4, 0
blue = 0, 0, 16
blue_light = 0, 8, 8
magenta = 8, 0, 8
yellow = 12, 8, 0
teal = 0, 5, 3
white = 12, 20, 8
nothing = 0, 0, 0
brown = 18, 4, 0

colors = (green, red, yellow, magenta, blue, nothing)
pix = np(machine.Pin(neo_pin), n * m)

# used at will
# button_start = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

def coord_to_pix(i, j):
        '''
        отримує координати матриці (row x col) row = i, col =  j
        вертає neopixel-коефіцієнт LED-матриці
        '''
        return m * i + j if i % 2 else m-j-1 + m * i

def clear():
    for i in range(len(pix)):
        pix[i] = 0, 0, 0
    pix.write()
    
class Deque():
        
    def __init__(self, iterable):
        self.iterable = iterable
        self.deque = self.build_deque()
                
    def build_deque(self):
        d = collections.deque((), len(self.iterable))
        for el in self.iterable:
            d.append(el)
        return d
    
    def rotate(self):
        left_el = self.deque.popleft()
        self.deque.append(left_el)
        return left_el

def find_path(n, m, rotation='right'):
    
    maxlen = n * m
    if rotation == 'right':
        cycle = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # вправо, вниз, вліво, вгору
        visited = {(0, m), (n, m-1), (n-1, -1)}
    else:
        cycle = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # вниз, вправо, вгору, вліво
        visited = {(n, 0), (n-1, m), (-1, m-1)}
        
    '''
    # циклічний зсув вліво
    deque = Deque(cycle)
    direction = deque.rotate()
    '''
    # використання класу collections.deque має перевагу лише для масивів > 400
    # тому циклічний зсув вліво робимо засобами класу list:
    direction = cycle.pop(0)
    cycle.append(direction)
    
    start = (0, 0)
    vertices = {}
    path = []
    while len(path) != maxlen:
        while start not in visited:
            visited.add(start)
            path.append(start)
            start = (start[0] + direction[0], start[1] + direction[1])
            
        # direction = deque.rotate()
        direction = cycle.pop(0)
        cycle.append(direction)
        
        start = (path[-1][0] + direction[0], path[-1][1] + direction[1])
    path = [coord_to_pix(i, j) for i, j in path]
    
    return path

def main_run(path_l, path_r, colors, color_2):
    l = list(colors)
    l.remove(color_2)
    color_1 = random.choice(l)
    l.remove(color_1)
    color_2 = random.choice(l)
               
    for vertex in path_r:
        pix[vertex] = color_1
        pix.write()
        time.sleep_ms(speed)
    for vertex in path_l[::-1]:
        pix[vertex] = color_2
        pix.write()
        time.sleep_ms(speed)
    return color_2

if __name__ == '__main__':
    
    path_l = find_path(n, m, 'left')  # шлях обходу вліво
    path_r = find_path(n, m)          # шлях обходу вправо
    color = random.choice(colors)   
    while True:
        color = main_run(path_l, path_r, colors, color)

    
