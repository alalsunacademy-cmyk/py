"""
admin_dashboard.py - لوحة تحكم المدير
"""

import flet as ft
from database import Database

class AdminDashboard:
    def __init__(self, page: ft.Page, db: Database, user_data: dict, clear_session_callback):
        self.page = page
        self.db = db
        self.user = user_data
        self.clear_session = clear_session_callback
        self.current_tab_index = 0
    
    def build(self):
        self.page.clean()
        self.page.title = "لوحة تحكم المدير"
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.padding = 0
        
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"مرحباً {self.user['username']} 👑", size=18, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.RED_700,
            color=ft.Colors.WHITE,
            actions=[ft.IconButton(ft.Icons.LOGOUT, on_click=self.logout)],
        )
        
        self.nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.DASHBOARD, label="الإحصائيات"),
                ft.NavigationDestination(icon=ft.Icons.PEOPLE, label="المستخدمين"),
                ft.NavigationDestination(icon=ft.Icons.PROJECT, label="المشاريع"),
            ],
            on_change=self.nav_change,
            bgcolor=ft.Colors.WHITE,
        )
        
        self.content_area = ft.Container(
            expand=True, 
            padding=15, 
            content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
        
        self.page.add(ft.Column(expand=True, spacing=0, controls=[self.content_area, self.nav_bar]))
        self.load_stats()
    
    def nav_change(self, e):
        self.current_tab_index = e.control.selected_index
        if self.current_tab_index == 0:
            self.load_stats()
        elif self.current_tab_index == 1:
            self.manage_users()
        elif self.current_tab_index == 2:
            self.manage_projects()
    
    def load_stats(self):
        users = self.db.get_all_users()
        projects = self.db.get_all_projects_admin()
        
        self.content_area.content = ft.Column([
            ft.Text("📊 الإحصائيات", size=24, weight=ft.FontWeight.BOLD),
            ft.Row([
                self._stat_card("المستخدمين", len(users), ft.Icons.PEOPLE, ft.Colors.BLUE),
                self._stat_card("المشاريع", len(projects), ft.Icons.PROJECT, ft.Colors.PURPLE),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
        self.page.update()
    
    def _stat_card(self, title, value, icon, color):
        return ft.Container(
            width=150, 
            padding=20, 
            bgcolor=color.with_opacity(0.1), 
            border_radius=15,
            content=ft.Column([
                ft.Icon(icon, size=30, color=color), 
                ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD), 
                ft.Text(title, size=12)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
        )
    
    def manage_users(self):
        users = self.db.get_all_users()
        if not users:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.PEOPLE, size=80, color=ft.Colors.GREY_400),
                ft.Text("لا يوجد مستخدمين", size=16, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            self.page.update()
            return
        
        user_cards = [ft.Text("👥 إدارة المستخدمين", size=22, weight=ft.FontWeight.BOLD)]
        for user in users:
            user_cards.append(self._user_card(user))
        
        self.content_area.content = ft.Column(user_cards, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def _user_card(self, user):
        status_color = ft.Colors.GREEN if user['status'] == 'active' else ft.Colors.RED
        status_text = "نشط" if user['status'] == 'active' else "محظور"
        user_type_text = {
            'freelancer': 'مستقل',
            'client': 'صاحب عمل',
            'admin': 'مدير'
        }.get(user['user_type'], user['user_type'])
        
        return ft.Card(
            margin=ft.margin.only(bottom=8),
            content=ft.Container(
                padding=12,
                width=self.page.window_width - 30,
                content=ft.Column([
                    ft.Row([
                        ft.Text(user['username'], size=16, weight=ft.FontWeight.BOLD, expand=True),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            bgcolor=status_color.with_opacity(0.2),
                            border_radius=12,
                            content=ft.Text(status_text, size=10, color=status_color)
                        ),
                    ]),
                    ft.Text(user['email'], size=12, color=ft.Colors.GREY_600),
                    ft.Text(f"نوع: {user_type_text}", size=11, color=ft.Colors.GREY_500),
                    ft.Row([
                        ft.IconButton(
                            ft.Icons.BLOCK, 
                            on_click=lambda e, uid=user['id'], s=user['status']: self.toggle_user(uid, s),
                            icon_color=ft.Colors.ORANGE,
                            tooltip="حظر/تنشيط"
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE, 
                            on_click=lambda e, uid=user['id'], uname=user['username']: self.delete_user(uid, uname),
                            icon_color=ft.Colors.RED,
                            tooltip="حذف"
                        ),
                    ], spacing=0, alignment=ft.MainAxisAlignment.END),
                ], spacing=8)
            )
        )
    
    def toggle_user(self, user_id, current_status):
        new_status = 'banned' if current_status == 'active' else 'active'
        self.db.update_user_status(user_id, new_status)
        self.show_snackbar(f"تم {'حظر' if new_status == 'banned' else 'تنشيط'} المستخدم", ft.Colors.GREEN)
        self.manage_users()
    
    def delete_user(self, user_id, username):
        def confirm_delete(e):
            self.db.delete_user(user_id)
            self.show_snackbar(f"تم حذف {username}", ft.Colors.RED)
            dialog.open = False
            self.manage_users()
        
        dialog = ft.AlertDialog(
            title=ft.Text("تأكيد الحذف"),
            content=ft.Text(f"هل أنت متأكد من حذف {username}؟"),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def manage_projects(self):
        projects = self.db.get_all_projects_admin()
        if not projects:
            self.content_area.content = ft.Column([
                ft.Icon(ft.Icons.PROJECT, size=80, color=ft.Colors.GREY_400),
                ft.Text("لا يوجد مشاريع", size=16, color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
            self.page.update()
            return
        
        project_cards = [ft.Text("📋 إدارة المشاريع", size=22, weight=ft.FontWeight.BOLD)]
        for project in projects:
            project_cards.append(self._project_card(project))
        
        self.content_area.content = ft.Column(project_cards, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.page.update()
    
    def _project_card(self, project):
        status_color = ft.Colors.GREEN if project['status'] == 'open' else ft.Colors.ORANGE
        status_text = "مفتوح" if project['status'] == 'open' else "مغلق"
        location_text = "عن بعد" if project['location'] == "Remote" else "في الموقع"
        
        return ft.Card(
            margin=ft.margin.only(bottom=8),
            content=ft.Container(
                padding=12,
                width=self.page.window_width - 30,
                content=ft.Column([
                    ft.Text(project['title'], size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(f"👤 {project['client_name']}", size=12, color=ft.Colors.GREY_600),
                    ft.Row([
                        ft.Icon(ft.Icons.CATEGORY, size=12, color=ft.Colors.GREY_500),
                        ft.Text(project['category'], size=11, color=ft.Colors.GREY_500),
                        ft.Icon(ft.Icons.LOCATION_ON, size=12, color=ft.Colors.GREY_500),
                        ft.Text(location_text, size=11, color=ft.Colors.GREY_500),
                        ft.Icon(ft.Icons.ATTACH_MONEY, size=12, color=ft.Colors.GREEN),
                        ft.Text(f"{project['budget']}$", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                    ], spacing=5, wrap=True),
                    ft.Row([
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            bgcolor=status_color.with_opacity(0.2),
                            border_radius=12,
                            content=ft.Text(status_text, size=10, color=status_color)
                        ),
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT, 
                                on_click=lambda e, pid=project['id'], s=project['status']: self.toggle_project(pid, s),
                                icon_color=ft.Colors.BLUE,
                                tooltip="تغيير الحالة"
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE, 
                                on_click=lambda e, pid=project['id'], title=project['title']: self.delete_project(pid, title),
                                icon_color=ft.Colors.RED,
                                tooltip="حذف"
                            ),
                        ], spacing=0),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=8)
            )
        )
    
    def toggle_project(self, project_id, current_status):
        new_status = 'closed' if current_status == 'open' else 'open'
        self.db.update_project(project_id, status=new_status)
        self.show_snackbar(f"تم {'إغلاق' if new_status == 'closed' else 'فتح'} المشروع", ft.Colors.GREEN)
        self.manage_projects()
    
    def delete_project(self, project_id, title):
        def confirm_delete(e):
            self.db.delete_project(project_id)
            self.show_snackbar(f"تم حذف {title}", ft.Colors.RED)
            dialog.open = False
            self.manage_projects()
        
        dialog = ft.AlertDialog(
            title=ft.Text("تأكيد الحذف"),
            content=ft.Text(f"هل أنت متأكد من حذف المشروع {title}؟"),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: self.close_dialog(dialog)),
                ft.ElevatedButton("حذف", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()
    
    def show_snackbar(self, message, color):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color, action="OK", duration=3000)
        self.page.snack_bar.open = True
        self.page.update()
    
    def logout(self, e):
        if self.clear_session:
            self.clear_session()
        from main import FreelancingPlatform
        FreelancingPlatform(self.page)
