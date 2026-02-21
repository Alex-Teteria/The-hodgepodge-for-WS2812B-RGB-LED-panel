# ----------------------------------------------------------------
# Contains the Graph class as an undirected graph
# ----------------------------------------------------------------
# Author: Alex Teteria
# v2.0
# 19.02.2026
"""
1. Оптимізовано побудову ребер build_edges()
  - Було: перебір усіх пар вершин через itertools.combinations → O(V²).
  - Стало: індекс (x, y) -> id і перевірка лише 2 сусідів (вправо/вниз) → O(V).
  - Причина: суміжність = відстань 1 на ґратці (4-сусідство),
    тому немає сенсу перевіряти всі пари.

2. Зроблено одночасну побудову edges і списків суміжності G
  - Додано build_edges_and_adjacency(), щоб не будувати спочатку ребра, а потім ще раз проходити по них для G.
  - Це швидше і логічно узгоджує edges та G.

3. Виправлено dfs() на “класичний” DFS (parent-map)
  - Тепер dfs(start) повертає {vertex: parent} де parent — реальний “батько” в дереві DFS.
  - Це робить результат DFS коректним як структура для дерева/відновлення шляху в DFS-дереві.

4. Додано окремий метод для анімації “шляху з поверненням назад”
  - dfs_walk_edges() повертає послідовність реальних кроків по ребрах (включно з поверненнями назад).
  - Це розділило дві різні задачі:
     “DFS як алгоритм” (dfs)
     “DFS як маршрут руху” для візуалізації (dfs_walk_edges)

5. Виправлено bfs() логічно (старт)
  - Старт одразу позначається як “відвіданий”, щоб він не потрапляв у чергу повторно через сусідів.
  - Повернення формату з None для старту збережено.

6. Покращено реалізацію черги в bfs()
  - Замість list.pop(0) (зсув елементів) використано список + індекс head.
  - Це повернуло BFS до правильної асимптотики для списків суміжності: Θ(V + E).

7. Виправлено dfs_tree()
  - Раніше воно намагалось вгадувати ребра через prev.
  - Тепер будує остовне дерево правильно: просто бере ребра (parent[v], v) з результату класичного dfs().

8. Компоненти зв’язності лишилися коректними
  - _find_components_dfs() як працював по множині ключів DFS, так і працює.
  - _find_components_uf() залишився без змін і використовує edges/UnionFind.

9. Покращено реалізацію черги в bfs_distance()
  - Замість list.pop(0) (зсув елементів) використано список + індекс head.
"""
# Implemented and tested on Pi Pico with RP2040
# Released under the MIT license

import itertools
from utils.graph_utils import UnionFind

class Graph():
    
    def __init__(self, vertices, edges=None):
        self.vertices = vertices
        if edges is None:
            self.edges, self.G = self.build_edges_and_adjacency()
        else:
            self.edges = edges
            self.G = self.build_adjacency_lists()

    def build_edges(self):
        '''Оптимізований build_edges() за O(V)
        '''
        # (x, y) -> vertex_id
        coord2v = {}
        for v, (x, y) in self.vertices.items():
            coord2v[(x, y)] = v

        edges = set()

        for v, (x, y) in self.vertices.items():
            # перевіряємо тільки вправо і вниз, щоб кожне ребро додати один раз
            v2 = coord2v.get((x + 1, y))
            if v2 is not None:
                edges.add((v, v2) if v < v2 else (v2, v))

            v2 = coord2v.get((x, y + 1))
            if v2 is not None:
                edges.add((v, v2) if v < v2 else (v2, v))
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
    
    def build_edges_and_adjacency(self):
        # (x, y) -> vertex_id
        coord2v = {}
        for v, (x, y) in self.vertices.items():
            coord2v[(x, y)] = v

        G = {v: set() for v in self.vertices}
        edges = set()

        for v, (x, y) in self.vertices.items():
            # вправо
            v2 = coord2v.get((x + 1, y))
            if v2 is not None:
                a, b = (v, v2) if v < v2 else (v2, v)
                edges.add((a, b))
                G[v].add(v2)
                G[v2].add(v)

            # вниз
            v2 = coord2v.get((x, y + 1))
            if v2 is not None:
                a, b = (v, v2) if v < v2 else (v2, v)
                edges.add((a, b))
                G[v].add(v2)
                G[v2].add(v)

        return edges, G
        
    def dfs(self, start):
        parent = {start: None}
        stack = [start]
        while stack:
            v = stack.pop()
            for u in self.G[v]:
                if u not in parent:
                    parent[u] = v
                    stack.append(u)
        return parent

    def dfs_walk_edges(self, start, finish=None):
        """
        Повертає маршрут обходу DFS як список ребер (кожне ребро — реальний крок по графу),
        включно з поверненнями назад. Якщо задано finish — зупиняється, коли його досягнуто.
        """
        visited = set([start])
        stack = [(start, iter(self.G[start]))]  # (вершина, ітератор по сусідах)
        walk = [start]                          # послідовність відвіданих кроків (вершин)

        if finish is not None and start == finish:
            return []

        while stack:
            v, it = stack[-1]
            try:
                u = next(it)
                if u not in visited:
                    visited.add(u)
                    walk.append(u)              # рух вперед v -> u
                    if finish is not None and u == finish:
                        break
                    stack.append((u, iter(self.G[u])))
            except StopIteration:
                stack.pop()
                if stack:
                    # повернення назад до батька
                    walk.append(stack[-1][0])

        # перетворюємо walk вершин у список ребер
        edges = []
        for i in range(len(walk) - 1):
            edges.append((walk[i], walk[i + 1]))
        return edges
 
    def bfs(self, start):
        '''Реалізація алгоритму пошуку вширину
           start - вершина з якої стартуємо
           асимптотика BFS як і повинно бути на списках суміжності: Θ(V + E)
           (список + pop(0)) замінили на (список + head)
        '''
        parent = {v: None for v in self.vertices}
        parent[start] = start  # маркер "відвідано"

        queue = [start]
        head = 0
        while head < len(queue):
            v = queue[head]
            head += 1
            for u in self.G[v]:
                if parent[u] is None:
                    parent[u] = v
                    queue.append(u)

        parent[start] = None
        return parent

    def bfs_distance(self, start):
        '''Пошук усіх найкоротших шляхів від вершини start за допомогою BFS
        '''
        # словник відстаней - вершина: відстань від start
        dist = {vertex: None for vertex in self.G}
        # словник попередніх вершин під час обходу вершин - вершина: попередня вершина
        prev = {start: None}
        dist[start] = 0

        queue = [start]  # створюємо чергу
        head = 0
        while head < len(queue):
            v = queue[head]
            head += 1
            for u in self.G[v]:
                if dist[u] is None:
                    dist[u] = dist[v] + 1
                    prev[u] = v
                    queue.append(u)
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
        """
        Повертає остовне дерево (spanning tree) компоненти, досяжної зі start,
        як список ребер (parent, vertex).
        Працює з dfs(), який повертає parent-map: {v: parent_v}.
        """
        parent = self.dfs(start)
        tree = []
        for v, p in parent.items():
            if p is not None:
                tree.append((p, v))
        return tree

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
    