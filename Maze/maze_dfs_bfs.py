# ----------------------------------------------------------------------------
# Implementation of finding a passage in a maze
# Result output on an LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------------------
# It is now common to say that this is the result of AI :),
# but it is simply an implementation of the depth-first search (DFS) algorithm
# ----------------------------------------------------------------------------
# Author: Alex Teteria
# v0.4
# 16.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import time, random
from neopixel import NeoPixel as np
from graph import Graph
import maze_generator
from maze_bfs import find_path_bfs


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


def find_path(graph, tour, *nodes):
    '''Вертає повний шлях до вершини vertex як список ребер, з урахуванням усіх повернень назад
       graph - граф
       tour - результат обходу графа алгоритмом DFS, словник виду - {вершина: попередня вершина, ...}
    '''
    *_, v = nodes # берем останню вершину із кортежу nodes
    G = graph.G          # словник - списки суміжностей
    edges = graph.edges  # ребра
    path = []
    all_path_back = []
    while tour.get(v) is not None:
        if tour[v] in G[v]:
            path.append((tour[v], v))
            v = tour[v]
        else:  # маршрути назад
            path.append(())  # в місця, де розрив маршруту, тобто шлях назад, вставляємо як маркери порожні ребра
            path_back = find_path_back(G, tour, (v, tour[v]))  # знаходимо маршрут назад між вершинами v та tour[v]
            all_path_back.append(path_back)  # додаємо цей маршрут у список усіх зворотніх маршрутів
            v = tour[v]
    path = insert_path_back(path[::-1], all_path_back, edges)
    
    return path

def insert_path_back(path, path_back, edges):
    edge_visited = set()    
    while path_back:
        index_insert = path.index(())
        path_insert = path_back.pop()
        
        # якщо вже там були, то викидуємо з маршруту
        path_insert = [edge for edge in path_insert if \
                       edge not in edge_visited and \
                       not edge_visited.add(edge)]
        
        # викидуємо з маршруту неіснуючі ребра та замикаємо в тому місці маршрут
        for i in range(len(path_insert)):
            u, v = path_insert[i]
            if (u, v) not in edges and (v, u) not in edges:
                path_insert[i] = (u, path_insert[i+1][0])
                
        path = path[:index_insert] + path_insert + path[index_insert+1:]
    return path


def find_path_back(G, tour, t):
    prev, vertex = t
    path = []
    v = vertex
    while v not in G[prev]:
        path.append((v, tour[v]))
        v = tour[v]
    path.append((v, prev))    
    return path 


def write_path_neo(path_1, path_2, finish):

    for edge_1, edge_2 in zip(path_1, path_2):
        a, b = edge_1
        c, d = edge_2
        pix[b] = red
        pix[a] = nothing
        pix[d] = green
        pix[c] = nothing
        pix.write()
        time.sleep_ms(speed)
    pix[d] = magenta if d == finish else red
    pix.write()
    #time.sleep_ms(400)

def find_vertex(vertices, coord):
    '''Вертає вершину за її координатами,
       якщо такої немає, то вертає None
    '''
    for key, val in vertices.items():
        if val == coord:
            return key
        

def main_run():
       
    start_vertex = find_vertex(vertices, coord_start)
    end_vertex = find_vertex(vertices, coord_end)
    
   # виводимо лабіринт
    for coord in maze:
        pix[coord_to_pix(*coord)] = brown
    pix.write()
    
    # виводимо точки старта та фініша
    pix[start_vertex] = green
    pix[end_vertex] = blue
    start_vertex_bfs = random.choice(list(vertices.keys()))
    pix[start_vertex_bfs] = red
    pix.write()
    
    # створюємо примірники графа
    graph = Graph(vertices)
        
    # знаходимо шляхи
    
    dfs = graph.dfs(start_vertex)
    bfs = graph.bfs(start_vertex_bfs)
    path_dfs = find_path(graph, dfs, end_vertex)
    #print(path_dfs[:6], path_dfs[-1])
    path_bfs_new = build_path_bfs(graph, start_vertex_bfs, path_dfs)
    #print(path_bfs_new[-6:-1])
    # path_bfs = find_path_bfs(graph, bfs, start_vertex_bfs, start_vertex)
    
    # виводимо шлях
    write_path_neo(path_bfs_new, path_dfs, end_vertex)

def build_path_bfs(graph, start, path_dfs):
    path_all = []
    for a, b in path_dfs:
        bfs = graph.bfs(start)
        path = find_path_bfs(graph, bfs, start, a)
        path_all.append(path[0])
        if len(path) == 1:
            return path_all
        if not len(path) % 2:
            start = path[0][0]
        else:
            start = path[0][1]
    return path_all      
        

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
    
