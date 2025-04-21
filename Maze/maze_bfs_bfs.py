# ----------------------------------------------------------------------------
# Implementation of finding a passage in a maze
# Result output on an LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------------------
# Route search simulation
# One point catches up with another
# The first point chooses the shortest route to the second point it is trying to cover
# The second point chooses the route to the farthest point in the maze
# so as not to intersect with the first point
# This repeats in a loop until the first point covers the second
# ----------------------------------------------------------------------------
# Author: Alex Teteria
# v0.4
# 19.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import time, random
from neopixel import NeoPixel as np
from graph import Graph
import maze_generator
from maze_bfs import find_path_bfs


n = 16         # number of row
m = 16         # number of col
neo_pin = 28   # pin number to the LEDs
speed = 40     # LED switching delay
num_cycle = 8  # number of cyclic repeat of route
# timer time (mc), after which the range of random paths selection changes
# to avoid cyclicality:
timer_period = 60000
num_random_path = 5  # initial number of first random paths
next_num_random_path = 15 # next number of first random paths (after timer_period)

# color definition
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

color_1 = red    # the point that runs away
color_2 = green  # the point that catches up

# creating an instance of a class NeoPixel
pix = np(machine.Pin(neo_pin), n * m)
# operating mode switching button
# btn = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)


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


def write_neo(path_1, path_2):
    for edge_1, edge_2 in zip(path_1, path_2):
        a, b = edge_1
        c, d = edge_2
        pix[b] = color_1
        pix[a] = nothing
        pix[d] = color_2
        pix[c] = nothing
        pix.write()
        if b == d:
            return b, b
        time.sleep_ms(speed)
    return b, d

def write_one_neo(path, color):
    for a, b in path:
        pix[b] = color
        if pix[a] == color:
            pix[a] = nothing
        pix.write()
        time.sleep_ms(speed)
    return b

def find_path(graph, start, path_2):
    global limit_ind
    dist, prev = graph.bfs_distance(start)
    farthest = sorted(list(dist.items()), key=lambda x: x[1], reverse=True)
    
    # для прискорення
    # -----------------------------
    limit = len(farthest) // 10
    if len(path_2) < 3:
       farthest = farthest[-limit:]
    # -----------------------------
    rand_ind = random.randint(0, limit_ind)
    for el in farthest[rand_ind:]:
        path = graph.find_path(start, el[0], prev)
        
        for edge_1, edge_2 in zip(path, path_2):
            a, b = edge_1
            c, d = edge_2
            if b == d or (a, b) == (d, c):
                break
        else:
            return path 
   


def write_path(graph, start_1, start_2):
    cnt_cycle = 0
    while start_1 != start_2 and not flag_exit:
        cnt_cycle += 1
        if cnt_cycle > num_cycle:
            path_2_prev = path_2[:]
            path_2 = []
            cnt_cycle = 0
        else:
            path_2 = graph.find_path(start_2, start_1)
        path_1 = find_path(graph, start_1, path_2)

        if path_1 and path_2:
            start_1, start_2 = write_neo(path_1, path_2)
        elif path_2:
            path_2 = graph.find_path(start_2, start_1)
            start_2 = write_one_neo(path_2, color_2)
        else:  # if path_2 == []
            path_1 = find_path(graph, start_1, path_2_prev)
            if not path_1: # if path_2 == [] and path_1 == []
                pix[start_1] = nothing
                pix.write()
                start_1 = start_2
            else:
                start_1 = write_one_neo(path_1, color_1)
                    
def find_vertex(vertices, coord):
    '''Вертає вершину за її координатами,
       якщо такої немає, то вертає None
    '''
    for key, val in vertices.items():
        if val == coord:
            return key
        

def main_run():
       
    start_1 = find_vertex(vertices, coord_start)
    
   # виводимо лабіринт
    for coord in maze:
        pix[coord_to_pix(*coord)] = brown
    pix.write()
    
    # виводимо точки старта
    pix[start_1] = color_1
    start_2 = random.choice(list(vertices.keys()))
    pix[start_2] = color_2
    pix.write()
    
    # створюємо примірник графа
    graph = Graph(vertices)

    write_path(graph, start_1, start_2)


def clear():
    for i in range(len(pix)):
        pix[i] = 0, 0, 0
    pix.write()


def f_timer_1(t):
    global limit_ind
    limit_ind = next_num_random_path
    print('!')
    
def f_timer_2(t):
    global flag_exit
    flag_exit = True
    print('!!')    

if __name__ == '__main__':
        
    # якщо лабіринт беремо з файла
    '''
    file_name = 'maze_1.txt'
    vertices = read_file(file_name)
    coord_start = (5, 0)
    coord_end = (0, 10)
    maze = {(i, j) for i in range(n) for j in range(m) if coord_to_pix(i, j) not in vertices}
    '''
    max_time = 0
    tim_1 = machine.Timer()
    tim_2 = machine.Timer()
    while True:
        
        # створюємо лабіринт
        maze, coord_start, coord_end = maze_generator.build_maze(num_random_hole=8, finish_en=False)
        # якщо без лабіринта (типу шукає в темній кімнаті кішку) 
        # maze, coord_start, coord_end = maze_generator.build_border(n, m)
         
        # вершини - решта точок, які не в лабіринті
        vertices = {coord_to_pix(i, j): (i, j) for i in range(n) for j in range(m) if (i, j) not in maze}
        clear()
        flag_exit = False
        
        limit_ind = num_random_path
        tim_1.init(period=timer_period, mode=machine.Timer.ONE_SHOT, callback=f_timer_1)
        tim_2.init(period=240_000, mode=machine.Timer.ONE_SHOT, callback=f_timer_2)
        
        main_run()
            
    
