import configparser
from flask import request, jsonify, session
from functools import wraps

class ApiKeyManager:
    def __init__(self, config_path='config.ini'):
        config = configparser.ConfigParser()
        config.read(config_path)
        keys = config['OIDC'].get('valid_api_keys', '')
        self.valid_keys = [k.strip() for k in keys.split(',') if k.strip()]

    def require_api_key(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('x-api-key')
            if not api_key or api_key not in self.valid_keys:
                return jsonify({'error': 'Unauthorized'}), 401
            return func(*args, **kwargs)
        return wrapper

    def require_auth_or_api_key(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_key = request.headers.get('x-api-key')
            user_authenticated = 'user' in session
            if user_authenticated or (api_key and api_key in self.valid_keys):
                return func(*args, **kwargs)
            return jsonify({'error': 'Unauthorized'}), 401
        return wrapper
