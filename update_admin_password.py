#!/usr/bin/env python3
"""
Script untuk mengupdate password admin
"""

from app.data_migration import create_app, db
from app.models import Admin

def update_admin_password():
    """Update password admin"""
    
    # Inisialisasi Flask app
    app = create_app()
    
    # Data akun admin
    USERNAME = "monitoring1"
    NEW_PASSWORD = "monitoringhafalan25"
    
    with app.app_context():
        # Cari admin dengan username tersebut
        admin = Admin.query.filter_by(username=USERNAME).first()
        
        if admin:
            # Update password
            admin.set_password(NEW_PASSWORD)
            db.session.commit()
            print(f"✅ Password admin '{USERNAME}' berhasil diupdate!")
            print(f"   Username: {USERNAME}")
            print(f"   Password baru: {NEW_PASSWORD}")
        else:
            print(f"❌ Admin dengan username '{USERNAME}' tidak ditemukan.")
            print("💡 Membuat akun admin baru...")
            
            # Buat admin baru
            new_admin = Admin(username=USERNAME)
            new_admin.set_password(NEW_PASSWORD)
            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ Akun admin '{USERNAME}' berhasil dibuat!")
            print(f"   Username: {USERNAME}")
            print(f"   Password: {NEW_PASSWORD}")

def verify_admin_login():
    """Verifikasi login admin"""
    
    app = create_app()
    
    USERNAME = "monitoring1"
    PASSWORD = "monitoringhafalan25"
    
    with app.app_context():
        admin = Admin.query.filter_by(username=USERNAME).first()
        
        if admin:
            if admin.check_password(PASSWORD):
                print("✅ Login admin berhasil!")
                print(f"   Username: {USERNAME}")
                print(f"   Password: {PASSWORD}")
                return True
            else:
                print("❌ Password admin salah!")
                return False
        else:
            print("❌ Admin tidak ditemukan!")
            return False

if __name__ == "__main__":
    print("🔧 Update password admin...")
    print("=" * 50)
    update_admin_password()
    
    print("\n🧪 Verifikasi login...")
    print("=" * 50)
    verify_admin_login()
    
    print("\n🎉 Selesai!") 