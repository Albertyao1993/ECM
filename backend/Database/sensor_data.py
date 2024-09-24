from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SensorData():
    temperature: float
    humidity: float
    light: float
    timestamp: datetime 

    ow_temperature: float = 0.0  
    ow_humidity: float = 0.0

    ow_weather_desc: str = ""

    person_count: int = 0

    def to_dict(self):
      
        data = asdict(self)
        
        return data

