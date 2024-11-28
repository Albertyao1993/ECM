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
        # Use CodecOptions to ensure timestamps are treated as local time
        self.collection = self.db.get_collection(
            collection_name,
            codec_options=CodecOptions(tz_aware=False)
        )
        
        # Create LED status collection
        self.led_collection = self.db.get_collection(
            'led_status',
            codec_options=CodecOptions(tz_aware=False)
        )

        # Ensure led_status collection exists
        if 'led_status' not in self.db.list_collection_names():
            self.db.create_collection('led_status')
            print("Created led_status collection")
        else:
            print("led_status collection already exists")

        # Create energy consumption collection
        self.energy_collection = self.db.get_collection(
            'energy_consumption',
            codec_options=CodecOptions(tz_aware=False)
        )

        # Ensure energy_consumption collection exists
        if 'energy_consumption' not in self.db.list_collection_names():
            self.db.create_collection('energy_consumption')
            print("Created energy_consumption collection")
        else:
            print("energy_consumption collection already exists")

        # Create heating predictions collection
        self.heating_predictions = self.db.get_collection(
            'heating_predictions',
            codec_options=CodecOptions(tz_aware=False)
        )

        # Ensure heating_predictions collection exists
        if 'heating_predictions' not in self.db.list_collection_names():
            self.db.create_collection('heating_predictions')
            print("Created heating_predictions collection")
        else:
            print("heating_predictions collection already exists")

        self.energy_calculator = EnergyCalculator()

    def create(self, data):
        """Insert a new record"""
        # Ensure timestamp is naive datetime (no timezone info)
        if 'timestamp' in data and isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].replace(tzinfo=None)
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def read(self, query):
        """Read records based on query"""
        return list(self.collection.find(query))

    def read_by_id(self, record_id):
        """Read a record by ID"""
        return self.collection.find_one({"_id": ObjectId(record_id)})

    def update(self, record_id, update_data):
        """Update a record by ID"""
        result = self.collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": update_data}
        )
        return result.modified_count

    def delete(self, record_id):
        """Delete a record by ID"""
        result = self.collection.delete_one({"_id": ObjectId(record_id)})
        return result.deleted_count

    def delete_many(self, query):
        """Delete multiple records based on query"""
        result = self.collection.delete_many(query)
        return result.deleted_count

    def read_all(self):
        """Read all records"""
        return list(self.collection.find({}, {'_id': False}))
    
    def read_by_time_range(self, start_time, end_time):
        """Read records within a time range"""
        query = {"timestamp": {"$gte": start_time, "$lte": end_time}}
        print(f"Executing query: {query}")  # Add this log
        records = list(self.collection.find(query, {'_id': False}))
        print(f"Found {len(records)} records")  # Add this log
        
        # Convert datetime objects to strings for JSON serialization
        for record in records:
            if isinstance(record.get('timestamp'), datetime):
                record['timestamp'] = record['timestamp'].isoformat()
        
        return records

    def read_latest(self):
        """Read the latest record"""
        try:
            latest_record = self.collection.find_one({}, sort=[("timestamp", -1)], projection={'_id': False})
            if latest_record and isinstance(latest_record.get('timestamp'), datetime):
                latest_record['timestamp'] = latest_record['timestamp'].isoformat()
            return latest_record
        except Exception as e:
            print(f"Error reading latest record: {e}")
            return None

    def create_led_status(self, status_data):
        """Insert a new record in the LED status collection"""
        try:
            result = self.led_collection.insert_one(status_data)
            print(f"Inserted LED status record: {status_data}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting LED status record: {e}")
            return None

    def get_led_stats(self):
        """Get LED usage statistics"""
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
        """Get recent LED status history"""
        cursor = self.led_collection.find().sort('timestamp', -1).limit(limit)
        return [LEDStatus.from_dict(doc) for doc in cursor]

    def create_energy_consumption(self, energy_data):
        """Insert a new record in the energy consumption collection"""
        result = self.energy_collection.insert_one(energy_data)
        return str(result.inserted_id)

    def get_energy_stats(self):
        """Get energy consumption statistics"""
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

    def create_heating_prediction(self, prediction_data):
        """存储供暖预测记录，包含实际值字段"""
        try:
            # 确保时间戳没有时区信息
            if 'timestamp' in prediction_data and isinstance(prediction_data['timestamp'], datetime):
                prediction_data['timestamp'] = prediction_data['timestamp'].replace(tzinfo=None)
            
            # 添加 actual_value 字段，默认值为 0
            prediction_data['actual_value'] = 0
            
            result = self.heating_predictions.insert_one(prediction_data)
            print(f"Inserted heating prediction record: {prediction_data}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting heating prediction record: {e}")
            return None

    def update_prediction_actual_value(self, timestamp, actual_value):
        """更新预测记录的实际值"""
        try:
            # 查找最接近给定时间戳的预测记录并更新实际值
            result = self.heating_predictions.update_one(
                {"timestamp": {"$lte": timestamp}},
                {"$set": {"actual_value": actual_value}},
                sort=[("timestamp", -1)]
            )
            return result.modified_count
        except Exception as e:
            print(f"Error updating actual value: {e}")
            return 0

    def get_recent_predictions(self, limit=24):
        """获取最近的预测记录，包含实际值"""
        try:
            cursor = self.heating_predictions.find(
                {},
                {'_id': 0}  # 不返回 _id 字段
            ).sort('timestamp', -1).limit(limit)
            
            predictions = list(cursor)
            # 转换时间戳为 ISO 格式字符串
            for pred in predictions:
                if isinstance(pred.get('timestamp'), datetime):
                    pred['timestamp'] = pred['timestamp'].isoformat()
            return predictions
        except Exception as e:
            print(f"Error getting recent predictions: {e}")
            return []