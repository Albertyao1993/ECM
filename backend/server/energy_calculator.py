from datetime import datetime

class EnergyCalculator:
    def __init__(self, led_power_watts=10):  # 假设LED功率为10瓦
        self.led_power_watts = led_power_watts

    def calculate_energy_consumption(self, duration_seconds):
        # 将秒转换为小时
        duration_hours = duration_seconds / 3600
        # 计算千瓦时 (kWh)
        energy_kwh = (self.led_power_watts * duration_hours) / 1000
        return energy_kwh

    def calculate_cost(self, energy_kwh, price_per_kwh=0.5):  # 假设电价为0.5元/kWh
        return energy_kwh * price_per_kwh