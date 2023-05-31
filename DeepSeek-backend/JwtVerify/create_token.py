import datetime
import json
import jwt


JWT_SALT = '254ac4523be56a1a724c4cd50437cfe343f0b4403d1c5a4def8ee8ce3259b9ad'


def create_token(payload, timeout=20):
    """
    :param payload:  例如：{'username': "admin",'password':'12345678'}用户信息
    :param timeout: token的过期时间，默认20分钟
    :return:
    """
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    payload = json.loads(payload)
    payload['status'] = True
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)
    result = jwt.encode(payload=payload, key=JWT_SALT, algorithm="HS256", headers=headers)
    return result
