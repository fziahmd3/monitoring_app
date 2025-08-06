#!/usr/bin/env python3
"""
Script untuk reset akun admin
"""

from app.data_migration import create_app, db
from app.models import Admin

def reset_admin():
    """Reset akun admin"""
    
    # Inisialisasi Flask app
    app = create_app()
    
    # Data akun admin
    USERNAME = "monitoring1"
    PASSWORD = "monitoringhafalan25"
    
    with app.app_context():
        # Hapus admin yang ada (jika ada)
        existing_admin = Admin.query.filter_by(username=USERNAME).first()
        if existing_admin:
            db.session.delete(existing_admin)
            db.session.commit()
            print(f"🗑️  Admin lama '{USERNAME}' dihapus.")
        
        # Buat admin baru
        new_admin = Admin(username=USERNAME)
        new_admin.set_password(PASSWORD)
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"✅ Akun admin baru berhasil dibuat!")
        print(f"   Username: {USERNAME}")
        print(f"   Password: {PASSWORD}")
        
        # Verifikasi
        admin = Admin.query.filter_by(username=USERNAME).first()
        if admin and admin.check_password(PASSWORD):
            print("✅ Verifikasi login berhasil!")
        else:
            print("❌ Verifikasi login gagal!")

if __name__ == "__main__":
    print("🔄 Reset akun admin...")
    print("=" * 50)
    reset_admin()
    print("\n🎉 Selesai!") 