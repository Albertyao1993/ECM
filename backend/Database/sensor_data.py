from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SensorData:
    temperature: float
    humidity: float
    light: float
    timestamp: datetime
    light_status: str = "OFF"
    ac_status: str = "OFF"
    sound_state: int = 0
    ow_temperature: float = 0.0
    ow_humidity: float = 0.0
    ow_weather_desc: str = ""
    person_count: int = 0

    def to_dict(self):
        data = asdict(self)
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].replace(tzinfo=None)
        return data
