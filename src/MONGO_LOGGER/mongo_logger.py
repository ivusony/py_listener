from pymongo import MongoClient
import json
import time


config = open("./mongo.config.json")


class Mongo_logger:
    def __init__(self, cluster):
        self.is_cluster = cluster
        self.mongo_url = None
        self.is_connected_to_mongo = False
        self.connection = False
        self.db = False
        self.collection = False

        if self.is_cluster:
            self.mongo_url = json.load(config)["cluster"]
        else:
            self.mongo_url = json.load(config)["harpia"]
    
    def cluster(self):
        return self.is_cluster

    def connect(self):
        try:
            self.connection = MongoClient(self.mongo_url)
            if self.is_cluster:
                print('Connected to mongo on cluster')
            else:
                print('Connected to  mongo')
            self.is_connected_to_mongo = True
            self.db = self.connection["db_name"]
            self.collection = self.db["_listener_logs"]
        except Exception:
            self.is_connected_to_mongo = False
    
    def log(self, data_size, imei, operation ):
        payload = { "timestamp" : int(time.time()), "imei" : imei, "size" : data_size, "operation" : operation}
        self.collection.insert_one( payload )