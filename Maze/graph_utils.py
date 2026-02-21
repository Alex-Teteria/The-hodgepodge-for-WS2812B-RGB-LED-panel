# graph_utils.py

class UnionFind:
    """
    Union-Find / DSU для довільних хешованих елементів.

    Основні операції:
      - add(x) / make_set(x): додати елемент як окрему множину
      - find(x): знайти представника множини (root) з компресією шляхів
      - union(a, b): об'єднати множини (union by size)
      - connected(a, b): чи в одній множині
      - to_sets(): отримати список множин (компоненти)
      - groups(): dict {root: set(elements)}

    Також підтримує:
      - uf[x] == uf.find(x)
      - len(uf) -> кількість елементів
      - uf.num_sets() -> кількість компонент
      - uf.component_size(x) -> розмір компоненти елемента
    """

    def __init__(self, elements=None):
        self.parent = {}     # element -> parent
        self._size = {}      # root -> size
        self._num_sets = 0

        if elements is not None:
            for x in elements:
                self.add(x)

    def add(self, x):
        """Додає елемент як окрему множину, якщо його ще не було."""
        if x not in self.parent:
            self.parent[x] = x
            self._size[x] = 1
            self._num_sets += 1

    make_set = add  # синонім

    def find(self, x):
        """Повертає root для x (з path compression). Якщо x не існує — додає."""
        if x not in self.parent:
            self.add(x)

        # знайти root
        root = x
        while self.parent[root] != root:
            root = self.parent[root]

        # path compression
        while self.parent[x] != x:
            p = self.parent[x]
            self.parent[x] = root
            x = p

        return root

    def union(self, a, b):
        """Об'єднує множини a і b (union by size). Повертає root."""
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return ra

        # меншу компоненту підвішуємо під більшу
        if self._size[ra] < self._size[rb]:
            ra, rb = rb, ra

        self.parent[rb] = ra
        self._size[ra] += self._size[rb]
        del self._size[rb]
        self._num_sets -= 1
        return ra

    def connected(self, a, b):
        """True, якщо a та b в одній множині."""
        return self.find(a) == self.find(b)

    same = connected  # синонім

    def component_size(self, x):
        """Розмір компоненти, де знаходиться x."""
        return self._size[self.find(x)]

    def num_sets(self):
        """Кількість компонент."""
        return self._num_sets

    def roots(self):
        """Множина root-ів."""
        r = set()
        for x in self.parent:
            r.add(self.find(x))
        return r

    def groups(self):
        """Повертає групи як {root: set(elements)}."""
        g = {}
        for x in self.parent:
            rx = self.find(x)
            if rx in g:
                g[rx].add(x)
            else:
                g[rx] = set([x])
        return g

    def to_sets(self):
        """Повертає список компонент як множини."""
        return list(self.groups().values())

    def representatives(self):
        """Словник {element: root}."""
        rep = {}
        for x in self.parent:
            rep[x] = self.find(x)
        return rep

    def __getitem__(self, x):
        return self.find(x)

    def __contains__(self, x):
        return x in self.parent

    def __iter__(self):
        return iter(self.parent)

    def __len__(self):
        return len(self.parent)

    def __repr__(self):
        return "UnionFind(n_elements={}, n_sets={})".format(len(self.parent), self._num_sets)

    def clear(self):
        self.parent.clear()
        self._size.clear()
        self._num_sets = 0

if __name__ == '__main__':
    # Приклад використання UnionFind

    # Нехай є особи 'a','b','c','d','h','f','i','j'
    nodes = {'a', 'b', 'c', 'd', 'h', 'f', 'i', 'j'}
    # Зв'язки між особами як список ребер графа:
    edges = [('a', 'b'), ('b', 'd'), ('h', 'h'), ('c', 'f'), ('c', 'i'), ('j', 'a')]
    
    relation = UnionFind(nodes) # створюємо екземпляр класу UnionFind
    
    for u, v in edges:
        if relation[u] != relation[v]:
            relation.union(u, v)
            
    for el in relation.to_sets():
        print(el)
    
    print(list(relation.to_sets()))
    # Чи існує зв'язок між персонами 'j' та 'b' ?
    print(relation['j'] == relation['b'])
    


