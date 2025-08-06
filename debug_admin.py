#!/usr/bin/env python3
"""
Script debug untuk memeriksa masalah password admin
"""

from app.data_migration import create_app, db
from app.models import Admin
from werkzeug.security import generate_password_hash, check_password_hash

def debug_admin():
    """Debug masalah admin"""
    
    app = create_app()
    
    USERNAME = "monitoring1"
    PASSWORD = "monitoringhafalan25"
    
    with app.app_context():
        # Cari admin
        admin = Admin.query.filter_by(username=USERNAME).first()
        
        if admin:
            print(f"✅ Admin ditemukan: {admin.username}")
            print(f"   Password hash: {admin.password_hash}")
            print(f"   Hash length: {len(admin.password_hash)}")
            
            # Test password check
            print(f"\n🧪 Testing password check...")
            print(f"   Password to check: {PASSWORD}")
            
            # Test dengan werkzeug langsung
            werkzeug_result = check_password_hash(admin.password_hash, PASSWORD)
            print(f"   Werkzeug check: {werkzeug_result}")
            
            # Test dengan method model
            model_result = admin.check_password(PASSWORD)
            print(f"   Model check: {model_result}")
            
            # Test dengan password yang salah
            wrong_result = admin.check_password("wrong_password")
            print(f"   Wrong password test: {wrong_result}")
            
            # Generate hash baru untuk perbandingan
            new_hash = generate_password_hash(PASSWORD)
            print(f"\n🔄 Generate hash baru:")
            print(f"   New hash: {new_hash}")
            print(f"   New hash length: {len(new_hash)}")
            
            # Test hash baru
            new_hash_result = check_password_hash(new_hash, PASSWORD)
            print(f"   New hash test: {new_hash_result}")
            
        else:
            print("❌ Admin tidak ditemukan!")

def create_simple_admin():
    """Buat admin dengan cara sederhana"""
    
    app = create_app()
    
    USERNAME = "monitoring1"
    PASSWORD = "monitoringhafalan25"
    
    with app.app_context():
        # Hapus admin yang ada
        existing = Admin.query.filter_by(username=USERNAME).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print("🗑️  Admin lama dihapus")
        
        # Buat admin baru dengan hash manual
        new_admin = Admin(username=USERNAME)
        new_admin.password_hash = generate_password_hash(PASSWORD)
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"✅ Admin baru dibuat:")
        print(f"   Username: {USERNAME}")
        print(f"   Password: {PASSWORD}")
        print(f"   Hash: {new_admin.password_hash}")
        
        # Test login
        if new_admin.check_password(PASSWORD):
            print("✅ Login test berhasil!")
        else:
            print("❌ Login test gagal!")

if __name__ == "__main__":
    print("🔍 Debug admin password...")
    print("=" * 50)
    debug_admin()
    
    print("\n🔄 Buat admin baru...")
    print("=" * 50)
    create_simple_admin()
    
    print("\n�� Debug selesai!") 