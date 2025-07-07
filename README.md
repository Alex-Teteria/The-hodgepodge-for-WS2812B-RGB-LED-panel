# The hodgepodge for WS2812B RGB LED panel
Some miscellaneous visualizations displaying on a WS2812B RGB LED panel using MicroPython.

## Content  

| File | Contain | Purpose |
| --- |  ---: |  --- |
| Maze |  |The folder containing the main program codes and auxiliary modules for visualizing path finding in a maze. It is now common to say that this is the result of AI :smile:, but it is simply an implementation of the depth-first search (DFS) or breadth-first search (BFS) algorithm. It looks something like this: [AI finds its way through a maze](https://youtube.com/shorts/KfYbfn5_Zk4) |
|  | maze_generator.py | Module for creating random mazes |
|  |graph.py | Contains the Graph class as an undirected graph |
|  | itertools.py | Contains functions creating iterators |
|  | maze.py | Main code that implementation of finding a passage in a maze. Switching search modes (DFS or BFS) is done by the button |
|  | maze_1.txt | Contains the coordinates of the test maze  |
|  | maze_dfs.py | Implementation of finding a passage in a maze by depth-first search (DFS) algorithm |
|  | maze_bfs.py | Implementation of finding a passage in a maze by breadth-first search (DFS) algorithm |
|  | maze_dfs_bfs.py | Route search simulation. One point catches up with another. The first point chooses the shortest route to the second point it is trying to cover. The second point chooses the route to the finish point in the maze. First point using the BFS algorithm. Second point using the DFS algorithm |
|  | maze_bfs_bfs.py | Route search simulation. One point catches up with another. The first point chooses the shortest route to the second point it is trying to cover. The second point chooses the route to the farthest point in the maze so as not to intersect with the first point. This repeats in a loop until the first point covers the second or until the allotted time runs out. https://www.youtube.com/watch?v=QLT3La0Wb3k |
||  |  |
| spiral.py |  | Spiral effect on LED matrix  |
||  |  |
| Ghost |  | The folder containing the main program code and auxiliary modules for visualizing moving ghost body pixels. The ghost's color changes depending on the ambient temperature, and its speed of movement depends on pressure. |
|  | ghost_microwave_sensor.py | Main code that implementation of visualizing moving ghost. The ghost's color and its speed changes depending on the distance to the person/object presen. A sensor of the HLK-LD2410 type was used to measure the distance. |
|  | maze.py | Main code that implementation of visualizing moving ghost. A BME280 type sensor was used to measure temperature and pressure |
|  | ghost_neo.py | Contains the Ghost class - ghost body pixels for WS2816, 16x16 rgb LEDs |
|  | bme280_float.py | This module borrows from the Adafruit BME280 Python library. A BME280 type sensor was used to measure temperature and pressure |
|  | ld2410.py | Module to support sensor type HLK-LD2410 (microwave sensor for measuring distance to a person/object). This module borrows from https://github.com/shabaz123/LD2410/blob/main/ld2410.py |
