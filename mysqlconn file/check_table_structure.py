#!/usr/bin/env python3
"""
Script untuk memeriksa struktur tabel orangtuasantri di database
"""

import mysql.connector
from mysql.connector import Error

def check_table_structure():
    """Memeriksa struktur tabel orangtuasantri"""
    
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
            
            print("🔍 Memeriksa struktur tabel orangtuasantri...")
            print("=" * 60)
            
            # Periksa struktur tabel orangtuasantri
            cursor.execute("DESCRIBE orangtuasantri")
            columns = cursor.fetchall()
            
            print("Struktur tabel orangtuasantri:")
            print(f"{'Field':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<15} {'Extra':<10}")
            print("-" * 85)
            
            for column in columns:
                field, type_, null, key, default, extra = column
                print(f"{field:<20} {type_:<20} {null:<10} {key:<10} {str(default):<15} {extra:<10}")
            
            print()
            print("=" * 60)
            
            # Periksa apakah kolom kode_orangtua ada
            column_names = [col[0] for col in columns]
            if 'kode_orangtua' in column_names:
                print("✅ Kolom kode_orangtua ADA di tabel")
            else:
                print("❌ Kolom kode_orangtua TIDAK ADA di tabel")
                print("💡 Perlu menjalankan migrasi untuk menambah kolom")
                
    except Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nKoneksi MySQL ditutup.")

if __name__ == "__main__":
    check_table_structure() 