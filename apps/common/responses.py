from django.http import JsonResponse


def success_response(data=None, message='success', status=200):
    return JsonResponse({
        'success': True,
        'message': message,
        'data': data or {},
    }, status=status)


def error_response(message='Something went wrong', errors=None, status=400):
    return JsonResponse({
        'success': False,
        'message': message,
        'errors': errors or {},
    }, status=status)
