"""
freelancer_dashboard.py - لوحة تحكم المستقل (Freelancer)
"""

import flet as ft
from database import Database

class FreelancerDashboard:
    """لوحة تحكم المستقل"""
    
    def __init__(self, page: ft.Page, db: Database, user_data: dict):
        self.page = page
        self.db = db
        self.user = user_data
        self.current_filter_category = None
        self.current_filter_location = None
    
    def build(self):
        """بناء واجهة لوحة تحكم المستقل"""
        self.page.clean()
        self.page.title = f"منصة العمل الحر - مرحباً {self.user['username']}"
        self.page.bgcolor = ft.Colors.GREY_50
        
        # شريط التطبيق العلوي
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"مرحباً {self.user['username']} 👋", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(ft.Icons.REFRESH, on_click=lambda e: self.refresh_view()),
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
                    icon=ft.Icons.SEARCH,
                    selected_icon=ft.Icons.SEARCH_OUTLINED,
                    label="استعراض المشاريع"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PROPOSAL,
                    selected_icon=ft.Icons.PROPOSAL_OUTLINED,
                    label="عروضي"
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
            content=ft.Column(scroll=ft.ScrollMode.AUTO)
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
        self.load_projects()
    
    def nav_change(self, e):
        """تغيير التنقل"""
        index = self.nav_rail.selected_index
        if index == 0:
            self.load_projects()
        elif index == 1:
            self.show_my_proposals()
        elif index == 2:
            self.show_chats()
    
    def refresh_view(self):
        """تحديث العرض الحالي"""
        index = self.nav_rail.selected_index
        if index == 0:
            self.load_projects()
        elif index == 1:
            self.show_my_proposals()
        elif index == 2:
            self.show_chats()
    
    def load_projects(self):
        """تحميل قائمة المشاريع مع الفلاتر"""
        projects = self.db.get_all_projects(
            category=self.current_filter_category,
            location=self.current_filter_location
        )
        
        # إنشاء شريط الفلاتر
        filter_row = ft.Container(
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            content=ft.Row([
                ft.Text("🔍 فلترة:", size=16, weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    width=150,
                    hint_text="نوع العمل",
                    options=[
                        ft.dropdown.Option(None, "الكل"),
                        ft.dropdown.Option("برمجة", "برمجة"),
                        ft.dropdown.Option("تصميم", "تصميم"),
                        ft.dropdown.Option("كتابة", "كتابة"),
                        ft.dropdown.Option("تسويق", "تسويق"),
                        ft.dropdown.Option("ترجمة", "ترجمة"),
                    ],
                    value=self.current_filter_category,
                    on_change=self.filter_by_category,
                ),
                ft.Dropdown(
                    width=150,
                    hint_text="الموقع",
                    options=[
                        ft.dropdown.Option(None, "الكل"),
                        ft.dropdown.Option("Remote", "عن بعد"),
                        ft.dropdown.Option("On-site", "في الموقع"),
                    ],
                    value=self.current_filter_location,
                    on_change=self.filter_by_location,
                ),
                ft.IconButton(ft.Icons.CLEAR, on_click=self.clear_filters, tooltip="إلغاء الفلاتر"),
            ], spacing=10)
        )
        
        if not projects:
            self.content_area.content = ft.Column([
                filter_row,
                ft.Icon(ft.Icons.FOLDER_OPEN, size=100, color=ft.Colors.GREY_400),
                ft.Text("لا توجد مشاريع متاحة حالياً", size=18, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
            return
        
        self.content_area.content = ft.Column(
            spacing=15,
            controls=[
                filter_row,
                ft.Text(f"📊 المشاريع المتاحة: {len(projects)}", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
            ] + [self._project_card(p) for p in projects]
        )
    
    def filter_by_category(self, e):
        """فلترة حسب نوع العمل"""
        self.current_filter_category = e.control.value
        self.load_projects()
    
    def filter_by_location(self, e):
        """فلترة حسب الموقع"""
        self.current_filter_location = e.control.value
        self.load_projects()
    
    def clear_filters(self, e):
        """إلغاء الفلاتر"""
        self.current_filter_category = None
        self.current_filter_location = None
        self.load_projects()
    
    def _project_card(self, project):
        """بطاقة مشروع"""
        return ft.Card(
            elevation=3,
            margin=ft.margin.only(bottom=10),
            content=ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Row([
                        ft.Text(project['title'], size=20, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            bgcolor=ft.Colors.GREEN.with_opacity(0.2),
                            border_radius=20,
                            content=ft.Text(f"{project['budget']} $", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
                        ),
                    ]),
                    ft.Text(project['description'][:150] + "...", size=14, color=ft.Colors.GREY_700),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.GREY_600),
                        ft.Text(project['client_name'], size=12, color=ft.Colors.GREY_600),
                        ft.Icon(ft.Icons.CATEGORY, size=16, color=ft.Colors.GREY_600),
                        ft.Text(project['category'], size=12, color=ft.Colors.GREY_600),
                        ft.Icon(ft.Icons.LOCATION_ON, size=16, color=ft.Colors.GREY_600),
                        ft.Text("عن بعد" if project['location'] == "Remote" else "في الموقع", size=12, color=ft.Colors.GREY_600),
                    ], spacing=10),
                    ft.Row([
                        ft.TextButton("🔍 عرض التفاصيل", on_click=lambda e, p=project: self.show_project_details(p)),
                        ft.ElevatedButton("📝 تقديم عرض", on_click=lambda e, p=project: self.show_proposal_form(p),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)),
                    ], alignment=ft.MainAxisAlignment.END, spacing=10),
                ])
            )
        )
    
    def show_project_details(self, project):
        """عرض تفاصيل المشروع"""
        dialog = ft.AlertDialog(
            title=ft.Text(project['title']),
            content=ft.Container(
                width=500,
                padding=20,
                content=ft.Column([
                    ft.Text(f"📝 الوصف:", weight=ft.FontWeight.BOLD),
                    ft.Text(project['description']),
                    ft.Divider(),
                    ft.Text(f"👤 صاحب المشروع: {project['client_name']}"),
                    ft.Text(f"📂 نوع العمل: {project['category']}"),
                    ft.Text(f"📍 الموقع: {'عن بعد' if project['location'] == 'Remote' else 'في الموقع'}"),
                    ft.Text(f"💰 الميزانية: {project['budget']} $", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                    ft.Text(f"📅 تاريخ النشر: {project['created_at']}"),
                ], spacing=10)
            ),
            actions=[
                ft.TextButton("إغلاق", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("تقديم عرض", on_click=lambda e: [self.close_dialog(dialog), self.show_proposal_form(project)]),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_proposal_form(self, project):
        """عرض نموذج تقديم العرض"""
        desc_field = ft.TextField(
            label="وصف العرض",
            multiline=True,
            min_lines=5,
            width=500,
            hint_text="اشرح لماذا أنت المرشح المناسب لهذا المشروع..."
        )
        price_field = ft.TextField(
            label="السعر المقترح ($)",
            width=500,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text=f"الميزانية المقترحة (الحد الأقصى: {project['budget']} $)"
        )
        
        def submit_proposal(e):
            if not desc_field.value or not price_field.value:
                self.show_snackbar("الرجاء تعبئة جميع الحقول", ft.Colors.RED)
                return
            
            try:
                price = float(price_field.value)
                if price > project['budget']:
                    self.show_snackbar(f"السعر المقترح لا يمكن أن يتجاوز {project['budget']} $", ft.Colors.RED)
                    return
                
                if self.db.create_proposal(project['id'], self.user['id'], desc_field.value, price):
                    self.show_snackbar("تم تقديم العرض بنجاح!", ft.Colors.GREEN)
                    self.close_dialog(dialog)
                else:
                    self.show_snackbar("حدث خطأ أثناء تقديم العرض", ft.Colors.RED)
            except ValueError:
                self.show_snackbar("السعر يجب أن يكون رقماً صحيحاً", ft.Colors.RED)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"تقديم عرض لمشروع: {project['title']}"),
            content=ft.Container(
                width=550,
                padding=20,
                content=ft.Column([
                    desc_field,
                    price_field,
                ], spacing=15)
            ),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("إرسال العرض", on_click=submit_proposal),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_my_proposals(self):
        """عرض عروضي المقدمة"""
        # جلب جميع العروض المقدمة من هذا المستخدم
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.description, p.price, p.status, p.created_at,
                       pr.title as project_title, pr.id as project_id
                FROM proposals p
                JOIN projects pr ON p.project_id = pr.id
                WHERE p.freelancer_id = ?
                ORDER BY p.created_at DESC
            """, (self.user['id'],))
            proposals = cursor.fetchall()
        
        if not proposals:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.PROPOSAL, size=100, color=ft.Colors.GREY_400),
                ft.Text("لم تقدم أي عروض بعد", size=18, color=ft.Colors.GREY_600),
                ft.ElevatedButton("🔍 استعراض المشاريع", on_click=lambda e: self.load_projects()),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)
            return
        
        proposal_cards = []
        for prop in proposals:
            status_color = {
                'pending': ft.Colors.ORANGE,
                'accepted': ft.Colors.GREEN,
                'rejected': ft.Colors.RED
            }.get(prop[3], ft.Colors.GREY)
            
            status_text = {
                'pending': 'قيد المراجعة',
                'accepted': '✅ مقبول',
                'rejected': '❌ مرفوض'
            }.get(prop[3], prop[3])
            
            proposal_cards.append(
                ft.Card(
                    elevation=2,
                    margin=ft.margin.only(bottom=10),
                    content=ft.Container(
                        padding=15,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(prop[5], size=16, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                                    bgcolor=status_color.with_opacity(0.2),
                                    border_radius=20,
                                    content=ft.Text(status_text, size=12, color=status_color)
                                ),
                            ]),
                            ft.Text(prop[1], size=14, color=ft.Colors.GREY_700),
                            ft.Row([
                                ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.GREEN),
                                ft.Text(f"{prop[2]} $", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                                ft.Text(f"تاريخ التقديم: {prop[4]}", size=12, color=ft.Colors.GREY_500),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ])
                    )
                )
            )
        
        self.content_area.content = ft.Column(
            spacing=15,
            controls=[
                ft.Text("📋 عروضي", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(f"إجمالي العروض: {len(proposals)}", size=14, color=ft.Colors.GREY_600),
                ft.Divider(),
            ] + proposal_cards
        )
    
    def show_chats(self):
        """عرض المحادثات"""
        from chat_system import ChatSystem
        
        chat_system = ChatSystem(self.page, self.db, self.user)
        chat_system.show_chats()
    
    def show_chat_with_user(self, other_user_id, other_user_name, project_id=None):
        """بدء محادثة مع مستخدم"""
        from chat_system import ChatSystem
        
        chat_system = ChatSystem(self.page, self.db, self.user)
        chat_system.show_chat(other_user_id, other_user_name, project_id)
    
    def close_dialog(self, dialog):
        """إغلاق الحوار"""
        dialog.open = False
        self.page.update()
    
    def show_snackbar(self, message, color):
        """عرض إشعار"""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
    
    def logout(self, e):
        """تسجيل الخروج"""
        from main import FreelancingPlatform
        FreelancingPlatform(self.page)