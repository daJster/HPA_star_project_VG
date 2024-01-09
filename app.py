from flask import Flask, render_template, send_from_directory, request, jsonify
from map import get_image_path, \
                create_obstacle_map,\
                load_npy,\
                draw_colored_square,\
                get_strategic_exit_points,\
                astar_pathfinding,\
                tuple_to_json,\
                run_astar_in_rectangle,\
                visualize_path,\
                map_dicts,\
                map_directory, supported_extensions
import numpy as np

app = Flask(__name__)

global loaded_array
loaded_array = load_npy(f"obstacle_maps/{map_dicts[0]['map_name']}_obstacle.npy")

@app.route('/')
def index() :
    # map_dict = map_dicts[2]  # Replace with the path to your image
    
    # image_path = get_image_path(map_directory, map_dict['map_name'], supported_extensions)
    # is_saved = create_obstacle_map(image_path, threshold_value=map_dict['threshold'])
    # # Load the NumPy array    
    # loaded_array = load_npy(f"obstacle_maps/{map_dict['map_name']}_obstacle.npy")
    
    # # Divide the loaded image into equal lengths on x-axis and y-axis
    # n_divisions = map_dict['grid_size']
    # x_divisions = np.linspace(0, loaded_array.shape[0], num=n_divisions, dtype=int)
    # y_divisions = np.linspace(0, loaded_array.shape[1], num=n_divisions, dtype=int)
    
    # # static exit_points
    # exit_points = get_strategic_exit_points(loaded_array, x_divisions, y_divisions)
    # # Set start and end coordinates (replace with your own coordinates) (X, Y)
    # start_coord = {'x': 100, 'y': 100}
    # end_coord = {'x': 110, 'y': 100}


    # # Run A* pathfinding algorithm
    # optimal_path = tuple_to_json(astar_pathfinding(loaded_array, (start_coord['x'], start_coord['y']), (end_coord['x'], end_coord['y'])))
    # main_path = [optimal_path, True]
    
    # # Run A* in each rectangle to compute paths between exit points
    # paths_between_exit_points = run_astar_in_rectangle(loaded_array, exit_points, x_divisions, y_divisions)
     
    # paths = paths_between_exit_points + [main_path] 

    # # Visualize the path on the image
    # visualize_path(loaded_array, paths, start_coord, end_coord, x_divisions, y_divisions, exit_points)

    return render_template('index.html')

@app.route('/maps/<filename>')
def maps(filename):
    return send_from_directory('maps', filename)

@app.route('/get_image_info', methods=['POST'])
def get_image_info():
    game_name = request.form.get('game_name')
    game_map_dict = {}
    for map_dict in map_dicts:
        if map_dict['map_name'] == game_name:
            game_map_dict = map_dict
            break
    
    # Assuming you have a function to get image info based on game_name
    image_path = get_image_path(map_directory, game_map_dict['map_name'], supported_extensions)
    global loaded_array
    loaded_array = load_npy(f"obstacle_maps/{game_map_dict['map_name']}_obstacle.npy")
    original_width, original_height = loaded_array.shape

    return jsonify({
        'image_path': image_path,
        'original_width': original_width,
        'original_height': original_height
    })
    
    
@app.route('/get_optimal_path', methods=['POST'])
def get_optimal_path():
    data = request.get_json()

    start_point = data.get('start_point')
    end_point = data.get('end_point')

    # Example: Validate the points (you can add your own validation logic)
    if loaded_array[start_point['x'], start_point['y']] == 0 or loaded_array[end_point['x'], end_point['y']] == 0:
        return jsonify({'error': 'Invalid starting or ending point'}), 400

    # Example: Your A* pathfinding logic here

    optimal_path = tuple_to_json(astar_pathfinding(loaded_array, (start_point['x'], start_point['y']), (end_point['x'], end_point['y'])))

    return jsonify({'path': optimal_path})

def convert_int64_to_int(item):
    if isinstance(item, np.int64):
        return int(item)
    elif isinstance(item, list):
        return [convert_int64_to_int(subitem) for subitem in item]
    elif isinstance(item, dict):
        return {key: convert_int64_to_int(value) for key, value in item.items()}
    else:
        return item
    
    
@app.route('/load_grid_and_exit_points', methods=['POST'])
def load_grid_and_exit_points():
    data = request.get_json()
    grid_size = int(data.get('grid_size'))
    n_divisions = grid_size
    x_divisions = np.linspace(0, loaded_array.shape[0], num=n_divisions, dtype=int)
    y_divisions = np.linspace(0, loaded_array.shape[1], num=n_divisions, dtype=int)
    exit_points = convert_int64_to_int(get_strategic_exit_points(loaded_array, x_divisions, y_divisions))
    
    return jsonify({'x_div' : x_divisions.tolist(), 'y_div' : y_divisions.tolist(), 'exit_points' : exit_points})


if __name__ == '__main__':
    app.run(debug=True)
