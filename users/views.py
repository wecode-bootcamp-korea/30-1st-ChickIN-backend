import json, bcrypt, jwt

from django.http  import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError

from users.models     import User
from users.validators import validate_email, validate_password
from my_settings      import SECRET_KEY, ALGORITHM

class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            username        = data.get('username')
            email           = data.get('email')
            password        = data.get('password')
            phone_number    = data.get('phone_number')
            address         = data.get('address')
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            if validate_email(email)==None:
                return JsonResponse({'messasge':'INVALID EMAIL'}, status=400) 
            if validate_password(password)==None:
                return JsonResponse({'messasge':'INVALID PASSWORD'}, status=400) 
            if User.objects.filter(email = email).exists():
                return JsonResponse({'messasge':'E-MAIL ALREADY EXISTED'}, status=400)

            User.objects.create(
                username     = username,
                email        = email,
                password     = hashed_password,
                phone_number = phone_number,
                address      = address,
                point        = 100000,
            )
            return JsonResponse({'message':'SUCCESS'}, status=201) 
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'},status=400) 
        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status = 400)

class LogInView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            email           = data['email']
            password        = data['password']
            user            = User.objects.get(email = email)
            hashed_password = user.password.encode('utf-8')
            access_token    = jwt.encode({'user.id':user.id}, SECRET_KEY, ALGORITHM)

            if not User.objects.filter(email = email).exists():
                return JsonResponse({'message' : 'INVALID_USER'},status=401)

            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                
                success_message = {
                    'SUCCESS' : {
                        'E-MAIL':email,
                        'ACCESS_TOKEN':access_token,
                    }
                }
            return JsonResponse(success_message, status=200)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message':'DOES NOT EXIST USER'}, status = 400)