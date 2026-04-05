"""
admin_dashboard.py - لوحة تحكم المدير (Admin)
"""

import flet as ft
from database import Database

class AdminDashboard:
    """لوحة تحكم المدير"""
    
    def __init__(self, page: ft.Page, db: Database, user_data: dict):
        self.page = page
        self.db = db
        self.user = user_data
    
    def build(self):
        """بناء واجهة لوحة تحكم الأدمن"""
        self.page.clean()
        self.page.title = "منصة العمل الحر - لوحة تحكم المدير"
        self.page.bgcolor = ft.Colors.GREY_50
        
        # شريط التطبيق العلوي
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"لوحة تحكم المدير - مرحباً {self.user['username']} 👑", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.RED_700,
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
            leading=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=40, color=ft.Colors.RED_700),
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD,
                    selected_icon=ft.Icons.DASHBOARD_OUTLINED,
                    label="الإحصائيات"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE,
                    selected_icon=ft.Icons.PEOPLE_OUTLINED,
                    label="إدارة المستخدمين"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PROJECT,
                    selected_icon=ft.Icons.PROJECT_OUTLINED,
                    label="إدارة المشاريع"
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
        self.load_stats()
    
    def nav_change(self, e):
        """تغيير التنقل"""
        index = self.nav_rail.selected_index
        if index == 0:
            self.load_stats()
        elif index == 1:
            self.manage_users()
        elif index == 2:
            self.manage_projects()
    
    def refresh_view(self):
        """تحديث العرض الحالي"""
        index = self.nav_rail.selected_index
        if index == 0:
            self.load_stats()
        elif index == 1:
            self.manage_users()
        elif index == 2:
            self.manage_projects()
    
    def load_stats(self):
        """تحميل الإحصائيات"""
        users = self.db.get_all_users()
        projects = self.db.get_all_projects_admin()
        
        # إحصائيات المستخدمين
        freelancers = len([u for u in users if u['user_type'] == 'freelancer'])
        clients = len([u for u in users if u['user_type'] == 'client'])
        banned = len([u for u in users if u['status'] == 'banned'])
        
        # إحصائيات المشاريع
        open_projects = len([p for p in projects if p['status'] == 'open'])
        closed_projects = len([p for p in projects if p['status'] == 'closed'])
        
        self.content_area.content = ft.Column(
            spacing=20,
            controls=[
                ft.Text("📊 إحصائيات المنصة", size=28, weight=ft.FontWeight.BOLD),
                ft.Row([
                    self._stat_card("إجمالي المستخدمين", len(users), ft.Icons.PEOPLE, ft.Colors.BLUE, "👥"),
                    self._stat_card("المستقلين", freelancers, ft.Icons.PERSON, ft.Colors.GREEN, "💼"),
                    self._stat_card("أصحاب العمل", clients, ft.Icons.BUSINESS, ft.Colors.ORANGE, "🏢"),
                    self._stat_card("المستخدمين المحظورين", banned, ft.Icons.BLOCK, ft.Colors.RED, "🚫"),
                ], spacing=15),
                ft.Row([
                    self._stat_card("إجمالي المشاريع", len(projects), ft.Icons.PROJECT, ft.Colors.PURPLE, "📋"),
                    self._stat_card("مشاريع مفتوحة", open_projects, ft.Icons.OPEN_IN_NEW, ft.Colors.GREEN, "🔓"),
                    self._stat_card("مشاريع مغلقة", closed_projects, ft.Icons.CHECK_CIRCLE, ft.Colors.GREY, "🔒"),
                ], spacing=15),
            ]
        )
    
    def _stat_card(self, title, value, icon, color, emoji):
        """بطاقة إحصائية"""
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor=color.with_opacity(0.1),
            border_radius=15,
            content=ft.Column([
                ft.Text(emoji, size=30),
                ft.Text(str(value), size=36, weight=ft.FontWeight.BOLD),
                ft.Text(title, size=14, color=ft.Colors.GREY_700),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def manage_users(self):
        """إدارة المستخدمين"""
        users = self.db.get_all_users()
        
        # إنشاء جدول المستخدمين
        user_rows = []
        for user in users:
            status_color = ft.Colors.GREEN if user['status'] == 'active' else ft.Colors.RED
            status_text = "نشط" if user['status'] == 'active' else "محظور"
            user_type_text = {
                'freelancer': 'مستقل',
                'client': 'صاحب عمل',
                'admin': 'مدير'
            }.get(user['user_type'], user['user_type'])
            
            def toggle_status(u_id=user['id'], current_status=user['status']):
                new_status = 'banned' if current_status == 'active' else 'active'
                self.db.update_user_status(u_id, new_status)
                self.show_snackbar(f"تم {'حظر' if new_status == 'banned' else 'تنشيط'} المستخدم", ft.Colors.GREEN)
                self.manage_users()
            
            def delete_user(u_id=user['id'], username=user['username']):
                def confirm_delete(e):
                    self.db.delete_user(u_id)
                    self.show_snackbar(f"تم حذف المستخدم {username}", ft.Colors.RED)
                    self.manage_users()
                    dialog.open = False
                
                dialog = ft.AlertDialog(
                    title=ft.Text("تأكيد الحذف"),
                    content=ft.Text(f"هل أنت متأكد من حذف المستخدم {username}؟"),
                    actions=[
                        ft.TextButton("إلغاء", on_click=lambda e: setattr(dialog, 'open', False)),
                        ft.ElevatedButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
                    ],
                )
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            
            user_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(user['id']))),
                    ft.DataCell(ft.Text(user['username'])),
                    ft.DataCell(ft.Text(user['email'])),
                    ft.DataCell(ft.Text(user_type_text)),
                    ft.DataCell(ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=status_color.with_opacity(0.2),
                        border_radius=20,
                        content=ft.Text(status_text, size=12, color=status_color)
                    )),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.BLOCK, on_click=toggle_status, 
                                    tooltip="حظر/تنشيط", icon_color=ft.Colors.ORANGE),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda e, u_id=user['id'], uname=user['username']: delete_user(u_id, uname),
                                    tooltip="حذف", icon_color=ft.Colors.RED),
                    ], spacing=0)),
                ])
            )
        
        users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("اسم المستخدم")),
                ft.DataColumn(ft.Text("البريد الإلكتروني")),
                ft.DataColumn(ft.Text("نوع المستخدم")),
                ft.DataColumn(ft.Text("الحالة")),
                ft.DataColumn(ft.Text("الإجراءات")),
            ],
            rows=user_rows,
            width=900,
        )
        
        self.content_area.content = ft.Column(
            spacing=20,
            controls=[
                ft.Text("👥 إدارة المستخدمين", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(f"إجمالي المستخدمين: {len(users)}", size=14, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Container(
                    content=users_table,
                    scroll=ft.ScrollMode.AUTO,
                    height=500,
                ),
            ]
        )
        self.page.update()
    
    def manage_projects(self):
        """إدارة المشاريع"""
        projects = self.db.get_all_projects_admin()
        
        # إنشاء جدول المشاريع
        project_rows = []
        for project in projects:
            status_color = ft.Colors.GREEN if project['status'] == 'open' else ft.Colors.ORANGE
            status_text = "مفتوح" if project['status'] == 'open' else "مغلق"
            location_text = "عن بعد" if project['location'] == "Remote" else "في الموقع"
            
            def delete_project(p_id=project['id'], title=project['title']):
                def confirm_delete(e):
                    self.db.delete_project(p_id)
                    self.show_snackbar(f"تم حذف المشروع {title}", ft.Colors.RED)
                    self.manage_projects()
                    dialog.open = False
                
                dialog = ft.AlertDialog(
                    title=ft.Text("تأكيد الحذف"),
                    content=ft.Text(f"هل أنت متأكد من حذف المشروع {title}؟"),
                    actions=[
                        ft.TextButton("إلغاء", on_click=lambda e: setattr(dialog, 'open', False)),
                        ft.ElevatedButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
                    ],
                )
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            
            def edit_project(p_id=project['id'], current_status=project['status']):
                new_status = 'closed' if current_status == 'open' else 'open'
                self.db.update_project(p_id, status=new_status)
                self.show_snackbar(f"تم {'إغلاق' if new_status == 'closed' else 'فتح'} المشروع", ft.Colors.GREEN)
                self.manage_projects()
            
            project_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(project['id']))),
                    ft.DataCell(ft.Text(project['title'][:30] + ("..." if len(project['title']) > 30 else ""))),
                    ft.DataCell(ft.Text(project['client_name'])),
                    ft.DataCell(ft.Text(project['category'])),
                    ft.DataCell(ft.Text(location_text)),
                    ft.DataCell(ft.Text(f"{project['budget']} $")),
                    ft.DataCell(ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=status_color.with_opacity(0.2),
                        border_radius=20,
                        content=ft.Text(status_text, size=12, color=status_color)
                    )),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.EDIT, on_click=lambda e, p_id=project['id'], s=project['status']: edit_project(p_id, s),
                                    tooltip="تغيير الحالة", icon_color=ft.Colors.BLUE),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda e, p_id=project['id'], title=project['title']: delete_project(p_id, title),
                                    tooltip="حذف", icon_color=ft.Colors.RED),
                    ], spacing=0)),
                ])
            )
        
        projects_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("العنوان")),
                ft.DataColumn(ft.Text("صاحب العمل")),
                ft.DataColumn(ft.Text("النوع")),
                ft.DataColumn(ft.Text("الموقع")),
                ft.DataColumn(ft.Text("الميزانية")),
                ft.DataColumn(ft.Text("الحالة")),
                ft.DataColumn(ft.Text("الإجراءات")),
            ],
            rows=project_rows,
            width=1100,
        )
        
        self.content_area.content = ft.Column(
            spacing=20,
            controls=[
                ft.Text("📋 إدارة المشاريع", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(f"إجمالي المشاريع: {len(projects)}", size=14, color=ft.Colors.GREY_600),
                ft.Divider(),
                ft.Container(
                    content=projects_table,
                    scroll=ft.ScrollMode.AUTO,
                    height=500,
                ),
            ]
        )
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
