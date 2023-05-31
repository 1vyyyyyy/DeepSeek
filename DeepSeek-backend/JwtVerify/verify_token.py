import jwt

JWT_SALT = '254ac4523be56a1a724c4cd50437cfe343f0b4403d1c5a4def8ee8ce3259b9ad'


def verify_token(payload, timeout=20):
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    result = jwt.decode(jwt=payload, key=JWT_SALT, algorithms=["HS256"], headers=headers)
    return result

