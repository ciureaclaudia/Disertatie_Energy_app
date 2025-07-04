from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, EnergyReadingViewSet, GenerateSyntheticDataView, DeleteClientReadingsView, PretDezechilibruViewSet, GenerateSyntheticPriceDezechilibruView

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'readings', EnergyReadingViewSet, basename='reading')
router.register(r'preturi-dezechilibru', PretDezechilibruViewSet, basename='preturi-dezechilibru')

urlpatterns = [
    path('', include(router.urls)),

    # Path special pentru readings filtrate pe client
    path('clients/<int:client_id>/readings/', EnergyReadingViewSet.as_view({'get': 'list'}), name='reading-list'),
    
    # Extra (non-ViewSet) endpoints
    path('clients/<int:pk>/generate_data/', GenerateSyntheticDataView.as_view(), name='generate-data'),
    path('clients/<int:pk>/delete_readings/', DeleteClientReadingsView.as_view(), name='delete-readings'),
    # path('clients/today-consumption/', TodayConsumptionView.as_view(), name="today-consumption"),

    path('generare_pret_dezechilibru/', GenerateSyntheticPriceDezechilibruView.as_view(), name='generare-pret-dezechilibru'),

   
]







# from django.urls import path
# from .views import ClientViewSet, EnergyReadingViewSet, GenerateSyntheticDataView, DeleteClientReadingsView

# client_list = ClientViewSet.as_view({
#     'get': 'list',
#     'post': 'create',
# })

# client_detail = ClientViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy',
# })

# reading_list = EnergyReadingViewSet.as_view({
#     'get': 'list',
#     'post': 'create',
# })

# reading_detail = EnergyReadingViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy',
# })

# urlpatterns = [
#     path('clients/', client_list, name='client-list'),
#     path('clients/<int:pk>/', client_detail, name='client-detail'),

#     # Readings list + detail
#     path('clients/<int:client_id>/readings/', reading_list, name='reading-list'),

#     # Synthetic data generator
#     path('clients/<int:pk>/generate_data/', GenerateSyntheticDataView.as_view(), name='generate-data'),

#     # Clean delete route
#     path('clients/<int:pk>/delete_readings/', DeleteClientReadingsView.as_view(), name='delete-readings'),
# ]
