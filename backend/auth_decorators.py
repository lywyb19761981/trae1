from flask import request, jsonify
import jwt
from functools import wraps

# 配置
SECRET_KEY = 'your-secret-key-change-in-production'

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """需要令牌的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '访问令牌缺失'}), 401
        
        try:
            token = token.split(' ')[1]  # 移除 'Bearer ' 前缀
            payload = verify_token(token)
            if not payload:
                return jsonify({'error': '无效的访问令牌'}), 403
            
            request.current_user = payload
        except:
            return jsonify({'error': '无效的访问令牌'}), 403
        
        return f(*args, **kwargs)
    return decorated