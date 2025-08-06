#!/usr/bin/env python3
"""
Script untuk membuat data test orang tua dan santri
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Santri, OrangTuaSantri, Guru, PenilaianHafalan
from datetime import datetime

def create_test_data():
    """Membuat data test untuk testing"""
    
    app = create_app()
    
    with app.app_context():
        print("🔧 Membuat Data Test...")
        print("=" * 50)
        
        # 1. Cek apakah sudah ada data
        existing_santri = Santri.query.first()
        existing_orangtua = OrangTuaSantri.query.first()
        
        if existing_santri and existing_orangtua:
            print("✅ Data sudah ada, tidak perlu membuat data test")
            return
        
        # 2. Buat Guru jika belum ada
        guru = Guru.query.filter_by(kode_guru='G01').first()
        if not guru:
            guru = Guru(
                kode_guru='G01',
                nama_lengkap='Guru Test',
                email='guru@test.com',
                password='password123'
            )
            db.session.add(guru)
            print("✅ Guru test dibuat")
        
        # 3. Buat Santri jika belum ada
        santri = Santri.query.filter_by(kode_santri='S01').first()
        if not santri:
            santri = Santri(
                kode_santri='S01',
                nama_lengkap='Santri Dio',
                tingkatan='Pemula',
                email='santri@test.com',
                password='password123'
            )
            db.session.add(santri)
            print("✅ Santri test dibuat")
        
        # 4. Buat Orang Tua jika belum ada
        orangtua = OrangTuaSantri.query.filter_by(kode_orangtua='OT01').first()
        if not orangtua:
            orangtua = OrangTuaSantri(
                kode_orangtua='OT01',
                nama_lengkap='Orang Tua Dio',
                email='orangtua@test.com',
                password='password123',
                santri_id=santri.santri_id if santri.santri_id else 1
            )
            db.session.add(orangtua)
            print("✅ Orang tua test dibuat")
        
        # 5. Commit perubahan
        try:
            db.session.commit()
            print("✅ Data test berhasil disimpan")
            
            # 6. Buat penilaian test jika belum ada
            existing_penilaian = PenilaianHafalan.query.first()
            if not existing_penilaian and santri.santri_id and guru.guru_id:
                penilaian = PenilaianHafalan(
                    santri_id=santri.santri_id,
                    guru_id=guru.guru_id,
                    surat='Al-Fatihah',
                    dari_ayat=1,
                    sampai_ayat=7,
                    tanggal_penilaian=datetime.now(),
                    nilai=85.0,
                    status='LULUS',
                    hasil_naive_bayes=85.0,
                    catatan='Hafalan bagus, perlu perbaikan tajwid'
                )
                db.session.add(penilaian)
                db.session.commit()
                print("✅ Penilaian test dibuat")
            
        except Exception as e:
            print(f"❌ Error menyimpan data: {e}")
            db.session.rollback()
        
        # 7. Tampilkan data yang dibuat
        print("\n📊 Data yang tersedia:")
        print("-" * 30)
        
        santri_list = Santri.query.all()
        print(f"Santri: {len(santri_list)} data")
        for s in santri_list:
            print(f"  - {s.kode_santri}: {s.nama_lengkap}")
        
        orangtua_list = OrangTuaSantri.query.all()
        print(f"Orang Tua: {len(orangtua_list)} data")
        for ot in orangtua_list:
            print(f"  - {ot.kode_orangtua}: {ot.nama_lengkap}")
        
        guru_list = Guru.query.all()
        print(f"Guru: {len(guru_list)} data")
        for g in guru_list:
            print(f"  - {g.kode_guru}: {g.nama_lengkap}")
        
        penilaian_list = PenilaianHafalan.query.all()
        print(f"Penilaian: {len(penilaian_list)} data")

if __name__ == "__main__":
    create_test_data() 