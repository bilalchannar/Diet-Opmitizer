from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from datetime import datetime
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
    food = request.json
    db['foods'].insert_one(food)
    return jsonify({'status': 'success'})

@app.route('/foods/<name>', methods=['DELETE'])
def delete_food(name):
    db['foods'].delete_one({'name': name})
    return jsonify({'status': 'deleted'})

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json or {}

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
    return jsonify(result_doc)          # return it to frontend too

@app.route('/results', methods=['GET'])
def get_results():
    results = list(db.results.find({}, {'_id': 0}))
    return jsonify(results)




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)