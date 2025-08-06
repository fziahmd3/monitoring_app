#!/usr/bin/env python3
"""
Script final untuk memperbaiki admin
"""

from app.data_migration import create_app, db
from app.models import Admin
from werkzeug.security import generate_password_hash, check_password_hash

def fix_admin_final():
    """Fix admin dengan algoritma hash yang konsisten"""
    
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
        
        # Buat admin baru dengan algoritma yang konsisten
        new_admin = Admin(username=USERNAME)
        # Gunakan algoritma pbkdf2:sha256 untuk konsistensi
        new_admin.password_hash = generate_password_hash(PASSWORD, method='pbkdf2:sha256')
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"✅ Admin baru dibuat:")
        print(f"   Username: {USERNAME}")
        print(f"   Password: {PASSWORD}")
        print(f"   Hash: {new_admin.password_hash}")
        
        # Test login
        if new_admin.check_password(PASSWORD):
            print("✅ Login test berhasil!")
            return True
        else:
            print("❌ Login test gagal!")
            return False

def test_login():
    """Test login admin"""
    
    app = create_app()
    
    USERNAME = "monitoring1"
    PASSWORD = "monitoringhafalan25"
    
    with app.app_context():
        admin = Admin.query.filter_by(username=USERNAME).first()
        
        if admin:
            print(f"🔍 Testing login untuk admin: {admin.username}")
            print(f"   Hash: {admin.password_hash}")
            
            if admin.check_password(PASSWORD):
                print("✅ Login berhasil!")
                print(f"   Username: {USERNAME}")
                print(f"   Password: {PASSWORD}")
                return True
            else:
                print("❌ Login gagal!")
                return False
        else:
            print("❌ Admin tidak ditemukan!")
            return False

if __name__ == "__main__":
    print("🔧 Fix admin final...")
    print("=" * 50)
    success = fix_admin_final()
    
    if success:
        print("\n🧪 Test login...")
        print("=" * 50)
        test_login()
    
    print("\n🎉 Selesai!")
    print("\n📋 Informasi Login Admin:")
    print("   URL: http://localhost:5000/login_admin")
    print("   Username: monitoring1")
    print("   Password: monitoringhafalan25") 