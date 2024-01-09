import cv2
import numpy as np
import matplotlib.pyplot as plt
from heapq import heappop, heappush
import os

supported_extensions = ['jpeg', 'png', 'jpg']
map_dicts = [{'map_name' : 'lol-map', 'threshold' : 20, 'grid_size' : 15, 'reverse' : False},
                {'map_name' : 'GTAV-map', 'threshold' : 75, 'grid_size' : 40, 'reverse' : False},
                {'map_name' : 'test-map', 'threshold' : 20, 'grid_size' : 4, 'reverse' : False},
                {'map_name' : 'Berlin-map', 'threshold' : 230, 'grid_size' : 40, 'reverse' : True},
                {'map_name' : 'Liverpool-map', 'threshold' : 200, 'grid_size' : 40, 'reverse' : True},
                {'map_name' : 'Paris-map', 'threshold' : 200, 'grid_size' : 40, 'reverse' : True},
                {'map_name' : 'Tokyo-map', 'threshold' : 160, 'grid_size' : 40, 'reverse' : True},
                {'map_name' : 'Rome-map', 'threshold' : 70, 'grid_size' : 40, 'reverse' : False},
                {'map_name' : 'France-map', 'threshold' : 240, 'grid_size' : 40, 'reverse' : True},
                {'map_name' : 'Russia-map', 'threshold' : 240, 'grid_size' : 40, 'reverse' : True}]

map_directory = "maps"

def create_obstacle_map(img_path, threshold_value=100, reverse=False):
    # Extract the file name without extension
    img_name = img_path.split('/')[-1].split('.')[0]

    # Read the RGB image
    original_img = cv2.imread(img_path)

    # Check if the image is loaded successfully
    if original_img is None:
        raise ValueError(f"Error: Unable to read the image at {img_path}")
    # Check the dimensions of the loaded image
    if len(original_img.shape) != 3:
        raise ValueError("Error: The loaded image is not in BGR format")
    
    # Convert the image to grayscale
    gray_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to create a binary obstacle map
    _, obstacle_map = cv2.threshold(gray_img, threshold_value, 255, cv2.THRESH_BINARY)
    
    # Display the obstacle map
    if reverse :
        obstacle_map = cv2.bitwise_not(obstacle_map)
        
    plt.imshow(obstacle_map, cmap='gray')
    plt.savefig(f'obstacle_maps/{img_name}_obstacle.jpg')
    plt.close()
    
    # Save the obstacle map as a NumPy array
    np.save(f'obstacle_maps/{img_name}_obstacle.npy', obstacle_map)
    return True


def load_npy(file_path):
    loaded_array = np.load(file_path)
    return loaded_array.transpose()

def astar_pathfinding(grid, start, end):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(point):
        x, y = point
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1),
                (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)]

    def is_valid(point):
        x, y = point
        return 0 <= x < grid.shape[0] and 0 <= y < grid.shape[1] and grid[x, y] == 255

    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        current_cost, current_point = heappop(open_set)

        if current_point == end:
            break

        for next_point in neighbors(current_point):
            if is_valid(next_point):
                new_cost = cost_so_far[current_point] + 1
                if next_point not in cost_so_far or new_cost < cost_so_far[next_point]:
                    cost_so_far[next_point] = new_cost
                    priority = new_cost + heuristic(end, next_point)
                    heappush(open_set, (priority, next_point))
                    came_from[next_point] = current_point

    # Reconstruct path
    path = []
    current_point = end
    while current_point != start:
        path.append(current_point)
        try :
            current_point = came_from[current_point]
        except KeyError:
            break
    path.append(start)
    path.reverse()
    return path

def is_empty_cell(grid, point):
    x, y = point
    return 0 <= x < grid.shape[0] and 0 <= y < grid.shape[1] and grid[x, y] == 255

