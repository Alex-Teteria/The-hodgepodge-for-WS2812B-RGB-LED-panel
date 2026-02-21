# ----------------------------------------------------------------------------
# Implementation of finding a passage in a maze
# Result output on an LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------------------
# It is now common to say that this is the result of AI :),
# but it is simply an implementation of the depth-first search (DFS) algorithm
# ----------------------------------------------------------------------------
# Author: Alex Teteria
# v2.0
# 20.02.2026
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import machine
import time, random
from neopixel import NeoPixel as np
from graph import Graph
import maze_generator


n = 16       # number of row
m = 16       # number of col
neo_pin = 20 # pin number to the LEDs
speed = 90  # LED switching delay
show_path = True

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

# creating an instance of a class NeoPixel
pix = np(machine.Pin(neo_pin), n * m)

def coord_to_pix(i, j):
        '''
        отримує координати матриці (row x col) row = i, col =  j
        вертає neopixel-коефіцієнт LED-матриці
        '''
        return m * i + j if i % 2 else m-j-1 + m * i

def read_file(name):
    '''Зчитує файл з координатами вершин x, y
       вертає словник вершин:
       {vertex1: (x1, y1), vertex2: (x2, y2), ...}
    '''
    with open(name) as file:
        vertices = {}
        for line in file:
            x, y = line.rstrip().split()
            vertices[coord_to_pix(int(x), int(y))] = int(x), int(y)
    return vertices


def light_path(path):
    visited = set()
    for a, b in path:
        if (a, b) not in visited:
            visited.add((b, a))
            pix[a] = green
        else:
            pix[a] = low_green
        pix.write()
        time.sleep_ms(speed)    

def write_path_neo(path, show_path=True):
    if show_path:
        light_path(path)
    else:
        for a, b in path:
            pix[b] = green
            pix[a] = nothing
            pix.write()
            time.sleep_ms(speed)
    pix[path[-1][1]] = red
    pix.write()
    time.sleep_ms(400)


def main_run():

    start_vertex = coord_to_pix(*coord_start)
    end_vertex = coord_to_pix(*coord_end)
    
    # виводимо лабіринт
    for coord in maze:
        pix[coord_to_pix(*coord)] = brown
    pix.write()
    
    # виводимо точки старта та фініша
    pix[start_vertex] = green
    pix[end_vertex] = blue
    pix.write()
    
    # створюємо примірник графа
    graph = Graph(vertices)
    
    # знаходимо шлях
    path = graph.dfs_walk_edges(start_vertex, end_vertex)
    assert path, "Path is empty: check start/finish and maze connectivity"
        
    # виводимо шлях
    write_path_neo(path, show_path=show_path)
    
def clear():
    for i in range(len(pix)):
        pix[i] = 0, 0, 0
    pix.write()


if __name__ == '__main__':
        
    # якщо лабіринт беремо з файла
    '''
    file_name = 'maze_1.txt'
    vertices = read_file(file_name)
    coord_start = (5, 0)
    coord_end = (0, 10)
    maze = {(i, j) for i in range(n) for j in range(m) if coord_to_pix(i, j) not in vertices}
    '''
    while True:

        # створюємо лабіринт
        maze, coord_start, coord_end = maze_generator.build_maze(num_random_hole=8)
        # якщо без лабіринта (типу шукає в темній кімнаті кішку) 
        # maze, coord_start, coord_end = maze_generator.build_border(n, m)
         
        # вершини - решта точок, які не в лабіринті
        vertices = {coord_to_pix(i, j): (i, j) for i in range(n) for j in range(m) if (i, j) not in maze}
        clear()
        main_run()
    