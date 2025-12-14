from pymongo import MongoClient
import os

class MongoDB:
    def __init__(self, uri=None, db_name='diet_optimizer'):
        if uri is None:
            uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def insert_result(self, result):
        return self.db.results.insert_one(result)

    def get_results(self, query=None):
        if query is None:
            query = {}
        return list(self.db.results.find(query, {'_id': 0}))

    def close(self):
        self.client.close()
