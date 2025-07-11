# app/__init__.py
import os
import pickle
import numpy as np
from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app.routes import register_routes
from app.extensions import db, migrate # Import db and migrate from extensions.py

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
        db.create_all()

    # ===============================================
    # Memuat Model Machine Learning dan Encoder
    # ===============================================
    global model, le_tingkat, le_kemajuan # Pastikan ini mengacu pada variabel global
    try:
        with open('output/model.pkl', 'rb') as f_model:
            app.model = pickle.load(f_model)
        with open('output/encoder.pkl', 'rb') as f_enc:
            encoders = pickle.load(f_enc)
            app.le_tingkat = encoders['tingkat_hafalan']
            app.le_kemajuan = encoders['kemajuan']
        print("Machine Learning model and encoders loaded successfully.")
    except FileNotFoundError:
        print("Error: model.pkl or encoder.pkl not found. Ensure 'output' directory and files exist.")
        # Opsi: app.logger.error("ML models not found...")
    except Exception as e:
        print(f"Error loading ML models: {e}")


    # ===============================================
    # Endpoint Aplikasi (Routes)
    # ===============================================

    # Register blueprints or routes
    register_routes(app)

    return app