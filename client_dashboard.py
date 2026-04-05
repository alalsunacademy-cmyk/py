"""
client_dashboard.py - لوحة تحكم صاحب العمل
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
        self.current_view = None
    
    def build(self):
        """بناء واجهة لوحة تحكم العميل"""
        self.page.clean()
        self.page.title = f"منصة العمل الحر - مرحباً {self.user['username']}"
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # شريط التطبيق العلوي
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"مرحباً {self.user['username']} 👋", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: self.refresh_view(), tooltip="تحديث"),
                ft.IconButton(ft.Icons.LOGOUT, on_click=self.logout, tooltip="تسجيل الخروج"),
            ]
        )
        
        # قائمة التنقل الجانبية
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            leading=ft.Icon(ft.Icons.WORK, size=40, color=ft.Colors.BLUE_700),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD,
                    selected_icon=ft.Icons.DASHBOARD_OUTLINED,
                    label="الرئيسية"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ADD_CIRCLE,
                    selected_icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    label="مشروع جديد"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST_ALT,
                    selected_icon=ft.Icons.LIST_ALT_OUTLINED,
                    label="مشاريعي"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.CHAT,
                    selected_icon=ft.Icons.CHAT_OUTLINED,
                    label="المحادثات"
                ),
            ],
            on_change=self.nav_change,
        )
        
        # منطقة المحتوى الرئيسية
        self.content_area = ft.Container(
            expand=True,
            padding=20,
            content=ft.Column(scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        # تخطيط الصفحة
        layout = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                self.nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area,
            ]
        )
        
        self.page.add(layout)
        self.load_dashboard()
    
    def nav_change(self, e):
        """تغيير التنقل"""
        index = self.nav_rail.selected_index
        if index == 0:
            self.load_dashboard()
        elif index == 1:
            self.show_create_project()
        elif index == 2:
            self.show_my_projects()
        elif index == 3:
            self.show_chats()
    
    def refresh_view(self):
        """تحديث العرض الحالي"""
        index = self.nav_rail.selected_index
        if index == 0:
            self.load_dashboard()
        elif index == 1:
            self.show_create_project()
        elif index == 2:
            self.show_my_projects()
        elif index == 3:
            self.show_chats()
    
    def load_dashboard(self):
        """تحميل لوحة التحكم الرئيسية"""
        projects_count = self.db.get_user_projects_count(self.user['id'])
        
        self.content_area.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        width=400,
                        padding=20,
                        content=ft.Column([
                            ft.Text("📊 نظرة عامة", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            ft.Row([
                                self._stat_card("المشاريع المنشورة", projects_count, ft.Icons.PROJECT, ft.Colors.BLUE),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                            ft.ElevatedButton(
                                "➕ إنشاء مشروع جديد",
                                on_click=lambda e: self.show_create_project(),
                                icon=ft.Icons.ADD,
                                width=250,
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
                    )
                ),
                ft.Text("📋 أحدث المشاريع", size=20, weight=ft.FontWeight.BOLD),
            ]
        )
        
        # عرض آخر 5 مشاريع
        projects = self.db.get_projects_by_client(self.user['id'])[:5]
        if projects:
            for project in projects:
                self.content_area.content.controls.append(self._project_card(project))
        else:
            self.content_area.content.controls.append(
                ft.Container(
                    padding=50,
                    content=ft.Column([
                        ft.Icon(ft.Icons.FOLDER_OPEN, size=80, color=ft.Colors.GREY_400),
                        ft.Text("لا توجد مشاريع بعد", size=16, color=ft.Colors.GREY_600),
                        ft.Text("انقر على 'إنشاء مشروع جديد' للبدء", size=14, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                )
            )
        
        self.page.update()
    
    def _stat_card(self, title, value, icon, color):
        """بطاقة إحصائية"""
        return ft.Container(
            width=200,
            padding=20,
            bgcolor=color.with_opacity(0.1),
            border_radius=15,
            content=ft.Column([
                ft.Icon(icon, size=40, color=color),
                ft.Text(str(value), size=32, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=14, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        )
    
    def _project_card(self, project):
        """بطاقة مشروع"""
        status_color = ft.Colors.GREEN if project['status'] == 'open' else ft.Colors.ORANGE
        status_text = "مفتوح" if project['status'] == 'open' else "مغلق"
        
        proposals = self.db.get_proposals_for_project(project['id'])
        proposals_count = len(proposals)
        
        return ft.Card(
            elevation=2,
            margin=ft.margin.only(bottom=10),
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Row([
                        ft.Text(project['title'], size=18, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            bgcolor=status_color.with_opacity(0.2),
                            border_radius=20,
                            content=ft.Text(status_text, size=12, color=status_color)
                        ),
                    ]),
                    ft.Text(project['description'][:100] + ("..." if len(project['description']) > 100 else ""), size=14, color=ft.Colors.GREY_700),
                    ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, size=16, color=ft.Colors.GREY_600),
                        ft.Text(project['category'], size=12, color=ft.Colors.GREY_600),
                        ft.Icon(ft.Icons.LOCATION_ON, size=16, color=ft.Colors.GREY_600),
                        ft.Text(project['location'], size=12, color=ft.Colors.GREY_600),
                        ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.GREY_600),
                        ft.Text(f"{project['budget']} $", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                    ], spacing=10),
                    ft.Row([
                        ft.Icon(ft.Icons.PROPOSAL, size=16, color=ft.Colors.BLUE),
                        ft.Text(f"{proposals_count} عروض", size=12, color=ft.Colors.BLUE),
                        ft.ElevatedButton(
                            "عرض العروض",
                            icon=ft.Icons.VISIBILITY,
                            on_click=lambda e, pid=project['id']: self.show_proposals(pid)
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ])
            )
        )
    
    def show_create_project(self):
        """عرض نموذج إنشاء مشروع جديد"""
        title_field = ft.TextField(label="عنوان المشروع", width=500)
        desc_field = ft.TextField(label="وصف المشروع", multiline=True, min_lines=5, width=500)
        category_dropdown = ft.Dropdown(
            label="نوع العمل",
            width=500,
            options=[
                ft.dropdown.Option("برمجة", "💻 برمجة"),
                ft.dropdown.Option("تصميم", "🎨 تصميم"),
                ft.dropdown.Option("كتابة", "✍️ كتابة"),
                ft.dropdown.Option("تسويق", "📢 تسويق"),
                ft.dropdown.Option("ترجمة", "🌐 ترجمة"),
            ]
        )
        location_dropdown = ft.Dropdown(
            label="الموقع",
            width=500,
            options=[
                ft.dropdown.Option("Remote", "🏠 عن بعد (Remote)"),
                ft.dropdown.Option("On-site", "🏢 في الموقع (On-site)"),
            ]
        )
        budget_field = ft.TextField(label="الميزانية ($)", width=500, keyboard_type=ft.KeyboardType.NUMBER)
        
        def create_project(e):
            if not all([title_field.value, desc_field.value, category_dropdown.value, 
                       location_dropdown.value, budget_field.value]):
                self.show_snackbar("الرجاء تعبئة جميع الحقول", ft.Colors.RED)
                return
            
            try:
                budget = float(budget_field.value)
                self.db.create_project(
                    self.user['id'],
                    title_field.value,
                    desc_field.value,
                    category_dropdown.value,
                    location_dropdown.value,
                    budget
                )
                self.show_snackbar("تم إنشاء المشروع بنجاح!", ft.Colors.GREEN)
                self.nav_rail.selected_index = 2
                self.show_my_projects()
            except ValueError:
                self.show_snackbar("الميزانية يجب أن تكون رقماً صحيحاً", ft.Colors.RED)
        
        self.content_area.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Text("➕ إنشاء مشروع جديد", size=28, weight=ft.FontWeight.BOLD),
                ft.Text("أدخل تفاصيل المشروع الذي تريد نشره", size=14, color=ft.Colors.GREY_600),
                ft.Divider(width=500),
                title_field,
                desc_field,
                category_dropdown,
                location_dropdown,
                budget_field,
                ft.Row([
                    ft.ElevatedButton("إلغاء", on_click=lambda e: self.load_dashboard()),
                    ft.ElevatedButton("نشر المشروع", on_click=create_project, 
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)),
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            ]
        )
        self.page.update()
    
    def show_my_projects(self):
        """عرض مشاريعي"""
        projects = self.db.get_projects_by_client(self.user['id'])
        
        if not projects:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.FOLDER_OPEN, size=100, color=ft.Colors.GREY_400),
                ft.Text("لم تقم بنشر أي مشاريع بعد", size=18, color=ft.Colors.GREY_600),
                ft.Text("انقر على 'مشروع جديد' لبدء نشر مشروعك الأول", size=14, color=ft.Colors.GREY_500),
                ft.ElevatedButton("➕ إنشاء مشروع", on_click=lambda e: self.show_create_project()),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
            self.page.update()
            return
        
        self.content_area.content = ft.Column(
            spacing=15,
            controls=[
                ft.Text("📋 مشاريعي", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(f"إجمالي المشاريع: {len(projects)}", size=14, color=ft.Colors.GREY_600),
                ft.Divider(),
            ] + [self._project_card(p) for p in projects]
        )
        self.page.update()
    
    def show_proposals(self, project_id):
        """عرض العروض المقدمة لمشروع"""
        proposals = self.db.get_proposals_for_project(project_id)
        project = self.db.get_project_by_id(project_id)
        
        if not proposals:
            self.content_area.content = ft.Column([
                ft.Text(f"📋 عروض مشروع: {project['title']}", size=24, weight=ft.FontWeight.BOLD),
                ft.Icon(ft.Icons.PROPOSAL, size=100, color=ft.Colors.GREY_400),
                ft.Text("لا توجد عروض لهذا المشروع بعد", size=16, color=ft.Colors.GREY_600),
                ft.Text("سيتم إشعارك عند تقديم أي عروض", size=14, color=ft.Colors.GREY_500),
                ft.ElevatedButton("العودة", on_click=lambda e: self.show_my_projects()),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
            self.page.update()
            return
        
        proposal_cards = []
        for proposal in proposals:
            status_color = {
                'pending': ft.Colors.ORANGE,
                'accepted': ft.Colors.GREEN,
                'rejected': ft.Colors.RED
            }.get(proposal['status'], ft.Colors.GREY)
            
            status_text = {
                'pending': 'قيد المراجعة',
                'accepted': 'مقبول',
                'rejected': 'مرفوض'
            }.get(proposal['status'], proposal['status'])
            
            def accept_proposal(proposal_id=proposal['id'], pid=project_id):
                self.db.update_proposal_status(proposal_id, 'accepted')
                self.show_snackbar("تم قبول العرض!", ft.Colors.GREEN)
                self.show_proposals(pid)
            
            def reject_proposal(proposal_id=proposal['id'], pid=project_id):
                self.db.update_proposal_status(proposal_id, 'rejected')
                self.show_snackbar("تم رفض العرض", ft.Colors.ORANGE)
                self.show_proposals(pid)
            
            action_buttons = []
            if proposal['status'] == 'pending':
                action_buttons = [
                    ft.ElevatedButton("قبول", icon=ft.Icons.CHECK, on_click=accept_proposal, 
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN)),
                    ft.ElevatedButton("رفض", icon=ft.Icons.CLOSE, on_click=reject_proposal,
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
                ]
            
            proposal_cards.append(
                ft.Card(
                    elevation=2,
                    margin=ft.margin.only(bottom=10),
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(proposal['freelancer_name'], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    bgcolor=status_color.with_opacity(0.2),
                                    border_radius=20,
                                    content=ft.Text(status_text, size=12, color=status_color)
                                ),
                            ]),
                            ft.Text(proposal['description'], size=14, color=ft.Colors.GREY_700),
                            ft.Row([
                                ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.GREEN),
                                ft.Text(f"{proposal['price']} $", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                                ft.Text(f"تاريخ التقديم: {proposal['created_at']}", size=12, color=ft.Colors.GREY_500),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row(action_buttons, spacing=10, alignment=ft.MainAxisAlignment.CENTER) if action_buttons else ft.Container(),
                        ])
                    )
                )
            )
        
        self.content_area.content = ft.Column(
            spacing=15,
            controls=[
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.show_my_projects()),
                    ft.Text(f"📋 عروض مشروع: {project['title']}", size=24, weight=ft.FontWeight.BOLD, expand=True),
                ]),
                ft.Divider(),
            ] + proposal_cards
        )
        self.page.update()
    
    def show_chats(self):
        """عرض المحادثات"""
        from chat_system import ChatSystem
        
        chat_system = ChatSystem(self.page, self.db, self.user)
        chat_system.show_chats()
    
    def show_snackbar(self, message, color):
        """عرض إشعار"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color, action="OK")
        self.page.snack_bar.open = True
        self.page.update()
    
    def logout(self, e):
        """تسجيل الخروج"""
        self.clear_session()
        from main import FreelancingPlatform
        FreelancingPlatform(self.page)