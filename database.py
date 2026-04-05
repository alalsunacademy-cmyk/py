"""
database.py - إدارة قاعدة البيانات لمنصة العمل الحر
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    """فئة إدارة قاعدة البيانات"""
    
    def __init__(self, db_name: str = "freelancing.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """إنشاء اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """إنشاء جميع الجداول المطلوبة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول المستخدمين
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    user_type TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول المشاريع
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    location TEXT NOT NULL,
                    budget REAL NOT NULL,
                    status TEXT DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES users (id)
                )
            """)
            
            # جدول العروض
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    freelancer_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    price REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects (id),
                    FOREIGN KEY (freelancer_id) REFERENCES users (id)
                )
            """)
            
            # جدول المحادثات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    project_id INTEGER,
                    message TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users (id),
                    FOREIGN KEY (receiver_id) REFERENCES users (id),
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )
            """)
            
            # إنشاء مستخدم Admin افتراضي إذا لم يكن موجوداً
            self.create_admin_user()
            
            conn.commit()
    
    def hash_password(self, password: str) -> str:
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_admin_user(self):
        """إنشاء مستخدم Admin افتراضي"""
        if not self.get_user_by_username("admin"):
            self.register_user("admin", "admin@platform.com", "admin123", "admin")
    
    def register_user(self, username: str, email: str, password: str, user_type: str) -> bool:
        """تسجيل مستخدم جديد"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                hashed_password = self.hash_password(password)
                cursor.execute("""
                    INSERT INTO users (username, email, password, user_type)
                    VALUES (?, ?, ?, ?)
                """, (username, email, hashed_password, user_type))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def login_user(self, username: str, password: str) -> Optional[Dict]:
        """تسجيل الدخول والتحقق من البيانات"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            hashed_password = self.hash_password(password)
            cursor.execute("""
                SELECT id, username, email, user_type, status
                FROM users
                WHERE username = ? AND password = ? AND status = 'active'
            """, (username, hashed_password))
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'user_type': user[3],
                    'status': user[4]
                }
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """الحصول على معلومات مستخدم بواسطة اسم المستخدم"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'user_type': user[4],
                    'status': user[5]
                }
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """الحصول على معلومات مستخدم بواسطة ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, email, user_type, status FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'user_type': user[3],
                    'status': user[4]
                }
            return None
    
    def create_project(self, client_id: int, title: str, description: str, 
                      category: str, location: str, budget: float) -> int:
        """إنشاء مشروع جديد"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO projects (client_id, title, description, category, location, budget)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (client_id, title, description, category, location, budget))
            conn.commit()
            return cursor.lastrowid
    
    def get_projects_by_client(self, client_id: int) -> List[Dict]:
        """الحصول على مشاريع عميل معين"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, category, location, budget, status, created_at
                FROM projects
                WHERE client_id = ?
                ORDER BY created_at DESC
            """, (client_id,))
            projects = cursor.fetchall()
            return [
                {
                    'id': p[0],
                    'title': p[1],
                    'description': p[2],
                    'category': p[3],
                    'location': p[4],
                    'budget': p[5],
                    'status': p[6],
                    'created_at': p[7]
                }
                for p in projects
            ]
    
    def get_all_projects(self, category: str = None, location: str = None) -> List[Dict]:
        """الحصول على جميع المشاريع مع إمكانية الفلترة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.title, p.description, p.category, p.location, p.budget, 
                       p.status, p.created_at, u.username as client_name
                FROM projects p
                JOIN users u ON p.client_id = u.id
                WHERE p.status = 'open'
            """
            params = []
            
            if category:
                query += " AND p.category = ?"
                params.append(category)
            if location:
                query += " AND p.location = ?"
                params.append(location)
            
            query += " ORDER BY p.created_at DESC"
            
            cursor.execute(query, params)
            projects = cursor.fetchall()
            return [
                {
                    'id': p[0],
                    'title': p[1],
                    'description': p[2],
                    'category': p[3],
                    'location': p[4],
                    'budget': p[5],
                    'status': p[6],
                    'created_at': p[7],
                    'client_name': p[8]
                }
                for p in projects
            ]
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        """الحصول على تفاصيل مشروع معين"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.title, p.description, p.category, p.location, p.budget, 
                       p.status, p.created_at, u.username as client_name, u.id as client_id
                FROM projects p
                JOIN users u ON p.client_id = u.id
                WHERE p.id = ?
            """, (project_id,))
            project = cursor.fetchone()
            if project:
                return {
                    'id': project[0],
                    'title': project[1],
                    'description': project[2],
                    'category': project[3],
                    'location': project[4],
                    'budget': project[5],
                    'status': project[6],
                    'created_at': project[7],
                    'client_name': project[8],
                    'client_id': project[9]
                }
            return None
    
    def create_proposal(self, project_id: int, freelancer_id: int, 
                       description: str, price: float) -> bool:
        """تقديم عرض على مشروع"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO proposals (project_id, freelancer_id, description, price)
                    VALUES (?, ?, ?, ?)
                """, (project_id, freelancer_id, description, price))
                conn.commit()
                return True
        except Exception:
            return False
    
    def get_proposals_for_project(self, project_id: int) -> List[Dict]:
        """الحصول على جميع العروض لمشروع معين"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.description, p.price, p.status, p.created_at,
                       u.username, u.id as freelancer_id
                FROM proposals p
                JOIN users u ON p.freelancer_id = u.id
                WHERE p.project_id = ?
                ORDER BY p.created_at DESC
            """, (project_id,))
            proposals = cursor.fetchall()
            return [
                {
                    'id': prop[0],
                    'description': prop[1],
                    'price': prop[2],
                    'status': prop[3],
                    'created_at': prop[4],
                    'freelancer_name': prop[5],
                    'freelancer_id': prop[6]
                }
                for prop in proposals
            ]
    
    def update_proposal_status(self, proposal_id: int, status: str) -> bool:
        """تحديث حالة عرض (قبول/رفض)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE proposals SET status = ? WHERE id = ?
            """, (status, proposal_id))
            conn.commit()
            return True
    
    def send_message(self, sender_id: int, receiver_id: int, 
                    message: str, project_id: int = None) -> bool:
        """إرسال رسالة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (sender_id, receiver_id, project_id, message)
                VALUES (?, ?, ?, ?)
            """, (sender_id, receiver_id, project_id, message))
            conn.commit()
            return True
    
    def get_messages(self, user1_id: int, user2_id: int, project_id: int = None) -> List[Dict]:
        """الحصول على المحادثة بين مستخدمين"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT m.id, m.sender_id, m.receiver_id, m.message, m.created_at,
                       u.username as sender_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE ((m.sender_id = ? AND m.receiver_id = ?) OR
                      (m.sender_id = ? AND m.receiver_id = ?))
            """
            params = [user1_id, user2_id, user2_id, user1_id]
            
            if project_id:
                query += " AND m.project_id = ?"
                params.append(project_id)
            
            query += " ORDER BY m.created_at ASC"
            
            cursor.execute(query, params)
            messages = cursor.fetchall()
            return [
                {
                    'id': m[0],
                    'sender_id': m[1],
                    'receiver_id': m[2],
                    'message': m[3],
                    'created_at': m[4],
                    'sender_name': m[5]
                }
                for m in messages
            ]
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين (للوحة تحكم الأدمن)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, user_type, status, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            users = cursor.fetchall()
            return [
                {
                    'id': u[0],
                    'username': u[1],
                    'email': u[2],
                    'user_type': u[3],
                    'status': u[4],
                    'created_at': u[5]
                }
                for u in users
            ]
    
    def update_user_status(self, user_id: int, status: str) -> bool:
        """تحديث حالة مستخدم (active/banned)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET status = ? WHERE id = ?", (status, user_id))
            conn.commit()
            return True
    
    def delete_user(self, user_id: int) -> bool:
        """حذف مستخدم"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
    
    def delete_project(self, project_id: int) -> bool:
        """حذف مشروع"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            return True
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """تحديث معلومات مشروع"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for key, value in kwargs.items():
                cursor.execute(f"UPDATE projects SET {key} = ? WHERE id = ?", (value, project_id))
            conn.commit()
            return True
    
    def get_all_projects_admin(self) -> List[Dict]:
        """الحصول على جميع المشاريع (للأدمن)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.title, p.description, p.category, p.location, p.budget, 
                       p.status, p.created_at, u.username as client_name
                FROM projects p
                JOIN users u ON p.client_id = u.id
                ORDER BY p.created_at DESC
            """)
            projects = cursor.fetchall()
            return [
                {
                    'id': p[0],
                    'title': p[1],
                    'description': p[2],
                    'category': p[3],
                    'location': p[4],
                    'budget': p[5],
                    'status': p[6],
                    'created_at': p[7],
                    'client_name': p[8]
                }
                for p in projects
            ]
    
    def get_user_projects_count(self, user_id: int) -> int:
        """عدد مشاريع المستخدم"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects WHERE client_id = ?", (user_id,))
            return cursor.fetchone()[0]
    
    def get_user_proposals_count(self, user_id: int) -> int:
        """عدد عروض المستخدم"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proposals WHERE freelancer_id = ?", (user_id,))
            return cursor.fetchone()[0]