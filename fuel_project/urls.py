"""
fuel_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def api_info(request):
    """Basic API info endpoint"""
    return JsonResponse({
        'message': 'Fuel Route Optimization API',
        'version': '1.0',
        'endpoints': {
            'route': '/api/route/ (POST)'
        }
    })

@csrf_exempt
def fuel_route_view(request):
    """Direct import to avoid circular imports"""
    from fuel_route.views import FuelRouteView
    from rest_framework.test import APIRequestFactory
    from rest_framework.request import Request
    
    # Convert Django request to DRF request
    factory = APIRequestFactory()
    drf_request = factory.post('/api/route/', request.body, content_type=request.content_type)
    drf_request = Request(drf_request)
    drf_request.user = request.user
    
    view = FuelRouteView()
    return view.post(drf_request)

@csrf_exempt
def simple_route_view(request):
    """Simple route endpoint without DRF to test CSRF"""
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            return JsonResponse({
                'status': 'success',
                'message': 'Simple route endpoint working!',
                'received_data': data,
                'method': request.method
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method allowed'
        }, status=405)

@csrf_exempt
def test_api_view(request):
    """Simple test endpoint to verify API is working"""
    return JsonResponse({
        'status': 'success',
        'message': 'API is working!',
        'method': request.method,
        'path': request.path
    })

@csrf_exempt
def test_post_view(request):
    """Test POST endpoint to verify CSRF is disabled"""
    if request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': 'POST request working!',
            'method': request.method,
            'path': request.path
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method allowed'
        }, status=405)

@csrf_exempt
def debug_view(request):
    """Debug endpoint to check database and basic functionality"""
    try:
        from fuel_route.models import FuelStation
        
        # Check database
        station_count = FuelStation.objects.count()
        
        # Check if we can import the view
        from fuel_route.views import FuelRouteView
        view = FuelRouteView()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Debug info',
            'database': {
                'fuel_stations_count': station_count,
                'database_working': True
            },
            'views': {
                'FuelRouteView_imported': True,
                'view_created': True
            },
            'environment': {
                'debug': DEBUG,
                'allowed_hosts': ALLOWED_HOSTS
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Debug failed: {str(e)}',
            'error_type': type(e).__name__
        }, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/route/', fuel_route_view, name='fuel_route'),
    path('api/simple-route/', simple_route_view, name='simple_route'),
    path('api/test/', test_api_view, name='test_api'),
    path('api/test-post/', test_post_view, name='test_post'),
    path('api/debug/', debug_view, name='debug'),
    path('', api_info, name='api_info'),
]