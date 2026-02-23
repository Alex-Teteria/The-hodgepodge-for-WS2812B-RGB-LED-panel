# The hodgepodge for WS2812B RGB LED panel
Some miscellaneous visualizations displaying on a WS2812B RGB LED panel using MicroPython.

# Візуалізації 
* [:game_die: Maze](./apps/maze/README.md)
* [📂 Бібліотеки](./lib/README.md)


## Content  

| App (Visualizations) | Purpose |
| --- |  --- |
| [maze](./apps/maze/README.md) | The folder containing program codes and auxiliary modules for visualizing path finding in a maze. It is now common to say that this is the result of AI, but it is simply an implementation of the depth-first search (DFS) or breadth-first search (BFS) algorithm. It looks something like this: [AI finds its way through a maze](https://youtube.com/shorts/KfYbfn5_Zk4) for DFS. [Route search simulation](https://www.youtube.com/watch?v=QLT3La0Wb3k)|
| spiral |  [Spiral effect on LED matrix](https://youtu.be/DPfMtILU69g) |
| ghost |  The folder containing program codes and auxiliary modules for visualizing moving ghost body pixels. The ghost's color and its speed changes depending on the distance to the person/object present. A sensor of the HLK-LD2410 type was used to measure the distance. [Ghost body pixels for WS2816, 16x16 rgb LEDs](https://youtu.be/FMxCccp73rI)|
| [lib](./lib/README.md) | Module ld2410.py to support sensor type HLK-LD2410 (microwave sensor for measuring distance to a person/object). |  

## LD2410 sensor connection diagram  
The UART interface is used to receive data from the sensor.
![image](https://github.com/user-attachments/assets/988554c0-2d21-4e60-a4eb-386cffd3efea)



