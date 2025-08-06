#!/usr/bin/env python3
"""
Script untuk memeriksa dan memperbaiki data penilaian hafalan
"""

from app.data_migration import create_app, db
from app.models import PenilaianHafalan, Santri, OrangTuaSantri

def check_penilaian_data():
    """Memeriksa data penilaian hafalan"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 Memeriksa data penilaian hafalan...")
        print("=" * 60)
        
        # Ambil semua penilaian
        penilaian_list = PenilaianHafalan.query.all()
        
        if not penilaian_list:
            print("❌ Tidak ada data penilaian di database")
            return
        
        print(f"📊 Total penilaian: {len(penilaian_list)}")
        print()
        
        # Periksa setiap penilaian
        for penilaian in penilaian_list:
            print(f"Penilaian ID: {penilaian.penilaian_id}")
            print(f"  Santri ID: {penilaian.santri_id}")
            print(f"  Guru ID: {penilaian.guru_id}")
            print(f"  Surat: {penilaian.surat}")
            print(f"  Dari Ayat: {penilaian.dari_ayat}")
            print(f"  Sampai Ayat: {penilaian.sampai_ayat}")
            print(f"  Hasil Naive Bayes: {penilaian.hasil_naive_bayes}")
            print(f"  Tanggal: {penilaian.tanggal_penilaian}")
            print()
        
        # Periksa relasi dengan santri
        print("🔗 Memeriksa relasi dengan santri...")
        print("=" * 60)
        
        for penilaian in penilaian_list:
            santri = Santri.query.filter_by(kode_santri=penilaian.santri_id).first()
            if santri:
                print(f"✅ Penilaian {penilaian.penilaian_id} -> Santri: {santri.nama_lengkap} ({santri.kode_santri})")
            else:
                print(f"❌ Penilaian {penilaian.penilaian_id} -> Santri tidak ditemukan: {penilaian.santri_id}")

def fix_penilaian_santri_id():
    """Memperbaiki santri_id di penilaian jika diperlukan"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Memperbaiki santri_id di penilaian...")
        print("=" * 60)
        
        # Ambil semua penilaian
        penilaian_list = PenilaianHafalan.query.all()
        
        if not penilaian_list:
            print("❌ Tidak ada data penilaian di database")
            return
        
        fixed_count = 0
        
        for penilaian in penilaian_list:
            # Cek apakah santri_id sudah benar (menggunakan kode_santri)
            santri = Santri.query.filter_by(kode_santri=penilaian.santri_id).first()
            
            if not santri:
                # Coba cari dengan santri_id sebagai ID numerik
                santri_by_id = Santri.query.filter_by(santri_id=penilaian.santri_id).first()
                if santri_by_id:
                    # Update santri_id menjadi kode_santri
                    old_santri_id = penilaian.santri_id
                    penilaian.santri_id = santri_by_id.kode_santri
                    db.session.commit()
                    print(f"✅ Fixed: Penilaian {penilaian.penilaian_id} - {old_santri_id} -> {santri_by_id.kode_santri}")
                    fixed_count += 1
                else:
                    print(f"❌ Penilaian {penilaian.penilaian_id} - Santri tidak ditemukan: {penilaian.santri_id}")
            else:
                print(f"✅ Penilaian {penilaian.penilaian_id} - Santri sudah benar: {penilaian.santri_id}")
        
        print(f"\n🎉 Selesai! {fixed_count} penilaian diperbaiki.")

def test_progress_anak():
    """Test endpoint progress anak"""
    
    app = create_app()
    
    with app.app_context():
        print("🧪 Test endpoint progress anak...")
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
            
            print(f"  ✅ Santri: {santri.nama_lengkap} ({santri.kode_santri})")
            
            # Cek penilaian
            penilaian_list = PenilaianHafalan.query.filter_by(santri_id=santri.kode_santri).all()
            print(f"  📊 Total penilaian: {len(penilaian_list)}")
            
            if penilaian_list:
                for penilaian in penilaian_list[:3]:  # Tampilkan 3 terakhir
                    print(f"    - {penilaian.surat} (Ayat {penilaian.dari_ayat}-{penilaian.sampai_ayat}) - {penilaian.hasil_naive_bayes}")

if __name__ == "__main__":
    print("🔧 Memperbaiki data penilaian hafalan...")
    print("=" * 60)
    
    # Periksa data
    check_penilaian_data()
    
    # Perbaiki data
    fix_penilaian_santri_id()
    
    # Test progress anak
    test_progress_anak()
    
    print("\n🎉 Selesai!") 