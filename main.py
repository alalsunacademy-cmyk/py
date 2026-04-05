"""
main.py - الملف الرئيسي لتطبيق منصة العمل الحر مع حفظ الجلسة
"""

import flet as ft
from database import Database
from auth import AuthScreen
from client_dashboard import ClientDashboard
from freelancer_dashboard import FreelancerDashboard
from admin_dashboard import AdminDashboard
import json
import os

class FreelancingPlatform:
    """الفئة الرئيسية لتطبيق منصة العمل الحر"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.setup_page()
        self.check_saved_session()
    
    def setup_page(self):
        """إعدادات الصفحة الرئيسية"""
        self.page.title = "منصة العمل الحر"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        self.page.padding = 20
        self.page.spacing = 10
        
        # إعدادات للأجهزة المحمولة
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        
        # تعيين لون الخلفية
        self.page.bgcolor = ft.Colors.GREY_50
    
    def check_saved_session(self):
        """التحقق من وجود جلسة محفوظة"""
        session_file = "session.json"
        
        if os.path.exists(session_file):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # التحقق من صحة الجلسة
                user = self.db.login_user(session_data['username'], session_data['password'])
                if user:
                    self.user_data = user
                    self.route_to_dashboard()
                    return
            except:
                pass
        
        # إذا لم توجد جلسة صالحة، عرض شاشة تسجيل الدخول
        self.show_auth_screen()
    
    def save_session(self, username, password):
        """حفظ جلسة المستخدم"""
        session_file = "session.json"
        session_data = {
            'username': username,
            'password': password
        }
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
    
    def clear_session(self):
        """مسح الجلسة المحفوظة"""
        session_file = "session.json"
        if os.path.exists(session_file):
            os.remove(session_file)
    
    def show_auth_screen(self):
        """عرض شاشة المصادقة"""
        def on_login_success(user_data, password):
            self.user_data = user_data
            self.save_session(user_data['username'], password)
            self.route_to_dashboard()
        
        auth_screen = AuthScreen(self.page, self.db, on_login_success)
        auth_screen.build()
    
    def route_to_dashboard(self):
        """توجيه المستخدم إلى لوحة التحكم المناسبة حسب نوعه"""
        user_type = self.user_data['user_type']
        
        if user_type == 'admin':
            admin_dashboard = AdminDashboard(self.page, self.db, self.user_data, self.clear_session)
            admin_dashboard.build()
        elif user_type == 'client':
            client_dashboard = ClientDashboard(self.page, self.db, self.user_data, self.clear_session)
            client_dashboard.build()
        else:  # freelancer
            freelancer_dashboard = FreelancerDashboard(self.page, self.db, self.user_data, self.clear_session)
            freelancer_dashboard.build()

def main(page: ft.Page):
    """الدالة الرئيسية لتشغيل التطبيق"""
    app = FreelancingPlatform(page)

if __name__ == "__main__":
    ft.app(target=main)