"""
freelancer_dashboard.py - لوحة تحكم المستقل مع تصميم محمول
"""

import flet as ft
from database import Database

class FreelancerDashboard:
    """لوحة تحكم المستقل"""
    
    def __init__(self, page: ft.Page, db: Database, user_data: dict, clear_session_callback):
        self.page = page
        self.db = db
        self.user = user_data
        self.clear_session = clear_session_callback
        self.current_filter_category = None
        self.current_filter_location = None
        self.current_tab_index = 0
    
    def build(self):
        """بناء واجهة لوحة تحكم المستقل"""
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
                ft.NavigationDestination(icon=ft.Icons.SEARCH, label="المشاريع"),
                ft.NavigationDestination(icon=ft.Icons.PROPOSAL, label="عروضي"),
                ft.NavigationDestination(icon=ft.Icons.PERSON, label="البروفايل"),
                ft.NavigationDestination(icon=ft.Icons.CHAT, label="المحادثات"),
            ],
            on_change=self.nav_change,
            bgcolor=ft.Colors.WHITE,
        )
        
        # منطقة المحتوى الرئيسية (قابلة للتمرير)
        self.content_area = ft.Container(
            expand=True,
            padding=ft.padding.all(15),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        
        # تخطيط الصفحة
        layout = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                self.content_area,
                self.nav_bar,
            ]
        )
        
        self.page.add(layout)
        self.load_projects()
    
    def nav_change(self, e):
        """تغيير التنقل"""
        self.current_tab_index = e.control.selected_index
        if self.current_tab_index == 0:
            self.load_projects()
        elif self.current_tab_index == 1:
            self.show_my_proposals()
        elif self.current_tab_index == 2:
            self.show_profile()
        elif self.current_tab_index == 3:
            self.show_chats()
    
    def refresh_view(self):
        """تحديث العرض الحالي"""
        if self.current_tab_index == 0:
            self.load_projects()
        elif self.current_tab_index == 1:
            self.show_my_proposals()
        elif self.current_tab_index == 2:
            self.show_profile()
        elif self.current_tab_index == 3:
            self.show_chats()
    
    def load_projects(self):
        """تحميل قائمة المشاريع مع الفلاتر"""
        projects = self.db.get_all_projects(
            category=self.current_filter_category,
            location=self.current_filter_location
        )
        
        # شريط الفلاتر
        filter_row = ft.Container(
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            margin=ft.margin.only(bottom=15),
            content=ft.Column([
                ft.Text("🔍 فلترة المشاريع", size=14, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Dropdown(
                        expand=True,
                        hint_text="نوع العمل",
                        options=[
                            ft.dropdown.Option(None, "الكل"),
                            ft.dropdown.Option("برمجة", "برمجة"),
                            ft.dropdown.Option("تصميم", "تصميم"),
                            ft.dropdown.Option("كتابة", "كتابة"),
                            ft.dropdown.Option("تسويق", "تسويق"),
                        ],
                        value=self.current_filter_category,
                        on_change=self.filter_by_category,
                        border_radius=10,
                    ),
                    ft.Dropdown(
                        expand=True,
                        hint_text="الموقع",
                        options=[
                            ft.dropdown.Option(None, "الكل"),
                            ft.dropdown.Option("Remote", "عن بعد"),
                            ft.dropdown.Option("On-site", "في الموقع"),
                        ],
                        value=self.current_filter_location,
                        on_change=self.filter_by_location,
                        border_radius=10,
                    ),
                ], spacing=10),
            ])
        )
        
        if not projects:
            self.content_area.content = ft.Column([
                filter_row,
                ft.Icon(ft.Icons.FOLDER_OPEN, size=80, color=ft.Colors.GREY_400),
                ft.Text("لا توجد مشاريع متاحة حالياً", size=16, color=ft.Colors.GREY_600),
                ft.Text("سيتم عرض المشاريع الجديدة هنا", size=14, color=ft.Colors.GREY_500),
                ft.ElevatedButton("تحديث", on_click=lambda e: self.load_projects(), icon=ft.Icons.REFRESH),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            self.page.update()
            return
        
        # بناء بطاقات المشاريع
        project_cards = [filter_row]
        for project in projects:
            project_cards.append(self._project_card(project))
        
        self.content_area.content = ft.Column(
            controls=project_cards,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.page.update()
    
    def filter_by_category(self, e):
        self.current_filter_category = e.control.value
        self.load_projects()
    
    def filter_by_location(self, e):
        self.current_filter_location = e.control.value
        self.load_projects()
    
    def _project_card(self, project):
        """بطاقة مشروع"""
        return ft.Card(
            elevation=2,
            margin=ft.margin.only(bottom=5),
            content=ft.Container(
                padding=15,
                width=self.page.window_width - 30,
                content=ft.Column([
                    ft.Row([
                        ft.Text(project['title'], size=18, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            bgcolor=ft.Colors.GREEN.with_opacity(0.2),
                            border_radius=20,
                            content=ft.Text(f"{project['budget']} $", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
                        ),
                    ]),
                    ft.Text(project['description'][:100] + ("..." if len(project['description']) > 100 else ""), 
                           size=13, color=ft.Colors.GREY_700),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=14, color=ft.Colors.GREY_600),
                        ft.Text(project['client_name'], size=11, color=ft.Colors.GREY_600),
                        ft.Icon(ft.Icons.CATEGORY, size=14, color=ft.Colors.GREY_600),
                        ft.Text(project['category'], size=11, color=ft.Colors.GREY_600),
                    ], spacing=8, wrap=True),
                    ft.Divider(height=1),
                    ft.Row([
                        ft.TextButton("🔍 تفاصيل", on_click=lambda e, p=project: self.show_project_details(p)),
                        ft.ElevatedButton("📝 تقديم عرض", on_click=lambda e, p=project: self.show_proposal_form(p),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=10))),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=10)
            )
        )
    
    def show_project_details(self, project):
        """عرض تفاصيل المشروع"""
        dialog = ft.AlertDialog(
            title=ft.Text(project['title']),
            content=ft.Container(
                width=350,
                padding=15,
                content=ft.Column([
                    ft.Text(f"📝 الوصف:", weight=ft.FontWeight.BOLD),
                    ft.Text(project['description'], size=13),
                    ft.Divider(),
                    ft.Text(f"👤 صاحب المشروع: {project['client_name']}"),
                    ft.Text(f"📂 نوع العمل: {project['category']}"),
                    ft.Text(f"📍 الموقع: {'عن بعد' if project['location'] == 'Remote' else 'في الموقع'}"),
                    ft.Text(f"💰 الميزانية: {project['budget']} $", color=ft.Colors.GREEN, weight=ft.FontWeight.BOLD),
                ], spacing=8, scroll=ft.ScrollMode.AUTO, height=300)
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
            min_lines=4,
            width=self.page.window_width - 80,
            hint_text="اشرح لماذا أنت المرشح المناسب..."
        )
        price_field = ft.TextField(
            label="السعر المقترح ($)",
            width=self.page.window_width - 80,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text=f"الحد الأقصى: {project['budget']} $"
        )
        
        def submit_proposal(e):
            if not desc_field.value or not price_field.value:
                self.show_snackbar("الرجاء تعبئة جميع الحقول", ft.Colors.RED)
                return
            
            try:
                price = float(price_field.value)
                if price > project['budget']:
                    self.show_snackbar(f"السعر لا يمكن أن يتجاوز {project['budget']} $", ft.Colors.RED)
                    return
                
                if self.db.create_proposal(project['id'], self.user['id'], desc_field.value, price):
                    self.show_snackbar("تم تقديم العرض بنجاح!", ft.Colors.GREEN)
                    self.close_dialog(dialog)
                else:
                    self.show_snackbar("حدث خطأ أثناء تقديم العرض", ft.Colors.RED)
            except ValueError:
                self.show_snackbar("السعر يجب أن يكون رقماً صحيحاً", ft.Colors.RED)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"تقديم عرض: {project['title'][:30]}"),
            content=ft.Container(
                width=self.page.window_width - 40,
                padding=15,
                content=ft.Column([
                    desc_field,
                    price_field,
                ], spacing=15, height=250)
            ),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("إرسال", on_click=submit_proposal),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_profile(self):
        """عرض صفحة البروفايل"""
        proposals_count = self.db.get_user_proposals_count(self.user['id'])
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proposals WHERE freelancer_id = ? AND status = 'accepted'", (self.user['id'],))
            accepted_proposals = cursor.fetchone()[0]
        
        profile_content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        padding=20,
                        width=self.page.window_width - 30,
                        content=ft.Column([
                            ft.CircleAvatar(
                                content=ft.Text(self.user['username'][0].upper(), size=30),
                                bgcolor=ft.Colors.BLUE_200,
                                radius=40,
                            ),
                            ft.Text(self.user['username'], size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(self.user['email'], size=13, color=ft.Colors.GREY_600),
                            ft.Container(
                                padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                bgcolor=ft.Colors.GREEN.with_opacity(0.2),
                                border_radius=20,
                                content=ft.Text("مستقل", size=12, color=ft.Colors.GREEN)
                            ),
                            ft.Divider(),
                            ft.Row([
                                self._stat_badge("العروض", proposals_count, ft.Icons.PROPOSAL),
                                self._stat_badge("مقبولة", accepted_proposals, ft.Icons.CHECK_CIRCLE),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12)
                    )
                ),
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=15,
                        width=self.page.window_width - 30,
                        content=ft.Column([
                            ft.Text("📝 معلومات الحساب", size=16, weight=ft.FontWeight.BOLD),
                            ft.ListTile(leading=ft.Icon(ft.Icons.PERSON), title=ft.Text("اسم المستخدم"), subtitle=ft.Text(self.user['username'])),
                            ft.ListTile(leading=ft.Icon(ft.Icons.EMAIL), title=ft.Text("البريد الإلكتروني"), subtitle=ft.Text(self.user['email'])),
                        ], spacing=5)
                    )
                ),
            ]
        )
        
        self.content_area.content = profile_content
        self.page.update()
    
    def _stat_badge(self, title, value, icon):
        return ft.Container(
            padding=10,
            bgcolor=ft.Colors.BLUE.with_opacity(0.1),
            border_radius=12,
            content=ft.Column([
                ft.Icon(icon, size=24, color=ft.Colors.BLUE),
                ft.Text(str(value), size=20, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=11, color=ft.Colors.GREY_700),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        )
    
    def show_my_proposals(self):
        """عرض عروضي"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.description, p.price, p.status, p.created_at,
                       pr.title as project_title
                FROM proposals p
                JOIN projects pr ON p.project_id = pr.id
                WHERE p.freelancer_id = ?
                ORDER BY p.created_at DESC
            """, (self.user['id'],))
            proposals = cursor.fetchall()
        
        if not proposals:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.PROPOSAL, size=80, color=ft.Colors.GREY_400),
                ft.Text("لم تقدم أي عروض بعد", size=16, color=ft.Colors.GREY_600),
                ft.ElevatedButton("🔍 استعراض المشاريع", on_click=lambda e: self.load_projects()),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            self.page.update()
            return
        
        proposal_cards = []
        for prop in proposals:
            status_color = {'pending': ft.Colors.ORANGE, 'accepted': ft.Colors.GREEN, 'rejected': ft.Colors.RED}.get(prop[3], ft.Colors.GREY)
            status_text = {'pending': '⏳ قيد المراجعة', 'accepted': '✅ مقبول', 'rejected': '❌ مرفوض'}.get(prop[3], prop[3])
            
            proposal_cards.append(
                ft.Card(
                    margin=ft.margin.only(bottom=8),
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(prop[5], size=15, weight=ft.FontWeight.BOLD, expand=True),
                                ft.Container(
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor=status_color.with_opacity(0.2),
                                    border_radius=15,
                                    content=ft.Text(status_text, size=10, color=status_color)
                                ),
                            ]),
                            ft.Text(prop[1][:80] + ("..." if len(prop[1]) > 80 else ""), size=12, color=ft.Colors.GREY_700),
                            ft.Row([
                                ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color=ft.Colors.GREEN),
                                ft.Text(f"{prop[2]} $", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ], spacing=8)
                    )
                )
            )
        
        self.content_area.content = ft.Column([
            ft.Text("📋 عروضي", size=22, weight=ft.FontWeight.BOLD),
            ft.Text(f"إجمالي العروض: {len(proposals)}", size=13, color=ft.Colors.GREY_600),
        ] + proposal_cards, spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def show_chats(self):
        """عرض المحادثات"""
        from chat_system import ChatSystem
        chat_system = ChatSystem(self.page, self.db, self.user)
        chat_system.show_chats()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snackbar(self, message, color):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color, action="OK", duration=3000)
        self.page.snack_bar.open = True
        self.page.update()
    
    def logout(self, e):
        self.clear_session()
        from main import FreelancingPlatform
        FreelancingPlatform(self.page)
