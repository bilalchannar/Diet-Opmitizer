import os
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient
from flask import Flask, request, jsonify
from genetic_algorithm import run_genetic_algorithm

app = Flask(__name__)
CORS(app)

# Use environment variable for MongoDB URI (works with Docker/Mongo Express)
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['diet_optimizer']

@app.route('/foods', methods=['GET'])
def get_foods():
    foods = list(db['foods'].find({}, {'_id': 0}))
    return jsonify(foods)

@app.route('/foods', methods=['POST'])
def add_food():
    food = request.json or {}

    # Basic validation
    required = ['name', 'calories', 'protein', 'carbs', 'fat', 'price']
    for f in required:
        if f not in food:
            return jsonify({'error': f'Missing field: {f}'}), 400

    try:
        food_doc = {
            'name': str(food['name']).strip(),
            'calories': float(food['calories']),
            'protein': float(food['protein']),
            'carbs': float(food['carbs']),
            'fat': float(food['fat']),
            'price': float(food['price']),
        }
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid field types; numeric fields must be numbers.'}), 400

    # Non-negative checks
    if any(x < 0 for x in (food_doc['calories'], food_doc['protein'], food_doc['carbs'], food_doc['fat'], food_doc['price'])):
        return jsonify({'error': 'Numeric fields must be non-negative.'}), 400

    db['foods'].insert_one(food_doc)
    return jsonify({'status': 'success'})

@app.route('/foods/<name>', methods=['DELETE'])
def delete_food(name):
    db['foods'].delete_one({'name': name})
    return jsonify({'status': 'deleted'})

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json or {}

    # Validate optimize input
    targets = data.get('targets')
    if not isinstance(targets, dict):
        return jsonify({'error': 'Missing or invalid "targets" object.'}), 400

    for k in ('calories', 'protein', 'carbs', 'fat'):
        if k not in targets:
            return jsonify({'error': f'Missing target: {k}'}), 400
        try:
            targets[k] = float(targets[k])
        except (TypeError, ValueError):
            return jsonify({'error': f'Invalid target value for {k}; must be a number.'}), 400

    try:
        budget = float(data.get('budget', 0))
        population_size = int(data.get('population_size', 0))
        generations = int(data.get('generations', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid numeric parameter(s) for budget/population_size/generations.'}), 400

    if budget < 0:
        return jsonify({'error': 'Budget must be non-negative.'}), 400
    if population_size <= 0 or generations <= 0:
        return jsonify({'error': 'population_size and generations must be positive integers.'}), 400


    # ✅ Only accept valid food docs from DB
    foods = list(db['foods'].find(
        {
            "name": {"$exists": True},
            "calories": {"$exists": True},
            "protein": {"$exists": True},
            "carbs": {"$exists": True},
            "fat": {"$exists": True},
            "price": {"$exists": True},
        },
        {'_id': 0}
    ))

    if not foods:
        return jsonify({"error": "Food database is empty. Add foods first."}), 400

    data['food_db'] = foods

    # ✅ Run GA
    result = run_genetic_algorithm(data)

    # ✅ Save BOTH inputs + outputs
    result_doc = {
        "inputs": {
            "targets": data.get("targets", {}),
            "budget": data.get("budget"),
            "population_size": data.get("population_size"),
            "generations": data.get("generations"),
        },
        "diet": result.get("diet", []),
        "score": result.get("score"),
        "totals": result.get("totals", {}),
        "cost": result.get("cost"),
        "created_at": datetime.utcnow().isoformat(),
    }

    db.results.insert_one(result_doc)
    del result_doc['_id']  # remove MongoDB internal ID before sending back
    return jsonify(result_doc)  # return it to frontend too

@app.route('/results', methods=['GET'])
def get_results():
    results = list(db.results.find({}, {'_id': 0}))
    return jsonify(results)


@app.route('/health', methods=['GET'])
def health():
    """Simple health check for service and MongoDB connectivity."""
    mongo_status = "unknown"
    try:
        # ping the server to confirm connectivity
        client.admin.command('ping')
        mongo_status = "ok"
    except Exception:
        mongo_status = "unreachable"

    return jsonify({"status": "ok", "mongo": mongo_status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
