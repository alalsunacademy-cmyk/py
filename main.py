"""
main.py - الملف الرئيسي لتطبيق منصة العمل الحر
"""

import flet as ft
from database import Database
import json
import os

class FreelancingPlatform:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.setup_page()
        self.check_saved_session()
    
    def setup_page(self):
        self.page.title = "منصة العمل الحر"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 400
        self.page.window_height = 800
        self.page.padding = 0
        self.page.bgcolor = ft.Colors.WHITE
    
    def check_saved_session(self):
        if os.path.exists("session.json"):
            try:
                with open("session.json", 'r') as f:
                    data = json.load(f)
                user = self.db.login_user(data['username'], data['password'])
                if user:
                    self.show_dashboard(user)
                    return
            except:
                pass
        self.show_login()
    
    def save_session(self, username, password):
        with open("session.json", 'w') as f:
            json.dump({'username': username, 'password': password}, f)
    
    def clear_session(self):
        if os.path.exists("session.json"):
            os.remove("session.json")
    
    def show_login(self):
        self.page.clean()
        
        # حقل اسم المستخدم
        username = ft.TextField(
            label="اسم المستخدم",
            width=self.page.window_width - 60,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
        )
        
        # حقل كلمة المرور
        password = ft.TextField(
            label="كلمة المرور",
            width=self.page.window_width - 60,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
        )
        
        # رسالة خطأ
        error_msg = ft.Text("", color=ft.Colors.RED, size=12)
        
        # زر تسجيل الدخول
        def do_login(e):
            if not username.value or not password.value:
                error_msg.value = "الرجاء إدخال اسم المستخدم وكلمة المرور"
                self.page.update()
                return
            
            user = self.db.login_user(username.value, password.value)
            if user:
                self.save_session(username.value, password.value)
                self.show_dashboard(user)
            else:
                error_msg.value = "اسم المستخدم أو كلمة المرور غير صحيحة"
                self.page.update()
        
        login_btn = ft.ElevatedButton(
            "تسجيل الدخول",
            width=self.page.window_width - 60,
            height=45,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
            on_click=do_login
        )
        
        # زر الانتقال للتسجيل
        def go_to_register(e):
            self.show_register()
        
        register_btn = ft.OutlinedButton(
            "إنشاء حساب جديد",
            width=self.page.window_width - 60,
            height=45,
            on_click=go_to_register
        )
        
        self.page.add(
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.WORK, size=80, color=ft.Colors.BLUE_700),
                        ft.Text("منصة العمل الحر", size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("سجل دخولك للمتابعة", size=14, color=ft.Colors.GREY_600),
                        ft.Container(height=30),
                        username,
                        password,
                        error_msg,
                        login_btn,
                        ft.Text("أو", size=14, color=ft.Colors.GREY_500),
                        register_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                )
            )
        )
        self.page.update()
    
    def show_register(self):
        self.page.clean()
        
        # حقول التسجيل
        username = ft.TextField(label="اسم المستخدم", width=self.page.window_width - 60, border_radius=10)
        email = ft.TextField(label="البريد الإلكتروني", width=self.page.window_width - 60, border_radius=10)
        password = ft.TextField(label="كلمة المرور", width=self.page.window_width - 60, password=True, can_reveal_password=True, border_radius=10)
        confirm = ft.TextField(label="تأكيد كلمة المرور", width=self.page.window_width - 60, password=True, can_reveal_password=True, border_radius=10)
        
        user_type = ft.Dropdown(
            label="نوع الحساب",
            width=self.page.window_width - 60,
            options=[
                ft.dropdown.Option("freelancer", "مستقل"),
                ft.dropdown.Option("client", "صاحب عمل"),
            ],
            value="freelancer",
            border_radius=10,
        )
        
        error_msg = ft.Text("", color=ft.Colors.RED, size=12)
        
        def do_register(e):
            if not all([username.value, email.value, password.value, confirm.value]):
                error_msg.value = "الرجاء تعبئة جميع الحقول"
                self.page.update()
                return
            
            if password.value != confirm.value:
                error_msg.value = "كلمة المرور غير متطابقة"
                self.page.update()
                return
            
            if len(password.value) < 6:
                error_msg.value = "كلمة المرور يجب أن تكون 6 أحرف على الأقل"
                self.page.update()
                return
            
            if "@" not in email.value or "." not in email.value:
                error_msg.value = "البريد الإلكتروني غير صالح"
                self.page.update()
                return
            
            if self.db.register_user(username.value, email.value, password.value, user_type.value):
                self.show_login()
            else:
                error_msg.value = "اسم المستخدم أو البريد موجود مسبقاً"
                self.page.update()
        
        register_btn = ft.ElevatedButton(
            "إنشاء حساب",
            width=self.page.window_width - 60,
            height=45,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE),
            on_click=do_register
        )
        
        def back_to_login(e):
            self.show_login()
        
        back_btn = ft.OutlinedButton(
            "العودة لتسجيل الدخول",
            width=self.page.window_width - 60,
            height=45,
            on_click=back_to_login
        )
        
        self.page.add(
            ft.Container(
                expand=True,
                alignment=ft.alignment.center,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.PERSON_ADD, size=80, color=ft.Colors.GREEN_700),
                        ft.Text("إنشاء حساب جديد", size=24, weight=ft.FontWeight.BOLD),
                        ft.Container(height=20),
                        username,
                        email,
                        password,
                        confirm,
                        user_type,
                        error_msg,
                        register_btn,
                        back_btn,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                )
            )
        )
        self.page.update()
    
    def show_dashboard(self, user):
        """عرض لوحة التحكم حسب نوع المستخدم"""
        if user['user_type'] == 'admin':
            self.show_admin_dashboard(user)
        elif user['user_type'] == 'client':
            self.show_client_dashboard(user)
        else:
            self.show_freelancer_dashboard(user)
    
    def show_admin_dashboard(self, user):
        """لوحة تحكم الأدمن"""
        self.page.clean()
        self.page.title = "لوحة تحكم المدير"
        
        # شريط العلوي
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"مرحباً {user['username']} 👑", size=18),
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: self.logout())
            ],
        )
        
        # إحصائيات
        users = self.db.get_all_users()
        projects = self.db.get_all_projects_admin()
        
        stats_row = ft.Row(
            [
                ft.Container(
                    width=150,
                    padding=20,
                    bgcolor=ft.Colors.BLUE.with_opacity(0.1),
                    border_radius=15,
                    content=ft.Column([
                        ft.Icon(ft.Icons.PEOPLE, size=30, color=ft.Colors.BLUE),
                        ft.Text(str(len(users)), size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("مستخدمين", size=12),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
                ft.Container(
                    width=150,
                    padding=20,
                    bgcolor=ft.Colors.PURPLE.with_opacity(0.1),
                    border_radius=15,
                    content=ft.Column([
                        ft.Icon(ft.Icons.PROJECT, size=30, color=ft.Colors.PURPLE),
                        ft.Text(str(len(projects)), size=28, weight=ft.FontWeight.BOLD),
                        ft.Text("مشاريع", size=12),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        
        # قائمة المستخدمين
        users_list = ft.Column(spacing=5)
        for u in users[:10]:  # عرض أول 10 مستخدمين
            users_list.controls.append(
                ft.Container(
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    content=ft.Row([
                        ft.Column([
                            ft.Text(u['username'], weight=ft.FontWeight.BOLD),
                            ft.Text(u['email'], size=11, color=ft.Colors.GREY_600),
                        ], expand=True),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            bgcolor=ft.Colors.GREEN.with_opacity(0.2) if u['status'] == 'active' else ft.Colors.RED.with_opacity(0.2),
                            border_radius=10,
                            content=ft.Text("نشط" if u['status'] == 'active' else "محظور", size=10),
                        ),
                    ])
                )
            )
        
        # شريط التنقل السفلي
        nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.DASHBOARD, label="الرئيسية"),
                ft.NavigationDestination(icon=ft.Icons.PEOPLE, label="المستخدمين"),
                ft.NavigationDestination(icon=ft.Icons.PROJECT, label="المشاريع"),
            ],
            on_change=lambda e: self.admin_nav_change(e, user),
            bgcolor=ft.Colors.WHITE,
        )
        
        # المحتوى الرئيسي
        self.main_content = ft.Container(
            expand=True,
            padding=15,
            content=ft.Column(
                [
                    ft.Text("📊 لوحة التحكم", size=22, weight=ft.FontWeight.BOLD),
                    stats_row,
                    ft.Text("👥 آخر المستخدمين", size=18, weight=ft.FontWeight.BOLD),
                    users_list,
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        
        self.page.add(ft.Column([self.main_content, nav_bar], expand=True, spacing=0))
        self.page.update()
    
    def admin_nav_change(self, e, user):
        index = e.control.selected_index
        if index == 0:
            self.show_admin_dashboard(user)
        elif index == 1:
            self.show_admin_users(user)
        elif index == 2:
            self.show_admin_projects(user)
    
    def show_admin_users(self, user):
        users = self.db.get_all_users()
        
        users_list = ft.Column(spacing=8)
        for u in users:
            users_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(u['username'], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    bgcolor=ft.Colors.GREEN.with_opacity(0.2) if u['status'] == 'active' else ft.Colors.RED.with_opacity(0.2),
                                    border_radius=10,
                                    content=ft.Text("نشط" if u['status'] == 'active' else "محظور", size=10),
                                ),
                            ]),
                            ft.Text(u['email'], size=12, color=ft.Colors.GREY_600),
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.BLOCK,
                                    on_click=lambda e, uid=u['id'], s=u['status']: self.toggle_user_status(uid, s),
                                    icon_color=ft.Colors.ORANGE,
                                ),
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    on_click=lambda e, uid=u['id']: self.delete_user_account(uid),
                                    icon_color=ft.Colors.RED,
                                ),
                            ], alignment=ft.MainAxisAlignment.END),
                        ], spacing=8)
                    )
                )
            )
        
        self.main_content.content = ft.Column([
            ft.Text("👥 إدارة المستخدمين", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"إجمالي المستخدمين: {len(users)}", size=13, color=ft.Colors.GREY_600),
            users_list,
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def toggle_user_status(self, user_id, current_status):
        new_status = 'banned' if current_status == 'active' else 'active'
        self.db.update_user_status(user_id, new_status)
        self.show_snackbar(f"تم {'حظر' if new_status == 'banned' else 'تنشيط'} المستخدم")
        self.show_admin_users(self.user)
    
    def delete_user_account(self, user_id):
        self.db.delete_user(user_id)
        self.show_snackbar("تم حذف المستخدم")
        self.show_admin_users(self.user)
    
    def show_admin_projects(self, user):
        projects = self.db.get_all_projects_admin()
        
        projects_list = ft.Column(spacing=8)
        for p in projects:
            projects_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Text(p['title'], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(p['description'][:80] + "...", size=12, color=ft.Colors.GREY_600),
                            ft.Row([
                                ft.Text(f"💰 {p['budget']}$", size=12, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                                ft.Text(f"👤 {p['client_name']}", size=11, color=ft.Colors.GREY_500),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    on_click=lambda e, pid=p['id']: self.delete_project_item(pid),
                                    icon_color=ft.Colors.RED,
                                ),
                            ], alignment=ft.MainAxisAlignment.END),
                        ], spacing=8)
                    )
                )
            )
        
        self.main_content.content = ft.Column([
            ft.Text("📋 إدارة المشاريع", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"إجمالي المشاريع: {len(projects)}", size=13, color=ft.Colors.GREY_600),
            projects_list,
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def delete_project_item(self, project_id):
        self.db.delete_project(project_id)
        self.show_snackbar("تم حذف المشروع")
        self.show_admin_projects(self.user)
    
    def show_client_dashboard(self, user):
        """لوحة تحكم صاحب العمل"""
        self.page.clean()
        self.page.title = "لوحة تحكم صاحب العمل"
        
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"مرحباً {user['username']} 👋", size=18),
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            actions=[ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: self.logout())],
        )
        
        # إحصائيات
        projects_count = self.db.get_user_projects_count(user['id'])
        
        stats = ft.Container(
            width=self.page.window_width - 30,
            padding=20,
            bgcolor=ft.Colors.BLUE.with_opacity(0.1),
            border_radius=15,
            content=ft.Column([
                ft.Icon(ft.Icons.PROJECT, size=40, color=ft.Colors.BLUE),
                ft.Text(str(projects_count), size=32, weight=ft.FontWeight.BOLD),
                ft.Text("المشاريع المنشورة", size=13),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        # مشاريعي
        my_projects = self.db.get_projects_by_client(user['id'])
        projects_list = ft.Column(spacing=8)
        for p in my_projects[:5]:
            projects_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(p['title'], size=15, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    bgcolor=ft.Colors.GREEN.with_opacity(0.2),
                                    border_radius=10,
                                    content=ft.Text(p['status'], size=10),
                                ),
                            ]),
                            ft.Text(p['description'][:60] + "...", size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"💰 {p['budget']}$", size=12, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                        ], spacing=6)
                    )
                )
            )
        
        if not my_projects:
            projects_list.controls.append(
                ft.Text("لا توجد مشاريع بعد", size=14, color=ft.Colors.GREY_500)
            )
        
        # شريط التنقل
        nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.DASHBOARD, label="الرئيسية"),
                ft.NavigationDestination(icon=ft.Icons.ADD_CIRCLE, label="مشروع جديد"),
                ft.NavigationDestination(icon=ft.Icons.LIST_ALT, label="مشاريعي"),
                ft.NavigationDestination(icon=ft.Icons.CHAT, label="المحادثات"),
            ],
            on_change=lambda e: self.client_nav_change(e, user),
            bgcolor=ft.Colors.WHITE,
        )
        
        self.main_content = ft.Container(
            expand=True,
            padding=15,
            content=ft.Column([
                ft.Text("📊 لوحة التحكم", size=22, weight=ft.FontWeight.BOLD),
                stats,
                ft.Text("📋 آخر مشاريعي", size=18, weight=ft.FontWeight.BOLD),
                projects_list,
                ft.ElevatedButton("➕ مشروع جديد", on_click=lambda e: self.show_new_project_form(user), width=200),
            ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        self.page.add(ft.Column([self.main_content, nav_bar], expand=True, spacing=0))
        self.page.update()
    
    def client_nav_change(self, e, user):
        index = e.control.selected_index
        if index == 0:
            self.show_client_dashboard(user)
        elif index == 1:
            self.show_new_project_form(user)
        elif index == 2:
            self.show_client_projects(user)
        elif index == 3:
            self.show_chats(user)
    
    def show_new_project_form(self, user):
        title = ft.TextField(label="عنوان المشروع", width=self.page.window_width - 50)
        desc = ft.TextField(label="وصف المشروع", multiline=True, min_lines=3, width=self.page.window_width - 50)
        category = ft.Dropdown(
            label="نوع العمل",
            width=self.page.window_width - 50,
            options=[
                ft.dropdown.Option("برمجة"),
                ft.dropdown.Option("تصميم"),
                ft.dropdown.Option("كتابة"),
                ft.dropdown.Option("تسويق"),
            ]
        )
        location = ft.Dropdown(
            label="الموقع",
            width=self.page.window_width - 50,
            options=[ft.dropdown.Option("Remote", "عن بعد"), ft.dropdown.Option("On-site", "في الموقع")]
        )
        budget = ft.TextField(label="الميزانية ($)", width=self.page.window_width - 50, keyboard_type=ft.KeyboardType.NUMBER)
        
        def save_project(e):
            if not all([title.value, desc.value, category.value, location.value, budget.value]):
                self.show_snackbar("الرجاء تعبئة جميع الحقول")
                return
            try:
                self.db.create_project(user['id'], title.value, desc.value, category.value, location.value, float(budget.value))
                self.show_snackbar("تم إنشاء المشروع بنجاح!")
                self.show_client_dashboard(user)
            except:
                self.show_snackbar("حدث خطأ")
        
        self.main_content.content = ft.Column([
            ft.Text("➕ مشروع جديد", size=22, weight=ft.FontWeight.BOLD),
            title, desc, category, location, budget,
            ft.Row([
                ft.OutlinedButton("إلغاء", on_click=lambda e: self.show_client_dashboard(user)),
                ft.ElevatedButton("نشر", on_click=save_project, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def show_client_projects(self, user):
        projects = self.db.get_projects_by_client(user['id'])
        
        projects_list = ft.Column(spacing=8)
        for p in projects:
            proposals = self.db.get_proposals_for_project(p['id'])
            projects_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Text(p['title'], size=16, weight=ft.FontWeight.BOLD),
                            ft.Text(p['description'][:80] + "...", size=12, color=ft.Colors.GREY_600),
                            ft.Row([
                                ft.Text(f"💰 {p['budget']}$", size=12, color=ft.Colors.GREEN),
                                ft.Text(f"📋 {len(proposals)} عروض", size=11, color=ft.Colors.BLUE),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.ElevatedButton("عرض العروض", on_click=lambda e, pid=p['id']: self.show_proposals_list(pid, user), size="small"),
                        ], spacing=8)
                    )
                )
            )
        
        self.main_content.content = ft.Column([
            ft.Text("📋 مشاريعي", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"الإجمالي: {len(projects)}", size=13, color=ft.Colors.GREY_600),
            projects_list,
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def show_proposals_list(self, project_id, user):
        proposals = self.db.get_proposals_for_project(project_id)
        project = self.db.get_project_by_id(project_id)
        
        proposals_list = ft.Column(spacing=8)
        for p in proposals:
            proposals_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Text(p['freelancer_name'], size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(p['description'], size=12, color=ft.Colors.GREY_600),
                            ft.Text(f"💰 {p['price']}$", size=13, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.ElevatedButton("قبول", on_click=lambda e, pid=p['id']: self.accept_proposal(pid, project_id, user), 
                                                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE), size="small"),
                                ft.OutlinedButton("رفض", on_click=lambda e, pid=p['id']: self.reject_proposal(pid, project_id, user), size="small"),
                            ], alignment=ft.MainAxisAlignment.END, spacing=8),
                        ], spacing=8)
                    )
                )
            )
        
        if not proposals:
            proposals_list.controls.append(ft.Text("لا توجد عروض بعد", size=14, color=ft.Colors.GREY_500))
        
        self.main_content.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.show_client_projects(user)),
                ft.Text(f"عروض: {project['title'][:20]}", size=18, weight=ft.FontWeight.BOLD, expand=True),
            ]),
            proposals_list,
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def accept_proposal(self, proposal_id, project_id, user):
        self.db.update_proposal_status(proposal_id, 'accepted')
        self.show_snackbar("تم قبول العرض!")
        self.show_proposals_list(project_id, user)
    
    def reject_proposal(self, proposal_id, project_id, user):
        self.db.update_proposal_status(proposal_id, 'rejected')
        self.show_snackbar("تم رفض العرض")
        self.show_proposals_list(project_id, user)
    
    def show_freelancer_dashboard(self, user):
        """لوحة تحكم المستقل"""
        self.page.clean()
        self.page.title = "لوحة تحكم المستقل"
        
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"مرحباً {user['username']} 👋", size=18),
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            actions=[ft.IconButton(ft.Icons.LOGOUT, on_click=lambda e: self.logout())],
        )
        
        # المشاريع المتاحة
        projects = self.db.get_all_projects()
        
        projects_list = ft.Column(spacing=8)
        for p in projects[:10]:
            projects_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(p['title'], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Text(f"💰 {p['budget']}$", size=13, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                            ]),
                            ft.Text(p['description'][:80] + "...", size=12, color=ft.Colors.GREY_600),
                            ft.Row([
                                ft.Text(f"📂 {p['category']}", size=11, color=ft.Colors.GREY_500),
                                ft.Text(f"📍 {'عن بعد' if p['location'] == 'Remote' else 'في الموقع'}", size=11, color=ft.Colors.GREY_500),
                                ft.Text(f"👤 {p['client_name']}", size=11, color=ft.Colors.GREY_500),
                            ], spacing=8, wrap=True),
                            ft.ElevatedButton("📝 تقديم عرض", on_click=lambda e, pid=p['id'], title=p['title'], budget=p['budget']: self.show_proposal_form(pid, title, budget, user), size="small"),
                        ], spacing=8)
                    )
                )
            )
        
        if not projects:
            projects_list.controls.append(
                ft.Text("لا توجد مشاريع متاحة حالياً", size=14, color=ft.Colors.GREY_500)
            )
        
        # شريط التنقل
        nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.SEARCH, label="المشاريع"),
                ft.NavigationDestination(icon=ft.Icons.PROPOSAL, label="عروضي"),
                ft.NavigationDestination(icon=ft.Icons.PERSON, label="البروفايل"),
                ft.NavigationDestination(icon=ft.Icons.CHAT, label="المحادثات"),
            ],
            on_change=lambda e: self.freelancer_nav_change(e, user),
            bgcolor=ft.Colors.WHITE,
        )
        
        self.main_content = ft.Container(
            expand=True,
            padding=15,
            content=ft.Column([
                ft.Text("🔍 المشاريع المتاحة", size=22, weight=ft.FontWeight.BOLD),
                ft.Text(f"عدد المشاريع: {len(projects)}", size=13, color=ft.Colors.GREY_600),
                projects_list,
            ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        self.page.add(ft.Column([self.main_content, nav_bar], expand=True, spacing=0))
        self.page.update()
    
    def freelancer_nav_change(self, e, user):
        index = e.control.selected_index
        if index == 0:
            self.show_freelancer_dashboard(user)
        elif index == 1:
            self.show_my_proposals_list(user)
        elif index == 2:
            self.show_profile(user)
        elif index == 3:
            self.show_chats(user)
    
    def show_proposal_form(self, project_id, project_title, max_budget, user):
        desc = ft.TextField(label="وصف العرض", multiline=True, min_lines=3, width=self.page.window_width - 50)
        price = ft.TextField(label="السعر المقترح ($)", width=self.page.window_width - 50, keyboard_type=ft.KeyboardType.NUMBER)
        
        def submit_proposal(e):
            if not desc.value or not price.value:
                self.show_snackbar("الرجاء تعبئة جميع الحقول")
                return
            try:
                p = float(price.value)
                if p > max_budget:
                    self.show_snackbar(f"السعر لا يمكن أن يتجاوز {max_budget}$")
                    return
                if self.db.create_proposal(project_id, user['id'], desc.value, p):
                    self.show_snackbar("تم تقديم العرض بنجاح!")
                    dialog.open = False
                    self.show_freelancer_dashboard(user)
                else:
                    self.show_snackbar("حدث خطأ")
            except:
                self.show_snackbar("السعر يجب أن يكون رقماً")
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"تقديم عرض: {project_title}"),
            content=ft.Container(width=350, padding=15, content=ft.Column([desc, price], spacing=15)),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("إرسال", on_click=submit_proposal),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_my_proposals_list(self, user):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.description, p.price, p.status, pr.title 
                FROM proposals p JOIN projects pr ON p.project_id = pr.id
                WHERE p.freelancer_id = ?
                ORDER BY p.created_at DESC
            """, (user['id'],))
            proposals = cursor.fetchall()
        
        proposals_list = ft.Column(spacing=8)
        for p in proposals:
            status_color = ft.Colors.ORANGE
            if p[2] == 'accepted':
                status_color = ft.Colors.GREEN
            elif p[2] == 'rejected':
                status_color = ft.Colors.RED
            
            proposals_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Text(p[3], size=15, weight=ft.FontWeight.BOLD),
                            ft.Text(p[0][:80] + "...", size=12, color=ft.Colors.GREY_600),
                            ft.Row([
                                ft.Text(f"💰 {p[1]}$", size=13, color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                    bgcolor=status_color.with_opacity(0.2),
                                    border_radius=10,
                                    content=ft.Text(p[2], size=10, color=status_color),
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ], spacing=8)
                    )
                )
            )
        
        if not proposals:
            proposals_list.controls.append(ft.Text("لم تقدم أي عروض بعد", size=14, color=ft.Colors.GREY_500))
        
        self.main_content.content = ft.Column([
            ft.Text("📋 عروضي", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"إجمالي العروض: {len(proposals)}", size=13, color=ft.Colors.GREY_600),
            proposals_list,
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def show_profile(self, user):
        proposals_count = self.db.get_user_proposals_count(user['id'])
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proposals WHERE freelancer_id = ? AND status = 'accepted'", (user['id'],))
            accepted = cursor.fetchone()[0]
        
        self.main_content.content = ft.Column([
            ft.Text("👤 البروفايل", size=22, weight=ft.FontWeight.BOLD),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.CircleAvatar(content=ft.Text(user['username'][0].upper(), size=30), bgcolor=ft.Colors.BLUE_200, radius=40),
                        ft.Text(user['username'], size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(user['email'], size=13, color=ft.Colors.GREY_600),
                        ft.Container(padding=ft.padding.symmetric(horizontal=12, vertical=4), bgcolor=ft.Colors.GREEN.with_opacity(0.2), border_radius=15, content=ft.Text("مستقل", size=12, color=ft.Colors.GREEN)),
                        ft.Divider(),
                        ft.Row([
                            ft.Container(expand=True, padding=10, bgcolor=ft.Colors.BLUE.with_opacity(0.1), border_radius=10, content=ft.Column([
                                ft.Text(str(proposals_count), size=24, weight=ft.FontWeight.BOLD), ft.Text("إجمالي العروض", size=11, color=ft.Colors.GREY_600),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                            ft.Container(expand=True, padding=10, bgcolor=ft.Colors.GREEN.with_opacity(0.1), border_radius=10, content=ft.Column([
                                ft.Text(str(accepted), size=24, weight=ft.FontWeight.BOLD), ft.Text("عروض مقبولة", size=11, color=ft.Colors.GREY_600),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                        ], spacing=10),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)
                )
            ),
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def show_chats(self, user):
        # جلب المحادثات
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT 
                    CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END as other_id,
                    u.username
                FROM messages m JOIN users u ON u.id = CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END
                WHERE sender_id = ? OR receiver_id = ?
            """, (user['id'], user['id'], user['id'], user['id']))
            chats = cursor.fetchall()
        
        if not chats:
            self.main_content.content = ft.Column([
                ft.Icon(ft.Icons.CHAT, size=80, color=ft.Colors.GREY_400),
                ft.Text("لا توجد محادثات بعد", size=16, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            self.page.update()
            return
        
        chats_list = ft.Column(spacing=8)
        for chat in chats:
            chats_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        on_click=lambda e, oid=chat[0], oname=chat[1]: self.open_chat(oid, oname, user),
                        content=ft.Row([
                            ft.CircleAvatar(content=ft.Text(chat[1][0].upper()), bgcolor=ft.Colors.BLUE_200),
                            ft.Text(chat[1], size=16, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                        ], spacing=10)
                    )
                )
            )
        
        self.main_content.content = ft.Column([
            ft.Text("💬 المحادثات", size=22, weight=ft.FontWeight.BOLD),
            chats_list,
        ], scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def open_chat(self, other_user_id, other_user_name, current_user):
        # جلب الرسائل
        messages = self.db.get_messages(current_user['id'], other_user_id)
        
        messages_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=8)
        for m in messages:
            is_me = m['sender_id'] == current_user['id']
            messages_list.controls.append(
                ft.Row([
                    ft.Container(
                        padding=10,
                        bgcolor=ft.Colors.BLUE_600 if is_me else ft.Colors.GREY_300,
                        border_radius=ft.border_radius.only(top_left=12, top_right=12, bottom_left=0 if is_me else 12, bottom_right=12 if is_me else 0),
                        content=ft.Text(m['message'], color=ft.Colors.WHITE if is_me else ft.Colors.BLACK, size=13),
                        max_width=250,
                    )
                ], alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START)
            )
        
        message_input = ft.TextField(hint_text="اكتب رسالتك...", expand=True, border_radius=25, filled=True, bgcolor=ft.Colors.GREY_100)
        
        def send_message(e):
            if message_input.value:
                self.db.send_message(current_user['id'], other_user_id, message_input.value)
                self.open_chat(other_user_id, other_user_name, current_user)
        
        send_btn = ft.IconButton(ft.Icons.SEND, on_click=send_message, icon_size=28, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, shape=ft.CircleBorder()))
        
        self.main_content.content = ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.show_chats(current_user)),
                ft.Text(other_user_name, size=18, weight=ft.FontWeight.BOLD, expand=True),
            ]),
            ft.Container(expand=True, content=messages_list),
            ft.Row([message_input, send_btn], spacing=10),
        ], expand=True, spacing=10)
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snackbar(self, message):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), action="OK", duration=2000)
        self.page.snack_bar.open = True
        self.page.update()
    
    def logout(self):
        self.clear_session()
        self.show_login()

def main(page: ft.Page):
    app = FreelancingPlatform(page)

if __name__ == "__main__":
    ft.app(target=main)
