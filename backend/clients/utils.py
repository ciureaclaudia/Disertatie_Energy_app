import math
import random
from datetime import timedelta
from collections import defaultdict
from .models import Client, EnergyReading

def generate_synthetic_readings_for_client(client, start_date, end_date):
    total_hours = int((end_date - start_date).total_seconds() // 3600)
    readings = []
    current_time = start_date

    # Clear previous readings in range
    EnergyReading.objects.filter(client=client, timestamp__range=(start_date, end_date)).delete()

    for _ in range(total_hours + 1):
        hour = current_time.hour
        day_of_year = current_time.timetuple().tm_yday

        production = 0
        if client.has_production:
            if client.energy_source == 'solar':
                if 7 <= hour <= 19:
                    daylight_factor = math.sin(math.pi * (hour - 7) / 12)

                    if daylight_factor < 0.17:
                        daylight_factor = 0

                    if daylight_factor > 0:
                        seasonal = 1 + 0.4 * math.cos(2 * math.pi * (day_of_year - 172) / 365)
                        production = client.max_production_mwh * daylight_factor * seasonal

                        # ⚠️ Add noise only if there's production!
                        production += random.gauss(0, 0.02 * client.max_production_mwh)
                    else:
                        production = 0
                else:
                    production = 0

            elif client.energy_source == 'wind':
                daily = 0.7 + 0.2 * math.sin(2 * math.pi * hour / 24)
                seasonal = 1 + 0.1 * math.cos(2 * math.pi * (day_of_year - 80) / 365)
                production = client.max_production_mwh * daily * seasonal
            production += random.gauss(0, 0.05 * client.max_production_mwh)

        consumption = 0
        if client.has_consumption:
            pattern = 0.6 + 0.4 * math.sin(math.pi * hour / 24)
            consumption = client.max_consumption_mwh * pattern
            consumption += random.gauss(0, 0.05 * client.max_consumption_mwh)

        readings.append(EnergyReading(
            client=client,
            timestamp=current_time,
            production_real=max(0, round(production, 2)),
            consumption_real=max(0, round(consumption, 2))
        ))

        current_time += timedelta(hours=1)

    EnergyReading.objects.bulk_create(readings)
    return len(readings)


# def generate_synthetic_readings(start_date, end_date):
#     total_hours = int((end_date - start_date).total_seconds() // 3600)
#
#     for client in Client.objects.all():
#         readings = []
#         current_time = start_date
#
#         for _ in range(total_hours + 1):
#             hour = current_time.hour
#             day_of_year = current_time.timetuple().tm_yday
#
#             # --------- PRODUCTION -----------
#             production = 0
#             if client.has_production:
#                 if client.energy_source == 'solar':
#                     daily_solar = max(0, math.sin(math.pi * (hour - 6) / 12))
#                     seasonal_solar = 1 + 0.4 * math.cos(2 * math.pi * (day_of_year - 172) / 365)
#                     production = client.max_production_mwh * daily_solar * seasonal_solar
#                 elif client.energy_source == 'wind':
#                     wind_daily = 0.7 + 0.2 * math.sin(2 * math.pi * hour / 24)
#                     wind_season = 1 + 0.1 * math.cos(2 * math.pi * (day_of_year - 80) / 365)
#                     production = client.max_production_mwh * wind_daily * wind_season
#                 production += random.gauss(0, 0.05 * client.max_production_mwh)
#
#             # --------- CONSUMPTION ----------
#             consumption = 0
#             if client.has_consumption:
#                 base_consumption = 0.6 + 0.4 * math.sin(math.pi * hour / 24)
#                 consumption = client.max_consumption_mwh * base_consumption
#                 consumption += random.gauss(0, 0.05 * client.max_consumption_mwh)
#
#             # Clamp and round
#             production = max(0, round(production, 2))
#             consumption = max(0, round(consumption, 2))
#
#             readings.append(EnergyReading(
#                 client=client,
#                 timestamp=current_time,
#                 production_mwh=production,
#                 consumption_mwh=consumption,
#             ))
#
#             current_time += timedelta(hours=1)
#
#         EnergyReading.objects.bulk_create(readings)

