"""
chat_system.py - نظام المحادثات المباشرة
"""

import flet as ft
from database import Database
import threading
import time

class ChatSystem:
    """نظام إدارة المحادثات"""
    
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
        """عرض قائمة المحادثات"""
        # جلب جميع المحادثات السابقة للمستخدم
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT 
                    CASE 
                        WHEN m.sender_id = ? THEN m.receiver_id
                        ELSE m.sender_id
                    END as other_user_id,
                    u.username as other_user_name,
                    MAX(m.created_at) as last_message_time
                FROM messages m
                JOIN users u ON u.id = CASE 
                    WHEN m.sender_id = ? THEN m.receiver_id
                    ELSE m.sender_id
                END
                WHERE m.sender_id = ? OR m.receiver_id = ?
                GROUP BY other_user_id
                ORDER BY last_message_time DESC
            """, (self.current_user['id'], self.current_user['id'], 
                  self.current_user['id'], self.current_user['id']))
            chats = cursor.fetchall()
        
        if not chats:
            # عرض رسالة عند عدم وجود محادثات
            self.page.clean()
            self.page.add(
                ft.Column(
                    [
                        ft.AppBar(title=ft.Text("المحادثات"), bgcolor=ft.Colors.BLUE_700),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.CHAT, size=100, color=ft.Colors.GREY_400),
                                    ft.Text("لا توجد محادثات بعد", size=18, color=ft.Colors.GREY_600),
                                    ft.Text("قم بتقديم عروض على مشاريع أو انتظر قبول عروضك لبدء المحادثة", 
                                           size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                            alignment=ft.alignment.center,
                        )
                    ],
                    expand=True,
                )
            )
            return
        
        # بناء واجهة قائمة المحادثات
        chat_cards = []
        for chat in chats:
            chat_cards.append(
                ft.Card(
                    elevation=2,
                    margin=ft.margin.only(bottom=10),
                    content=ft.Container(
                        padding=15,
                        on_click=lambda e, uid=chat[0], uname=chat[1]: self.show_chat(uid, uname),
                        content=ft.Row([
                            ft.CircleAvatar(
                                content=ft.Text(chat[1][0].upper() if chat[1] else "?"),
                                bgcolor=ft.Colors.BLUE_200,
                            ),
                            ft.Column([
                                ft.Text(chat[1], size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"آخر رسالة: {chat[2]}", size=12, color=ft.Colors.GREY_600),
                            ], spacing=5, expand=True),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400),
                        ], spacing=10)
                    )
                )
            )
        
        self.page.clean()
        self.page.title = "المحادثات"
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.appbar = ft.AppBar(
            title=ft.Text("💬 المحادثات", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.go_back()),
        )
        
        self.page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        ft.Text("المحادثات السابقة", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text(f"لديك {len(chats)} محادثة", size=14, color=ft.Colors.GREY_600),
                        ft.Divider(),
                        ft.Column(chat_cards, scroll=ft.ScrollMode.AUTO, expand=True),
                    ],
                    spacing=15,
                )
            )
        )
        self.page.update()
    
    def show_chat(self, other_user_id: int, other_user_name: str, project_id: int = None):
        """عرض نافذة المحادثة مع مستخدم محدد"""
        self.current_chat_user_id = other_user_id
        self.current_chat_user_name = other_user_name
        self.current_project_id = project_id
        
        # جلب رسائل المحادثة
        messages = self.db.get_messages(self.current_user['id'], other_user_id, project_id)
        
        # إنشاء قائمة الرسائل
        self.messages_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        
        # إضافة الرسائل الموجودة
        for msg in messages:
            self.add_message_to_list(msg)
        
        # حقل إدخال الرسالة
        self.message_field = ft.TextField(
            hint_text="اكتب رسالتك هنا...",
            expand=True,
            border_radius=30,
            filled=True,
            bgcolor=ft.Colors.GREY_100,
            on_submit=lambda e: self.send_message(),
        )
        
        send_button = ft.IconButton(
            icon=ft.Icons.SEND,
            icon_size=30,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE),
            on_click=lambda e: self.send_message(),
        )
        
        # بناء واجهة المحادثة
        self.page.clean()
        self.page.title = f"محادثة مع {other_user_name}"
        self.page.bgcolor = ft.Colors.GREY_50
        self.page.appbar = ft.AppBar(
            title=ft.Text(f"💬 محادثة مع {other_user_name}", size=18, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self.show_chats()),
        )
        
        self.page.add(
            ft.Container(
                expand=True,
                padding=20,
                content=ft.Column(
                    [
                        self.messages_list,
                        ft.Divider(height=1),
                        ft.Row(
                            [
                                self.message_field,
                                send_button,
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    expand=True,
                )
            )
        )
        
        self.page.update()
        
        # بدء التحديث التلقائي للرسائل
        self.start_auto_update()
    
    def add_message_to_list(self, message: dict):
        """إضافة رسالة إلى قائمة المحادثة"""
        is_me = message['sender_id'] == self.current_user['id']
        
        message_container = ft.Container(
            margin=ft.margin.only(bottom=5),
            content=ft.Row(
                [
                    ft.Container(
                        padding=ft.padding.all(12),
                        bgcolor=ft.Colors.BLUE_600 if is_me else ft.Colors.GREY_300,
                        border_radius=ft.border_radius.only(
                            top_left=15,
                            top_right=15,
                            bottom_left=0 if is_me else 15,
                            bottom_right=15 if is_me else 0,
                        ),
                        content=ft.Text(
                            message['message'],
                            color=ft.Colors.WHITE if is_me else ft.Colors.BLACK,
                            size=14,
                        ),
                        max_width=400,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START,
            ),
        )
        
        # إضافة اسم المرسل وتاريخ الرسالة
        time_text = ft.Text(
            f"{message['sender_name']} • {message['created_at']}",
            size=10,
            color=ft.Colors.GREY_500,
            text_align=ft.TextAlign.RIGHT if is_me else ft.TextAlign.LEFT,
        )
        
        self.messages_list.controls.append(ft.Column([message_container, time_text], spacing=2))
        self.page.update()
    
    def send_message(self):
        """إرسال رسالة"""
        message_text = self.message_field.value
        
        if not message_text or not message_text.strip():
            return
        
        # حفظ الرسالة في قاعدة البيانات
        self.db.send_message(
            self.current_user['id'],
            self.current_chat_user_id,
            message_text.strip(),
            self.current_project_id
        )
        
        # إضافة الرسالة إلى الواجهة
        new_message = {
            'sender_id': self.current_user['id'],
            'receiver_id': self.current_chat_user_id,
            'message': message_text.strip(),
            'created_at': time.strftime("%Y-%m-%d %H:%M:%S"),
            'sender_name': self.current_user['username'],
        }
        self.add_message_to_list(new_message)
        
        # مسح حقل الإدخال
        self.message_field.value = ""
        self.page.update()
    
    def start_auto_update(self):
        """بدء التحديث التلقائي للرسائل الجديدة"""
        if self.update_thread_running:
            return
        
        def update_messages():
            self.update_thread_running = True
            last_message_count = len(self.messages_list.controls) if self.messages_list else 0
            
            while self.update_thread_running:
                time.sleep(2)  # التحقق كل 2 ثانية
                
                if not self.messages_list or not self.current_chat_user_id:
                    continue
                
                # جلب الرسائل الجديدة
                messages = self.db.get_messages(
                    self.current_user['id'],
                    self.current_chat_user_id,
                    self.current_project_id
                )
                
                if len(messages) > last_message_count:
                    # إضافة الرسائل الجديدة فقط
                    new_messages = messages[last_message_count:]
                    for msg in new_messages:
                        # تجنب إضافة الرسالة التي أرسلها المستخدم الحالي (أضيفت بالفعل)
                        if msg['sender_id'] != self.current_user['id']:
                            self.page.run_task(self.add_message_to_list, msg)
                    last_message_count = len(messages)
                    self.page.update()
        
        # تشغيل التحديث في خيط منفصل
        thread = threading.Thread(target=update_messages, daemon=True)
        thread.start()
    
    def stop_auto_update(self):
        """إيقاف التحديث التلقائي"""
        self.update_thread_running = False
    
    def go_back(self):
        """العودة إلى الشاشة السابقة"""
        self.stop_auto_update()
        from main import FreelancingPlatform
        # إعادة توجيه حسب نوع المستخدم
        user = self.current_user
        if user['user_type'] == 'admin':
            from admin_dashboard import AdminDashboard
            AdminDashboard(self.page, self.db, user).build()
        elif user['user_type'] == 'client':
            from client_dashboard import ClientDashboard
            ClientDashboard(self.page, self.db, user).build()
        else:
            from freelancer_dashboard import FreelancerDashboard
            FreelancerDashboard(self.page, self.db, user).build()