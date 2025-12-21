import os
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient
from flask import Flask, request, jsonify
from genetic_algorithm import run_genetic_algorithm
from csp_solver import run_csp_solver

app = Flask(__name__)
CORS(app)

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

    if any(x < 0 for x in (food_doc['calories'], food_doc['protein'], food_doc['carbs'], food_doc['fat'], food_doc['price'])):
        return jsonify({'error': 'Numeric fields must be non-negative.'}), 400

    db['foods'].insert_one(food_doc)
    return jsonify({'status': 'success'})


@app.route('/foods/<name>', methods=['DELETE'])
def delete_food(name):
    res = db['foods'].delete_one({'name': name})
    return jsonify({'deleted_count': res.deleted_count})



@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json or {}

    technique = data.get('technique', 'ga').lower()
    if technique not in ('ga', 'csp', 'both'):
        return jsonify({'error': 'Invalid technique. Use "ga", "csp", or "both".'}), 400

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
        population_size = int(data.get('population_size', 30))
        generations = int(data.get('generations', 50))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid numeric parameter(s) for budget/population_size/generations.'}), 400

    if budget < 0:
        return jsonify({'error': 'Budget must be non-negative.'}), 400

    if technique in ('ga', 'both'):
        if population_size <= 0 or generations <= 0:
            return jsonify({'error': 'population_size and generations must be positive integers.'}), 400

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

    if technique == 'ga':
        result = run_genetic_algorithm(data)
        result['technique'] = 'Genetic Algorithm'
    elif technique == 'csp':
        result = run_csp_solver(data)
        result['technique'] = 'CSP'
    else:  # both
        ga_result = run_genetic_algorithm(data)
        ga_result['technique'] = 'Genetic Algorithm'
        csp_result = run_csp_solver(data)
        csp_result['technique'] = 'CSP'
    
        combined_result = {
            'ga': ga_result,
            'csp': csp_result,
            'technique': 'both'
        }
  
        result_doc = {
            "inputs": {
                "targets": data.get("targets", {}),
                "budget": data.get("budget"),
                "population_size": data.get("population_size"),
                "generations": data.get("generations"),
                "technique": "both"
            },
            "ga_result": ga_result,
            "csp_result": csp_result,
            "created_at": datetime.utcnow().isoformat(),
        }
        db.results.insert_one(result_doc)
        return jsonify(combined_result)

    result_doc = {
        "inputs": {
            "targets": data.get("targets", {}),
            "budget": data.get("budget"),
            "population_size": data.get("population_size"),
            "generations": data.get("generations"),
            "technique": result.get("technique"),

        },
        "diet": result.get("diet", []),
        "score": result.get("score"),
        "totals": result.get("totals", {}),
        "cost": result.get("cost"),
        "technique": result.get("technique"),
        "created_at": datetime.utcnow().isoformat(),
    }

    db.results.insert_one(result_doc)
    result_doc.pop('_id', None)
    return jsonify(result_doc)


@app.route('/results', methods=['GET'])
def get_results():
    results = list(db.results.find({}, {'_id': 0}))
    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
