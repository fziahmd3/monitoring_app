#!/usr/bin/env python3
"""
Script untuk memeriksa dan memastikan semua tabel database sudah dibuat dengan benar
"""

import mysql.connector
from mysql.connector import Error

def check_database_tables():
    """Memeriksa apakah semua tabel database sudah dibuat"""
    
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
            
            # Daftar tabel yang seharusnya ada
            expected_tables = [
                'admin',
                'guru', 
                'santri',
                'orangtuasantri',  # Nama tabel yang benar
                'penilaianhafalan',  # Nama tabel yang benar
                'alembic_version'
            ]
            
            print("🔍 Memeriksa tabel database...")
            print("=" * 50)
            
            # Ambil daftar tabel yang ada
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            print(f"Tabel yang ada di database: {existing_tables}")
            print()
            
            # Periksa setiap tabel yang diharapkan
            missing_tables = []
            for table in expected_tables:
                if table in existing_tables:
                    print(f"✅ Tabel {table} - ADA")
                    
                    # Hitung jumlah record
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"   📊 Jumlah record: {count}")
                    except Error as e:
                        print(f"   ⚠️  Error menghitung record: {e}")
                else:
                    print(f"❌ Tabel {table} - TIDAK ADA")
                    missing_tables.append(table)
            
            print()
            print("=" * 50)
            
            if missing_tables:
                print(f"⚠️  Tabel yang hilang: {missing_tables}")
                print("💡 Jalankan migrasi database untuk membuat tabel yang hilang")
            else:
                print("✅ Semua tabel database sudah tersedia!")
                
            # Test query untuk memastikan koneksi berfungsi
            print("\n🧪 Testing query sederhana...")
            try:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    print("✅ Query test berhasil!")
                else:
                    print("❌ Query test gagal!")
            except Error as e:
                print(f"❌ Error pada query test: {e}")
                
    except Error as e:
        print(f"❌ Error: {e}")
        print("\nTips troubleshooting:")
        print("1. Pastikan MySQL server berjalan")
        print("2. Pastikan user monitoringapp sudah dibuat")
        print("3. Pastikan password monitoringhafalan25 benar")
        print("4. Pastikan database monitoring_app sudah dibuat")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nKoneksi MySQL ditutup.")

def create_missing_tables():
    """Membuat tabel yang hilang menggunakan Flask-SQLAlchemy"""
    try:
        print("\n🔧 Membuat tabel yang hilang...")
        
        # Import aplikasi Flask
        from app.data_migration import create_app
        from app.extensions import db
        
        # Buat aplikasi
        app = create_app()
        
        with app.app_context():
            # Buat semua tabel
            db.create_all()
            print("✅ Semua tabel berhasil dibuat!")
            
    except Exception as e:
        print(f"❌ Error membuat tabel: {e}")

if __name__ == "__main__":
    print("🚀 Memeriksa database monitoring_app...")
    check_database_tables()
    
    # Tanya user apakah ingin membuat tabel yang hilang
    response = input("\nApakah Anda ingin membuat tabel yang hilang? (y/n): ")
    if response.lower() in ['y', 'yes', 'ya']:
        create_missing_tables()
    
    print("\nSelesai!") 