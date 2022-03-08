import json, bcrypt, jwt

from django.http  import JsonResponse
from django.views import View

from users.models     import User
from users.validators import validate_email, validate_password
from my_settings      import SECRET_KEY, ALGORITHM

class SignUpView(View):
    def post(self, request):
        DEFAULT_POINT = 100000
        
        try:
            data = json.loads(request.body)
            username        = data['username']
            email           = data['email']
            password        = data['password']
            phone_number    = data['phone_number']
            address         = data['address']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            if not validate_email(email):
                return JsonResponse({'message':'INVALID EMAIL'}, status=400)
            
            if not validate_password(password):
                return JsonResponse({'message':'INVALID PASSWORD'}, status=400) 
            
            if User.objects.filter(email = email).exists():
                return JsonResponse({'message':'E-MAIL ALREADY EXISTED'}, status=400)

            User.objects.create(
                username     = username,
                email        = email,
                password     = hashed_password,
                phone_number = phone_number,
                address      = address,
                point        = DEFAULT_POINT,
            )
            return JsonResponse({'message':'SUCCESS'}, status=201) 
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'},status=400)

class LogInView(View):
    def post(self, request):
        data = json.loads(request.body)
        try:
            email           = data['email']
            password        = data['password']
            user            = User.objects.get(email = email)
            hashed_password = user.password.encode('utf-8')
            access_token    = jwt.encode({'user_id':user.id}, SECRET_KEY, ALGORITHM)

            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return JsonResponse({'message' : 'INVALID_USER'}, status = 401)
                
            return JsonResponse({'message':'SUCCESS', 'access_token':access_token}, status=200)
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message':'DOES NOT EXIST USER'}, status = 400)