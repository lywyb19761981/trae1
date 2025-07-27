import sqlite3
import os
from datetime import datetime

# 数据库路径
TODO_DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'todo.db')

def init_todo_db():
    """初始化todo数据库"""
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(TODO_DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(TODO_DATABASE_PATH)
    cursor = conn.cursor()
    
    # 创建todos表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
            due_date DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 创建分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#007bff',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, name)
        )
    ''')
    
    # 创建todo-分类关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todo_categories (
            todo_id INTEGER,
            category_id INTEGER,
            PRIMARY KEY (todo_id, category_id),
            FOREIGN KEY (todo_id) REFERENCES todos (id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
        )
    ''')
    
    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_todos_user_id ON todos(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_todos_due_date ON todos(due_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id)')
    
    conn.commit()
    conn.close()
    print("Todo数据库初始化完成")

def get_todo_db_connection():
    """获取todo数据库连接"""
    conn = sqlite3.connect(TODO_DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class TodoModel:
    """Todo数据模型"""
    
    @staticmethod
    def create_todo(user_id, title, description=None, priority='medium', due_date=None, category_ids=None):
        """创建新的todo"""
        conn = get_todo_db_connection()
        cursor = conn.cursor()
        
        # 插入todo
        cursor.execute('''
            INSERT INTO todos (user_id, title, description, priority, due_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, description, priority, due_date))
        
        todo_id = cursor.lastrowid
        
        # 如果有分类，添加关联
        if category_ids:
            for category_id in category_ids:
                cursor.execute('''
                    INSERT INTO todo_categories (todo_id, category_id)
                    VALUES (?, ?)
                ''', (todo_id, category_id))
        
        conn.commit()
        
        # 获取创建的todo
        todo = cursor.execute('''
            SELECT * FROM todos WHERE id = ?
        ''', (todo_id,)).fetchone()
        
        conn.close()
        return dict(todo)
    
    @staticmethod
    def get_todos_by_user(user_id, completed=None, category_id=None):
        """获取用户的todos"""
        conn = get_todo_db_connection()
        
        query = '''
            SELECT t.*, GROUP_CONCAT(c.name) as categories
            FROM todos t
            LEFT JOIN todo_categories tc ON t.id = tc.todo_id
            LEFT JOIN categories c ON tc.category_id = c.id
            WHERE t.user_id = ?
        '''
        params = [user_id]
        
        if completed is not None:
            query += ' AND t.completed = ?'
            params.append(completed)
        
        if category_id:
            query += ' AND tc.category_id = ?'
            params.append(category_id)
        
        query += ' GROUP BY t.id ORDER BY t.created_at DESC'
        
        todos = conn.execute(query, params).fetchall()
        conn.close()
        
        return [dict(todo) for todo in todos]
    
    @staticmethod
    def update_todo(todo_id, user_id, **kwargs):
        """更新todo"""
        conn = get_todo_db_connection()
        cursor = conn.cursor()
        
        # 构建更新语句
        set_clauses = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['title', 'description', 'completed', 'priority', 'due_date']:
                set_clauses.append(f'{key} = ?')
                params.append(value)
        
        if set_clauses:
            set_clauses.append('updated_at = CURRENT_TIMESTAMP')
            params.extend([todo_id, user_id])
            
            query = f'''
                UPDATE todos 
                SET {', '.join(set_clauses)}
                WHERE id = ? AND user_id = ?
            '''
            
            cursor.execute(query, params)
            conn.commit()
        
        # 获取更新后的todo
        todo = cursor.execute('''
            SELECT * FROM todos WHERE id = ? AND user_id = ?
        ''', (todo_id, user_id)).fetchone()
        
        conn.close()
        return dict(todo) if todo else None
    
    @staticmethod
    def delete_todo(todo_id, user_id):
        """删除todo"""
        conn = get_todo_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM todos WHERE id = ? AND user_id = ?
        ''', (todo_id, user_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted

class CategoryModel:
    """分类数据模型"""
    
    @staticmethod
    def create_category(user_id, name, color='#007bff'):
        """创建新分类"""
        conn = get_todo_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO categories (user_id, name, color)
                VALUES (?, ?, ?)
            ''', (user_id, name, color))
            
            category_id = cursor.lastrowid
            conn.commit()
            
            # 获取创建的分类
            category = cursor.execute('''
                SELECT * FROM categories WHERE id = ?
            ''', (category_id,)).fetchone()
            
            conn.close()
            return dict(category)
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    @staticmethod
    def get_categories_by_user(user_id):
        """获取用户的分类"""
        conn = get_todo_db_connection()
        
        categories = conn.execute('''
            SELECT c.*, COUNT(tc.todo_id) as todo_count
            FROM categories c
            LEFT JOIN todo_categories tc ON c.id = tc.category_id
            WHERE c.user_id = ?
            GROUP BY c.id
            ORDER BY c.name
        ''', (user_id,)).fetchall()
        
        conn.close()
        return [dict(category) for category in categories]
    
    @staticmethod
    def delete_category(category_id, user_id):
        """删除分类"""
        conn = get_todo_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM categories WHERE id = ? AND user_id = ?
        ''', (category_id, user_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted