import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

class Database:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def create(self, data):
        """插入一条新记录"""
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def read(self, query):
        """根据查询条件读取记录"""
        return list(self.collection.find(query))

    def read_by_id(self, record_id):
        """根据ID读取记录"""
        return self.collection.find_one({"_id": ObjectId(record_id)})

    def update(self, record_id, update_data):
        """根据ID更新记录"""
        result = self.collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": update_data}
        )
        return result.modified_count

    def delete(self, record_id):
        """根据ID删除记录"""
        result = self.collection.delete_one({"_id": ObjectId(record_id)})
        return result.deleted_count

    def delete_many(self, query):
        """根据查询条件删除多条记录"""
        result = self.collection.delete_many(query)
        return result.deleted_count

    def read_all(self):
        """读取所有记录"""
        return list(self.collection.find())