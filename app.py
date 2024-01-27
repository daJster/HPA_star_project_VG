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
                map_directory, supported_extensions, create_directory
import numpy as np

app = Flask(__name__)

global loaded_array
try :
    loaded_array = load_npy(f"obstacle_maps/{map_dicts[0]['map_name']}_obstacle.npy")
except Exception as e :
    create_directory("obstacle_maps")
    print(e)
    

@app.route('/')
def index() :
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
    try :
        loaded_array = load_npy(f"obstacle_maps/{game_map_dict['map_name']}_obstacle.npy")
    except Exception as e :
        create_obstacle_map(image_path, threshold_value=game_map_dict['threshold'], reverse=game_map_dict['reverse'])
        loaded_array = load_npy(f"obstacle_maps/{game_map_dict['map_name']}_obstacle.npy")
        print(e)
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
    # paths_between_exit_points = run_astar_in_rectangle(loaded_array, exit_points, x_divisions, y_divisions)
    return jsonify({'path': optimal_path})

@app.route('/get_hpa_path', methods=['POST'])
def get_hpa_path():
    data = request.get_json()
    x_divisions = data.get('x_divisions')
    y_divisions = data.get('y_divisions')
    exit_points = data.get('exit_points')
    optimal_paths = run_astar_in_rectangle(loaded_array, exit_points=exit_points, x_divisions=x_divisions, y_divisions=y_divisions, js_api=True)
    return jsonify({'paths': optimal_paths})

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
