# The hodgepodge for WS2812B RGB LED panel
Some miscellaneous visualizations displaying on a WS2812B RGB LED panel using MicroPython.

## Content  

| File | Contain | Purpose |
| --- |  ---: |  --- |
| Maze |  |The folder containing the main program code and auxiliary modules for visualizing path finding in a maze. It is now common to say that this is the result of AI :smile:, but it is simply an implementation of the depth-first search (DFS) algorithm. It looks something like this: [AI finds its way through a maze](https://youtube.com/shorts/KfYbfn5_Zk4) |
|  | maze_generator.py | Module for creating mazes |
|  |graph.py | Contains the Graph class as an undirected graph |
|  | itertools.py | Contains functions creating iterators |
|  | maze.py | Main code that implementation of finding a passage in a maze |
|  | maze_1.txt | Contains the coordinates of the test maze  |
||  |  |
| spiral.py |  | Spiral effect on LED matrix  |
||  |  |
| Ghost |  | The folder containing the main program code and auxiliary modules for visualizing moving ghost body pixels. The ghost's color changes depending on the ambient temperature, and its speed of movement depends on pressure. |
|  | maze.py | Main code that implementation of visualizing moving ghost. A BME280 type sensor was used to measure temperature and pressure |
|  | ghost_neo.py | Contains the Ghost class - ghost body pixels for WS2816, 16x16 rgb LEDs |
