# ----------------------------------------------------------------
# Генератор лабіринта 
# для реалізації на RGB LED-панелi типу WS2816, 16х16 світлодіодів
# ----------------------------------------------------------------
# Maze generator 
# for implementation on RGB LED panel type WS2816, 16x16 LEDs
# ----------------------------------------------------------------
# Author: Alex Teteria
# v2.0
# 20.02.2026
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

"""
Виправлені баги:
  - жорстко прошиті числа 15 замінено на n-1 та m-1;
  - build_grid() — помилка для прямокутної матриці (було n == m)
  - змінено random_sample()
  - graph = Graph(components, edges) виправлено на graph = Graph(components, set(edges))

Деякі роз'яснення щодо способу побудови лабіринта
1. Будуються стіни як суцільні горизонтальні та вертикальні лінії (плюс рамка),
товщина стіни — 1 клітинка.
Це розбиває поле на “кімнати/комірки” (прямокутні області прохідних клітин),
які утворюють зв’язну ґратку по сусідству (кімната має сусідів через спільну стіну).
2. Далі, випадковим чином, утворюємо “дірки” у стінах → це об’єднує деякі кімнати в більші компоненти.
3. Будуємо граф з точoк, що не увійшли до стін лабіринту
   - Створюємо словник вершин:
     vertices = {vertex1: (i1, j1), vertex2: (i2, j2), ...}
   - будуємо граф:
     graph = Graph(vertices)
4. Знаходяться компоненти зв’язності (components) графа який утворився.
5. Будуємо граф між компонентами зв'язності, де
    вершини - компоненти
    ребра - коли відстань між компонентами = 2 (коли якісь вершини торкаються кутами),
            або = 4, коли вершини розміщені через клітинку 
   Ключове: для будь-яких двох “сусідніх кімнат” між ними є стіна товщиною 1,
   отже існують дві прохідні клітинки по різні боки стіни на відстані dist==4
   (або dist==2 для кутового випадку),
   і тому функції build_edges / find_neighbor таке ребро знайдуть.
   Тому граф компонент буде зв’язаним (один компонент зв'язності).
6. Будуємо остовне дерево
    path = graph.dfs_tree(0)
   За умов (п.5) dfs_tree(0) охопить усі компоненти.
7. Пробиваємо перегородки в стінах в місцях ребер остовного дерева
    break_wall(path, grid, edges, vertices)
8. Створюємо вхід та вихід з лабіринта

Доведення можливості побудови прохідного лабіринту:
   Повинна бути гарантія того, що dfs_tree(0) на графі компонент охоплював усі компоненти
   (граф компонент зв’язний).
   1) Умови, за яких гарантія виконується:
   - Стіни мають товщину 1 клітинку (перегородка — один ряд/стовпчик клітин).
   - Тому будь-які дві області (компоненти прохідних клітин), які
     розділені стіною, мають пару вершин по різні боки стіни, між якими:
     dist == 4 (через одну клітинку по горизонталі/вертикалі), або
     dist == 2 (діагональний дотик “кутами”, якщо це враховується).
   2) Функції build_edges/find_neighbor додають ребро між компонентами,
      якщо існує хоча б одна така пара вершин з dist ∈ {2,4}.
   3) “Пробиття отворів” (видалення стін) лише об’єднує компоненти
      і не може зробити граф незв’язним (це еквівалент “контракції” у зв’язному графі).

Висновок: граф компонент зв’язний ⇒ існує остовне дерево ⇒
          ⇒ dfs_tree(0) охоплює всі компоненти ⇒
          ⇒ після break_wall() лабіринт стає зв’язним.

Зауваження:
Якщо змінювати генератор (товщина стін, правила сусідства/пробиття),
ці умови треба перевірити заново.
"""

import random
from neopixel import NeoPixel as np
from graph import Graph
from itertools import combinations


n = 16        # number of row
m = 16        # number of col
neo_pin = 20  # pin to LED matrix

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
    num = random.randint(1, n-3)
    for i in range(0, n, 2):
        ind_i = i + 1 if i > num else i
        for j in range(m):
            grid.append((ind_i, j))
    # build vertical lines
    num = random.randint(1, m-3)
    for j in range(0, m, 2):
        ind_j = j + 1 if j > num else j
        for i in range(n):
            grid.append((i, ind_j))
    
    return set(grid)


def random_sample(max_index, k):
    """
    Повертає k унікальних випадкових чисел у діапазоні [0 .. max_index].
    """
    count = max_index + 1
    if k >= count:
        # повертаємо всі індекси (у довільному порядку)
        return list(range(count))

    picked = set()
    while len(picked) < k:
        picked.add(random.randint(0, max_index))
    return list(picked)


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
    grid_internal = [(i, j) for i, j in grid if (i != 0 and i != n-1 and j != 0 and j != m-1) \
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
     
def create_start_finish(grid, start_en=True, finish_en=True):
    '''Створює вхід та вихід з лабіринта
       вхід - ліворуч, вихід - праворуч
    '''
    start, finish = None, None
    if start_en:
        i = random.randint(1, n-2)
        while (i, 1) in grid:
            i = random.randint(1, n-2)
        start = i, 0
        grid.remove(start)
    
    if finish_en:
        i = random.randint(1, n-2)
        while (i, m-2) in grid:
            i = random.randint(1, n-2)
        finish = i, m-1
        grid.remove(finish)
        
    return start, finish


def build_border(n, m):
    '''вертає множину координат прямокутника (n x m)
       та координати випадкових точок на лівій і правій стороні
       Створено для перевірки роботи на порожньому лабіринті 
    '''
    border = {(i, j) for i in (0, n-1) for j in range(m)}
    border.update({(i, j) for i in range(1, n-1) for j in (0, m-1)})
    i_start = random.randint(1, n-2)
    i_finish = random.randint(1, n-2)
    j_finish = random.randint(1, m-2)
    border.remove((i_start, 0))
    return border, (i_start, 0), (i_finish, j_finish)

def build_maze(n=16, m=16, num_random_hole=30, start_en=True, finish_en=True):
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
    graph = Graph(components, set(edges))
        
    # будуємо остовне дерево
    path = graph.dfs_tree(0)
    
    # пробиваємо перегородки в стінах в місцях ребер остовного дерева
    break_wall(path, grid, edges, vertices)
    
    # Створюємо вхід та вихід з лабіринта
    start, finish = None, None
    if start_en or finish_en:
        start, finish = create_start_finish(grid, start_en, finish_en)
    
    return grid, start, finish
    
    

if __name__ == '__main__':
    
    pix = np(machine.Pin(neo_pin), n * m)
    
    maze, start, finish = build_maze(num_random_hole=8, start_en=True, finish_en=True)
    for ind in maze:
        pix[coord_to_pix(*ind)] = brown
    
    # -----------------------------------------------
    # перевіряємо на зв'язність утворений граф
    
    vertices = {coord_to_pix(i, j): (i, j) for i in range(n) for j in range(m) if (i, j) not in maze}
    graph = Graph(vertices)
    
    # знаходимо компоненти зв'язності графа
    components = graph.find_components()
    
    # повинна бути одна компонента зв'язності
    for num, comp in components.items():
        print(num, comp)
        print(len(comp))
    
    # -------------------------------------------------

    pix.write()
    # гасимо LED
    for i in range(len(pix)):
        pix[i] = nothing
    
    # pix.write()
    
    
