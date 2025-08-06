#!/usr/bin/env python3
"""
Script untuk membuat user database monitoringapp dengan password monitoringhafalan25
"""

import mysql.connector
from mysql.connector import Error

def create_database_user():
    """Membuat user database monitoringapp dengan password monitoringhafalan25"""
    
    # Konfigurasi koneksi ke MySQL sebagai root
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  # Sesuaikan dengan password root MySQL Anda
        'port': 3306
    }
    
    try:
        # Koneksi ke MySQL
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 1. Buat user monitoringapp
            print("Membuat user monitoringapp...")
            create_user_query = """
            CREATE USER IF NOT EXISTS 'monitoringapp'@'localhost' 
            IDENTIFIED BY 'monitoringhafalan25';
            """
            cursor.execute(create_user_query)
            
            # 2. Buat database monitoring_app jika belum ada
            print("Membuat database monitoring_app...")
            create_database_query = "CREATE DATABASE IF NOT EXISTS monitoring_app;"
            cursor.execute(create_database_query)
            
            # 3. Berikan hak akses penuh ke database monitoring_app
            print("Memberikan hak akses ke database monitoring_app...")
            grant_privileges_query = """
            GRANT ALL PRIVILEGES ON monitoring_app.* TO 'monitoringapp'@'localhost';
            """
            cursor.execute(grant_privileges_query)
            
            # 4. Berikan hak akses untuk membuat database (jika diperlukan)
            print("Memberikan hak akses tambahan...")
            grant_create_query = """
            GRANT CREATE ON *.* TO 'monitoringapp'@'localhost';
            """
            cursor.execute(grant_create_query)
            
            # 5. Terapkan perubahan
            print("Menerapkan perubahan...")
            cursor.execute("FLUSH PRIVILEGES;")
            
            print("✅ User database berhasil dibuat!")
            print("Username: monitoringapp")
            print("Password: monitoringhafalan25")
            print("Database: monitoring_app")
            
            # Test koneksi dengan user baru
            print("\n🧪 Testing koneksi dengan user baru...")
            test_config = {
                'host': 'localhost',
                'user': 'monitoringapp',
                'password': 'monitoringhafalan25',
                'database': 'monitoring_app',
                'port': 3306
            }
            
            test_connection = mysql.connector.connect(**test_config)
            if test_connection.is_connected():
                print("✅ Koneksi dengan user baru berhasil!")
                test_connection.close()
            else:
                print("❌ Koneksi dengan user baru gagal!")
                
    except Error as e:
        print(f"❌ Error: {e}")
        print("\nTips troubleshooting:")
        print("1. Pastikan MySQL server berjalan")
        print("2. Pastikan password root MySQL benar")
        print("3. Pastikan Anda memiliki hak akses untuk membuat user")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("Koneksi MySQL ditutup.")

if __name__ == "__main__":
    print("🚀 Membuat user database untuk monitoring_app...")
    print("=" * 50)
    create_database_user()
    print("=" * 50)
    print("Selesai!") 