from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from auth_decorators import token_required

app = Flask(__name__)
CORS(app)

# 配置
SECRET_KEY = 'your-secret-key-change-in-production'
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'users.db')

# 确保数据库目录存在
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """加密密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id, username):
    """创建JWT令牌"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# 路由
@app.route('/')
def index():
    """返回前端页面"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    # 如果是API路由，跳过
    if filename.startswith('api/'):
        return jsonify({'error': 'API路由不存在'}), 404
    
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    try:
        return send_from_directory(frontend_path, filename)
    except:
        return jsonify({'error': '文件不存在'}), 404

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({'status': 'OK', 'message': '服务器运行正常'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'detail': '用户名、邮箱和密码都是必填项'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    
    if len(password) < 6:
        return jsonify({'detail': '密码长度至少为6位'}), 400
    
    conn = get_db_connection()
    
    # 检查用户是否已存在
    existing_user = conn.execute(
        'SELECT * FROM users WHERE username = ? OR email = ?',
        (username, email)
    ).fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({'detail': '用户名或邮箱已存在'}), 400
    
    # 创建新用户
    hashed_password = hash_password(password)
    cursor = conn.execute(
        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
        (username, email, hashed_password)
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    
    # 获取用户信息
    user = conn.execute(
        'SELECT id, username, email, created_at FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    
    conn.close()
    
    # 创建令牌
    token = create_token(user_id, username)
    
    return jsonify({
        'access_token': token,
        'token_type': 'bearer',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'password')):
        return jsonify({'detail': '用户名和密码都是必填项'}), 400
    
    username = data['username']
    password = data['password']
    
    conn = get_db_connection()
    
    # 查找用户
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? OR email = ?',
        (username, username)
    ).fetchone()
    
    if not user or not verify_password(password, user['password']):
        conn.close()
        return jsonify({'detail': '用户名或密码错误'}), 401
    
    conn.close()
    
    # 创建令牌
    token = create_token(user['id'], user['username'])
    
    return jsonify({
        'access_token': token,
        'token_type': 'bearer',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
        }
    })

@app.route('/api/auth/profile')
@token_required
def get_profile():
    """获取用户信息"""
    user_id = request.current_user['user_id']
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT id, username, email, created_at FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'created_at': user['created_at']
    })

# 注册todo蓝图
from todo_routes import todo_bp
app.register_blueprint(todo_bp)

if __name__ == '__main__':
    init_db()
    print("🚀 Flask服务器启动成功！")
    print("🌐 前端页面地址: http://127.0.0.1:8000")
    print("📖 API健康检查: http://127.0.0.1:8000/api/health")
    print("📝 Todo API: http://127.0.0.1:8000/api/todo")
    app.run(host='127.0.0.1', port=8000, debug=False)