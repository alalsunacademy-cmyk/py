"""
client_dashboard.py - لوحة تحكم صاحب العمل مع تصميم محمول
"""

import flet as ft
from database import Database

class ClientDashboard:
    """لوحة تحكم صاحب العمل"""
    
    def __init__(self, page: ft.Page, db: Database, user_data: dict, clear_session_callback):
        self.page = page
        self.db = db
        self.user = user_data
        self.clear_session = clear_session_callback
        self.current_tab_index = 0
    
    def build(self):
        """بناء واجهة لوحة تحكم العميل"""
        self.page.clean()
        self.page.title = f"مرحباً {self.user['username']}"
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 0
        
        # شريط التطبيق العلوي
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"مرحباً {self.user['username']} 👋", size=18, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: self.refresh_view(), tooltip="تحديث"),
                ft.IconButton(ft.Icons.LOGOUT, on_click=self.logout, tooltip="تسجيل الخروج"),
            ],
        )
        
        # شريط التنقل السفلي
        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.DASHBOARD, label="الرئيسية"),
                ft.NavigationDestination(icon=ft.Icons.ADD_CIRCLE, label="مشروع جديد"),
                ft.NavigationDestination(icon=ft.Icons.LIST_ALT, label="مشاريعي"),
                ft.NavigationDestination(icon=ft.Icons.CHAT, label="المحادثات"),
            ],
            on_change=self.nav_change,
            bgcolor=ft.Colors.WHITE,
        )
        
        # منطقة المحتوى الرئيسية
        self.content_area = ft.Container(
            expand=True,
            padding=ft.padding.all(15),
            content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        layout = ft.Column(expand=True, spacing=0, controls=[self.content_area, self.nav_bar])
        self.page.add(layout)
        self.load_dashboard()
    
    def nav_change(self, e):
        self.current_tab_index = e.control.selected_index
        if self.current_tab_index == 0:
            self.load_dashboard()
        elif self.current_tab_index == 1:
            self.show_create_project()
        elif self.current_tab_index == 2:
            self.show_my_projects()
        elif self.current_tab_index == 3:
            self.show_chats()
    
    def refresh_view(self):
        if self.current_tab_index == 0:
            self.load_dashboard()
        elif self.current_tab_index == 1:
            self.show_create_project()
        elif self.current_tab_index == 2:
            self.show_my_projects()
        elif self.current_tab_index == 3:
            self.show_chats()
    
    def load_dashboard(self):
        """تحميل لوحة التحكم الرئيسية"""
        projects_count = self.db.get_user_projects_count(self.user['id'])
        
        self.content_area.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        padding=20,
                        width=self.page.window_width - 30,
                        content=ft.Column([
                            ft.Text("📊 نظرة عامة", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            ft.Container(
                                padding=20,
                                bgcolor=ft.Colors.BLUE.with_opacity(0.1),
                                border_radius=15,
                                content=ft.Column([
                                    ft.Icon(ft.Icons.PROJECT, size=40, color=ft.Colors.BLUE),
                                    ft.Text(str(projects_count), size=32, weight=ft.FontWeight.BOLD),
                                    ft.Text("المشاريع المنشورة", size=13, color=ft.Colors.GREY_700),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
                            ),
                            ft.ElevatedButton(
                                "➕ مشروع جديد",
                                on_click=lambda e: self.show_create_project(),
                                icon=ft.Icons.ADD,
                                width=200,
                            )
                        ], spacing=15)
                    )
                ),
                ft.Text("📋 آخر المشاريع", size=18, weight=ft.FontWeight.BOLD),
            ]
        )
        
        projects = self.db.get_projects_by_client(self.user['id'])[:5]
        if projects:
            for project in projects:
                self.content_area.content.controls.append(self._project_card(project))
        else:
            self.content_area.content.controls.append(
                ft.Container(
                    padding=30,
                    content=ft.Column([
                        ft.Icon(ft.Icons.FOLDER_OPEN, size=60, color=ft.Colors.GREY_400),
                        ft.Text("لا توجد مشاريع بعد", size=14, color=ft.Colors.GREY_600),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                )
            )
        self.page.update()
    
    def _project_card(self, project):
        """بطاقة مشروع"""
        status_color = ft.Colors.GREEN if project['status'] == 'open' else ft.Colors.ORANGE
        status_text = "مفتوح" if project['status'] == 'open' else "مغلق"
        proposals_count = len(self.db.get_proposals_for_project(project['id']))
        
        return ft.Card(
            margin=ft.margin.only(bottom=8),
            content=ft.Container(
                padding=12,
                width=self.page.window_width - 30,
                content=ft.Column([
                    ft.Row([
                        ft.Text(project['title'], size=16, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            bgcolor=status_color.with_opacity(0.2),
                            border_radius=15,
                            content=ft.Text(status_text, size=10, color=status_color)
                        ),
                    ]),
                    ft.Text(project['description'][:80] + ("..." if len(project['description']) > 80 else ""), size=12, color=ft.Colors.GREY_700),
                    ft.Row([
                        ft.Icon(ft.Icons.PROPOSAL, size=14, color=ft.Colors.BLUE),
                        ft.Text(f"{proposals_count} عروض", size=11, color=ft.Colors.BLUE),
                        ft.ElevatedButton("عرض", on_click=lambda e, pid=project['id']: self.show_proposals(pid), 
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=8)
            )
        )
    
    def show_create_project(self):
        """عرض نموذج إنشاء مشروع جديد"""
        title_field = ft.TextField(label="عنوان المشروع", width=self.page.window_width - 50)
        desc_field = ft.TextField(label="وصف المشروع", multiline=True, min_lines=4, width=self.page.window_width - 50)
        category_dropdown = ft.Dropdown(
            label="نوع العمل", width=self.page.window_width - 50,
            options=[ft.dropdown.Option("برمجة", "💻 برمجة"), ft.dropdown.Option("تصميم", "🎨 تصميم"),
                    ft.dropdown.Option("كتابة", "✍️ كتابة"), ft.dropdown.Option("تسويق", "📢 تسويق")]
        )
        location_dropdown = ft.Dropdown(
            label="الموقع", width=self.page.window_width - 50,
            options=[ft.dropdown.Option("Remote", "🏠 عن بعد"), ft.dropdown.Option("On-site", "🏢 في الموقع")]
        )
        budget_field = ft.TextField(label="الميزانية ($)", width=self.page.window_width - 50, keyboard_type=ft.KeyboardType.NUMBER)
        
        def create_project(e):
            if not all([title_field.value, desc_field.value, category_dropdown.value, location_dropdown.value, budget_field.value]):
                self.show_snackbar("الرجاء تعبئة جميع الحقول", ft.Colors.RED)
                return
            try:
                budget = float(budget_field.value)
                self.db.create_project(self.user['id'], title_field.value, desc_field.value,
                                      category_dropdown.value, location_dropdown.value, budget)
                self.show_snackbar("تم إنشاء المشروع بنجاح!", ft.Colors.GREEN)
                self.current_tab_index = 2
                self.show_my_projects()
            except ValueError:
                self.show_snackbar("الميزانية يجب أن تكون رقماً", ft.Colors.RED)
        
        self.content_area.content = ft.Column([
            ft.Text("➕ مشروع جديد", size=24, weight=ft.FontWeight.BOLD),
            title_field, desc_field, category_dropdown, location_dropdown, budget_field,
            ft.Row([
                ft.ElevatedButton("إلغاء", on_click=lambda e: self.load_dashboard()),
                ft.ElevatedButton("نشر", on_click=create_project, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        self.page.update()
    
    def show_my_projects(self):
        """عرض مشاريعي"""
        projects = self.db.get_projects_by_client(self.user['id'])
        
        if not projects:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.FOLDER_OPEN, size=80, color=ft.Colors.GREY_400),
                ft.Text("لم تنشر أي مشاريع بعد", size=16, color=ft.Colors.GREY_600),
                ft.ElevatedButton("➕ مشروع جديد", on_click=lambda e: self.show_create_project()),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            self.page.update()
            return
        
        self.content_area.content = ft.Column([
            ft.Text("📋 مشاريعي", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"الإجمالي: {len(projects)}", size=13, color=ft.Colors.GREY_600),
        ] + [self._project_card(p) for p in projects], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def show_proposals(self, project_id):
        """عرض العروض المقدمة"""
        proposals = self.db.get_proposals_for_project(project_id)
        project = self.db.get_project_by_id(project_id)
        
        if not proposals:
            self.content_area.content = ft.Column([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.show_my_projects(), alignment=ft.alignment.center_left),
                ft.Text(f"عروض: {project['title']}", size=18, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.PROPOSAL, size=80, color=ft.Colors.GREY_400),
                ft.Text("لا توجد عروض بعد", size=14, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            self.page.update()
            return
        
        proposal_cards = []
        for proposal in proposals:
            status_color = {'pending': ft.Colors.ORANGE, 'accepted': ft.Colors.GREEN, 'rejected': ft.Colors.RED}.get(proposal['status'], ft.Colors.GREY)
            status_text = {'pending': 'قيد المراجعة', 'accepted': 'مقبول', 'rejected': 'مرفوض'}.get(proposal['status'], proposal['status'])
            
            def make_accept(p_id=proposal['id'], pid=project_id):
                def accept(e):
                    self.db.update_proposal_status(p_id, 'accepted')
                    self.show_snackbar("تم قبول العرض!", ft.Colors.GREEN)
                    self.show_proposals(pid)
                return accept
            
            def make_reject(p_id=proposal['id'], pid=project_id):
                def reject(e):
                    self.db.update_proposal_status(p_id, 'rejected')
                    self.show_snackbar("تم رفض العرض", ft.Colors.ORANGE)
                    self.show_proposals(pid)
                return reject
            
            action_buttons = []
            if proposal['status'] == 'pending':
                action_buttons = [
                    ft.ElevatedButton("قبول", on_click=make_accept(), style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)),
                    ft.OutlinedButton("رفض", on_click=make_reject()),
                ]
            
            proposal_cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(proposal['freelancer_name'], size=15, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(padding=ft.padding.symmetric(horizontal=6, vertical=2), bgcolor=status_color.with_opacity(0.2),
                                            border_radius=12, content=ft.Text(status_text, size=10, color=status_color))
                            ]),
                            ft.Text(proposal['description'][:100], size=12, color=ft.Colors.GREY_700),
                            ft.Text(f"💰 {proposal['price']} $", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                            ft.Row(action_buttons, spacing=8) if action_buttons else ft.Container(),
                        ], spacing=8)
                    )
                )
            )
        
        self.content_area.content = ft.Column([
            ft.Row([ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.show_my_projects()), ft.Text(f"📋 عروض: {project['title'][:20]}", size=16, weight=ft.FontWeight.BOLD, expand=True)]),
        ] + proposal_cards, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def show_chats(self):
        from chat_system import ChatSystem
        ChatSystem(self.page, self.db, self.user).show_chats()
    
    def show_snackbar(self, message, color):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color, action="OK", duration=3000)
        self.page.snack_bar.open = True
        self.page.update()
    
    def logout(self, e):
        self.clear_session()
        from main import FreelancingPlatform
        FreelancingPlatform(self.page)