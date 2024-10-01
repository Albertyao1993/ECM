from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['sensor_data']
collection = db['readings']

for doc in collection.find():
    timestamp_str = doc['timestamp']
    if isinstance(timestamp_str, str):
        try:
            # 根据存储的格式解析时间字符串
            timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'timestamp': timestamp_dt}}
            )
        except ValueError as e:
            print(f"Error parsing timestamp for document {doc['_id']}: {e}")
