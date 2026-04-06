"""
chat_system.py - نظام المحادثات
"""

import flet as ft
from database import Database
import threading
import time

class ChatSystem:
    def __init__(self, page: ft.Page, db: Database, current_user: dict):
        self.page = page
        self.db = db
        self.current_user = current_user
        self.current_chat_user_id = None
        self.current_chat_user_name = None
        self.current_project_id = None
        self.messages_list = None
        self.message_field = None
        self.update_thread_running = False
    
    def show_chats(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT 
                    CASE WHEN m.sender_id = ? THEN m.receiver_id ELSE m.sender_id END as other_user_id,
                    u.username as other_user_name,
                    MAX(m.created_at) as last_message_time
                FROM messages m JOIN users u ON u.id = CASE WHEN m.sender_id = ? THEN m.receiver_id ELSE m.sender_id END
                WHERE m.sender_id = ? OR m.receiver_id = ?
                GROUP BY other_user_id ORDER BY last_message_time DESC
            """, (self.current_user['id'], self.current_user['id'], self.current_user['id'], self.current_user['id']))
            chats = cursor.fetchall()
        
        self.page.clean()
        self.page.title = "المحادثات"
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.appbar = ft.AppBar(title=ft.Text("💬 المحادثات"), bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE,
                                     leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.go_back()))
        
        if not chats:
            self.page.add(ft.Container(expand=True, alignment=ft.alignment.center,
                                       content=ft.Column([ft.Icon(ft.Icons.CHAT, size=80, color=ft.Colors.GREY_400),
                                                         ft.Text("لا توجد محادثات", size=16, color=ft.Colors.GREY_600)],
                                                         horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)))
            self.page.update()
            return
        
        chat_cards = []
        for chat in chats:
            chat_cards.append(
                ft.Card(content=ft.Container(padding=15, on_click=lambda e, uid=chat[0], uname=chat[1]: self.show_chat(uid, uname),
                                            content=ft.Row([ft.CircleAvatar(content=ft.Text(chat[1][0].upper()), bgcolor=ft.Colors.BLUE_200),
                                                           ft.Column([ft.Text(chat[1], size=16, weight=ft.FontWeight.BOLD),
                                                                     ft.Text(f"آخر رسالة: {chat[2]}", size=11, color=ft.Colors.GREY_600)], expand=True),
                                                           ft.Icon(ft.Icons.CHEVRON_RIGHT)]))))
        
        self.page.add(ft.Container(expand=True, padding=15, content=ft.Column(chat_cards, scroll=ft.ScrollMode.AUTO, spacing=10)))
        self.page.update()
    
    def show_chat(self, other_user_id, other_user_name, project_id=None):
        self.current_chat_user_id = other_user_id
        self.current_chat_user_name = other_user_name
        self.current_project_id = project_id
        
        messages = self.db.get_messages(self.current_user['id'], other_user_id, project_id)
        self.messages_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        
        for msg in messages:
            self.add_message_to_list(msg)
        
        self.message_field = ft.TextField(hint_text="اكتب رسالتك...", expand=True, border_radius=30, filled=True,
                                          bgcolor=ft.Colors.GREY_100, on_submit=lambda e: self.send_message())
        send_button = ft.IconButton(icon=ft.Icons.SEND, icon_size=28, on_click=lambda e: self.send_message(),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE, shape=ft.CircleBorder()))
        
        self.page.clean()
        self.page.title = f"محادثة مع {other_user_name}"
        self.page.appbar = ft.AppBar(title=ft.Text(f"💬 {other_user_name}"), bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE,
                                     leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.show_chats()))
        self.page.add(ft.Column([self.messages_list, ft.Row([self.message_field, send_button], spacing=10)], expand=True, spacing=15))
        self.page.update()
        self.start_auto_update()
    
    def add_message_to_list(self, message):
        is_me = message['sender_id'] == self.current_user['id']
        self.messages_list.controls.append(
            ft.Row([ft.Container(padding=10, bgcolor=ft.Colors.BLUE_600 if is_me else ft.Colors.GREY_300,
                                border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_left=0 if is_me else 15, bottom_right=15 if is_me else 0),
                                content=ft.Text(message['message'], color=ft.Colors.WHITE if is_me else ft.Colors.BLACK, size=13), max_width=300)],
                  alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START))
        self.page.update()
    
    def send_message(self):
        if not self.message_field.value or not self.message_field.value.strip():
            return
        self.db.send_message(self.current_user['id'], self.current_chat_user_id, self.message_field.value.strip(), self.current_project_id)
        self.add_message_to_list({'sender_id': self.current_user['id'], 'message': self.message_field.value.strip(),
                                  'sender_name': self.current_user['username'], 'created_at': time.strftime("%Y-%m-%d %H:%M:%S")})
        self.message_field.value = ""
        self.page.update()
    
    def start_auto_update(self):
        def update():
            last_count = len(self.messages_list.controls)
            while True:
                time.sleep(2)
                if not self.messages_list or not self.current_chat_user_id:
                    break
                messages = self.db.get_messages(self.current_user['id'], self.current_chat_user_id, self.current_project_id)
                if len(messages) > last_count:
                    for msg in messages[last_count:]:
                        if msg['sender_id'] != self.current_user['id']:
                            self.page.run_task(self.add_message_to_list, msg)
                    last_count = len(messages)
        threading.Thread(target=update, daemon=True).start()
    
    def go_back(self):
        from main import FreelancingPlatform
        FreelancingPlatform(self.page)