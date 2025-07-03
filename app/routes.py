from flask import request, jsonify, render_template, redirect, url_for
from app.data_migration import db, model, le_tingkat, le_kemajuan
from werkzeug.security import generate_password_hash, check_password_hash # Meskipun ini tidak langsung dipakai di sini, tapi di models.py
import datetime
import numpy as np

def register_routes(app):
    # Endpoint untuk Manajemen Guru
    @app.route('/guru', methods=['GET', 'POST'])
    def manajemen_guru():
        from app.models import Guru  # Import model Guru di sini
        if request.method == 'POST':
            # Logika untuk menambah guru baru
            nama_lengkap = request.form['nama_lengkap']
            nip = request.form['nip']
            pendidikan_terakhir = request.form.get('pendidikan_terakhir')
            no_tlp = request.form.get('no_tlp')
            password = request.form['password']

            new_guru = Guru(
                nama_lengkap=nama_lengkap,
                nip=nip,
                pendidikan_terakhir=pendidikan_terakhir,
                no_tlp=no_tlp
            )
            new_guru.set_password(password)
            db.session.add(new_guru)
            db.session.commit()
            return redirect(url_for('manajemen_guru'))
        
        # Logika untuk menampilkan daftar guru
        gurus = Guru.query.all()
        return render_template('guru.html', gurus=gurus)

    @app.route('/guru/edit/<int:guru_id>', methods=['GET', 'POST'])
    def edit_guru(guru_id):
        from app.models import Guru
        guru = Guru.query.get_or_404(guru_id)
        if request.method == 'POST':
            guru.nama_lengkap = request.form['nama_lengkap']
            guru.nip = request.form['nip']
            guru.pendidikan_terakhir = request.form.get('pendidikan_terakhir')
            guru.no_tlp = request.form.get('no_tlp')
            password = request.form.get('password')
            if password:
                guru.set_password(password)
            db.session.commit()
            return redirect(url_for('manajemen_guru'))
        return render_template('edit_guru.html', guru=guru)

    @app.route('/guru/delete/<int:guru_id>', methods=['POST'])
    def delete_guru(guru_id):
        from app.models import Guru
        guru = Guru.query.get_or_404(guru_id)
        db.session.delete(guru)
        db.session.commit()
        return redirect(url_for('manajemen_guru'))

    # Endpoint untuk Manajemen Santri
    @app.route('/santri', methods=['GET', 'POST'])
    def manajemen_santri():
        from app.models import Santri # Import model Santri di sini
        if request.method == 'POST':
            # Logika untuk menambah santri baru
            nama_lengkap = request.form['nama_lengkap']
            nis = request.form['nis']
            kelas = request.form.get('kelas')
            alamat = request.form.get('alamat')
            nama_orang_tua = request.form.get('nama_orang_tua')
            password = request.form['password']

            new_santri = Santri(
                nama_lengkap=nama_lengkap,
                nis=nis,
                kelas=kelas,
                alamat=alamat,
                nama_orang_tua=nama_orang_tua
            )
            new_santri.set_password(password)
            db.session.add(new_santri)
            db.session.commit()
            return redirect(url_for('manajemen_santri'))
        
        # Logika untuk menampilkan daftar santri
        santris = Santri.query.all()
        return render_template('santri.html', santris=santris)

    @app.route('/santri/edit/<int:santri_id>', methods=['GET', 'POST'])
    def edit_santri(santri_id):
        from app.models import Santri
        santri = Santri.query.get_or_404(santri_id)
        if request.method == 'POST':
            santri.nama_lengkap = request.form['nama_lengkap']
            santri.nis = request.form['nis']
            santri.kelas = request.form.get('kelas')
            santri.alamat = request.form.get('alamat')
            santri.nama_orang_tua = request.form.get('nama_orang_tua')
            password = request.form.get('password')
            if password:
                santri.set_password(password)
            db.session.commit()
            return redirect(url_for('manajemen_santri'))
        return render_template('edit_santri.html', santri=santri)

    @app.route('/santri/delete/<int:santri_id>', methods=['POST'])
    def delete_santri(santri_id):
        from app.models import Santri
        santri = Santri.query.get_or_404(santri_id)
        db.session.delete(santri)
        db.session.commit()
        return redirect(url_for('manajemen_santri'))

    # Endpoint untuk Halaman Input Web (Frontend Form)
    @app.route('/predict_form')
    def predict_form_page():
        return render_template('index.html')

    # Endpoint untuk Prediksi dari Formulir Web (POST)
    @app.route('/predict_web', methods=['POST'])
    def predict_web():
        if model is None or le_tingkat is None or le_kemajuan is None:
            return render_template('result.html', hasil_prediksi='Error: Machine Learning model not loaded.'), 500

        print('Data diterima dari web form:', request.form)

        try:
            from app.models import Santri, Kehadiran # Import model Santri dan Kehadiran
            tingkat_hafalan_str = request.form['tingkat_hafalan']
            jumlah_setoran = int(request.form['jumlah_setoran'])
            kehadiran_persentase = int(request.form['kehadiran']) # Ubah nama variabel agar tidak ambigu
            nis = request.form['nis'] # Ambil NIS dari form

            # Cari santri berdasarkan NIS
            santri = Santri.query.filter_by(nis=nis).first()
            if not santri:
                return render_template('result.html', hasil_prediksi=f'Error: Santri dengan NIS {nis} tidak ditemukan.'), 404

            # Tentukan status kehadiran dan nilai kehadiran
            status_kehadiran = "Hadir" if kehadiran_persentase > 0 else "Tidak Hadir"
            nilai_kehadiran_db = 1 if kehadiran_persentase > 0 else 0 # 1 jika hadir, 0 jika tidak

            # Simpan data kehadiran ke database
            new_kehadiran = Kehadiran(
                santri_id=santri.santri_id,
                tanggal=datetime.date.today(), # Tanggal hari ini
                status_kehadiran=status_kehadiran,
                nilai_kehadiran=nilai_kehadiran_db
            )
            db.session.add(new_kehadiran)
            db.session.commit()

        except KeyError as e:
            return render_template('result.html', hasil_prediksi=f'Error: Field missing from form ({e})'), 400
        except ValueError:
            return render_template('result.html', hasil_prediksi='Error: Jumlah setoran dan kehadiran harus berupa angka.'), 400

        # Encode tingkat_hafalan_str
        try:
            tingkat_hafalan_encoded = le_tingkat.transform([tingkat_hafalan_str])[0]
        except ValueError:
            return render_template('result.html', hasil_prediksi=f"Error: Tingkat hafalan tidak valid. Harusnya salah satu dari: {le_tingkat.classes_.tolist()}"), 400

        # Buat input array NumPy (gunakan kehadiran_persentase untuk prediksi)
        X_input = np.array([[tingkat_hafalan_encoded, jumlah_setoran, kehadiran_persentase]])
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

    @app.route('/')
    def admin_dashboard():
        return render_template('dashboard.html')