def get_strategic_exit_points(grid, x_divisions, y_divisions):
    exit_points_list = []

    for i in range(len(x_divisions) - 1):
        for j in range(len(y_divisions) - 1):
            # Get the corners of the rectangle
            top_left = (x_divisions[i], y_divisions[j])
            top_right = (x_divisions[i + 1], y_divisions[j])
            bottom_left = (x_divisions[i], y_divisions[j + 1])
            bottom_right = (x_divisions[i + 1], y_divisions[j + 1])

            # Get the middle points of the edges
            top_middle = (x_divisions[i] + x_divisions[i + 1]) // 2, y_divisions[j]
            bottom_middle = (x_divisions[i] + x_divisions[i + 1]) // 2, y_divisions[j + 1]
            left_middle = x_divisions[i], (y_divisions[j] + y_divisions[j + 1]) // 2
            right_middle = x_divisions[i + 1], (y_divisions[j] + y_divisions[j + 1]) // 2

            middle_points = [top_middle, bottom_middle, left_middle, right_middle]

            # Check if the middle point is full
            if not is_empty_cell(grid, top_middle):
                # If the middle point is full, find the two closest points within the rectangle
                center = ((x_divisions[i] + x_divisions[i + 1]) // 2, (y_divisions[j] + y_divisions[j + 1]) // 2)
                middle_points = sorted(middle_points, key=lambda p: np.linalg.norm(np.array(p) - np.array(center)))

            # Add strategic exit points for the rectangle if both sides are empty (0)
            exit_points_list.append([{'x': i, 'y': j}, [{'x': point[0], 'y': point[1]} for point in [top_left, top_right, bottom_left, bottom_right] + middle_points
                                   if is_empty_cell(grid, point)]])

    return exit_points_list

def transform_to_subgrid_coordinates(global_coord, subgrid_start):
    return (global_coord[0] - subgrid_start[0], global_coord[1] - subgrid_start[1])

def transform_to_global_coordinates(subgrid_coord, subgrid_start):
    return (subgrid_coord[0] + subgrid_start[0], subgrid_coord[1] + subgrid_start[1])

def run_astar_in_rectangle(grid, exit_points, x_divisions, y_divisions):
    paths_list = []
    for i, rectangle_points in enumerate(exit_points):
        print(f"exit_point : {i+1}/{len(exit_points)}")
        rectangle_indices = rectangle_points[0]
        rectangle_exit_points = rectangle_points[1]
        
        if rectangle_indices['x'] + 1 < len(x_divisions) and rectangle_indices['y'] + 1 < len(y_divisions):
            subgrid_start = (x_divisions[rectangle_indices['x']], y_divisions[rectangle_indices['y']])
            subgrid_end = (x_divisions[rectangle_indices['x'] + 1], y_divisions[rectangle_indices['y'] + 1])
        else:
            continue
        
        subgrid = grid[subgrid_start[0]:subgrid_end[0]+1, subgrid_start[1]:subgrid_end[1]+1]

        for start_point in rectangle_exit_points:
            for end_point in rectangle_exit_points:
                if start_point != end_point:
                    # Transform coordinates to subgrid
                    start_point_subgrid = transform_to_subgrid_coordinates((start_point['x'], start_point['y']), subgrid_start)
                    end_point_subgrid = transform_to_subgrid_coordinates((end_point['x'], end_point['y']), subgrid_start)
                    
                    # Run A* on the subgrid
                    path = astar_pathfinding(subgrid, start_point_subgrid, end_point_subgrid)

                    # Transform A* path coordinates back to global grid
                    path_global = tuple_to_json([transform_to_global_coordinates(point, subgrid_start) for point in path])
                    paths_list.append([path_global, False])

    return paths_list

def draw_colored_square(grid, coord, color, point_size=1):
    for i in range(-point_size, point_size + 1):
        for j in range(-point_size, point_size + 1):
            grid[(coord['x'] + i)%grid.shape[0], (coord['y'] + j)%grid.shape[1]] = np.array(color)
            

def visualize_path(grid, paths, start_coord, end_coord, x_indices, y_indices, exit_points):
    # Create a copy of the grid to avoid modifying the original
    visual_grid = np.copy(grid)
    # Convert the grayscale grid to RGB
    visual_grid = cv2.cvtColor(visual_grid, cv2.COLOR_GRAY2RGB)
    
    draw_colored_square(visual_grid, start_coord, color=[0, 255, 0], point_size=6) # green
    draw_colored_square(visual_grid, end_coord, color=[255, 0, 0], point_size=6) # red
                
    # Draw the path as blue
    for path in paths :
        path_color = [255, 255, 0] # yellow
        
        if path[1]:
            path_color = [0, 255, 255] # cyan
            
        for point in path[0]:
            draw_colored_square(visual_grid, point, color=path_color) 
            
            

    # Draw the x-axis divisions in violet
    for x_index in x_indices:
        for idy in range(grid.shape[1]):
            draw_colored_square(visual_grid, {'x': x_index, 'y': idy}, color=[148, 0, 211])  # violet

    # Draw the y-axis divisions in violet
    for y_index in y_indices:
        for idx in range(grid.shape[0]):
            draw_colored_square(visual_grid, {'x':  idx, 'y': y_index}, color=[148, 0, 211])  # violet


    for exit_point in exit_points:
            for point in exit_point[1]:
                draw_colored_square(visual_grid, point, color=[255, 0, 0], point_size=2)  # yellow
                
                
    # Display the image with the colored path
    plt.imshow(visual_grid.transpose((1, 0, 2)))
    plt.title('A* Pathfinding with Colored Path Visualization')
    plt.savefig("solution.png")
    
def get_image_path(map_directory, image_name, supported_extensions=['jpeg', 'png', 'jpg']):
    for extension in supported_extensions:
        potential_path = os.path.join(map_directory, f"{image_name}.{extension}")
        if os.path.exists(potential_path):
            return potential_path
    raise FileNotFoundError(f"Image '{image_name}' not found in '{map_directory}' with supported extensions: {supported_extensions}")


def tuple_to_json(path) :
    json_list = []
    for point in path :
        json_list.append({'x' : point[0], 'y' : point[1]})
    return json_list

if __name__ == "__main__":
    
    map_dict = map_dicts[-4]  # Replace with the path to your image
    
    image_path = get_image_path(map_directory, map_dict['map_name'], supported_extensions)
    is_saved = create_obstacle_map(image_path, threshold_value=map_dict['threshold'], reverse=map_dict['reverse'])
    # Load the NumPy array    
    loaded_array = load_npy(f"obstacle_maps/{map_dict['map_name']}_obstacle.npy")
    
    # Divide the loaded image into equal lengths on x-axis and y-axis
    n_divisions = map_dict['grid_size']
    x_divisions = np.linspace(0, loaded_array.shape[0], num=n_divisions, dtype=int)
    y_divisions = np.linspace(0, loaded_array.shape[1], num=n_divisions, dtype=int)
    
    # static exit_points
    exit_points = get_strategic_exit_points(loaded_array, x_divisions, y_divisions)
    # Set start and end coordinates (replace with your own coordinates) (X, Y)
    start_coord = {'x': 0, 'y': 0}
    end_coord = {'x': 0, 'y': 10}


    # Run A* pathfinding algorithm
    optimal_path = tuple_to_json(astar_pathfinding(loaded_array, (start_coord['x'], start_coord['y']), (end_coord['x'], end_coord['y'])))
    main_path = [optimal_path, True]
    
    # Run A* in each rectangle to compute paths between exit points
    # paths_between_exit_points = run_astar_in_rectangle(loaded_array, exit_points, x_divisions, y_divisions)
     
    paths = [main_path] 
    # print(paths)
    # Visualize the path on the image
    visualize_path(loaded_array, paths, start_coord, end_coord, x_divisions, y_divisions, exit_points)

    # Return the path as a list of coordinates
    # print("A* Path:", path)