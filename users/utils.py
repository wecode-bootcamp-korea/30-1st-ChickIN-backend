import jwt

from django.http  import JsonResponse

from users.models import User
from my_settings  import SECRET_KEY, ALGORITHM

def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        if 'Authorization' not in request.headers:
            return JsonResponse ({'message' : 'UNAUTHORIZED'}, status=401)
        try:
            access_token = request.headers.get('Authorization')
            payload      = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            request.user = User.objects.get(email = payload['email'])
        
        except jwt.DecodeError:
            return JsonResponse({'message': 'INVALID_TOKEN'}, status = 401)
        except User.DoesNotExist:
            return JsonResponse({'message': 'USER_DOES_NOT_EXIST'}, status = 400)
        return func(self, request, *args, **kwargs)   
    return wrapper