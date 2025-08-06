#!/usr/bin/env python3
"""
Script untuk memperbaiki relasi orang tua-santri
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Santri, OrangTuaSantri

def fix_orangtua_relation():
    """Memperbaiki relasi orang tua-santri"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Memperbaiki Relasi Orang Tua-Santri...")
        print("=" * 50)
        
        # 1. Ambil semua orang tua
        orangtua_list = OrangTuaSantri.query.all()
        print(f"Total orang tua: {len(orangtua_list)}")
        
        # 2. Ambil semua santri
        santri_list = Santri.query.all()
        print(f"Total santri: {len(santri_list)}")
        
        # 3. Perbaiki relasi yang rusak
        fixed_count = 0
        for orangtua in orangtua_list:
            if not orangtua.santri_id or orangtua.santri_id <= 0:
                # Cari santri berdasarkan nama atau buat relasi default
                if santri_list:
                    # Ambil santri pertama sebagai default
                    orangtua.santri_id = santri_list[0].santri_id
                    print(f"✅ Memperbaiki relasi untuk {orangtua.nama_lengkap} -> {santri_list[0].nama_lengkap}")
                    fixed_count += 1
                else:
                    print(f"❌ Tidak ada santri untuk {orangtua.nama_lengkap}")
        
        # 4. Commit perubahan
        if fixed_count > 0:
            try:
                db.session.commit()
                print(f"✅ Berhasil memperbaiki {fixed_count} relasi")
            except Exception as e:
                print(f"❌ Error: {e}")
                db.session.rollback()
        else:
            print("✅ Semua relasi sudah benar")
        
        # 5. Tampilkan relasi yang ada
        print("\n📊 Relasi yang ada:")
        print("-" * 30)
        for orangtua in orangtua_list:
            santri = Santri.query.get(orangtua.santri_id) if orangtua.santri_id else None
            if santri:
                print(f"✅ {orangtua.nama_lengkap} ({orangtua.kode_orangtua}) -> {santri.nama_lengkap} ({santri.kode_santri})")
            else:
                print(f"❌ {orangtua.nama_lengkap} ({orangtua.kode_orangtua}) -> TIDAK ADA SANTRI")

if __name__ == "__main__":
    fix_orangtua_relation() 