from flask import Flask, render_template, jsonify, request
import random
import time

app = Flask(__name__)

# Game state
snake_game = {
    'width': 600,
    'height': 400,
    'snake_pos': [[300, 200]],
    'snake_size': 20,
    'direction': "RIGHT",
    'food_pos': [0, 0],
    'score': 0,
    'high_score': 0,
    'running': True
}

# Initialize food position
snake_game['food_pos'] = [random.randrange(1, (snake_game['width']//snake_game['snake_size'])) * snake_game['snake_size'], 
                         random.randrange(1, (snake_game['height']//snake_game['snake_size'])) * snake_game['snake_size']]

# Load high score
try:
    with open("highscore.dat", "r") as f:
        snake_game['high_score'] = int(f.read())
except:
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game_state')
def get_game_state():
    return jsonify(snake_game)

@app.route('/input', methods=['POST'])
def handle_input():
    data = request.json
    direction = data.get('direction')
    
    current_dir = snake_game['direction']
    if direction == "UP" and current_dir != "DOWN":
        snake_game['direction'] = "UP"
    elif direction == "DOWN" and current_dir != "UP":
        snake_game['direction'] = "DOWN"
    elif direction == "LEFT" and current_dir != "RIGHT":
        snake_game['direction'] = "LEFT"
    elif direction == "RIGHT" and current_dir != "LEFT":
        snake_game['direction'] = "RIGHT"
    
    return jsonify({'status': 'success'})

@app.route('/update', methods=['POST'])
def update_game():
    if not snake_game['running']:
        return jsonify(snake_game)
    
    # Snake movement
    head = snake_game['snake_pos'][0].copy()
    if snake_game['direction'] == "UP":
        head[1] -= snake_game['snake_size']
    elif snake_game['direction'] == "DOWN":
        head[1] += snake_game['snake_size']
    elif snake_game['direction'] == "LEFT":
        head[0] -= snake_game['snake_size']
    elif snake_game['direction'] == "RIGHT":
        head[0] += snake_game['snake_size']
    
    # Check collisions
    if (head[0] < 0 or head[0] >= snake_game['width'] or
        head[1] < 0 or head[1] >= snake_game['height']):
        snake_game['running'] = False
    
    # Check self-collision
    for segment in snake_game['snake_pos'][1:]:
        if head == segment:
            snake_game['running'] = False
            break
    
    if snake_game['running']:
        snake_game['snake_pos'].insert(0, head)
        
        # Check food collision
        if head == snake_game['food_pos']:
            snake_game['score'] += 1
            snake_game['high_score'] = max(snake_game['score'], snake_game['high_score'])
            snake_game['food_pos'] = [
                random.randrange(1, (snake_game['width']//snake_game['snake_size'])) * snake_game['snake_size'],
                random.randrange(1, (snake_game['height']//snake_game['snake_size'])) * snake_game['snake_size']
            ]
        else:
            snake_game['snake_pos'].pop()
    
    return jsonify(snake_game)

@app.route('/reset', methods=['POST'])
def reset_game():
    snake_game.update({
        'snake_pos': [[300, 200]],
        'direction': "RIGHT",
        'score': 0,
        'running': True,
        'food_pos': [
            random.randrange(1, (snake_game['width']//snake_game['snake_size'])) * snake_game['snake_size'],
            random.randrange(1, (snake_game['height']//snake_game['snake_size'])) * snake_game['snake_size']
        ]
    })
    with open("highscore.dat", "w") as f:
        f.write(str(snake_game['high_score']))
    return jsonify(snake_game)

if __name__ == '__main__':
    app.run(debug=True)