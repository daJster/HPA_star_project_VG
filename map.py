import cv2
import numpy as np
import matplotlib.pyplot as plt
from heapq import heappop, heappush
import os


def create_obstacle_map(img_path, threshold_value=100):
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
    
    # second filter application to make sure there are no gray pixels
    obstacle_map[gray_img > threshold_value] = 255 # eliminate gray pixels
    obstacle_map[gray_img <= threshold_value] = 0 # eliminate gray pixels
    
    # Display the obstacle map
    plt.imshow(obstacle_map, cmap='gray')
    plt.savefig(f'obstacle_maps/{img_name}_obstacle.jpg')
    plt.close()
    
    # Save the obstacle map as a NumPy array
    np.save(f'obstacle_maps/{img_name}_obstacle.npy', obstacle_map)
    return True


def load_npy(file_path):
    loaded_array = np.load(file_path)
    return loaded_array

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
        current_point = came_from[current_point]
    path.append(start)
    path.reverse()

    return path


def draw_colored_square(grid, coord, point_size, color):
    for i in range(-point_size, point_size + 1):
        for j in range(-point_size, point_size + 1):
            grid[coord[0] + i, coord[1] + j] = np.array(color)
            

def visualize_path(grid, path, start_coord, end_coord):
    # Create a copy of the grid to avoid modifying the original
    visual_grid = np.copy(grid)
    # Convert the grayscale grid to RGB
    visual_grid = cv2.cvtColor(visual_grid, cv2.COLOR_GRAY2RGB)
    
    draw_colored_square(visual_grid, start_coord, 6, [0, 255, 0]) # green
    draw_colored_square(visual_grid, end_coord, 6, [255, 0, 0]) # red

    # Draw the path as blue
    for point in path:
        draw_colored_square(visual_grid, point, 1, [0, 255, 255]) # cyan

    # Display the image with the colored path
    plt.imshow(visual_grid)
    plt.title('A* Pathfinding with Colored Path Visualization')
    plt.savefig("solution.png")
    
def get_image_path(map_directory, image_name, supported_extensions=['jpeg', 'png', 'jpg']):
    for extension in supported_extensions:
        potential_path = os.path.join(map_directory, f"{image_name}.{extension}")
        if os.path.exists(potential_path):
            return potential_path
    raise FileNotFoundError(f"Image '{image_name}' not found in '{map_directory}' with supported extensions: {supported_extensions}")


if __name__ == "__main__":
    supported_extensions = ['jpeg', 'png', 'jpg']
    map_directory = "maps"
    image_name = 'GTAV-map'  # Replace with the path to your image
    image_path = get_image_path(map_directory, image_name, supported_extensions)
    is_saved = create_obstacle_map(image_path, threshold_value=70)
    # Load the NumPy array    
    loaded_array = load_npy(f'obstacle_maps/{image_name}_obstacle.npy')

    # # Set start and end coordinates (replace with your own coordinates)
    start_coord = (200, 100)
    end_coord = (240, 86    0)

    # # Run A* pathfinding algorithm
    path = astar_pathfinding(loaded_array, start_coord, end_coord)

    # # Visualize the path on the image
    visualize_path(loaded_array, path, start_coord, end_coord)

    # Return the path as a list of coordinates
    # print("A* Path:", path)