"""
main.py - الملف الرئيسي لتطبيق منصة العمل الحر
يحتوي على نقطة الدخول الرئيسية وإدارة التوجيه بين الشاشات
"""

import flet as ft
from database import Database
from auth import AuthScreen
from client_dashboard import ClientDashboard
from freelancer_dashboard import FreelancerDashboard
from admin_dashboard import AdminDashboard

class FreelancingPlatform:
    """الفئة الرئيسية لتطبيق منصة العمل الحر"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.setup_page()
        self.show_auth_screen()
    
    def setup_page(self):
        """إعدادات الصفحة الرئيسية"""
        self.page.title = "منصة العمل الحر"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        self.page.padding = 0
        self.page.spacing = 0
        
        # تعيين لون الخلفية
        self.page.bgcolor = ft.Colors.GREY_50
    
    def show_auth_screen(self):
        """عرض شاشة المصادقة"""
        def on_login_success(user_data):
            self.user_data = user_data
            self.route_to_dashboard()
        
        auth_screen = AuthScreen(self.page, self.db, on_login_success)
        auth_screen.build()
    
    def route_to_dashboard(self):
        """توجيه المستخدم إلى لوحة التحكم المناسبة حسب نوعه"""
        user_type = self.user_data['user_type']
        
        if user_type == 'admin':
            admin_dashboard = AdminDashboard(self.page, self.db, self.user_data)
            admin_dashboard.build()
        elif user_type == 'client':
            client_dashboard = ClientDashboard(self.page, self.db, self.user_data)
            client_dashboard.build()
        else:  # freelancer
            freelancer_dashboard = FreelancerDashboard(self.page, self.db, self.user_data)
            freelancer_dashboard.build()

def main(page: ft.Page):
    """الدالة الرئيسية لتشغيل التطبيق"""
    app = FreelancingPlatform(page)

if __name__ == "__main__":
    ft.app(target=main)