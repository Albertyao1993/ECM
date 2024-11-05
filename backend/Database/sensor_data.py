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
    person_count: int = 0
    
    # OpenWeather 数据字段
    ow_temperature: float = 0.0
    ow_humidity: float = 0.0
    ow_weather_desc: str = ""
    ow_dewpoint: float = 0.0
    ow_wind_speed: float = 0.0
    ow_wind_direction: float = 0.0
    ow_precipitation: float = 0.0
    ow_sun_duration: float = 0.0

    def to_dict(self):
        data = asdict(self)
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].replace(tzinfo=None)
        return data
