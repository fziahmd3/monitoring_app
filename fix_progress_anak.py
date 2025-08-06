#!/usr/bin/env python3
"""
Script untuk memperbaiki endpoint progress anak
"""

from app.data_migration import create_app, db
from app.models import PenilaianHafalan, Santri, OrangTuaSantri

def check_santri_data():
    """Memeriksa data santri"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Memeriksa data santri...")
        print("=" * 60)
        
        # Ambil semua santri
        santri_list = Santri.query.all()
        
        for santri in santri_list:
            print(f"ID: {santri.santri_id}, Kode: {santri.kode_santri}, Nama: {santri.nama_lengkap}")

def check_penilaian_santri_mapping():
    """Memeriksa mapping antara penilaian dan santri"""
    
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Memeriksa mapping penilaian-santri...")
        print("=" * 60)
        
        # Ambil semua penilaian
        penilaian_list = PenilaianHafalan.query.all()
        
        for penilaian in penilaian_list:
            # Cari santri berdasarkan santri_id (integer)
            santri = Santri.query.filter_by(santri_id=penilaian.santri_id).first()
            if santri:
                print(f"✅ Penilaian {penilaian.penilaian_id} -> Santri: {santri.nama_lengkap} (ID: {santri.santri_id}, Kode: {santri.kode_santri})")
            else:
                print(f"❌ Penilaian {penilaian.penilaian_id} -> Santri tidak ditemukan: {penilaian.santri_id}")

def test_progress_anak_endpoint():
    """Test endpoint progress anak"""
    
    app = create_app()
    
    with app.app_context():
        print("\n🧪 Test endpoint progress anak...")
        print("=" * 60)
        
        # Ambil beberapa orang tua untuk test
        orangtua_list = OrangTuaSantri.query.limit(3).all()
        
        for orangtua in orangtua_list:
            print(f"\nTest untuk: {orangtua.nama} ({orangtua.kode_orangtua})")
            
            # Cek santri
            santri = orangtua.santri
            if not santri:
                print("  ❌ Santri tidak ditemukan")
                continue
            
            print(f"  ✅ Santri: {santri.nama_lengkap} (ID: {santri.santri_id}, Kode: {santri.kode_santri})")
            
            # Cek penilaian menggunakan santri_id (integer)
            penilaian_list = PenilaianHafalan.query.filter_by(santri_id=santri.santri_id).all()
            print(f"  📊 Total penilaian: {len(penilaian_list)}")
            
            if penilaian_list:
                for penilaian in penilaian_list[:3]:  # Tampilkan 3 terakhir
                    print(f"    - {penilaian.surat} (Ayat {penilaian.dari_ayat}-{penilaian.sampai_ayat}) - {penilaian.hasil_naive_bayes}")

def fix_progress_anak_endpoint():
    """Memperbaiki endpoint progress anak di routes.py"""
    
    print("\n🔧 Memperbaiki endpoint progress anak...")
    print("=" * 60)
    
    # Baca file routes.py
    with open('app/routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ganti query untuk menggunakan santri_id (integer) bukan kode_santri
    old_query = "penilaian_list = PenilaianHafalan.query.filter_by(santri_id=santri.kode_santri).order_by(PenilaianHafalan.tanggal_penilaian.desc()).all()"
    new_query = "penilaian_list = PenilaianHafalan.query.filter_by(santri_id=santri.santri_id).order_by(PenilaianHafalan.tanggal_penilaian.desc()).all()"
    
    if old_query in content:
        content = content.replace(old_query, new_query)
        
        # Tulis kembali ke file
        with open('app/routes.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Endpoint progress anak berhasil diperbaiki!")
        print("   Menggunakan santri_id (integer) untuk query penilaian")
    else:
        print("⚠️  Query tidak ditemukan, mungkin sudah benar")

if __name__ == "__main__":
    print("🔧 Memperbaiki progress anak...")
    print("=" * 60)
    
    # Periksa data santri
    check_santri_data()
    
    # Periksa mapping penilaian-santri
    check_penilaian_santri_mapping()
    
    # Test endpoint progress anak
    test_progress_anak_endpoint()
    
    # Perbaiki endpoint
    fix_progress_anak_endpoint()
    
    print("\n🎉 Selesai!") 