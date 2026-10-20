import datetime
from django.utils import timezone
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Unified exception handler transforming DRF exceptions into standard error envelopes:
    {
      "success": false,
      "error": {
        "code": "...",
        "message": "...",
        "details": ...
      },
      "timestamp": "..."
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_code = 'VALIDATION_ERROR'
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_code = 'AUTHENTICATION_REQUIRED'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_code = 'PERMISSION_DENIED'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_code = 'NOT_FOUND'
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_code = 'RATE_LIMIT_EXCEEDED'
        elif response.status_code == status.HTTP_409_CONFLICT:
            error_code = 'CONFLICT'

        message = 'An error occurred while processing your request.'
        details = response.data

        if isinstance(response.data, dict):
            if 'detail' in response.data:
                message = str(response.data['detail'])
                details = None
            elif 'error' in response.data and isinstance(response.data['error'], dict):
                error_code = response.data['error'].get('code', error_code)
                message = response.data['error'].get('message', message)
                details = response.data['error'].get('details', None)

        response.data = {
            'success': False,
            'error': {
                'code': error_code,
                'message': message,
                'details': details,
            },
            'timestamp': timezone.now().isoformat(),
        }
    return response
