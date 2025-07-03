# run.py
from app import create_app, db # Impor fungsi create_app dan objek db
from app.models import Admin, Guru, Santri # Impor model-model Anda

# ===============================================
# Main Block untuk Menjalankan Aplikasi
# ===============================================
if __name__ == '__main__':
    app = create_app() # Buat instance aplikasi Flask

    # Hapus db.create_all() dan data dummy karena migrasi akan menanganinya

    print("Flask app running. Endpoints:")
    print(app.url_map)
    app.run(debug=True)