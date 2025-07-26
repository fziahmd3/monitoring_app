import os
from flask import request, jsonify, render_template, redirect, url_for, session
from app.extensions import db # Import db dari extensions.py
from app.data_migration import model, le_tingkat, le_kemajuan # Import model dan encoder dari data_migration.py
from werkzeug.security import generate_password_hash, check_password_hash # Meskipun ini tidak langsung dipakai di sini, tapi di models.py
from werkzeug.utils import secure_filename
import datetime
import numpy as np
from app.models import Santri, Guru, Admin, OrangTuaSantri, PenilaianHafalan # Import semua models yang dibutuhkan
from sklearn.naive_bayes import GaussianNB # Import Gaussian Naive Bayes
from sklearn.preprocessing import LabelEncoder # Import LabelEncoder

# Direktori untuk menyimpan foto profil
UPLOAD_FOLDER = 'app/static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app):
    # Inisialisasi dan latih model Naive Bayes sederhana
    global naive_bayes_model, le_hasil_penilaian
    
    # Contoh data pelatihan (X: tajwid, kelancaran, kefasihan; y: hasil penilaian)
    # Ini adalah contoh sederhana. Dalam aplikasi nyata, Anda akan melatih ini dengan data historis yang lebih besar.
    X_train_nb = np.array([
        [5, 5, 5], # Sangat Baik
        [4, 5, 4], # Sangat Baik
        [5, 4, 5], # Sangat Baik
        [4, 4, 4], # Baik
        [3, 4, 3], # Baik
        [4, 3, 4], # Baik
        [3, 3, 3], # Cukup
        [2, 3, 2], # Cukup
        [3, 2, 3], # Cukup
        [2, 2, 2], # Kurang
        [1, 2, 1], # Kurang
        [2, 1, 2], # Kurang
        [1, 1, 1], # Sangat Kurang
    ])
    y_train_nb = np.array([
        'Sangat Baik', 'Sangat Baik', 'Sangat Baik',
        'Baik', 'Baik', 'Baik',
        'Cukup', 'Cukup', 'Cukup',
        'Kurang', 'Kurang', 'Kurang',
        'Sangat Kurang',
    ])

    le_hasil_penilaian = LabelEncoder()
    y_train_encoded = le_hasil_penilaian.fit_transform(y_train_nb)

    naive_bayes_model = GaussianNB()
    naive_bayes_model.fit(X_train_nb, y_train_encoded)
    
    print("Naive Bayes model and encoder for penilaian loaded successfully.")

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

    # Endpoint untuk Penilaian Hafalan (POST)
    @app.route('/api/penilaian', methods=['POST'])
    def api_penilaian():
        from app.models import Santri, PenilaianHafalan
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body must be JSON'}), 400
            
            # Pastikan model Naive Bayes dan encoder sudah dimuat
            global naive_bayes_model, le_hasil_penilaian
            if naive_bayes_model is None or le_hasil_penilaian is None:
                print("Error: Naive Bayes model or encoder not loaded.")
                return jsonify({'error': 'Machine Learning model not loaded on server.'}), 500

            try:
                kode_santri = data['kode_santri']
                surat = data['surat']
                dari_ayat = int(data['dari_ayat'])
                sampai_ayat = int(data['sampai_ayat'])
                penilaian_tajwid = int(data['penilaian_tajwid']) # Diubah menjadi int
                kelancaran = int(data['kelancaran']) # Field baru
                kefasihan = int(data['kefasihan']) # Field baru
            except KeyError as e:
                return jsonify({'error': f'Missing required field: {e}'}), 400
            except ValueError:
                return jsonify({'error': 'dari_ayat, sampai_ayat, penilaian_tajwid, kelancaran, dan kefasihan harus berupa angka'}), 400

            santri = Santri.query.filter_by(kode_santri=kode_santri).first()
            if not santri:
                return jsonify({'error': f'Santri dengan NIS {kode_santri} tidak ditemukan.'}), 404

            # Prediksi dengan Naive Bayes
            try:
                input_features = np.array([[penilaian_tajwid, kelancaran, kefasihan]])
                predicted_encoded = naive_bayes_model.predict(input_features)
                hasil_prediksi_naive_bayes = le_hasil_penilaian.inverse_transform(predicted_encoded)[0]
            except Exception as e:
                # Ini akan menangkap error dari prediksi model itu sendiri
                return jsonify({'error': f'Gagal memprediksi dengan Naive Bayes: {e}'}), 500

            penilaian = PenilaianHafalan(
                santri_id=santri.santri_id,
                surat=surat,
                dari_ayat=dari_ayat,
                sampai_ayat=sampai_ayat,
                penilaian_tajwid=penilaian_tajwid,
                kelancaran=kelancaran,
                kefasihan=kefasihan,
                hasil_naive_bayes=hasil_prediksi_naive_bayes # Simpan hasil prediksi
            )
            db.session.add(penilaian)
            db.session.commit()
            return jsonify({'message': 'Penilaian hafalan berhasil disimpan.', 'hasil_prediksi_naive_bayes': hasil_prediksi_naive_bayes}), 200
        except Exception as e:
            # Tangkap setiap exception yang tidak tertangkap di atas dan kembalikan JSON error
            print(f"Unhandled error in api_penilaian: {e}")
            return jsonify({'error': f'Terjadi kesalahan server tidak terduga: {e}'}), 500

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
                'kelancaran': p.kelancaran,
                'kefasihan': p.kefasihan,
                'hasil_naive_bayes': p.hasil_naive_bayes, # Tambahkan ini
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

    # Endpoint untuk profil santri
    @app.route('/api/santri_profile/<string:credential>', methods=['GET'])
    def santri_profile(credential):
        from app.models import Santri
        santri = Santri.query.filter_by(kode_santri=credential).first()
        if not santri:
            return jsonify({'message': 'Santri not found'}), 404
        
        profile_data = {
            'nama_lengkap': santri.nama_lengkap,
            'nis': santri.kode_santri, # Menggunakan kode_santri sebagai NIS
            'kelas': santri.tingkatan, # Menggunakan tingkatan sebagai kelas
            'alamat': santri.alamat,
            'profile_picture': santri.profile_picture
        }
        return jsonify(profile_data), 200

    # Endpoint untuk profil guru
    @app.route('/api/guru_profile/<string:credential>', methods=['GET'])
    def guru_profile(credential):
        from app.models import Guru
        guru = Guru.query.filter_by(kode_guru=credential).first()
        if not guru:
            return jsonify({'message': 'Guru not found'}), 404

        profile_data = {
            'nama_lengkap': guru.nama_lengkap,
            'nip': guru.kode_guru,
            'pendidikan_terakhir': guru.status_pengajar, # Menggunakan status_pengajar sebagai pendidikan terakhir
            'nomor_telepon': guru.nomor_telepon,
            'profile_picture': guru.profile_picture
        }
        return jsonify(profile_data), 200

    # Endpoint untuk profil orang tua santri
    @app.route('/api/orangtua_profile/<string:credential>', methods=['GET'])
    def orangtua_profile(credential):
        from app.models import OrangTuaSantri
        orangtua = OrangTuaSantri.query.filter_by(nama_santri_terkait=credential).first()
        if not orangtua:
            return jsonify({'message': 'Orang Tua Santri not found'}), 404
        
        profile_data = {
            'nama': orangtua.nama,
            'nama_santri': orangtua.santri.nama_lengkap, # Mengambil nama santri dari relasi
            'alamat': orangtua.alamat,
            'nomor_telepon': orangtua.nomor_telepon,
            'profile_picture': orangtua.santri.profile_picture # Asumsi foto profil ortu sama dengan santri terkait
        }
        return jsonify(profile_data), 200

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

    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Request body must be JSON'}), 400

        user_type = data.get('user_type')
        credential = data.get('credential')
        # password = data.get('password') # Hapus password dari data yang diharapkan

        if not user_type or not credential:
            return jsonify({'message': 'Missing user_type or credential'}), 400

        user = None
        display_name = ''

        if user_type == 'Guru':
            user = Guru.query.filter_by(kode_guru=credential).first()
            if user:
                display_name = user.nama_lengkap
        elif user_type == 'Santri':
            user = Santri.query.filter_by(kode_santri=credential).first()
            if user:
                display_name = user.nama_lengkap
        elif user_type == 'Orang Tua Santri':
            user = OrangTuaSantri.query.filter_by(nama_santri_terkait=credential).first()
            if user:
                display_name = user.nama # Asumsi OrangTuaSantri memiliki field nama

        # Modifikasi kondisi login: cek keberadaan user saja, tanpa password
        if user:
            return jsonify({
                'message': 'Login successful',
                'user_type': user_type,
                'credential': credential,
                'display_name': display_name
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    @app.route('/')
    def admin_dashboard():
        return render_template('dashboard.html')