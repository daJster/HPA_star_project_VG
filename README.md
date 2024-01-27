# HPA* Pathfinding in Video Games

This project focuses on implementing HPA* (Hierarchical Pathfinding A*) for efficient pathfinding in video games, with the ultimate goal of creating a working mini-map GPS system to guide players within the game world. The project includes two main applications: `map.py` and `app.py`.

## `map.py`

`map.py` contains the core functions implementing both A* and HPA* algorithms. The most crucial functions to explore are:

1. **astar_pathfinding**: This function performs A* pathfinding and calculates the optimal path between two points on the map.

2. **get_strategic_exit_points** and **run_astar_in_rectangle**: These functions are essential for HPA*, handling the strategic exit points and running A* within rectangles during map division (x_divisions : x-axis divisions, y_divisions: y_axis divisions, and find optimal paths in each mini rectangle).

```bash
python3 map.py --image_path maps/Tokyo-map.png --start_coord 420 400 --end_coord 360 110 --grid_size 30 --reverse True --threshold 160
```

## `app.py`

`app.py` serves as a Flask API web application to showcase the project's functionality. To run the application, execute `python3 app.py`, and the website will be launched on a localhost port. Here's a guide on using the application:

1. **Explore the App**: Upon launching the app, navigate through the interface to get familiar with the features.

2. **A* Pathfinding**:
   - Click on the map twice to set a start and end point.
   - A* pathfinding will be executed, and the result will be displayed on the map.

3. **HPA* Pathfinding**:
   - Choose a grid size and apply HPA* using the designated button.
   - Observe the terminal for the progressive construction of paths during the HPA* process.
   - At the end, all the paths that can be used will be displayed on the map.

## Note

There is an initialization issue that requires clicking on map and grid size buttons to initiate the map array and exit points for the app to work correctly, especially for HPA* functionality. Ensure that you follow this step before attempting to run HPA*. High grid size may cause lagging in the app :) 

Feel free to explore and contribute to the project for further improvements in video game pathfinding in mini maps navigation!

