"""
utils.py - دوال مساعدة للتطبيق
"""

import re
from datetime import datetime

def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    """التحقق من قوة كلمة المرور"""
    return len(password) >= 6

def format_date(date_string: str) -> str:
    """تنسيق التاريخ بشكل مقروء"""
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        return date_obj.strftime("%Y-%m-%d %H:%M")
    except:
        return date_string

def truncate_text(text: str, max_length: int = 100) -> str:
    """قص النص الطويل"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def get_category_icon(category: str) -> str:
    """الحصول على أيقونة حسب نوع العمل"""
    icons = {
        "برمجة": ft.Icons.CODE,
        "تصميم": ft.Icons.DESIGN_SERVICES,
        "كتابة": ft.Icons.CREATE,
        "تسويق": ft.Icons.CAMPAIGN,
        "ترجمة": ft.Icons.TRANSLATE,
    }
    return icons.get(category, ft.Icons.WORK)

def get_status_color(status: str) -> str:
    """الحصول على لون حسب الحالة"""
    colors = {
        "open": ft.Colors.GREEN,
        "closed": ft.Colors.RED,
        "pending": ft.Colors.ORANGE,
        "accepted": ft.Colors.GREEN,
        "rejected": ft.Colors.RED,
        "active": ft.Colors.GREEN,
        "banned": ft.Colors.RED,
    }
    return colors.get(status, ft.Colors.GREY)