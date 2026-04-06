"""
auth.py - نظام تسجيل الدخول والتسجيل مع تصميم محمول
"""

import flet as ft
from database import Database

class AuthScreen:
    """شاشة المصادقة (تسجيل الدخول والتسجيل)"""
    
    def __init__(self, page: ft.Page, db: Database, on_login_success):
        self.page = page
        self.db = db
        self.on_login_success = on_login_success
        self.user_type = "freelancer"
        self.is_login = True  # True: login, False: register
    
    def build(self):
        """بناء واجهة المصادقة"""
        self.page.clean()
        self.page.title = "منصة العمل الحر"
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.scroll = ft.ScrollMode.AUTO
        
        # حاوية قابلة للتمرير
        main_container = ft.Container(
            expand=True,
            padding=ft.padding.symmetric(horizontal=20, vertical=30),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                controls=self.get_login_ui() if self.is_login else self.get_register_ui()
            )
        )
        
        self.page.add(main_container)
        self.page.update()
    
    def get_login_ui(self):
        """واجهة تسجيل الدخول"""
        self.username_field = ft.TextField(
            label="اسم المستخدم",
            width=self.page.window_width - 60,
            border_radius=15,
            prefix_icon=ft.Icons.PERSON,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.password_field = ft.TextField(
            label="كلمة المرور",
            width=self.page.window_width - 60,
            password=True,
            can_reveal_password=True,
            border_radius=15,
            prefix_icon=ft.Icons.LOCK,
            bgcolor=ft.Colors.WHITE,
        )
        
        login_button = ft.ElevatedButton(
            content=ft.Text("تسجيل الدخول", size=18, weight=ft.FontWeight.BOLD),
            width=self.page.window_width - 60,
            height=50,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                shape=ft.RoundedRectangleBorder(radius=15),
            ),
            on_click=self.handle_login
        )
        
        register_button = ft.OutlinedButton(
            content=ft.Text("إنشاء حساب جديد", size=16),
            width=self.page.window_width - 60,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15),
            ),
            on_click=lambda e: self.toggle_mode()
        )
        
        return [
            ft.Container(height=40),
            ft.Icon(ft.Icons.WORK, size=80, color=ft.Colors.BLUE_700),
            ft.Text("مرحباً بك", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("في منصة العمل الحر", size=16, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            self.username_field,
            self.password_field,
            login_button,
            ft.Text("أو", size=14, color=ft.Colors.GREY_500),
            register_button,
        ]
    
    def get_register_ui(self):
        """واجهة التسجيل"""
        self.reg_username = ft.TextField(
            label="اسم المستخدم",
            width=self.page.window_width - 60,
            border_radius=15,
            prefix_icon=ft.Icons.PERSON,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.reg_email = ft.TextField(
            label="البريد الإلكتروني",
            width=self.page.window_width - 60,
            border_radius=15,
            prefix_icon=ft.Icons.EMAIL,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.reg_password = ft.TextField(
            label="كلمة المرور",
            width=self.page.window_width - 60,
            password=True,
            can_reveal_password=True,
            border_radius=15,
            prefix_icon=ft.Icons.LOCK,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.reg_confirm_password = ft.TextField(
            label="تأكيد كلمة المرور",
            width=self.page.window_width - 60,
            password=True,
            can_reveal_password=True,
            border_radius=15,
            prefix_icon=ft.Icons.LOCK,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.user_type_dropdown = ft.Dropdown(
            label="نوع الحساب",
            width=self.page.window_width - 60,
            options=[
                ft.dropdown.Option("freelancer", "مستقل (Freelancer)"),
                ft.dropdown.Option("client", "صاحب عمل (Client)"),
            ],
            value="freelancer",
            border_radius=15,
            bgcolor=ft.Colors.WHITE,
        )
        
        register_button = ft.ElevatedButton(
            content=ft.Text("إنشاء حساب", size=18, weight=ft.FontWeight.BOLD),
            width=self.page.window_width - 60,
            height=50,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
                shape=ft.RoundedRectangleBorder(radius=15),
            ),
            on_click=self.handle_register
        )
        
        login_button = ft.OutlinedButton(
            content=ft.Text("لديك حساب؟ تسجيل الدخول", size=16),
            width=self.page.window_width - 60,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=15),
            ),
            on_click=lambda e: self.toggle_mode()
        )
        
        return [
            ft.Container(height=20),
            ft.Icon(ft.Icons.PERSON_ADD, size=80, color=ft.Colors.GREEN_700),
            ft.Text("إنشاء حساب جديد", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("انضم إلى منصة العمل الحر", size=16, color=ft.Colors.GREY_600),
            ft.Container(height=20),
            self.reg_username,
            self.reg_email,
            self.reg_password,
            self.reg_confirm_password,
            self.user_type_dropdown,
            register_button,
            login_button,
        ]
    
    def toggle_mode(self):
        """التبديل بين وضعي تسجيل الدخول والتسجيل"""
        self.is_login = not self.is_login
        self.build()
    
    def handle_login(self, e):
        """معالجة طلب تسجيل الدخول"""
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.show_snackbar("الرجاء إدخال اسم المستخدم وكلمة المرور", ft.Colors.RED)
            return
        
        user = self.db.login_user(username, password)
        
        if user:
            self.show_snackbar(f"مرحباً {username}! تم تسجيل الدخول بنجاح", ft.Colors.GREEN)
            self.on_login_success(user, password)
        else:
            self.show_snackbar("اسم المستخدم أو كلمة المرور غير صحيحة", ft.Colors.RED)
    
    def handle_register(self, e):
        """معالجة طلب التسجيل"""
        username = self.reg_username.value
        email = self.reg_email.value
        password = self.reg_password.value
        confirm_password = self.reg_confirm_password.value
        user_type = self.user_type_dropdown.value
        
        # التحقق من صحة المدخلات
        if not all([username, email, password, confirm_password]):
            self.show_snackbar("الرجاء تعبئة جميع الحقول", ft.Colors.RED)
            return
        
        if password != confirm_password:
            self.show_snackbar("كلمة المرور وتأكيدها غير متطابقين", ft.Colors.RED)
            return
        
        if len(password) < 6:
            self.show_snackbar("كلمة المرور يجب أن تكون 6 أحرف على الأقل", ft.Colors.RED)
            return
        
        if "@" not in email or "." not in email:
            self.show_snackbar("البريد الإلكتروني غير صالح", ft.Colors.RED)
            return
        
        # محاولة التسجيل
        if self.db.register_user(username, email, password, user_type):
            self.show_snackbar("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن", ft.Colors.GREEN)
            self.is_login = True
            self.build()
        else:
            self.show_snackbar("اسم المستخدم أو البريد الإلكتروني موجود مسبقاً", ft.Colors.RED)
    
    def show_snackbar(self, message: str, color: str):
        """عرض إشعار منبثق"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            action="OK",
            duration=3000,
        )
        self.page.snack_bar.open = True
        self.page.update()