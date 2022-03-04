import re

def validate_email(email):
    return re.match('\w+@\w+\.\w', email)

def validate_password(password):
    return re.match('(?=.*[a-zA-Z])(?=.*\d)(?=.*[?!@#$%^&*-]).{8,}', password)