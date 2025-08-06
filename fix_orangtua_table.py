#!/usr/bin/env python3
"""
Script untuk memperbaiki struktur tabel orangtuasantri dengan menambahkan kolom yang hilang
"""

import mysql.connector
from mysql.connector import Error

def fix_orangtua_table():
    """Memperbaiki struktur tabel orangtuasantri"""
    
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
            
            print("🔧 Memperbaiki struktur tabel orangtuasantri...")
            print("=" * 60)
            
            # Daftar kolom yang perlu ditambahkan
            columns_to_add = [
                "ADD COLUMN kode_orangtua VARCHAR(20) UNIQUE NOT NULL AFTER ortu_id",
                "ADD COLUMN password_hash VARCHAR(128) NOT NULL DEFAULT '' AFTER kode_orangtua",
                "ADD COLUMN last_login DATETIME NULL AFTER password_hash",
                "ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP AFTER last_login",
                "ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at",
                "ADD COLUMN santri_id INT(11) NOT NULL AFTER updated_at",
                "ADD FOREIGN KEY (santri_id) REFERENCES Santri(santri_id)"
            ]
            
            # Tambahkan kolom satu per satu
            for i, column_def in enumerate(columns_to_add, 1):
                try:
                    print(f"Menambahkan kolom {i}/{len(columns_to_add)}...")
                    cursor.execute(f"ALTER TABLE orangtuasantri {column_def}")
                    print(f"✅ Berhasil menambahkan: {column_def}")
                except Error as e:
                    if "Duplicate column name" in str(e):
                        print(f"⚠️  Kolom sudah ada: {column_def}")
                    elif "Duplicate key name" in str(e):
                        print(f"⚠️  Foreign key sudah ada: {column_def}")
                    else:
                        print(f"❌ Error menambahkan kolom: {e}")
                        print(f"   Query: ALTER TABLE orangtuasantri {column_def}")
            
            # Commit perubahan
            connection.commit()
            print("\n✅ Perubahan berhasil disimpan!")
            
            # Tampilkan struktur tabel setelah perbaikan
            print("\n🔍 Struktur tabel setelah perbaikan:")
            print("=" * 60)
            cursor.execute("DESCRIBE orangtuasantri")
            columns = cursor.fetchall()
            
            print(f"{'Field':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<15} {'Extra':<10}")
            print("-" * 85)
            
            for column in columns:
                field, type_, null, key, default, extra = column
                print(f"{field:<20} {type_:<20} {null:<10} {key:<10} {str(default):<15} {extra:<10}")
                
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nKoneksi MySQL ditutup.")

def update_existing_data():
    """Update data yang sudah ada dengan nilai default"""
    
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
            cursor = connection.cursor()
            
            print("\n🔄 Update data yang sudah ada...")
            
            # Update kode_orangtua untuk data yang sudah ada
            cursor.execute("SELECT ortu_id, nama FROM orangtuasantri WHERE kode_orangtua IS NULL OR kode_orangtua = ''")
            records = cursor.fetchall()
            
            for ortu_id, nama in records:
                # Buat kode_orangtua dari nama
                kode_orangtua = f"ORTU{ortu_id:03d}"
                cursor.execute("UPDATE orangtuasantri SET kode_orangtua = %s WHERE ortu_id = %s", (kode_orangtua, ortu_id))
                print(f"✅ Updated ortu_id {ortu_id}: {nama} -> kode_orangtua: {kode_orangtua}")
            
            # Update password_hash untuk data yang sudah ada
            cursor.execute("UPDATE orangtuasantri SET password_hash = %s WHERE password_hash = ''", ('default_password_hash',))
            print("✅ Updated password_hash untuk data yang kosong")
            
            connection.commit()
            print("✅ Update data selesai!")
            
    except Error as e:
        print(f"❌ Error update data: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    fix_orangtua_table()
    update_existing_data()
    print("\n🎉 Perbaikan tabel orangtuasantri selesai!") 