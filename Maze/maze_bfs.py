# ----------------------------------------------------------------------------
# Implementation of finding a passage in a maze
# Result output on an LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------------------
# 
# Implementation of the Breadth First Search (BFS) algorithm
# ----------------------------------------------------------------------------
# Author: Alex Teteria
# v0.4
# 16.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import time, random
import machine
from neopixel import NeoPixel as np
from graph import Graph
import maze_generator


n = 16       # number of row
m = 16       # number of col
neo_pin = 28 # pin number to the LEDs
speed = 100  # LED switching delay

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

def find_vertex(vertices, coord):
    '''Вертає вершину за її координатами,
       якщо такої немає, то вертає None
    '''
    for key, val in vertices.items():
        if val == coord:
            return key
        
def find_path_bfs(graph, tour, start, end):
    '''Вертає повний шлях до вершини end як список ребер
       graph - граф
       tour - результат обходу графа алгоритмом BFS, словник виду - {вершина: попередня вершина, ...}
    '''
    G = graph.G          # словник - списки суміжностей
    edges = graph.edges  # ребра
    path = []
    v = end
    while tour.get(v) != start: # поки не дійшли до стартової вершини
        if tour[v] in G[v]:
            path.append((tour[v], v))
            v = tour[v]
        else:
            print('Error!')
            v = tour[v]
    path.append((start, v))        
    return path[::-1]


def main_run():
    '''   
    start_vertex = find_vertex(vertices, coord_start)
    end_vertex = find_vertex(vertices, coord_end)
    '''
   # виводимо лабіринт
    for coord in maze:
        pix[coord_to_pix(*coord)] = brown
    pix.write()
    
    # виводимо точки старта та фініша з випадковими координатами
    start_vertex = random.choice(list(vertices.keys()))
    temp_list = list(vertices.keys())[:]
    temp_list.remove(start_vertex)
    end_vertex = random.choice(temp_list)
    pix[start_vertex] = green
    pix[end_vertex] = blue
    pix.write()
    
    # створюємо примірник графа
    graph = Graph(vertices)

    # знаходимо шлях
    bfs = graph.bfs(start_vertex)
    path = find_path_bfs(graph, bfs, start_vertex, end_vertex)
    
    # виводимо шлях
    write_path_neo(path, show_path=False)
    
    
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
        maze, *_ = maze_generator.build_maze(num_random_hole=8, start_en=False, finish_en=False)
        # якщо без лабіринта (типу шукає в темній кімнаті кішку) 
        # maze, coord_start, coord_end = maze_generator.build_border(n, m)
        
        # вершини - решта точок, які не в лабіринті
        vertices = {coord_to_pix(i, j): (i, j) for i in range(n) for j in range(m) if (i, j) not in maze}
        clear()
        main_run()
    
