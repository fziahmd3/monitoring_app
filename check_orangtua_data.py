#!/usr/bin/env python3
"""
Script untuk memeriksa data orang tua dan relasinya dengan santri
"""

import mysql.connector
from mysql.connector import Error

def check_orangtua_data():
    """Memeriksa data orang tua dan relasinya"""
    
    config = {
        'host': 'localhost',
        'user': 'monitoringapp',
        'password': 'monitoringhafalan25',
        'database': 'monitoring_app',
        'port': 3306
    }
    
    try:
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("🔍 Memeriksa Data Orang Tua...")
            print("=" * 60)
            
            # 1. Periksa tabel orangtuasantri
            print("\n1. Data Tabel OrangTuaSantri:")
            cursor.execute("SELECT * FROM orangtuasantri")
            orangtua_data = cursor.fetchall()
            
            if orangtua_data:
                for data in orangtua_data:
                    print(f"   Kode Orang Tua: {data['kode_orangtua']}")
                    print(f"   Nama: {data['nama_lengkap']}")
                    print(f"   Santri ID: {data['santri_id']}")
                    print(f"   Email: {data['email']}")
                    print("   ---")
            else:
                print("   ❌ Tidak ada data orang tua!")
            
            # 2. Periksa tabel santri
            print("\n2. Data Tabel Santri:")
            cursor.execute("SELECT * FROM santri")
            santri_data = cursor.fetchall()
            
            if santri_data:
                for data in santri_data:
                    print(f"   Santri ID: {data['santri_id']}")
                    print(f"   Kode Santri: {data['kode_santri']}")
                    print(f"   Nama: {data['nama_lengkap']}")
                    print(f"   Tingkatan: {data['tingkatan']}")
                    print("   ---")
            else:
                print("   ❌ Tidak ada data santri!")
            
            # 3. Periksa relasi
            print("\n3. Relasi Orang Tua - Santri:")
            cursor.execute("""
                SELECT ot.kode_orangtua, ot.nama_lengkap as nama_orangtua, 
                       s.kode_santri, s.nama_lengkap as nama_santri, s.tingkatan
                FROM orangtuasantri ot
                LEFT JOIN santri s ON ot.santri_id = s.santri_id
            """)
            relasi_data = cursor.fetchall()
            
            if relasi_data:
                for data in relasi_data:
                    print(f"   Orang Tua: {data['nama_orangtua']} ({data['kode_orangtua']})")
                    if data['nama_santri']:
                        print(f"   → Santri: {data['nama_santri']} ({data['kode_santri']}) - {data['tingkatan']}")
                    else:
                        print(f"   → ❌ Santri tidak ditemukan!")
                    print("   ---")
            else:
                print("   ❌ Tidak ada relasi orang tua-santri!")
            
            # 4. Test endpoint dengan data yang ada
            print("\n4. Test Endpoint Progress Anak:")
            if orangtua_data:
                for data in orangtua_data:
                    kode_orangtua = data['kode_orangtua']
                    print(f"   Testing: /api/orangtua/{kode_orangtua}/progress_anak")
                    break  # Test hanya yang pertama
            else:
                print("   ❌ Tidak ada data orang tua untuk testing!")
                
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nKoneksi MySQL ditutup.")

if __name__ == "__main__":
    check_orangtua_data() 