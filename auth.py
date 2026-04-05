"""
auth.py - نظام تسجيل الدخول والتسجيل
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
    
    def build(self):
        """بناء واجهة المصادقة"""
        self.page.clean()
        self.page.title = "منصة العمل الحر - تسجيل الدخول"
        self.page.bgcolor = ft.Colors.GREY_50
        
        # حاوية المحتوى الرئيسية
        container = ft.Container(
            expand=True,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=500,
                        padding=30,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=20,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=15,
                            color=ft.Colors.BLACK12,
                        ),
                        content=self.get_login_tab()
                    )
                ]
            )
        )
        
        self.page.add(container)
    
    def get_login_tab(self):
        """إنشاء تبويب تسجيل الدخول"""
        self.username_field = ft.TextField(
            label="اسم المستخدم",
            width=400,
            border_radius=10,
            prefix_icon=ft.Icons.PERSON,
        )
        
        self.password_field = ft.TextField(
            label="كلمة المرور",
            width=400,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            prefix_icon=ft.Icons.LOCK,
        )
        
        login_button = ft.ElevatedButton(
            content=ft.Text("تسجيل الدخول", size=18, weight=ft.FontWeight.BOLD),
            width=400,
            height=50,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.handle_login
        )
        
        register_link = ft.TextButton(
            content=ft.Text("ليس لديك حساب؟ سجل الآن", size=14, color=ft.Colors.BLUE_600),
            on_click=self.show_register_tab
        )
        
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.Icons.WORK, size=80, color=ft.Colors.BLUE_700),
                ft.Text("مرحباً بك في منصة العمل الحر", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("سجل الدخول للوصول إلى لوحة التحكم", size=14, color=ft.Colors.GREY_600),
                ft.Divider(height=30),
                self.username_field,
                self.password_field,
                login_button,
                register_link,
            ]
        )
    
    def show_register_tab(self, e):
        """عرض نموذج التسجيل"""
        self.page.clean()
        container = ft.Container(
            expand=True,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=500,
                        padding=30,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=20,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=15,
                            color=ft.Colors.BLACK12,
                        ),
                        content=self.get_register_form()
                    )
                ]
            )
        )
        self.page.add(container)
    
    def get_register_form(self):
        """إنشاء نموذج التسجيل"""
        self.reg_username = ft.TextField(
            label="اسم المستخدم",
            width=400,
            border_radius=10,
            prefix_icon=ft.Icons.PERSON,
        )
        
        self.reg_email = ft.TextField(
            label="البريد الإلكتروني",
            width=400,
            border_radius=10,
            prefix_icon=ft.Icons.EMAIL,
        )
        
        self.reg_password = ft.TextField(
            label="كلمة المرور",
            width=400,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            prefix_icon=ft.Icons.LOCK,
        )
        
        self.reg_confirm_password = ft.TextField(
            label="تأكيد كلمة المرور",
            width=400,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            prefix_icon=ft.Icons.LOCK,
        )
        
        # خيارات نوع الحساب
        self.user_type_dropdown = ft.Dropdown(
            label="نوع الحساب",
            width=400,
            options=[
                ft.dropdown.Option("freelancer", "مستقل (Freelancer)"),
                ft.dropdown.Option("client", "صاحب عمل (Client)"),
            ],
            value="freelancer",
            border_radius=10,
        )
        
        register_button = ft.ElevatedButton(
            content=ft.Text("إنشاء حساب", size=18, weight=ft.FontWeight.BOLD),
            width=400,
            height=50,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self.handle_register
        )
        
        login_link = ft.TextButton(
            content=ft.Text("لديك حساب بالفعل؟ تسجيل الدخول", size=14, color=ft.Colors.BLUE_600),
            on_click=lambda e: self.build()
        )
        
        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.Icons.PERSON_ADD, size=80, color=ft.Colors.GREEN_700),
                ft.Text("إنشاء حساب جديد", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("انضم إلى منصة العمل الحر", size=14, color=ft.Colors.GREY_600),
                ft.Divider(height=30),
                self.reg_username,
                self.reg_email,
                self.reg_password,
                self.reg_confirm_password,
                self.user_type_dropdown,
                register_button,
                login_link,
            ]
        )
    
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
            self.on_login_success(user)
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
            self.build()  # العودة إلى شاشة تسجيل الدخول
        else:
            self.show_snackbar("اسم المستخدم أو البريد الإلكتروني موجود مسبقاً", ft.Colors.RED)
    
    def show_snackbar(self, message: str, color: str):
        """عرض إشعار منبثق"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()