# The hodgepodge for WS2812B RGB LED panel
Some miscellaneous visualizations displaying on a WS2812B RGB LED panel using MicroPython.

## Content  

| App (Visualizations) | Purpose |
| --- |  --- |
| [maze](./apps/maze/README.md) | The folder containing program codes and auxiliary modules for visualizing path finding in a maze. It is now common to say that this is the result of AI, but it is simply an implementation of the depth-first search (DFS) or breadth-first search (BFS) algorithm. It looks something like this: [AI finds its way through a maze](https://youtube.com/shorts/KfYbfn5_Zk4) for DFS. [Route search simulation](https://www.youtube.com/watch?v=QLT3La0Wb3k) (BFS)|
| [spiral](./apps/spiral/README.md) |  [Spiral effect on LED matrix](https://youtu.be/DPfMtILU69g) |
| [ghost](./apps/ghost/README.md) |  The folder containing program codes and auxiliary modules for visualizing moving ghost body pixels. The ghost's color and its speed changes depending on the distance to the person/object present. A sensor of the HLK-LD2410 type was used to measure the distance. [Ghost body pixels for WS2816, 16x16 rgb LEDs](https://youtu.be/FMxCccp73rI)|
| [smart-snake-neopixel](https://github.com/Alex-Teteria/smart-snake-neopixel) | Smart snake AI chasing points on a 16x16 NeoPixel matrix - MicroPython for RP2040 https://www.youtube.com/watch?v=LGbLxqmCGBI |
| [audio-spectrum-visualizer](./apps/rectangular-neo-spectrum/README.md) | Audio spectrum is visualized as colored concentric rectangles. Calculating the spectrum of the audio signal and displaying it on the WS2812B 16×16 RGB LED matrix (NeoPixel) in the form of concentric squares, where the size corresponds to the signal level, and the color to the spectral components. |
| [switcher](./apps/switcher/README.md) | The switcher utility implements switching between applications from the apps/ directory by pressing a button. The current application index is stored in the app_idx.txt file. After a confirmed press, the index is incremented and machine.reset() is executed.  |
| [lib](./lib/README.md) | Module ld2410.py to support sensor type HLK-LD2410 (microwave sensor for measuring distance to a person/object). |  

* [📂 Бібліотеки](./lib/README.md)
  
