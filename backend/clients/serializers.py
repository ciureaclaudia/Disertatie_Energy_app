from rest_framework import serializers
from .models import Client, EnergyReading, PretDezechilibru


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class EnergyReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnergyReading
        fields = '__all__'

class PretDezechilibruSerializer(serializers.ModelSerializer):
    class Meta:
        model = PretDezechilibru
        fields = '__all__'