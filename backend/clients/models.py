from django.db import models

# ASTEA SUNT TABELELE MELE
# ORICE MODIFCARE AICI : run in terminal: makemigrations+migrate

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    lat = models.FloatField()
    long = models.FloatField()
    energy_source  = models.CharField(max_length=20,
                                 choices=[('solar', 'Solar'), ('wind', 'Wind')])
    max_consumption_mwh = models.FloatField(default=0.0)
    max_production_mwh = models.FloatField(default=0.0)
    has_consumption = models.BooleanField(default=True)
    has_production = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class EnergyReading(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField()
    consumption_real = models.FloatField(default=0.0)
    consumption_forecast = models.FloatField(default=0.0)
    production_real = models.FloatField(default=0.0)
    production_forecast = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.client.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"