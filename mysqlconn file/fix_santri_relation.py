#!/usr/bin/env python3
"""
Script untuk memperbaiki relasi antara orang tua dan santri
"""

import mysql.connector
from mysql.connector import Error

def fix_santri_relation():
    """Memperbaiki relasi antara orang tua dan santri"""
    
    # Konfigurasi koneksi dengan user monitoringapp
    config = {
        'host': 'localhost',
        'user': 'monitoringapp',
        'password': 'monitoringhafalan25',
        'database': 'monitoring_app',
        'port': 3306
    }
    
    try:
        # Koneksi ke MySQL
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("🔧 Memperbaiki relasi orang tua - santri...")
            print("=" * 60)
            
            # Ambil data orang tua yang belum memiliki santri_id
            cursor.execute("""
                SELECT ortu_id, nama, nama_santri 
                FROM orangtuasantri 
                WHERE santri_id IS NULL
            """)
            records = cursor.fetchall()
            
            if not records:
                print("✅ Semua orang tua sudah memiliki relasi dengan santri")
                return
            
            print(f"Menemukan {len(records)} record yang perlu diperbaiki:")
            
            for ortu_id, nama_ortu, nama_santri in records:
                print(f"\n🔍 Mencari santri untuk: {nama_ortu} (anak: {nama_santri})")
                
                # Cari santri berdasarkan nama
                cursor.execute("""
                    SELECT santri_id, nama_lengkap, kode_santri 
                    FROM Santri 
                    WHERE nama_lengkap = %s OR nama_orang_tua = %s
                """, (nama_santri, nama_ortu))
                
                santri_result = cursor.fetchone()
                
                if santri_result:
                    santri_id, nama_lengkap, kode_santri = santri_result
                    cursor.execute("""
                        UPDATE orangtuasantri 
                        SET santri_id = %s 
                        WHERE ortu_id = %s
                    """, (santri_id, ortu_id))
                    
                    print(f"✅ Ditemukan: {nama_lengkap} (ID: {santri_id}, Kode: {kode_santri})")
                    print(f"   Relasi diperbaiki untuk ortu_id: {ortu_id}")
                else:
                    print(f"❌ Tidak ditemukan santri untuk: {nama_santri}")
                    print(f"   Mencoba mencari berdasarkan nama orang tua: {nama_ortu}")
                    
                    # Coba cari berdasarkan nama orang tua
                    cursor.execute("""
                        SELECT santri_id, nama_lengkap, kode_santri 
                        FROM Santri 
                        WHERE nama_orang_tua = %s
                    """, (nama_ortu,))
                    
                    santri_result = cursor.fetchone()
                    
                    if santri_result:
                        santri_id, nama_lengkap, kode_santri = santri_result
                        cursor.execute("""
                            UPDATE orangtuasantri 
                            SET santri_id = %s 
                            WHERE ortu_id = %s
                        """, (santri_id, ortu_id))
                        
                        print(f"✅ Ditemukan berdasarkan nama ortu: {nama_lengkap} (ID: {santri_id})")
                    else:
                        print(f"❌ Tidak ditemukan santri untuk ortu: {nama_ortu}")
                        print(f"   Akan menggunakan santri pertama sebagai default")
                        
                        # Gunakan santri pertama sebagai default
                        cursor.execute("SELECT santri_id, nama_lengkap FROM Santri LIMIT 1")
                        default_santri = cursor.fetchone()
                        
                        if default_santri:
                            default_santri_id, default_nama = default_santri
                            cursor.execute("""
                                UPDATE orangtuasantri 
                                SET santri_id = %s 
                                WHERE ortu_id = %s
                            """, (default_santri_id, ortu_id))
                            
                            print(f"⚠️  Menggunakan default: {default_nama} (ID: {default_santri_id})")
            
            # Commit perubahan
            connection.commit()
            print("\n✅ Relasi orang tua - santri berhasil diperbaiki!")
            
            # Tampilkan hasil akhir
            print("\n📊 Hasil akhir:")
            cursor.execute("""
                SELECT o.ortu_id, o.nama, s.nama_lengkap as nama_santri, s.kode_santri
                FROM orangtuasantri o
                LEFT JOIN Santri s ON o.santri_id = s.santri_id
                ORDER BY o.ortu_id
            """)
            
            results = cursor.fetchall()
            print(f"{'Ortu ID':<10} {'Nama Ortu':<20} {'Nama Santri':<20} {'Kode Santri':<15}")
            print("-" * 70)
            
            for ortu_id, nama_ortu, nama_santri, kode_santri in results:
                print(f"{ortu_id:<10} {nama_ortu:<20} {nama_santri or 'N/A':<20} {kode_santri or 'N/A':<15}")
                
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nKoneksi MySQL ditutup.")

if __name__ == "__main__":
    fix_santri_relation()
    print("\n🎉 Perbaikan relasi selesai!") 