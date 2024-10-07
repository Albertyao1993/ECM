from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class LEDStatus:
    timestamp: datetime
    status: str
    duration: float

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            timestamp=data['timestamp'],
            status=data['status'],
            duration=data['duration']
        )