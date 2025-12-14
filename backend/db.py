from pymongo import MongoClient

class MongoDB:
    def __init__(self, uri='mongodb://localhost:27017/', db_name='diet_optimizer'):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def insert_result(self, result):
        return self.db.results.insert_one(result)

    def get_results(self, query=None):
        if query is None:
            query = {}
        return list(self.db.results.find(query))

    def close(self):
        self.client.close()
