from functools import wraps
from flask import request, jsonify
from firebase_admin import auth


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or 'Bearer ' not in auth_header:
            return jsonify({'message': 'Missing or invalid token'}), 401

        token = auth_header.split('Bearer ')[1]
        try:
            decoded_token = auth.verify_id_token(token)
            request.uid = decoded_token['uid']
        except Exception as e:
            return jsonify({'message': 'Invalid or expired token'}), 401

        return f(*args, **kwargs)
    return decorated_function