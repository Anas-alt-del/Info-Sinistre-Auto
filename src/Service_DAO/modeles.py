
# classe principale :
#   - Incident
# classes secondaires :
#   - Localisation
#   - MeteoHourly
#   - MeteoDaily

class Incident:
    def __init__(self, id_reclamation, date, heure, localisation, meteo_hourly, meteo_daily, zone_degel, id_incident=None):
        self.id_incident = id_incident
        self.id_reclamation = id_reclamation
        self.date = date
        self.heure = heure
        self.localisation = localisation
        self.meteo_hourly = meteo_hourly
        self.meteo_daily = meteo_daily
        self.zone_degel = zone_degel

    def to_dict(self):
        return {
            "id_incident": self.id_incident,
            "id_reclamation": self.id_reclamation,
            "date": self.date,
            "heure": self.heure,
            "localisation": self.localisation.to_dict(),
            "meteo_hourly": self.meteo_hourly.to_dict(),
            "meteo_daily": self.meteo_daily.to_dict(),
            "zone_degel": self.zone_degel
        }

class Localisation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        }

class MeteoHourly:
    def __init__(self, temperature, rain, snow, cloud, wind_speed, wind_direction, weather_code):
        self.temperature = temperature
        self.rain = rain
        self.snow = snow
        self.cloud = cloud
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.weather_code = weather_code

    def to_dict(self):
        return {
            "temperature": self.temperature,
            "rain": self.rain,
            "snow": self.snow,
            "cloud": self.cloud,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "weather_code": self.weather_code
        }

class MeteoDaily:
    def __init__(self, temperature_min_24h, temperature_max_24h, rain_24h, snow_24h, sunrise, sunset):
        self.temperature_min_24h = temperature_min_24h
        self.temperature_max_24h = temperature_max_24h
        self.rain_24h = rain_24h
        self.snow_24h = snow_24h
        self.sunrise = sunrise
        self.sunset = sunset

    def to_dict(self):
        return {
            "temperature_min_24h": self.temperature_min_24h,
            "temperature_max_24h": self.temperature_max_24h,
            "rain_24h": self.rain_24h,
            "snow_24h": self.snow_24h,
            "sunrise": self.sunrise,
            "sunset": self.sunset
        }

