from flask import Blueprint, request, jsonify
from todo_models import TodoModel, CategoryModel, init_todo_db
from auth_decorators import token_required
from datetime import datetime

# 创建蓝图
todo_bp = Blueprint('todo', __name__, url_prefix='/api/todo')

# 初始化数据库
init_todo_db()

@todo_bp.route('/todos', methods=['GET'])
@token_required
def get_todos():
    """获取用户的todos"""
    user_id = request.current_user['user_id']
    completed = request.args.get('completed')
    category_id = request.args.get('category_id')
    
    # 转换completed参数
    if completed is not None:
        completed = completed.lower() == 'true'
    
    # 转换category_id参数
    if category_id:
        try:
            category_id = int(category_id)
        except ValueError:
            category_id = None
    
    todos = TodoModel.get_todos_by_user(user_id, completed, category_id)
    return jsonify(todos)

@todo_bp.route('/todos', methods=['POST'])
@token_required
def create_todo():
    """创建新的todo"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'detail': '标题是必填项'}), 400
    
    title = data['title']
    description = data.get('description')
    priority = data.get('priority', 'medium')
    due_date = data.get('due_date')
    category_ids = data.get('category_ids', [])
    
    # 验证优先级
    if priority not in ['low', 'medium', 'high']:
        return jsonify({'detail': '优先级必须是 low, medium 或 high'}), 400
    
    # 验证日期格式
    if due_date:
        try:
            datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'detail': '日期格式不正确'}), 400
    
    todo = TodoModel.create_todo(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        due_date=due_date,
        category_ids=category_ids
    )
    
    return jsonify(todo), 201

@todo_bp.route('/todos/<int:todo_id>', methods=['PUT'])
@token_required
def update_todo(todo_id):
    """更新todo"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    if not data:
        return jsonify({'detail': '请提供更新数据'}), 400
    
    # 验证优先级
    if 'priority' in data and data['priority'] not in ['low', 'medium', 'high']:
        return jsonify({'detail': '优先级必须是 low, medium 或 high'}), 400
    
    # 验证日期格式
    if 'due_date' in data and data['due_date']:
        try:
            datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'detail': '日期格式不正确'}), 400
    
    todo = TodoModel.update_todo(todo_id, user_id, **data)
    
    if not todo:
        return jsonify({'detail': 'Todo不存在或无权限'}), 404
    
    return jsonify(todo)

@todo_bp.route('/todos/<int:todo_id>', methods=['DELETE'])
@token_required
def delete_todo(todo_id):
    """删除todo"""
    user_id = request.current_user['user_id']
    
    deleted = TodoModel.delete_todo(todo_id, user_id)
    
    if not deleted:
        return jsonify({'detail': 'Todo不存在或无权限'}), 404
    
    return jsonify({'message': 'Todo删除成功'})

@todo_bp.route('/todos/<int:todo_id>/toggle', methods=['PATCH'])
@token_required
def toggle_todo(todo_id):
    """切换todo完成状态"""
    user_id = request.current_user['user_id']
    
    # 先获取当前状态
    todos = TodoModel.get_todos_by_user(user_id)
    current_todo = next((t for t in todos if t['id'] == todo_id), None)
    
    if not current_todo:
        return jsonify({'detail': 'Todo不存在或无权限'}), 404
    
    # 切换完成状态
    new_completed = not current_todo['completed']
    todo = TodoModel.update_todo(todo_id, user_id, completed=new_completed)
    
    return jsonify(todo)

# 分类相关路由
@todo_bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    """获取用户的分类"""
    user_id = request.current_user['user_id']
    categories = CategoryModel.get_categories_by_user(user_id)
    return jsonify(categories)

@todo_bp.route('/categories', methods=['POST'])
@token_required
def create_category():
    """创建新分类"""
    user_id = request.current_user['user_id']
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'detail': '分类名称是必填项'}), 400
    
    name = data['name']
    color = data.get('color', '#007bff')
    
    category = CategoryModel.create_category(user_id, name, color)
    
    if not category:
        return jsonify({'detail': '分类名称已存在'}), 400
    
    return jsonify(category), 201

@todo_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(category_id):
    """删除分类"""
    user_id = request.current_user['user_id']
    
    deleted = CategoryModel.delete_category(category_id, user_id)
    
    if not deleted:
        return jsonify({'detail': '分类不存在或无权限'}), 404
    
    return jsonify({'message': '分类删除成功'})

@todo_bp.route('/stats', methods=['GET'])
@token_required
def get_stats():
    """获取todo统计信息"""
    user_id = request.current_user['user_id']
    
    all_todos = TodoModel.get_todos_by_user(user_id)
    completed_todos = [t for t in all_todos if t['completed']]
    pending_todos = [t for t in all_todos if not t['completed']]
    
    # 按优先级统计
    priority_stats = {
        'high': len([t for t in pending_todos if t['priority'] == 'high']),
        'medium': len([t for t in pending_todos if t['priority'] == 'medium']),
        'low': len([t for t in pending_todos if t['priority'] == 'low'])
    }
    
    # 过期任务统计
    now = datetime.now().isoformat()
    overdue_todos = [
        t for t in pending_todos 
        if t['due_date'] and t['due_date'] < now
    ]
    
    stats = {
        'total': len(all_todos),
        'completed': len(completed_todos),
        'pending': len(pending_todos),
        'overdue': len(overdue_todos),
        'completion_rate': round(len(completed_todos) / len(all_todos) * 100, 1) if all_todos else 0,
        'priority_stats': priority_stats
    }
    
    return jsonify(stats)