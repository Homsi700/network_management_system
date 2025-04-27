import os
import sys
from email_validator import validate_email, EmailNotValidError

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from backend.database.database import SessionLocal, engine
from backend.database.models import Admin, Base
from backend.api.auth import get_password_hash
import getpass

def validate_input_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def create_initial_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # التحقق من وجود مشرف
    admin = db.query(Admin).first()
    if admin:
        print("يوجد مشرف بالفعل في النظام!")
        return

    print("=== إنشاء حساب المشرف الأول ===")
    
    while True:
        username = input("اسم المستخدم: ").strip()
        if len(username) >= 3:
            break
        print("اسم المستخدم يجب أن يكون 3 أحرف على الأقل")

    while True:
        password = getpass.getpass("كلمة المرور: ")
        if len(password) < 8:
            print("كلمة المرور يجب أن تكون 8 أحرف على الأقل")
            continue
            
        confirm_password = getpass.getpass("تأكيد كلمة المرور: ")
        if password != confirm_password:
            print("كلمات المرور غير متطابقة!")
            continue
        break

    full_name = input("الاسم الكامل: ").strip()
    
    while True:
        email = input("البريد الإلكتروني: ").strip()
        if validate_input_email(email):
            break
        print("البريد الإلكتروني غير صالح!")

    admin = Admin(
        username=username,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        email=email,
        role="super_admin"
    )

    try:
        db.add(admin)
        db.commit()
        print("\nتم إنشاء حساب المشرف بنجاح!")
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()