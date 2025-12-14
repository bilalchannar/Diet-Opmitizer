from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
from genetic_algorithm import run_genetic_algorithm

app = Flask(__name__)
CORS(app)

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['diet_optimizer']

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    result = run_genetic_algorithm(data)
    # Insert result, but do not return ObjectId
    db.results.insert_one(dict(result))
    # Only return serializable result
    return jsonify(result)

@app.route('/results', methods=['GET'])
def get_results():
    results = list(db.results.find({}, {'_id': 0}))
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=False)