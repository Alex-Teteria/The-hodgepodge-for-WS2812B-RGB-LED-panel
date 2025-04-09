# ----------------------------------------------------------------
# Генератор лабіринта 
# для реалізації на RGB LED-панелi типу WS2816, 16х16 світлодіодів
# ----------------------------------------------------------------
# Maze generator 
# for implementation on RGB LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------
# Author: Alex Teteria
# v0.1
# 04.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import random
from neopixel import NeoPixel as np
from graph import Graph
from itertools import combinations

n = 16        # number of row
m = 16        # number of col
neo_pin = 28  # pin to LED matrix

brown = 20, 4, 0
green = 0, 24, 0
nothing = 0, 0, 0

def coord_to_pix(i, j):
        '''
        отримує координати матриці (row x col) row = i, col = j
        вертає neopixel-індекс LED-матриці
        '''
        return m * i + j if i % 2 else m-j-1 + m * i

def build_grid(n, m):
    grid = []
    # build horizontal lines
    num = random.randint(1, 13)
    for i in range(0, n, 2):
        ind_i = i + 1 if i > num else i
        for j in range(m):
            grid.append((ind_i, j))
    # build vertical lines
    num = random.randint(1, 13)
    for j in range(0, n, 2):
        ind_j = j + 1 if j > num else j
        for i in range(n):
            grid.append((i, ind_j))
    
    return set(grid)

def random_sample(max_num, num):
    l = []
    while len(l) < num:
        n = random.randint(0, max_num)
        while n in l:
            n = random.randint(0, max_num)
        l.append(n)
    return l

def build_wall(n, m, num_random_hole):
    '''вертає множину випадкових координат на площині розміром n x m
       метод отримання:
         - наноситься сітка через клітинку
         - в сітці робляться випадково отвори
         - кількість отворів задається параметром num_random_hole
         - додається контур площини
    '''
    grid = build_grid(n, m)
    border = set()
    grid_internal = [(i, j) for i, j in grid if (i != 0 and i != 15 and j != 0 and j != 15) \
                     or border.add((i, j))]
    random_index = random_sample(len(grid_internal), num_random_hole)
    grid_internal = {grid_internal[i] for i in range(len(grid_internal)) if i not in random_index}
    grid = border.union(grid_internal)
    return grid

def find_neighbor(comp_1, comp_2, vertices):
    
    '''comp_1, comp_2 - компоненти вершин (множина, список, tuple, iter)
       Вертає першу (при переборі) пару вершин, які є сусідніми
       Якщо таких немає, то вертає None
       сусідні вершини - коли відстань між ними == 2 або 4
       відстань з координатами визначаємо: (x1-x2)**2 + (y1-y2)**2, тобто без кореня
    '''
    for u in comp_1:
        x1, y1 = vertices[u]
        for v in comp_2:
            x2, y2 = vertices[v]
            dist = (x1-x2)**2 + (y1-y2)**2
            if dist == 2 or dist == 4:
                return u, v
        
def build_edges(components, vertices):
    '''вертає множину ребер між компонентами графа
    '''
    edges = {}
    for a, b in combinations(components, 2):
        edge = find_neighbor(components[a], components[b], vertices)
        if edge:
            edges[(a, b)] = edge
    return edges

    
def break_wall(path, grid, edges, vertices):
    '''пробиваємо перегородки в сітці в місцях ребер, які беремо з path
    '''
    holes_set = set()
    for a, b in path:
        node_1, node_2 = edges[(a, b)] if (a, b) in edges else edges[(b, a)]
        x1, y1 = vertices[node_1]
        x2, y2 = vertices[node_2]
        dist = (x1 - x2)**2 + (y1 - y2)**2
        if dist == 4:
            x = x1 - (x1-x2) // 2
            y = y1 - (y1-y2) // 2
        elif x2 > x1:
            x = x1 + 1
            y = y1
        else:
            x = x1 - 1
            y = y1
        if (x, y) in grid:
            grid.remove((x, y))
     
def create_start_finish(grid):
    '''Створює вхід та вихід з лабіринта
    '''
    i = random.randint(1, n-2)
    while (i, 1) in grid:
        i = random.randint(1, n-2)
    start = i, 0
    grid.remove(start)
    
    i = random.randint(1, n-2)
    while (i, m-2) in grid:
        i = random.randint(1, n-2)
    finish = i, m-1
    grid.remove(finish)
    
    return start, finish
    
def build_maze(n=16, m=16, num_random_hole=30):
    # створюємо заготовку лабіринта
    grid = build_wall(n, m, num_random_hole)
    
    # Будуємо граф з точoк, що не увійшли до стіни лабіринту
    # Створюємо словник вершин:
    # {vertex1: (x1, y1), vertex2: (x2, y2), ...}
    vertices = {coord_to_pix(i, j): (i, j) for i in range(n) for j in range(m) if (i, j) not in grid}
    graph = Graph(vertices)
    
    # знаходимо компоненти зв'язності графа
    components = graph.find_components()
    
    # Будуємо граф між компонентами зв'язності, де
    # вершини - компоненти
    # ребра - коли відстань між компонентами = 2 (коли якісь вершини торкаються кутами),
    #        або = 4, коли вершини розміщені через клітинку 
    edges = build_edges(components, vertices)
    graph = Graph(components, edges)
    
    # будуємо остовне дерево
    path = graph.dfs_tree(0)
    
    # пробиваємо перегородки в стінах в місцях ребер остовного дерева
    break_wall(path, grid, edges, vertices)
    
    # Створюємо вхід та вихід з лабіринта
    start, finish = create_start_finish(grid)
    
    return grid, start, finish
    
    

if __name__ == '__main__':
    
    pix = np(machine.Pin(neo_pin), n * m)
    
    maze, start, finish = build_maze()
    
    for ind in maze:
        pix[coord_to_pix(*ind)] = brown
    
    # -----------------------------------------------
    # перевіряємо на зв'язність утворений граф
    '''
    vertices = {coord_to_pix(i, j): (i, j) for i in range(n) for j in range(m) if (i, j) not in grid}
    graph = Graph(vertices)
    
    # знаходимо компоненти зв'язності графа
    components = graph.find_components()
    
    # повинна бути одна компонента зв'язності
    for num, comp in components.items():
        print(num, comp)
        print(len(comp))
    '''
    # -------------------------------------------------

    pix.write()
    # гасимо LED
    for i in range(len(pix)):
        pix[i] = nothing
    
    #pix.write()
    
    
    
        
        
    

