from functools import wraps
from flask import request, jsonify
from firebase_admin import auth


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #request.uid = "1"
        #return f(*args, **kwargs)
        auth_header = request.headers.get('Authorization')
        if not auth_header or 'Bearer ' not in auth_header:
            return jsonify({'message': 'Missing or invalid token'}), 401

        token = auth_header.split('Bearer ')[1]
        print(token)
        try:
            #print(token)
            decoded_token = auth.verify_id_token(token)
            #print(decoded_token)
            request.uid = decoded_token['uid']
        except Exception as e:
            return jsonify({'message': 'Invalid or expired token'}), 401

        return f(*args, **kwargs)
    return decorated_function
