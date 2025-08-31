from django.urls import path
from .views import FuelRouteView

app_name = 'fuel_route'

urlpatterns = [
    path('route/', FuelRouteView.as_view(), name='fuel_route'),
]