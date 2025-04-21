# ----------------------------------------------------------------------------
# Implementation of finding a passage in a maze
# Result output on an LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------------------
# It is now common to say that this is the result of AI :),
# but it is simply an implementation of the Depth First Search (DFS) or
# Breadth First Search (BFS) algorithm
# Switching search modes is done by the button
# ----------------------------------------------------------------------------
# Author: Alex Teteria
# v0.3
# 14.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import time, random
from neopixel import NeoPixel as np
from graph import Graph
import maze_generator
import _thread
import spiral


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
btn = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)


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


class Modes:
    '''Атрибути:
       mode - режими роботи:
            0 - обхід графа в довжину, шлях показується
            1 - обхід графа в довжину, шлях не показується
            2 - обхід графа в ширину, шлях показується
            3 - обхід графа в ширину, шлях не показується
       graph - екземпляр класа Graph
       start_vertex - початкова вершина шляху
       end_vertex - кінцева вершина шляху
    '''
    def __init__(self, mode, graph, start_vertex, end_vertex):
        self.mode = mode
        self.graph = graph
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        
    def path(self):
        mode_path = {0: find_path, 1: find_path, 2: find_path_bfs, 3: find_path_bfs}
        mode_search = {0: self.graph.dfs, 1: self.graph.dfs, 2: self.graph.bfs, 3: self.graph.bfs}
        search = mode_search[self.mode](self.start_vertex)
        return mode_path[self.mode](self.graph, search, self.start_vertex, self.end_vertex)
    
    def show_path(self):
        show = {0: True, 1: False, 2: True, 3: False}
        return show[self.mode]


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
    pix.write()
    
    # створюємо примірник графа
    graph = Graph(vertices)
    # визначаємо режим роботи
    mode = Modes(cnt_task, graph, start_vertex, end_vertex)
    # виводимо шлях
    if cnt_task <= 3:
        write_path_neo(mode.path(), show_path=mode.show_path())
    
    
def clear():
    for i in range(len(pix)):
        pix[i] = 0, 0, 0
    pix.write()

#-----------------------------------------------------------
# second_thread
led = machine.Pin(25, machine.Pin.OUT)

def second_thread_run(num):
    global cnt_task
    while True:
        wait_button()
        task_cnt(num)
        led.value(not led.value())
                
def task_cnt(num):
    global cnt_task
    cnt_task = (cnt_task + 1) % num  # результат додавання 1 по модулю num
    
def wait_button():
    btn_prev = btn.value()
    while btn.value() == 1 or btn.value() == btn_prev:
        btn_prev = btn.value()
        time.sleep(0.04)
# ------------------------------------------------------------

def run_spiral(color):
    color = spiral.main_run(path_spiral_l, path_spiral_r, spiral.colors, color)
    return color

if __name__ == '__main__':
        
    cnt_task = 4  # лічильник завдань
    num_task = 5  # кількість завдань
    
    # якщо лабіринт беремо з файла
    '''
    file_name = 'maze_1.txt'
    vertices = read_file(file_name)
    coord_start = (5, 0)
    coord_end = (0, 10)
    maze = {(i, j) for i in range(n) for j in range(m) if coord_to_pix(i, j) not in vertices}
    '''
    # запускаємо другий потік
    _thread.start_new_thread(second_thread_run, (num_task,))
    
    path_spiral_l = spiral.find_path(n, m, 'left')  # шлях обходу вліво
    path_spiral_r = spiral.find_path(n, m)          # шлях обходу вправо
    color_spiral = random.choice(spiral.colors)   
    
    while True:
        
        if cnt_task == 4:
            color_spiral = run_spiral(color_spiral)
        else:
            # створюємо лабіринт
            maze, coord_start, coord_end = maze_generator.build_maze(num_random_hole=8)
            # якщо без лабіринта (типу шукає в темній кімнаті кішку) 
            # maze, coord_start, coord_end = maze_generator.build_border(n, m)
            
            # вершини - решта точок, які не в лабіринті
            vertices = {coord_to_pix(i, j): (i, j) for i in range(n) for j in range(m) if (i, j) not in maze}
            clear()
            main_run()
    
