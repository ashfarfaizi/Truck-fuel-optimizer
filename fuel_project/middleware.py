from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class CSRFExemptMiddleware(MiddlewareMixin):
    """Middleware to exempt API endpoints from CSRF protection"""
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check if the request is for an API endpoint
        if request.path.startswith('/api/'):
            # Completely disable CSRF for API endpoints
            setattr(request, '_dont_enforce_csrf_checks', True)
            setattr(view_func, 'csrf_exempt', True)
            # Also disable CSRF middleware for this request
            request.META['CSRF_COOKIE'] = None
        return None
