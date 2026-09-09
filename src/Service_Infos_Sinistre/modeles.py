
# classe principale :
#   - Incident
# classes secondaires :
#   - Localisation
#   - MeteoHourly
#   - MeteoDaily

class Localisation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

class MeteoHourly:
    def __init__(self, temperature, rain, snow, cloud, wind_speed, wind_direction, weather):
        self.temperature = temperature
        self.rain = rain
        self.snow = snow
        self.cloud = cloud
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.weather = weather

class MeteoDaily:
    def __init__(self, temperature_min_24h, temperature_max_24h, rain_24h, snow_24h, sunrise, sunset):
        self.temperature_min_24h = temperature_min_24h
        self.temperature_max_24h = temperature_max_24h
        self.rain_24h = rain_24h
        self.snow_24h = snow_24h
        self.sunrise = sunrise
        self.sunset = sunset

class Incident:
    def __init__(self, id_reclamation, date, heure, localisation, meteo_hourly, meteo_daily, zone_degel):
        self.id_reclamation = id_reclamation
        self.date = date
        self.heure = heure
        self.localisation = localisation
        self.meteo_hourly = meteo_hourly
        self.meteo_daily = meteo_daily
        self.zone_degel = zone_degel
