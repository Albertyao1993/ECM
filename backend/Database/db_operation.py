import datetime
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timezone
from bson.codec_options import CodecOptions
from Database.led_status import LEDStatus
from server.energy_calculator import EnergyCalculator

class Database:
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        # 使用 CodecOptions 来确保时间戳被视为本地时间
        self.collection = self.db.get_collection(
            collection_name,
            codec_options=CodecOptions(tz_aware=False)
        )
        
        # 创建 LED 状态集合
        self.led_collection = self.db.get_collection(
            'led_status',
            codec_options=CodecOptions(tz_aware=False)
        )

        # 确保 led_status 集合存在
        if 'led_status' not in self.db.list_collection_names():
            self.db.create_collection('led_status')
            print("创建了 led_status 集合")
        else:
            print("led_status 集合已存在")

        # 创建能源消耗集合
        self.energy_collection = self.db.get_collection(
            'energy_consumption',
            codec_options=CodecOptions(tz_aware=False)
        )
        self.energy_calculator = EnergyCalculator()

    def create(self, data):
        """插入一条新记录"""
        # 确保时间戳是 naive datetime（无时区信息）
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].replace(tzinfo=None)
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
        # return list(self.collection.find())
        return list(self.collection.find({}, {'_id': False}))
    
    def read_by_time_range(self, start_time, end_time):
        """根据时间范围读取记录"""
        query = {"timestamp": {"$gte": start_time, "$lte": end_time}}
        print(f"Executing query: {query}")  # 添加这行日志
        records = list(self.collection.find(query, {'_id': False}))
        print(f"Found {len(records)} records")  # 添加这行日志
        
        # 将 datetime 对象转换为字符串，便于 JSON 序列化
        for record in records:
            if isinstance(record.get('timestamp'), datetime):
                record['timestamp'] = record['timestamp'].isoformat()
        
        return records

    def read_latest(self):
        """读取最新的一条记录"""
        try:
            latest_record = self.collection.find_one({}, sort=[("timestamp", -1)], projection={'_id': False})
            if latest_record and isinstance(latest_record.get('timestamp'), datetime):
                latest_record['timestamp'] = latest_record['timestamp'].isoformat()
            return latest_record
        except Exception as e:
            print(f"Error reading latest record: {e}")
            return None

    def create_led_status(self, status_data):
        """在LED状态集合中插入新记录"""
        try:
            result = self.led_collection.insert_one(status_data)
            print(f"插入LED状态记录: {status_data}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"插入LED状态记录时发生错误: {e}")
            return None

    def get_led_stats(self):
        """获取LED使用统计信息"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_on_time': {'$sum': '$duration'},
                    'on_count': {'$sum': {'$cond': [{'$eq': ['$status', 'ON']}, 1, 0]}}
                }
            }
        ]
        result = list(self.led_collection.aggregate(pipeline))
        if result:
            stats = result[0]
            return {
                'total_on_time': stats.get('total_on_time', 0),
                'on_count': stats.get('on_count', 0)
            }
        return {'total_on_time': 0, 'on_count': 0}

    def get_led_status_history(self, limit=10):
        """获取最近的LED状态历史"""
        cursor = self.led_collection.find().sort('timestamp', -1).limit(limit)
        return [LEDStatus.from_dict(doc) for doc in cursor]

    def create_energy_consumption(self, energy_data):
        """在能源消耗集合中插入新记录"""
        result = self.energy_collection.insert_one(energy_data)
        return str(result.inserted_id)

    def get_energy_stats(self):
        """获取能源消耗统计信息"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_energy': {'$sum': '$energy_kwh'},
                    'total_cost': {'$sum': '$cost'}
                }
            }
        ]
        result = list(self.energy_collection.aggregate(pipeline))
        if result:
            stats = result[0]
            return {
                'total_energy': stats.get('total_energy', 0),
                'total_cost': stats.get('total_cost', 0)
            }
        return {'total_energy': 0, 'total_cost': 0}

    def update_energy_consumption(self, led_status):
        energy_kwh = self.energy_calculator.calculate_energy_consumption(led_status.duration)
        cost = self.energy_calculator.calculate_cost(energy_kwh)
        energy_data = {
            'timestamp': led_status.timestamp,
            'duration': led_status.duration,
            'energy_kwh': energy_kwh,
            'cost': cost
        }
        self.create_energy_consumption(energy_data)