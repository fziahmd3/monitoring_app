#!/usr/bin/env python3
"""
Script untuk memperbaiki password semua akun orang tua
"""

from app.data_migration import create_app, db
from app.models import OrangTuaSantri
from werkzeug.security import generate_password_hash, check_password_hash

def fix_orangtua_passwords():
    """Memperbaiki password semua akun orang tua"""
    
    app = create_app()
    
    with app.app_context():
        # Ambil semua akun orang tua
        orangtua_list = OrangTuaSantri.query.all()
        
        if not orangtua_list:
            print("❌ Tidak ada data orang tua di database")
            return
        
        print(f"🔧 Memperbaiki password untuk {len(orangtua_list)} akun orang tua...")
        print("=" * 60)
        
        for orangtua in orangtua_list:
            # Buat password default berdasarkan kode orang tua
            default_password = f"ortu{orangtua.kode_orangtua.lower()}"
            
            # Update password
            orangtua.password_hash = generate_password_hash(default_password, method='pbkdf2:sha256')
            
            print(f"✅ Updated {orangtua.nama} (ID: {orangtua.ortu_id})")
            print(f"   Kode: {orangtua.kode_orangtua}")
            print(f"   Password: {default_password}")
            print(f"   Santri: {orangtua.santri.nama_lengkap if orangtua.santri else 'N/A'}")
            print()
        
        # Commit perubahan
        db.session.commit()
        print("✅ Semua password orang tua berhasil diupdate!")
        
        # Tampilkan daftar kredensial
        print("\n📋 Daftar Kredensial Orang Tua:")
        print("=" * 60)
        print(f"{'Nama Ortu':<20} {'Kode':<15} {'Password':<15} {'Nama Santri':<20}")
        print("-" * 80)
        
        for orangtua in orangtua_list:
            default_password = f"ortu{orangtua.kode_orangtua.lower()}"
            nama_santri = orangtua.santri.nama_lengkap if orangtua.santri else 'N/A'
            print(f"{orangtua.nama:<20} {orangtua.kode_orangtua:<15} {default_password:<15} {nama_santri:<20}")

def test_orangtua_login():
    """Test login untuk beberapa akun orang tua"""
    
    app = create_app()
    
    with app.app_context():
        # Ambil 3 akun orang tua pertama untuk test
        orangtua_list = OrangTuaSantri.query.limit(3).all()
        
        print("\n🧪 Test Login Orang Tua:")
        print("=" * 60)
        
        for orangtua in orangtua_list:
            default_password = f"ortu{orangtua.kode_orangtua.lower()}"
            
            if orangtua.check_password(default_password):
                print(f"✅ Login berhasil: {orangtua.nama}")
                print(f"   Kode: {orangtua.kode_orangtua}")
                print(f"   Password: {default_password}")
            else:
                print(f"❌ Login gagal: {orangtua.nama}")
                print(f"   Kode: {orangtua.kode_orangtua}")
                print(f"   Password: {default_password}")
            print()

def create_missing_orangtua():
    """Buat akun orang tua yang hilang berdasarkan data santri"""
    
    app = create_app()
    
    from app.models import Santri
    
    with app.app_context():
        # Ambil semua santri yang belum memiliki orang tua
        santri_list = Santri.query.all()
        
        print(f"\n🔍 Memeriksa santri yang belum memiliki akun orang tua...")
        print("=" * 60)
        
        for santri in santri_list:
            # Cek apakah sudah ada orang tua untuk santri ini
            existing_ortu = OrangTuaSantri.query.filter_by(santri_id=santri.santri_id).first()
            
            if not existing_ortu:
                # Buat akun orang tua baru
                kode_orangtua = f"ORTU{santri.santri_id:03d}"
                nama_ortu = santri.nama_orang_tua if santri.nama_orang_tua else f"Orang Tua {santri.nama_lengkap}"
                default_password = f"ortu{kode_orangtua.lower()}"
                
                new_ortu = OrangTuaSantri(
                    nama=nama_ortu,
                    kode_orangtua=kode_orangtua,
                    santri_id=santri.santri_id,
                    alamat=santri.alamat,
                    nomor_telepon="",
                    password_hash=generate_password_hash(default_password, method='pbkdf2:sha256')
                )
                
                db.session.add(new_ortu)
                print(f"✅ Dibuat: {nama_ortu} untuk {santri.nama_lengkap}")
                print(f"   Kode: {kode_orangtua}")
                print(f"   Password: {default_password}")
            else:
                print(f"⚠️  Sudah ada: {existing_ortu.nama} untuk {santri.nama_lengkap}")
        
        db.session.commit()
        print("\n✅ Pembuatan akun orang tua selesai!")

if __name__ == "__main__":
    print("🔧 Memperbaiki akun orang tua...")
    print("=" * 60)
    
    # Buat akun orang tua yang hilang
    create_missing_orangtua()
    
    # Perbaiki password
    fix_orangtua_passwords()
    
    # Test login
    test_orangtua_login()
    
    print("\n🎉 Selesai!")
    print("\n📋 Cara Login Orang Tua:")
    print("   1. Buka aplikasi mobile")
    print("   2. Pilih 'Orang Tua Santri'")
    print("   3. Masukkan kode orang tua (contoh: ORTU001)")
    print("   4. Masukkan password (contoh: ortuortu001)") 