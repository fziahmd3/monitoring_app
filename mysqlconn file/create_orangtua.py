#!/usr/bin/env python3
"""
Script untuk menambahkan data Orang Tua Santri ke database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, OrangTuaSantri, Santri
from werkzeug.security import generate_password_hash

def create_orangtua():
    app = create_app()
    
    with app.app_context():
        try:
            # Cek apakah ada data santri
            santri_list = Santri.query.all()
            if not santri_list:
                print("❌ Tidak ada data santri di database!")
                print("Silakan tambahkan data santri terlebih dahulu.")
                return
            
            print("📋 Daftar Santri yang tersedia:")
            for i, santri in enumerate(santri_list, 1):
                print(f"{i}. {santri.nama_lengkap} (Kode: {santri.kode_santri})")
            
            print("\n" + "="*50)
            
            # Input data orang tua
            print("📝 Masukkan data Orang Tua Santri:")
            
            # Pilih santri
            while True:
                try:
                    santri_index = int(input("Pilih nomor santri (1-{}): ".format(len(santri_list)))) - 1
                    if 0 <= santri_index < len(santri_list):
                        selected_santri = santri_list[santri_index]
                        break
                    else:
                        print("❌ Nomor tidak valid!")
                except ValueError:
                    print("❌ Masukkan angka yang valid!")
            
            # Input data orang tua
            nama = input("Nama Orang Tua: ").strip()
            if not nama:
                print("❌ Nama tidak boleh kosong!")
                return
            
            alamat = input("Alamat (opsional): ").strip() or None
            nomor_telepon = input("Nomor Telepon (opsional): ").strip() or None
            
            # Generate kode orang tua
            kode_orangtua = f"ORTU{selected_santri.kode_santri}"
            
            # Password default
            password = "123456"  # Password default
            
            # Cek apakah sudah ada orang tua untuk santri ini
            existing_orangtua = OrangTuaSantri.query.filter_by(santri_id=selected_santri.santri_id).first()
            if existing_orangtua:
                print(f"❌ Sudah ada data orang tua untuk santri {selected_santri.nama_lengkap}!")
                print(f"   Nama: {existing_orangtua.nama}")
                print(f"   Kode: {existing_orangtua.kode_orangtua}")
                return
            
            # Cek apakah kode orang tua sudah ada
            existing_kode = OrangTuaSantri.query.filter_by(kode_orangtua=kode_orangtua).first()
            if existing_kode:
                print(f"❌ Kode orang tua {kode_orangtua} sudah ada!")
                return
            
            # Buat data orang tua
            orangtua = OrangTuaSantri(
                nama=nama,
                alamat=alamat,
                nomor_telepon=nomor_telepon,
                santri_id=selected_santri.santri_id,
                kode_orangtua=kode_orangtua
            )
            orangtua.set_password(password)
            
            # Simpan ke database
            db.session.add(orangtua)
            db.session.commit()
            
            print("\n✅ Data Orang Tua berhasil ditambahkan!")
            print("="*50)
            print(f"📋 Detail Data:")
            print(f"   Nama: {nama}")
            print(f"   Kode: {kode_orangtua}")
            print(f"   Santri: {selected_santri.nama_lengkap} ({selected_santri.kode_santri})")
            print(f"   Password: {password}")
            print(f"   Alamat: {alamat or '-'}")
            print(f"   Telepon: {nomor_telepon or '-'}")
            print("\n💡 Informasi Login:")
            print(f"   User Type: Orang Tua Santri")
            print(f"   Credential: {kode_orangtua}")
            print(f"   Password: {password}")
            
        except KeyboardInterrupt:
            print("\n❌ Operasi dibatalkan oleh user.")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

def list_orangtua():
    app = create_app()
    
    with app.app_context():
        try:
            orangtua_list = OrangTuaSantri.query.all()
            
            if not orangtua_list:
                print("📭 Tidak ada data orang tua di database.")
                return
            
            print("📋 Daftar Orang Tua Santri:")
            print("="*80)
            print(f"{'No':<3} {'Kode':<12} {'Nama':<25} {'Santri':<25} {'Telepon':<15}")
            print("-"*80)
            
            for i, orangtua in enumerate(orangtua_list, 1):
                santri_nama = orangtua.santri.nama_lengkap if orangtua.santri else "N/A"
                telepon = orangtua.nomor_telepon or "-"
                print(f"{i:<3} {orangtua.kode_orangtua:<12} {orangtua.nama:<25} {santri_nama:<25} {telepon:<15}")
            
            print("-"*80)
            print(f"Total: {len(orangtua_list)} orang tua")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Script Manajemen Data Orang Tua Santri")
    print("="*50)
    
    while True:
        print("\n📋 Menu:")
        print("1. Tambah Orang Tua")
        print("2. Lihat Daftar Orang Tua")
        print("3. Keluar")
        
        try:
            choice = input("\nPilih menu (1-3): ").strip()
            
            if choice == "1":
                create_orangtua()
            elif choice == "2":
                list_orangtua()
            elif choice == "3":
                print("👋 Terima kasih!")
                break
            else:
                print("❌ Pilihan tidak valid!")
                
        except KeyboardInterrupt:
            print("\n👋 Terima kasih!")
            break
        except Exception as e:
            print(f"❌ Error: {e}") 