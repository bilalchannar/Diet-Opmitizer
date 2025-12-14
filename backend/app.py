from flask import Flask, request, jsonify
from pymongo import MongoClient
from genetic_algorithm import run_genetic_algorithm

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['diet_optimizer']

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.json
    result = run_genetic_algorithm(data)
    db.results.insert_one(result)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)