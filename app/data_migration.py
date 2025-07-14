# app/__init__.py
import sys
import os
import pickle
import numpy as np
from flask import Flask, request, jsonify, render_template
from app.extensions import db, migrate # Mengimpor objek db dan migrate dari extensions.py
from werkzeug.security import generate_password_hash, check_password_hash # Meskipun ini tidak langsung dipakai di sini, tapi di models.py

# ===============================================
# Inisialisasi SQLAlchemy (tanpa app dulu)
# ===============================================
# db = SQLAlchemy()
# migrate = Migrate()

__all__ = ['create_app', 'db', 'migrate']

# Variabel global untuk model ML (akan dimuat di create_app)
model = None
le_tingkat = None
le_kemajuan = None

# ===============================================
# Fungsi Factory untuk Membuat Aplikasi Flask
# ===============================================
def create_app():
    app = Flask(__name__, template_folder='../admin', static_folder='static')

    # Konfigurasi Database MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost:3306/monitoring_app' # Ganti dengan kredensial MySQL Anda yang sebenarnya
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_super_secret_key_here' # Ganti dengan kunci rahasia yang kuat

    # Inisialisasi db dengan aplikasi Flask
    db.init_app(app)
    migrate.init_app(app, db)

    # Import Models setelah db diinisialisasi
    from app import models # Ini akan mengimpor semua model dari models.py

    # Buat tabel database jika belum ada
    with app.app_context():
        # db.create_all() # Tidak perlu lagi di sini, migrasi yang akan menanganinya
        pass

    # ===============================================
    # Memuat Model Machine Learning dan Encoder
    # ===============================================
    global model, le_tingkat, le_kemajuan
    try:
        with open('output/model.pkl', 'rb') as f_model:
            model = pickle.load(f_model)
        with open('output/encoder.pkl', 'rb') as f_enc:
            encoders = pickle.load(f_enc)
            le_tingkat = encoders['tingkat_hafalan']
            le_kemajuan = encoders['kemajuan']
        print("Machine Learning model and encoders loaded successfully.")
    except FileNotFoundError:
        print("Error: model.pkl or encoder.pkl not found. Ensure 'output' directory and files exist.")
        # Opsi: app.logger.error("ML models not found...")
    except Exception as e:
        print(f"Error loading ML models: {e}")

    # Import dan daftarkan rute
    from app.routes import register_routes
    register_routes(app)

    return app # Mengembalikan instance aplikasi Flask

def update_santri_id_orangtua():
    from app.models import db, OrangTuaSantri, Santri
    updated = 0
    with db.session.begin():
        ortu_list = OrangTuaSantri.query.all()
        for ortu in ortu_list:
            # Cari santri yang nama_orang_tua-nya sama dengan nama ortu
            santri = Santri.query.filter_by(nama_orang_tua=ortu.nama).first()
            if santri:
                ortu.santri_id = santri.santri_id
                updated += 1
                print(f"Ortu ID {ortu.ortu_id} diupdate ke santri_id {santri.santri_id}")
            else:
                print(f"Tidak ditemukan santri untuk ortu_id {ortu.ortu_id} (nama ortu: {ortu.nama})")
    db.session.commit()
    print(f"Update selesai. Total data terupdate: {updated}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from run import app
    with app.app_context():
        update_santri_id_orangtua()