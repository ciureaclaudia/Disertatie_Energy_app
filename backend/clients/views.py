from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.views import APIView
from datetime import datetime
from .models import Client,EnergyReading
from .serializers import ClientSerializer,EnergyReadingSerializer
from .utils import generate_synthetic_readings_for_client, redistribute_energy
from rest_framework.decorators import action
from django.utils.timezone import make_aware, timedelta
import pandas as pd
import pytz



# in a view= This is where we gather the information we need to send back a proper response.
# Django views are Python functions that take http requests and return http response, like HTML documents
# Views use utils — not the other way around
# the views are endpoints 


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class EnergyReadingViewSet(viewsets.ModelViewSet):
    queryset = EnergyReading.objects.all()
    serializer_class = EnergyReadingSerializer

    def get_queryset(self):
        client_id = self.kwargs.get('client_id')
        if client_id is not None:
            return self.queryset.filter(client__id=client_id)
        return self.queryset.none()  # or raise error if you want to restrict access
    
    @action(detail=False, methods=['get'], url_path='today-consumption')
    def today_consumption(self, request):
        today = datetime.now().date()
        readings = EnergyReading.objects.filter(timestamp__date=today)


        result = [
            {
                "timestamp": reading.timestamp.isoformat(),
                "consumption_real": reading.consumption_real,
                "energy_source": reading.client.energy_source,
            }
            for reading in readings
        ]

        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='today-production')
    def today_production(self, request):
        today = datetime.now().date()
        readings = EnergyReading.objects.filter(timestamp__date=today)

        result = [
            {
                "timestamp": reading.timestamp.isoformat(),
                "production_real": reading.production_real,
                "energy_source": reading.client.energy_source,
            }
            for reading in readings
        ]

        return Response(result)
    
# interactiune cu gridul, macheta pt maine pt fiecare client
    @action(detail=False, methods=['get'], url_path='forecast-diff-tomorrow-hourly')
    def forecast_diff_tomorrow_hourly(self, request):
        tomorrow = datetime.now().date() + timedelta(days=1)
        readings = EnergyReading.objects.filter(timestamp__date=tomorrow)

        hourly_data_by_client = {}

        for reading in readings:
            client = reading.client
            hour = reading.timestamp.strftime("%H:%M")

            if client.id not in hourly_data_by_client:
                hourly_data_by_client[client.id] = {
                    "client": client.name,
                    "client_id": client.id,
                    "date": tomorrow.strftime("%Y-%m-%d"),
                    "hourly": []
                }

            prod = reading.production_forecast or 0
            cons = reading.consumption_forecast or 0
            diff = round(cons - prod, 2)

            hourly_data_by_client[client.id]["hourly"].append({
                "hour": hour,
                "difference": diff
            })

        return Response(list(hourly_data_by_client.values()))

#  preiau datele de consum si prod real si forecast de cu o ora inainte
    @action(detail=False, methods=['get'], url_path='last-hour-data')
    def last_hour_data(self, request):
        tz = pytz.timezone("Europe/Bucharest")
        now = datetime.now(tz)
        previous_hour = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        next_hour = previous_hour + timedelta(hours=1)

        readings = EnergyReading.objects.filter(timestamp__gte=previous_hour, timestamp__lt=next_hour)

        # result este o listă de dicționare , unde fiecare dicționar conține informațiile 
        # extrase dintr-un obiect EnergyReading  -> list comprehensions
        result = [
            {
                "timestamp": reading.timestamp.isoformat(),
                "client_id": reading.client.id,
                "client": reading.client.name,
                "consumption_real": reading.consumption_real,
                "production_real": reading.production_real,
                "consumption_forecast":reading.consumption_forecast,
                "production_forecast":reading.production_forecast
            }
            for reading in readings
        ]

        return Response(result)

    @action(detail=False, methods=['post'], url_path='redistribute-energy')
    def redistribute_energy_api(self, request):
        try:
            data = request.data
            if not isinstance(data, list):
                return Response({"error": "Expected a list of client data"}, status=status.HTTP_400_BAD_REQUEST)

            df = pd.DataFrame(data)

            if "Client" not in df.columns or "Cantitate Energie" not in df.columns or "Status" not in df.columns:
                return Response({"error": "Missing required columns: 'Client', 'Cantitate Energie', 'Status'"}, status=status.HTTP_400_BAD_REQUEST)

            transfers, excedent_final, deficit_final = redistribute_energy(df)

            return Response({
                "transfers": transfers,
                "excedent": excedent_final.to_dict(orient="records"),
                "deficit": deficit_final.to_dict(orient="records"),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

class GenerateSyntheticDataView(APIView):
    def post(self, request, pk):
        ROMANIA_TZ = pytz.timezone("Europe/Bucharest")

        start_raw = request.data.get('start_date')
        end_raw = request.data.get('end_date')

        if not start_raw or not end_raw:
            return Response({"error": "start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_dt = datetime.fromisoformat(start_raw)
            end_dt = datetime.fromisoformat(end_raw)

            start_dt = ROMANIA_TZ.localize(start_dt)
            end_dt = ROMANIA_TZ.localize(end_dt)

        except ValueError:
            return Response({"error": "Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM"}, status=status.HTTP_400_BAD_REQUEST)

        if start_dt >= end_dt:
            return Response({"error": "start_date must be before end_date."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        # Call the generator only for this client
        stats = generate_synthetic_readings_for_client(client, start_dt, end_dt)

        return Response({
            "message": f"Synthetic data generated for client '{client.name}'.",
            "readings_added": stats
        }, status=status.HTTP_201_CREATED)


class DeleteClientReadingsView(APIView):
    def delete(self, request, pk):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        # Optional filtering by date
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        readings = EnergyReading.objects.filter(client=client)

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                readings = readings.filter(timestamp__gte=start_dt)
            except ValueError:
                return Response({"error": "Invalid start_date format. Use ISO format: YYYY-MM-DDTHH:MM"}, status=status.HTTP_400_BAD_REQUEST)

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                readings = readings.filter(timestamp__lte=end_dt)
            except ValueError:
                return Response({"error": "Invalid end_date format. Use ISO format: YYYY-MM-DDTHH:MM"}, status=status.HTTP_400_BAD_REQUEST)

        count = readings.count()
        readings.delete()

        return Response({
            "message": f"Deleted {count} readings for client '{client.name}'."
        }, status=status.HTTP_200_OK)


# class TodayConsumptionView(APIView):
#     def get(self, request):
#         today = datetime.now().date()
#         readings = EnergyReading.objects.filter(timestamp__date=today)

#         consumption_by_client = {}

#         for reading in readings:
#             client_name = reading.client.name
#             consumption_by_client[client_name] = consumption_by_client.get(client_name, 0) + reading.consumption_real

#         result = [
#             {"client": name, "consumption_real": round(value, 2)}
#             for name, value in consumption_by_client.items()
#         ]

#         return Response(result, status=status.HTTP_200_OK)
