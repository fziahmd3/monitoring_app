# app/__init__.py
import os
import pickle
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash # Meskipun ini tidak langsung dipakai di sini, tapi di models.py

# ===============================================
# Inisialisasi SQLAlchemy (tanpa app dulu)
# ===============================================
db = SQLAlchemy()
migrate = Migrate()

# Variabel global untuk model ML (akan dimuat di create_app)
model = None
le_tingkat = None
le_kemajuan = None

# ===============================================
# Fungsi Factory untuk Membuat Aplikasi Flask
# ===============================================
def create_app():
    app = Flask(__name__)

    # Konfigurasi Database MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost:3306/monitoring_app' # Ganti dengan kredensial MySQL Anda yang sebenarnya
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_super_secret_key_here' # Ganti dengan kunci rahasia yang kuat

    # Inisialisasi db dengan aplikasi Flask
    db.init_app(app)
    migrate.init_app(app, db) # Inisialisasi Flask-Migrate

    # Import Models setelah db diinisialisasi
    from app import models # Ini akan mengimpor semua model dari models.py

    # ===============================================
    # Memuat Model Machine Learning dan Encoder
    # ===============================================
    global model, le_tingkat, le_kemajuan # Pastikan ini mengacu pada variabel global
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


    # ===============================================
    # Endpoint Aplikasi (Routes)
    # ===============================================

    # Endpoint untuk Halaman Input Web (Frontend Form)
    @app.route('/')
    def index():
        return render_template('index.html')

    # Endpoint untuk Prediksi dari Formulir Web (POST)
    @app.route('/predict_web', methods=['POST'])
    def predict_web():
        if model is None or le_tingkat is None or le_kemajuan is None:
            return render_template('result.html', hasil_prediksi='Error: Machine Learning model not loaded.'), 500

        print('Data diterima dari web form:', request.form)

        try:
            tingkat_hafalan_str = request.form['tingkat_hafalan']
            jumlah_setoran = int(request.form['jumlah_setoran'])
            kehadiran = int(request.form['kehadiran'])
        except KeyError as e:
            return render_template('result.html', hasil_prediksi=f'Error: Field missing from form ({e})'), 400
        except ValueError:
            return render_template('result.html', hasil_prediksi='Error: Jumlah setoran dan kehadiran harus berupa angka.'), 400

        # Encode tingkat_hafalan_str
        try:
            tingkat_hafalan_encoded = le_tingkat.transform([tingkat_hafalan_str])[0]
        except ValueError:
            return render_template('result.html', hasil_prediksi=f"Error: Tingkat hafalan tidak valid. Harusnya salah satu dari: {le_tingkat.classes_.tolist()}"), 400

        # Buat input array NumPy
        X_input = np.array([[tingkat_hafalan_encoded, jumlah_setoran, kehadiran]])
        print('X_input untuk prediksi (web):', X_input)

        # Lakukan prediksi
        y_pred_encoded = model.predict(X_input)

        # Inverse transform hasil prediksi
        label = le_kemajuan.inverse_transform(y_pred_encoded)[0]

        # Render halaman hasil dengan prediksi
        return render_template('result.html', hasil_prediksi=label)

    # Endpoint untuk API (JSON/Query Params)
    @app.route('/api/predict', methods=['POST', 'GET'])
    def api_predict():
        if model is None or le_tingkat is None or le_kemajuan is None:
            return jsonify({'error': 'Machine Learning model not loaded.'}), 500

        tingkat_hafalan_str = None
        jumlah_setoran = None
        kehadiran = None

        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body must be JSON for POST method'}), 400
            print('Data diterima (API POST):', data)
            try:
                tingkat_hafalan_str = data['tingkat_hafalan']
                jumlah_setoran = int(data['jumlah_setoran'])
                kehadiran = int(data['kehadiran'])
            except KeyError as e:
                return jsonify({'error': f'Missing required field in JSON: {e}'}), 400
            except ValueError:
                return jsonify({'error': 'jumlah_setoran and kehadiran must be integers in JSON'}), 400

        elif request.method == 'GET':
            print('Data diterima (API GET dari query parameters):', request.args)
            try:
                tingkat_hafalan_str = request.args.get('tingkat_hafalan')
                jumlah_setoran = int(request.args.get('jumlah_setoran'))
                kehadiran = int(request.args.get('kehadiran'))
            except (TypeError, ValueError) as e:
                return jsonify({'error': f'Invalid or missing query parameters. Ensure tingkat_hafalan (string), jumlah_setoran (int), and kehadiran (int) are provided. Error: {e}'}), 400

            if not all([tingkat_hafalan_str, jumlah_setoran is not None, kehadiran is not None]):
                return jsonify({'error': 'Missing required query parameters: tingkat_hafalan, jumlah_setoran, kehadiran'}), 400

        if tingkat_hafalan_str is None:
            return jsonify({'error': 'No input data provided for prediction'}), 400

        try:
            tingkat_hafalan_encoded = le_tingkat.transform([tingkat_hafalan_str])[0]
        except ValueError:
            return jsonify({'error': f"Invalid 'tingkat_hafalan'. Must be one of: {le_tingkat.classes_.tolist()}"}), 400

        X_input = np.array([[tingkat_hafalan_encoded, jumlah_setoran, kehadiran]])
        print('X_input untuk prediksi (API):', X_input)

        y_pred_encoded = model.predict(X_input)
        label = le_kemajuan.inverse_transform(y_pred_encoded)[0]

        return jsonify({'hasil_hafalan': label})

    return app # Mengembalikan instance aplikasi Flask