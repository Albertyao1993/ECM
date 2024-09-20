import datetime
from dataclasses import dataclass, asdict

@dataclass
class SensorData():

    temperature: float
    humidity: float
    timestamp: datetime 

    ow_temperture: float = 0.0
    ow_humidity: float = 0.0
    ow_weather_desc: str = ""

    person_count: int = 0


    def to_dict(self):
        return asdict(self)