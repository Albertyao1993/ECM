import datetime
from dataclasses import dataclass, asdict

@dataclass
class SensorData():

    temperature: float
    humidity: float
    timestamp: datetime
    person_count: int = 0

    def to_dict(self):
        return asdict(self)