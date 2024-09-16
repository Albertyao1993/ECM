import datetime
from dataclasses import dataclass, asdict

@dataclass
class SensorData():

    temperature: float
    humidity: float
    timestamp: datetime

    def to_dict(self):
        return asdict(self)