import os
from flask import request, jsonify, render_template, redirect, url_for, session
from app.extensions import db # Import db dari extensions.py
from app.data_migration import model, le_tingkat, le_kemajuan # Import model dan encoder dari data_migration.py
from werkzeug.security import generate_password_hash, check_password_hash # Meskipun ini tidak langsung dipakai di sini, tapi di models.py
from werkzeug.utils import secure_filename
import datetime
import numpy as np
from app.models import Santri, Guru, Admin, OrangTuaSantri # Import semua models yang dibutuhkan

# Direktori untuk menyimpan foto profil
UPLOAD_FOLDER = 'app/static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app):
    # Pastikan direktori upload ada
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Endpoint untuk upload foto profil
    @app.route('/api/upload_profile_picture', methods=['POST'])
    def upload_profile_picture():
        from app.models import Santri, Guru, Admin # Import models
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        file = request.files['file']
        user_type = request.form.get('user_type')
        credential = request.form.get('credential')

        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if not user_type or not credential:
            return jsonify({'message': 'Missing user_type or credential'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(f"{user_type}_{credential}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Simpan jalur gambar di database
            user = None
            if user_type == 'Santri':
                user = Santri.query.filter_by(nis=credential).first()
            elif user_type == 'Guru':
                user = Guru.query.filter_by(kode_guru=credential).first()
            elif user_type == 'Admin':
                user = Admin.query.filter_by(username=credential).first()

            if user:
                user.profile_picture = filename # Simpan hanya nama file atau jalur relatif
                db.session.commit()
                return jsonify({'message': 'Profile picture uploaded successfully', 'url': f'/static/profile_pics/{filename}'}), 200
            else:
                return jsonify({'message': 'User not found'}), 404
        else:
            return jsonify({'message': 'File type not allowed'}), 400

    # Endpoint untuk Manajemen Guru
    @app.route('/guru', methods=['GET', 'POST'])
    def manajemen_guru():
        from app.models import Guru  # Import model Guru di sini
        if request.method == 'POST':
            nama_lengkap = request.form['nama_lengkap']
            kode_guru = request.form['kode_guru']
            status_pengajar = request.form.get('status_pengajar')
            no_tlp = request.form.get('no_tlp')
            password = request.form['password']

            new_guru = Guru(
                nama_lengkap=nama_lengkap,
                kode_guru=kode_guru,
                status_pengajar=status_pengajar,
                nomor_telepon=no_tlp
            )
            new_guru.set_password(password)
            db.session.add(new_guru)
            db.session.commit()
            return redirect(url_for('manajemen_guru'))
        
        gurus = Guru.query.all()
        return render_template('guru.html', gurus=gurus)

    @app.route('/guru/edit/<int:guru_id>', methods=['GET', 'POST'])
    def edit_guru(guru_id):
        from app.models import Guru
        guru = Guru.query.get_or_404(guru_id)
        if request.method == 'POST':
            guru.nama_lengkap = request.form['nama_lengkap']
            guru.kode_guru = request.form['kode_guru']
            guru.status_pengajar = request.form.get('status_pengajar')
            guru.nomor_telepon = request.form.get('no_tlp')
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
            nama_lengkap = request.form['nama_lengkap']
            kode_santri = request.form['kode_santri']
            tingkatan = request.form.get('tingkatan')
            alamat = request.form.get('alamat')
            nama_orang_tua = request.form.get('nama_orang_tua')
            password = request.form['password']

            new_santri = Santri(
                nama_lengkap=nama_lengkap,
                kode_santri=kode_santri,
                tingkatan=tingkatan,
                alamat=alamat,
                nama_orang_tua=nama_orang_tua
            )
            new_santri.set_password(password)
            db.session.add(new_santri)
            db.session.commit()
            return redirect(url_for('manajemen_santri'))
        
        santris = Santri.query.all()
        return render_template('santri.html', santris=santris)

    @app.route('/santri/edit/<int:santri_id>', methods=['GET', 'POST'])
    def edit_santri(santri_id):
        from app.models import Santri
        santri = Santri.query.get_or_404(santri_id)
        if request.method == 'POST':
            santri.nama_lengkap = request.form['nama_lengkap']
            santri.kode_santri = request.form['kode_santri']
            santri.tingkatan = request.form.get('tingkatan')
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
            kode_santri = request.form['kode_santri'] # Ambil NIS dari form

            santri = Santri.query.filter_by(kode_santri=kode_santri).first()
            if not santri:
                return render_template('result.html', hasil_prediksi=f'Error: Santri dengan NIS {kode_santri} tidak ditemukan.'), 404

            status_kehadiran = "Hadir" if kehadiran_persentase > 0 else "Tidak Hadir"
            nilai_kehadiran_db = 1 if kehadiran_persentase > 0 else 0

            new_kehadiran = Kehadiran(
                santri_id=santri.santri_id,
                tanggal=datetime.date.today(),
                status_kehadiran=status_kehadiran,
                nilai_kehadiran=nilai_kehadiran_db
            )
            db.session.add(new_kehadiran)
            db.session.commit()

        except KeyError as e:
            return render_template('result.html', hasil_prediksi=f'Error: Field missing from form ({e})'), 400
        except ValueError:
            return render_template('result.html', hasil_prediksi='Error: Jumlah setoran dan kehadiran harus berupa angka.'), 400

        try:
            tingkat_hafalan_encoded = le_tingkat.transform([tingkat_hafalan_str])[0]
        except ValueError:
            return render_template('result.html', hasil_prediksi=f"Error: Tingkat hafalan tidak valid. Harusnya salah satu dari: {le_tingkat.classes_.tolist()}"), 400

        X_input = np.array([[tingkat_hafalan_encoded, jumlah_setoran, kehadiran_persentase]])
        print('X_input untuk prediksi (web):', X_input)

        y_pred_encoded = model.predict(X_input)

        label = le_kemajuan.inverse_transform(y_pred_encoded)[0]

        return render_template('result.html', hasil_prediksi=label)

    # Endpoint untuk API (JSON/Query Params)
    @app.route('/api/predict', methods=['POST', 'GET'])
    def api_predict():
        if model is None or le_tingkat is None or le_kemajuan is None:
            return jsonify({'error': 'Machine Learning model not loaded.'}), 500

        tingkat_hafalan_str = None
        jumlah_setoran = None
        kehadiran = None
        kode_santri = None # Tambahkan variabel nis

        if request.method == 'POST':
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body must be JSON for POST method'}), 400
            print('Data diterima (API POST):', data)
            try:
                tingkat_hafalan_str = data['tingkat_hafalan']
                jumlah_setoran = int(data['jumlah_setoran'])
                kehadiran = int(data['kehadiran'])
                kode_santri = data['kode_santri'] # Ambil NIS dari request
            except KeyError as e:
                return jsonify({'error': f'Missing required field in JSON: {e}'}), 400
            except ValueError:
                return jsonify({'error': 'jumlah_setoran, kehadiran, and kode_santri must be valid types in JSON'}), 400

        elif request.method == 'GET':
            print('Data diterima (API GET dari query parameters):', request.args)
            try:
                tingkat_hafalan_str = request.args.get('tingkat_hafalan')
                jumlah_setoran = int(request.args.get('jumlah_setoran'))
                kehadiran = int(request.args.get('kehadiran'))
                kode_santri = request.args.get('kode_santri') # Ambil NIS dari query params
            except (TypeError, ValueError) as e:
                return jsonify({'error': f'Invalid or missing query parameters. Ensure tingkat_hafalan (string), jumlah_setoran (int), kehadiran (int), and kode_santri (string) are provided. Error: {e}'}), 400

        # Cari santri berdasarkan NIS
        santri = Santri.query.filter_by(kode_santri=kode_santri).first()
        if not santri:
            return jsonify({'error': f'Santri with NIS {kode_santri} not found.'}), 404

        try:
            tingkat_hafalan_encoded = le_tingkat.transform([tingkat_hafalan_str])[0]
        except ValueError:
            return jsonify({'error': f"Invalid tingkat_hafalan. Must be one of: {le_tingkat.classes_.tolist()}"}), 400

        X_input = np.array([[tingkat_hafalan_encoded, jumlah_setoran, kehadiran]])
        print('X_input untuk prediksi (API):', X_input)

        y_pred_encoded = model.predict(X_input)
        label = le_kemajuan.inverse_transform(y_pred_encoded)[0]

        # Simpan hasil prediksi ke database
        new_prediction = PredictionResult(
            santri_id=santri.santri_id,
            tingkat_hafalan=tingkat_hafalan_str,
            jumlah_setoran=jumlah_setoran,
            kehadiran=kehadiran,
            hasil_prediksi=label
        )
        db.session.add(new_prediction)
        db.session.commit()

        return jsonify({'hasil_hafalan': label}), 200

    # Endpoint baru untuk mengambil riwayat prediksi santri
    @app.route('/api/santri/<string:kode_santri>/predictions', methods=['GET'])
    def get_santri_predictions(kode_santri):
        from app.models import Santri, PredictionResult # Pastikan import models di sini juga
        santri = Santri.query.filter_by(kode_santri=kode_santri).first()
        if not santri:
            return jsonify({'error': f'Santri with NIS {kode_santri} not found.'}), 404
        
        predictions = PredictionResult.query.filter_by(santri_id=santri.santri_id).order_by(PredictionResult.predicted_at.desc()).all()
        
        prediction_list = []
        for pred in predictions:
            prediction_list.append({
                'prediction_id': pred.prediction_id,
                'tingkat_hafalan': pred.tingkat_hafalan,
                'jumlah_setoran': pred.jumlah_setoran,
                'kehadiran': pred.kehadiran,
                'hasil_prediksi': pred.hasil_prediksi,
                'predicted_at': pred.predicted_at.isoformat() # Format tanggal ke string ISO 8601
            })
        return jsonify(prediction_list), 200

    # Endpoint untuk API Aplikasi Mobile
    @app.route('/api/login', methods=['POST'])
    def api_login():
        from app.models import Admin, Guru, Santri # Import model di sini
        
        try:
            data = request.get_json(silent=True)
            if data is None or not isinstance(data, dict):
                return jsonify({'message': 'Invalid JSON or missing JSON in request body'}), 400

            user_type = data.get('user_type')
            credential = data.get('credential')
            password = data.get('password')

            if not all([user_type, credential]):
                return jsonify({'message': 'Missing user_type or credential'}), 400

            user = None
            if user_type == 'Admin':
                if not password:
                    return jsonify({'message': 'Password is required for Admin login'}), 400
                user = Admin.query.filter_by(username=credential).first()
                if user and user.check_password(password):
                    return jsonify({'message': 'Login successful!', 'display_name': user.nama_lengkap}), 200
                else:
                    return jsonify({'message': 'Invalid Admin credentials'}), 401
            elif user_type == 'Guru':
                user = Guru.query.filter_by(kode_guru=credential).first()
                if user:
                    return jsonify({'message': 'Login successful!', 'display_name': user.nama_lengkap}), 200
                else:
                    return jsonify({'message': 'Invalid Guru credentials'}), 401
            elif user_type == 'Santri':
                user = Santri.query.filter_by(kode_santri=credential).first()
                if user:
                    return jsonify({'message': 'Login successful!', 'display_name': user.nama_lengkap, 'profile_picture': user.profile_picture}), 200
                else:
                    return jsonify({'message': 'Invalid Santri credentials'}), 401
            elif user_type == 'Orang Tua Santri':
                user = Santri.query.filter_by(nama_lengkap=credential).first()
                if user:
                    return jsonify({'message': 'Login successful!', 'display_name': user.nama_orang_tua}), 200
                else:
                    return jsonify({'message': 'Invalid Orang Tua Santri credentials'}), 401

            return jsonify({'message': 'Invalid user type'}), 400

        except Exception as e:
            return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500

    # Endpoint untuk API Profil Santri
    @app.route('/api/santri_profile/<string:kode_santri>', methods=['GET'])
    def santri_profile(kode_santri):
        from app.models import Santri
        santri = Santri.query.filter_by(kode_santri=kode_santri).first()
        if santri:
            return jsonify({
                'nama_lengkap': santri.nama_lengkap,
                'kode_santri': santri.kode_santri,
                'tingkatan': santri.tingkatan,
                'alamat': santri.alamat,
                'nama_orang_tua': santri.nama_orang_tua,
                'profile_picture': santri.profile_picture # Sertakan path gambar profil
            }), 200
        else:
            return jsonify({'message': 'Santri not found'}), 404

    # Endpoint untuk API Profil Guru
    @app.route('/api/guru_profile/<string:kode_guru>', methods=['GET'])
    def guru_profile(kode_guru):
        from app.models import Guru
        guru = Guru.query.filter_by(kode_guru=kode_guru).first()
        if guru:
            return jsonify({
                'nama_lengkap': guru.nama_lengkap,
                'kode_guru': guru.kode_guru,
                'status_pengajar': guru.status_pengajar,
                'nomor_telepon': guru.nomor_telepon,
                'profile_picture': guru.profile_picture
            }), 200
        else:
            return jsonify({'message': 'Guru not found'}), 404

    # Endpoint untuk API Profil Orang Tua Santri
    @app.route('/api/orangtua_profile/<string:nama_santri>', methods=['GET'])
    def orangtua_profile(nama_santri):
        from app.models import Santri, OrangTuaSantri
        santri = Santri.query.filter_by(nama_lengkap=nama_santri).first()
        if not santri:
            return jsonify({'message': 'Santri not found'}), 404
        ortu = OrangTuaSantri.query.filter_by(santri_id=santri.santri_id).first()
        if ortu:
            return jsonify({
                'nama': ortu.nama,
                'alamat': ortu.alamat,
                'nama_santri': nama_santri,
                'nomor_telepon': ortu.nomor_telepon
            }), 200
        else:
            return jsonify({'message': 'Orang Tua Santri not found'}), 404

    @app.route('/orangtua', methods=['GET', 'POST'])
    def manajemen_orangtua():
        if request.method == 'POST':
            nama = request.form['nama']
            alamat = request.form.get('alamat')
            nama_santri = request.form['nama_santri']
            nomor_telepon = request.form.get('nomor_telepon')
            ortu = OrangTuaSantri(
                nama=nama,
                alamat=alamat,
                nama_santri=nama_santri,
                nomor_telepon=nomor_telepon
            )
            db.session.add(ortu)
            db.session.commit()
            return redirect(url_for('manajemen_orangtua'))
        ortus = OrangTuaSantri.query.all()
        return render_template('orangtua.html', ortus=ortus)

    @app.route('/orangtua/edit/<int:ortu_id>', methods=['GET', 'POST'])
    def edit_orangtua(ortu_id):
        ortu = OrangTuaSantri.query.get_or_404(ortu_id)
        if request.method == 'POST':
            ortu.nama = request.form['nama']
            ortu.alamat = request.form.get('alamat')
            ortu.nama_santri = request.form['nama_santri']
            ortu.nomor_telepon = request.form.get('nomor_telepon')
            db.session.commit()
            return redirect(url_for('manajemen_orangtua'))
        return render_template('edit_orangtua.html', ortu=ortu)

    @app.route('/orangtua/delete/<int:ortu_id>', methods=['POST'])
    def delete_orangtua(ortu_id):
        ortu = OrangTuaSantri.query.get_or_404(ortu_id)
        db.session.delete(ortu)
        db.session.commit()
        return redirect(url_for('manajemen_orangtua'))

    # Endpoint untuk Penilaian Hafalan (POST)
    @app.route('/api/penilaian', methods=['POST'])
    def api_penilaian():
        from app.models import Santri, PenilaianHafalan
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        try:
            kode_santri = data['kode_santri']
            surat = data['surat']
            dari_ayat = int(data['dari_ayat'])
            sampai_ayat = int(data['sampai_ayat'])
            penilaian_tajwid = data['penilaian_tajwid']
        except KeyError as e:
            return jsonify({'error': f'Missing required field: {e}'}), 400
        except ValueError:
            return jsonify({'error': 'dari_ayat dan sampai_ayat harus berupa angka'}), 400

        santri = Santri.query.filter_by(kode_santri=kode_santri).first()
        if not santri:
            return jsonify({'error': f'Santri dengan NIS {kode_santri} tidak ditemukan.'}), 404

        penilaian = PenilaianHafalan(
            santri_id=santri.santri_id,
            surat=surat,
            dari_ayat=dari_ayat,
            sampai_ayat=sampai_ayat,
            penilaian_tajwid=penilaian_tajwid
        )
        db.session.add(penilaian)
        db.session.commit()
        return jsonify({'message': 'Penilaian hafalan berhasil disimpan.'}), 200

    # Endpoint untuk mengambil riwayat penilaian hafalan santri
    @app.route('/api/santri/<string:kode_santri>/penilaian', methods=['GET'])
    def get_riwayat_penilaian(kode_santri):
        from app.models import Santri, PenilaianHafalan
        santri = Santri.query.filter_by(kode_santri=kode_santri).first()
        if not santri:
            return jsonify({'error': f'Santri dengan NIS {kode_santri} tidak ditemukan.'}), 404
        penilaian_list = PenilaianHafalan.query.filter_by(santri_id=santri.santri_id).order_by(PenilaianHafalan.tanggal_penilaian.desc()).all()
        result = []
        for p in penilaian_list:
            result.append({
                'penilaian_id': p.penilaian_id,
                'surat': p.surat,
                'dari_ayat': p.dari_ayat,
                'sampai_ayat': p.sampai_ayat,
                'penilaian_tajwid': p.penilaian_tajwid,
                'tanggal_penilaian': p.tanggal_penilaian.isoformat()
            })
        return jsonify(result), 200

    # Endpoint untuk daftar santri (untuk dropdown guru di mobile)
    @app.route('/api/daftar_santri', methods=['GET'])
    def api_daftar_santri():
        from app.models import Santri
        santri_list = Santri.query.all()
        result = []
        for s in santri_list:
            result.append({
                'kode_santri': s.kode_santri,
                'nama_lengkap': s.nama_lengkap
            })
        return jsonify(result), 200

    # Endpoint Login Admin (Web)
    @app.route('/login_admin', methods=['GET', 'POST'])
    def login_admin():
        from app.models import Admin
        error = None
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            admin = Admin.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session['admin_logged_in'] = True
                session['admin_username'] = username
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Username atau password salah.'
        return render_template('login_admin.html', error=error)

    @app.route('/')
    def admin_dashboard():
        return render_template('dashboard.html')