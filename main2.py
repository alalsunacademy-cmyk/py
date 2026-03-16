import time
import random
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import MoveTargetOutOfBoundsException, ElementNotInteractableException

# ========== إعدادات المحاكاة البشرية ==========
url="https://github.com/emails.txt"


def random_sleep(min_sec=0.5, max_sec=2.0):
    """تأخير عشوائي"""
    time.sleep(random.uniform(min_sec, max_sec))

def type_like_human(element, text, min_delay=0.05, max_delay=0.15):
    """كتابة النص حرف حرف"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

def safe_click(driver, element):
    """نقر آمن بدون أخطاء"""
    try:
        # تمرير العنصر لمكان آمن
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});", element)
        time.sleep(0.5)
        
        # محاولة النقر بالجافاسكريبت (الأكثر أماناً)
        driver.execute_script("arguments[0].click();", element)
    except:
        try:
            # محاولة النقر العادي
            element.click()
        except:
            pass
    time.sleep(random.uniform(0.5, 1.0))

def safe_move_and_click(driver, element):
    """تحريك الماوس والنقر بشكل آمن"""
    try:
        # التأكد أن العنصر ظاهر
        if element.is_displayed() and element.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # محاولة استخدام ActionChains بشكل آمن
            try:
                actions = ActionChains(driver)
                actions.move_to_element(element).pause(0.3).click().perform()
            except MoveTargetOutOfBoundsException:
                # إذا فشل، استخدم الجافاسكريبت
                driver.execute_script("arguments[0].click();", element)
        else:
            # إذا مش ظاهر، استخدم الجافاسكريبت
            driver.execute_script("arguments[0].click();", element)
    except:
        # آخر محاولة
        try:
            driver.execute_script("arguments[0].click();", element)
        except:
            pass
    time.sleep(random.uniform(0.5, 1.0))

# ========== البيانات ==========
PASSWORD = "p+F7HhE6tLzC-B."
EMAILS_FILE = "emails.txt"
COUNTRIES_FILE = "countries.txt"
PHONES_FILE = "phones.txt"

print("="*70)
print("           برنامج تسجيل الدخول التلقائي - Eneba")
print("="*70)

# التحقق من وجود الملفات
print("\n📁 التحقق من الملفات...")
files_ok = True

for file_name in [EMAILS_FILE, COUNTRIES_FILE, PHONES_FILE]:
    if not os.path.exists(file_name):
        print(f"❌ الملف غير موجود: {file_name}")
        files_ok = False
    else:
        with open(file_name, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            print(f"✅ {file_name}: {len(lines)} سطر")

if not files_ok:
    print("\n❌ تأكد من وجود جميع الملفات المطلوبة")
    input("\nاضغط Enter للخروج...")
    sys.exit()

# قراءة الملفات
with open(EMAILS_FILE, "r", encoding="utf-8") as f:
    emails = [line.strip() for line in f if line.strip()]

with open(COUNTRIES_FILE, "r", encoding="utf-8") as f:
    countries = [line.strip() for line in f if line.strip()]

with open(PHONES_FILE, "r", encoding="utf-8") as f:
    phones = [line.strip() for line in f if line.strip()]

print(f"\n📊 تم قراءة:")
print(f"   - {len(emails)} إيميل")
print(f"   - {len(countries)} كود دولة")
print(f"   - {len(phones)} رقم هاتف")

# ========== إعداد المتصفح ==========
def setup_driver():
    """إعداد المتصفح بطريقة بسيطة ومضمونة"""
    chrome_options = Options()
    
    # إعدادات أساسية فقط
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--lang=ar")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except:
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            print(f"❌ فشل فتح المتصفح: {e}")
            return None

# ========== الدالة الرئيسية ==========
def process_account(email, country_code, phone_number):
    print(f"\n{'='*70}")
    print(f"🚀 بدأ: {email}")
    print(f"📱 +{country_code} {phone_number}")
    print(f"{'='*70}")
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # ===== 1. فتح الموقع =====
        print("\n📌 [1/7] فتح الموقع...")
        driver.get("https://my.eneba.com/ar/login?from=%2Far")
        time.sleep(5)
        
        # ===== 2. الضغط على "تسجيل الدخول بكلمة مرور" =====
        print("📌 [2/7] البحث عن 'تسجيل الدخول بكلمة مرور'...")
        time.sleep(2)
        
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if "كلمة مرور" in btn.text or "password" in btn.text.lower():
                    safe_click(driver, btn)
                    print("   ✅ تم الضغط على الزر")
                    time.sleep(5)
                    break
        except:
            print("   ⚠️ المتابعة...")
        
        # ===== 3. إدخال الإيميل وكلمة السر =====
        print("📌 [3/7] إدخال بيانات الدخول...")
        
        # إدخال الإيميل
        try:
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            email_input.click()
            time.sleep(0.5)
            email_input.clear()
            time.sleep(0.3)
            type_like_human(email_input, email)
            print("   ✅ تم إدخال الإيميل")
            time.sleep(5)
        except Exception as e:
            print(f"   ❌ {e}")
            return
        
        # إدخال كلمة السر
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.click()
            time.sleep(0.5)
            password_input.clear()
            time.sleep(0.3)
            type_like_human(password_input, PASSWORD)
            print("   ✅ تم إدخال كلمة السر")
            time.sleep(5)
        except Exception as e:
            print(f"   ❌ {e}")
            return
        
        # الضغط على زر الدخول
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            safe_click(driver, login_button)
            print("   ✅ تم الضغط على زر الدخول")
            time.sleep(50)
        except Exception as e:
            print(f"   ❌ {e}")
            return
        
        # ===== 4. فتح صفحة الملف الشخصي =====
        print("📌 [4/7] فتح صفحة الملف الشخصي...")
        try:
            driver.get("https://my.eneba.com/ar/profile-wizard")
            time.sleep(5)
            print("   ✅ تم فتح صفحة الملف الشخصي")
        except:
            print("   ⚠️ استمرار...")
        
        # ===== 5. اختيار كود الدولة =====
        print("📌 [5/7] اختيار كود الدولة...")
        time.sleep(3)
        
        try:
            # البحث عن حقل الدولة (بالـ HTML اللي أرسلته)
            country_field = None
            
            # 1. البحث بالـ class
            country_fields = driver.find_elements(By.CSS_SELECTOR, ".react-select__input")
            if country_fields:
                country_field = country_fields[0]
            
            # 2. البحث بالـ role
            if not country_field:
                country_fields = driver.find_elements(By.CSS_SELECTOR, "input[role='combobox']")
                if country_fields:
                    country_field = country_fields[0]
            
            if country_field:
                safe_click(driver, country_field)
                time.sleep(5)
                
                # كتابة كود الدولة
                country_field.send_keys(country_code)
                time.sleep(20)
                
                # الضغط على Enter
                country_field.send_keys(Keys.ENTER)
                print(f"   ✅ تم اختيار +{country_code}")
                time.sleep(5)
            else:
                print("   ⚠️ لم نجد حقل الدولة")
                
        except Exception as e:
            print(f"   ⚠️ {e}")
        
        # ===== 6. إدخال رقم الهاتف =====
        print("📌 [6/7] إدخال رقم الهاتف...")
        time.sleep(10)
        
        try:
            phone_input = None
            
            # 1. البحث بالـ ID
            try:
                phone_input = driver.find_element(By.ID, "phoneNumber")
            except:
                pass
            
            # 2. البحث بالـ name
            if not phone_input:
                try:
                    phone_input = driver.find_element(By.NAME, "phoneNumber")
                except:
                    pass
            
            # 3. البحث بالـ data attribute
            if not phone_input:
                try:
                    phone_input = driver.find_element(By.CSS_SELECTOR, "input[data-hj-suppress='true']")
                except:
                    pass
            
            if phone_input:
                phone_input.click()
                time.sleep(0.5)
                phone_input.clear()
                time.sleep(0.3)
                phone_input.send_keys(phone_number)
                print(f"   ✅ تم إدخال {phone_number}")
                time.sleep(10)
            else:
                print("   ❌ لم نجد حقل الهاتف")
                return
                
        except Exception as e:
            print(f"   ❌ {e}")
            return
        
        # ===== 7. الضغط على "إرسال الرمز" =====
        print("📌 [7/7] البحث عن 'إرسال الرمز'...")
        time.sleep(2)
        
        try:
            send_button = None
            buttons = driver.find_elements(By.TAG_NAME, "button")
            
            for btn in buttons:
                if "إرسال" in btn.text or "رمز" in btn.text:
                    send_button = btn
                    break
            
            if send_button:
                safe_click(driver, send_button)
                print("   ✅ تم الضغط على 'إرسال الرمز'")
                time.sleep(120)
            else:
                print("   ⚠️ لم نجد الزر")
                
        except Exception as e:
            print(f"   ⚠️ {e}")
        
        # حفظ لقطة شاشة
        filename = email.split('@')[0].replace('.', '_')
        driver.save_screenshot(f"{filename}_done.png")
        print(f"\n✅ تم الحفظ: {filename}_done.png")
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        try:
            driver.save_screenshot(f"error_{email.split('@')[0]}.png")
        except:
            pass
    
    finally:
        time.sleep(2)
        driver.quit()
        print(f"✅ انتهى: {email}")

# ========== التنفيذ ==========
print("\n" + "="*70)
print("🚀 بدء التنفيذ...")
print("="*70)

min_length = min(len(emails), len(countries), len(phones))
print(f"\n📊 سيتم معالجة {min_length} حساب")

for i in range(min_length):
    process_account(emails[i], countries[i], phones[i])
    
    if i < min_length - 1:
        wait_time = random.randint(15, 25)
        print(f"\n⏳ انتظار {wait_time} ثانية...")
        time.sleep(wait_time)

print("\n" + "="*70)
print("✨ تم الانتهاء!")
print("="*70)
input("\nاضغط Enter للخروج...")