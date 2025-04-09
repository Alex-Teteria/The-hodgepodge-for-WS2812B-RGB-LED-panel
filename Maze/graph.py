# ----------------------------------------------------------------
# Contains the Graph class as an undirected graph
# ----------------------------------------------------------------
# Author: Alex Teteria
# v0.1
# 04.04.2025
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import itertools

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

    def find_components(self):
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
           