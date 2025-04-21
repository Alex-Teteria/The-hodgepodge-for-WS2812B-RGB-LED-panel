# ----------------------------------------------------------------
# Contains the Graph class as an undirected graph
# ----------------------------------------------------------------
# Author: Alex Teteria
# v0.4
# 17.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import itertools
from utils import UnionFind

class Graph():
    
    def __init__(self, vertices, edges=None):
        self.vertices = vertices
        self.edges = edges if edges is not None else self.build_edges()
        self.G = self.build_adjacency_lists()
            
    def if_adjacency(self, u, v):
        x1, y1 = self.vertices[u]
        x2, y2 = self.vertices[v]
        # вершини будуть суміжними, коли евклідова відстань між ними = 1
        dist = (x1 - x2)**2 + (y1 - y2)**2
        return dist == 1 

    def build_edges(self):
        edges = {(u, v) for u, v in itertools.combinations(self.vertices, 2) \
                 if self.if_adjacency(u, v)}
        return edges

    def build_adjacency_lists(self):
        '''Створює і вертає граф як списки суміжностей
           Списки суміжостей - словник виду
           {vertex_1: {neighbor_1, neighbor_2, ...}, vertex_2: {...}, ...}
        '''
        G = {v: set() for v in self.vertices}
        for u, v in self.edges:
            G[u].add(v)
            G[v].add(u)
        return G

    def dfs(self, start):
        '''Нерекурсивна реалізація алгоритму пошуку вглибину
           Обхід всіх вузлів 
           G - граф як словник списків суміжностей
           start - вершина з якої стартуємо
        '''
        # словник обходу - вершина: попередня вершина, з якої прийшли
        dfs_dict = {}
        prev = None  # попередня вершина
        # Створюємо стек
        stack = [start]
        while stack:                # поки стек не порожній
            v = stack.pop()
            if v not in dfs_dict:   # якщо вершина ще не розглянута
                dfs_dict[v] = prev  # заносимо вершину в словник та присвоюємо їй попереднє значення
                prev = v
                stack.extend(self.G[v])  # додаємо вершини суміжні з v в стек

        return dfs_dict

    def bfs(self, start):
        '''Реалізація алгоритму пошуку вширину
           start - вершина з якої стартуємо
        '''
        # словник обходу - вершина: попередня вершина
        bfs = {vertex: None for vertex in self.vertices}
        
        # Створюємо чергу
        queue = [start]
               
        while queue:                 # поки черга не порожня
            v = queue.pop(0)         # беремо наступну вершину з черги 
            for u in self.G[v]:      # ітерація по списку суміжностей для вершини v
                if bfs[u] is None:   # якщо вершина ще не розглянута
                    bfs[u] = v       # присвоюємо вершині значення попередньої вершини
                    queue.append(u)  # додаємо вершину в кінець черги
        #bfs[start] = None
        return bfs
    
    def bfs_distance(self, start):
        '''Пошук усіх найкоротших шляхів від вершини start за допомогою BFS
        '''
        # словник відстаней - вершина: відстань від start
        dist = {vertex: None for vertex in self.G}
        # словник попередніх вершин під час обходу вершин - вершина: попередня вершина
        prev = {start: None}
        dist[start] = 0  # відстань до вершини з якої стартуємо
        # Створюємо чергу
        queue = []
        queue.append(start)
        while queue:                       # поки черга не порожня
            v = queue.pop(0)               # беремо наступну вершину з черги 
            for u in self.G[v]:            # ітерація по списку суміжностей для вершини v
                if dist[u] is None:        # якщо вершина ще не розглянута
                    dist[u] = dist[v] + 1  
                    prev[u] = v
                    queue.append(u)    # додаємо вершину в кінець черги
        return dist, prev    

    def _find_components_dfs(self):
        # знаходимо компоненти зв'язності графа
        components = {}
        vertices_set = set(self.vertices)
        num = 0
        while vertices_set:
            v = vertices_set.pop()
            comp = set(self.dfs(v))
            components[num] = comp
            vertices_set -= comp
            num += 1
        return components
    '''
    def _find_components_dfs(self):
        # трошки змінена реалізація пошуку компонент зв'язності, трошки швидша
        # проте компоненти у словнику не як множина, а як об'єкти dict_keys([v1, v2, ...])
        components = {}
        visited = set()
        num = 0
        for v in self.vertices:
            if v not in visited:
                comp = self.dfs(v).keys()
                components[num] = comp
                visited.update(comp)
                num += 1
        return components    
    '''
    def _find_components_uf(self):
        # знаходимо компоненти зв'язності графа за допомогою структури даних UnionFind       
        relation = UnionFind(self.vertices)   # створюємо примірник класу UnionFind
        # об'єднуємо вершини в кластери, якщо між ними зв'язок (існує ребро) 
        for u, v in self.edges:
            if relation[u] != relation[v]:
                relation.union(u, v)
        return {num: el for num, el in enumerate(relation.to_sets())}
                
    def find_components(self, method='dfs'):
        if method == 'dfs':
            return self._find_components_dfs()
        elif method == 'UnionFind':
            return self._find_components_uf()
        else:
            print('Error! Unknown method')
    
    def dfs_tree(self, start):
        '''Вертає остовне дерево (spanning tree) графа як список ребер
           для побудови остовного дерева використано алгоритм DFS
        '''
        visited = set()
        path = []
        prev = start
        stack = [start]
        while stack:                     # поки стек не порожній
            v = stack.pop()
            if v not in visited:         # якщо вершина ще не розглянута
                visited.add(v)
                if v in self.G[prev]:    # якщо існує ребро
                    path.append((prev, v))
                else:                    # ребро не існує, тобто повернення назад в маршруті
                    for el in self.G[v]: # додаємо ребро із списка суміжностей з вершин, які вже дослідили
                        if el in visited:
                            path.append((el, v))
                            break
                prev = v
                stack.extend(self.G[v])  # додаємо усі вершини суміжні з v в стек
              
        return path
    
    def find_path(self, start, finish, prev=None):
        '''повертає найкоротший маршрут від вершини start до вершини finish
           prev - словник попередніх вершин, результат bfs_distance() {вершина: попередня вершина}
        '''
        if prev is None:
            _ , prev = self.bfs_distance(start)  # шукаємо шляхи від вершини start
        current = prev.get(finish)               # попередня вершина для finish
        route = finish                           # маршрут, починаємо з вершини finish
        path = []
        while current is not None:
            path.append((current, route))
            current, route = prev.get(current), current
        return path[::-1]


# -------------------------------------------------
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

def coord_to_pix(i, j):
    '''
    отримує координати матриці (row x col) row = i, col =  j
    вертає neopixel-коефіцієнт LED-матриці
    '''
    return m * i + j if i % 2 else m-j-1 + m * i


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



if __name__ == '__main__':
    import time
    
    n = 16
    m = 16
       
    # лабіринт беремо з файла
    file_name = 'maze_1.txt'
    vertices = read_file(file_name)
    start = coord_to_pix(5, 0)
    end = coord_to_pix(0, 10)
        
    graph = Graph(vertices)
    
    tic = time.ticks_us()
    path = graph.find_path(start, end)
    print(time.ticks_us() - tic)
    #print(path)
    
    # знаходимо шлях, інший спосіб
    tic = time.ticks_us()
    bfs = graph.bfs(start)
    path_2 = find_path_bfs(graph, bfs, start, end)
    print(time.ticks_us() - tic)

    
    


    
    
