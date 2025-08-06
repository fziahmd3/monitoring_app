import os
from flask import request, jsonify, render_template, redirect, url_for, session
from app.extensions import db # Import db dari extensions.py
import pickle # Import pickle
# from app.data_migration import model, le_tingkat, le_kemajuan # Import model dan encoder dari data_migration.py
from werkzeug.security import generate_password_hash, check_password_hash # Meskipun ini tidak langsung dipakai di sini, tapi di models.py
from werkzeug.utils import secure_filename
import datetime
import numpy as np
from app.models import Santri, Guru, Admin, OrangTuaSantri, PenilaianHafalan # Import semua models yang dibutuhkan
# from sklearn.naive_bayes import GaussianNB # Import Gaussian Naive Bayes
# from sklearn.preprocessing import LabelEncoder # Import LabelEncoder

# Direktori untuk menyimpan foto profil
UPLOAD_FOLDER = 'app/static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app):
    # Definisikan UPLOAD_FOLDER dan ALLOWED_EXTENSIONS di level fungsi
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'recordings')
    ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'wav', 'aac'}

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Muat model dan KKM Naive Bayes yang sudah dilatih
    global naive_bayes_model, kkm
    try:
        # Pastikan jalur relatif sudah benar dari root aplikasi
        with open('output/naive_bayes_model.pkl', 'rb') as f_model:
            naive_bayes_model = pickle.load(f_model)
        with open('output/kkm.pkl', 'rb') as f_kkm:
            kkm = pickle.load(f_kkm)
        print("Naive Bayes model and KKM for penilaian loaded successfully from output/.")
    except FileNotFoundError:
        print("Error: Model Naive Bayes atau KKM tidak ditemukan di folder output/. Pastikan build_model.py telah dijalankan.")
        naive_bayes_model = None
        kkm = None
    except Exception as e:
        print(f"Error loading Naive Bayes model or KKM: {e}")
        naive_bayes_model = None
        kkm = None
    
    # from app.data_migration import model, le_tingkat, le_kemajuan
    # Inisialisasi model untuk predict_web (jika terpisah)
    global model, le_tingkat, le_kemajuan
    try:
        with open('output/model.pkl', 'rb') as f_model_general:
            model = pickle.load(f_model_general)
        with open('output/encoder.pkl', 'rb') as f_enc_general:
            encoders = pickle.load(f_enc_general)
            le_tingkat = encoders['tingkat_hafalan']
            le_kemajuan = encoders['kemajuan']
        print("General prediction model and encoders loaded successfully from output/.")
    except FileNotFoundError:
        print("Error: General prediction model or encoders not found in output/ folder. Ensure build_model.py has been run.")
        model = None
        le_tingkat = None
        le_kemajuan = None

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

    # Endpoint untuk Manajemen Orang Tua Santri
    @app.route('/orangtua', methods=['GET', 'POST'])
    def manajemen_orangtua():
        from app.models import OrangTuaSantri, Santri
        if request.method == 'POST':
            nama = request.form['nama']
            kode_orangtua = request.form['kode_orangtua']
            alamat = request.form.get('alamat')
            nomor_telepon = request.form.get('nomor_telepon')
            santri_id = request.form.get('santri_id')

            new_orangtua = OrangTuaSantri(
                nama=nama,
                kode_orangtua=kode_orangtua,
                alamat=alamat,
                nomor_telepon=nomor_telepon,
                santri_id=santri_id
            )
            db.session.add(new_orangtua)
            db.session.commit()
            return redirect(url_for('manajemen_orangtua'))
        
        orangtua_list = OrangTuaSantri.query.all()
        santri_list = Santri.query.all()  # Untuk dropdown pilihan santri
        return render_template('orangtua.html', orangtua_list=orangtua_list, santri_list=santri_list)

    @app.route('/orangtua/edit/<int:orangtua_id>', methods=['GET', 'POST'])
    def edit_orangtua(orangtua_id):
        from app.models import OrangTuaSantri, Santri
        orangtua = OrangTuaSantri.query.get_or_404(orangtua_id)
        if request.method == 'POST':
            orangtua.nama = request.form['nama']
            orangtua.kode_orangtua = request.form['kode_orangtua']
            orangtua.alamat = request.form.get('alamat')
            orangtua.nomor_telepon = request.form.get('nomor_telepon')
            orangtua.santri_id = request.form.get('santri_id')
            db.session.commit()
            return redirect(url_for('manajemen_orangtua'))
        santri_list = Santri.query.all()  # Untuk dropdown pilihan santri
        return render_template('edit_orangtua.html', orangtua=orangtua, santri_list=santri_list)

    @app.route('/orangtua/delete/<int:orangtua_id>', methods=['POST'])
    def delete_orangtua(orangtua_id):
        from app.models import OrangTuaSantri
        orangtua = OrangTuaSantri.query.get_or_404(orangtua_id)
        db.session.delete(orangtua)
        db.session.commit()
        return redirect(url_for('manajemen_orangtua'))

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
            
            # Pastikan model Naive Bayes dan KKM sudah dimuat
            global naive_bayes_model, kkm
            if naive_bayes_model is None or kkm is None:
                print("Error: Naive Bayes model or KKM not loaded.")
                return jsonify({'error': 'Machine Learning model not loaded on server.'}), 500

            try:
                kode_santri = data['kode_santri']
                kode_guru = data.get('kode_guru', kode_santri) # Ambil kode guru, default ke kode santri jika tidak ada
                surat = data['surat']
                dari_ayat = int(data['dari_ayat'])
                sampai_ayat = int(data['sampai_ayat'])
                # Mapping kategori ke angka jika perlu
                kategori_ke_float = {
                    'Sangat Baik': 4.0,
                    'Baik': 3.0,
                    'Cukup': 2.0,
                    'Kurang': 1.0
                }
                def parse_nilai(val):
                    if isinstance(val, str) and val in kategori_ke_float:
                        return kategori_ke_float[val]
                    try:
                        return float(val)
                    except Exception:
                        return 0.0
                penilaian_tajwid = parse_nilai(data['penilaian_tajwid']) # Skala 1-100 atau kategori
                kelancaran = parse_nilai(data['kelancaran']) # Skala 1-100 atau kategori
                kefasihan = parse_nilai(data['kefasihan']) # Skala 1-100 atau kategori
                catatan = data.get('catatan', '') # Field baru untuk catatan (opsional)
            except KeyError as e:
                return jsonify({'error': f'Missing required field: {e}'}), 400
            except ValueError:
                return jsonify({'error': 'dari_ayat, sampai_ayat, penilaian_tajwid, kelancaran, dan kefasihan harus berupa angka'}), 400

            # Validasi skala nilai (1-100)
            if not (1 <= penilaian_tajwid <= 100 and 1 <= kelancaran <= 100 and 1 <= kefasihan <= 100):
                return jsonify({'error': 'Nilai tajwid, kelancaran, dan kefasihan harus dalam skala 1-100'}), 400

            santri = Santri.query.filter_by(kode_santri=kode_santri).first()
            if not santri:
                return jsonify({'error': f'Santri dengan NIS {kode_santri} tidak ditemukan.'}), 404
                
            guru = Guru.query.filter_by(kode_guru=kode_guru).first()
            if not guru:
                return jsonify({'error': f'Guru dengan kode {kode_guru} tidak ditemukan.'}), 404

            # Prediksi dengan Naive Bayes untuk mendapatkan nilai akhir
            try:
                # Hitung rata-rata dari 3 komponen penilaian
                rata_rata_nilai = (penilaian_tajwid + kelancaran + kefasihan) / 3
                
                # Gunakan rata-rata sebagai nilai akhir
                predicted_nilai = round(rata_rata_nilai)
                
                # Tentukan status lulus/tidak lulus berdasarkan KKM
                status_lulus = "LULUS" if predicted_nilai >= kkm else "TIDAK LULUS"
                warna_hasil = "hijau" if predicted_nilai >= kkm else "merah"
                
                hasil_prediksi_naive_bayes = f"{predicted_nilai:.0f}"
                
            except Exception as e:
                # Ini akan menangkap error dari prediksi model itu sendiri
                return jsonify({'error': f'Gagal memprediksi dengan Naive Bayes: {e}'}), 500

            # Simpan penilaian dengan guru_id
            penilaian = PenilaianHafalan(
                santri_id=santri.santri_id,
                guru_id=guru.guru_id, # Aktifkan guru_id setelah migration
                surat=surat,
                dari_ayat=dari_ayat,
                sampai_ayat=sampai_ayat,
                penilaian_tajwid=penilaian_tajwid,
                kelancaran=kelancaran,
                kefasihan=kefasihan,
                catatan=catatan, # Simpan catatan
                hasil_naive_bayes=hasil_prediksi_naive_bayes # Simpan hasil prediksi
            )
            db.session.add(penilaian)
            db.session.commit()
            
            return jsonify({
                'message': 'Penilaian hafalan berhasil disimpan.', 
                'hasil_prediksi_naive_bayes': hasil_prediksi_naive_bayes,
                'status_lulus': status_lulus,
                'warna_hasil': warna_hasil,
                'kkm': kkm
            }), 200
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
                'catatan': p.catatan, # Tambahkan catatan
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
        orangtua = OrangTuaSantri.query.filter_by(kode_orangtua=credential).first()
        if not orangtua:
            return jsonify({'message': 'Orang Tua Santri not found'}), 404
        
        profile_data = {
            'nama': orangtua.nama,
            'nama_santri': orangtua.santri.nama_lengkap, # Mengambil nama santri dari relasi
            'kode_santri': orangtua.santri.kode_santri, # Tambahkan kode santri
            'alamat': orangtua.alamat,
            'nomor_telepon': orangtua.nomor_telepon,
            'profile_picture': orangtua.santri.profile_picture # Asumsi foto profil ortu sama dengan santri terkait
        }
        return jsonify(profile_data), 200

    # Endpoint untuk mendapatkan progress anak dari orang tua
    @app.route('/api/orangtua/<string:kode_orangtua>/progress_anak', methods=['GET'])
    def get_progress_anak(kode_orangtua):
        try:
            print(f"=== Get Progress Anak for Orang Tua: {kode_orangtua} ===")
            
            def parse_float(val):
                try:
                    return float(val)
                except Exception:
                    return 0.0
            # Cari orang tua
            orangtua = OrangTuaSantri.query.filter_by(kode_orangtua=kode_orangtua).first()
            print(f"Orang tua found: {orangtua is not None}")
            
            if not orangtua:
                print(f"Orang tua dengan kode {kode_orangtua} tidak ditemukan")
                return jsonify({'error': 'Orang tua tidak ditemukan'}), 404
            
            # Ambil data santri (anak)
            santri = orangtua.santri
            if not santri:
                return jsonify({'error': 'Data santri tidak ditemukan'}), 404
            
            # Ambil data penilaian santri
            penilaian_list = PenilaianHafalan.query.filter_by(santri_id=santri.santri_id).order_by(PenilaianHafalan.tanggal_penilaian.desc()).all()
            
            if not penilaian_list:
                return jsonify({
                    'santri_info': {
                        'nama': santri.nama_lengkap,
                        'kode_santri': santri.kode_santri,
                        'tingkatan': santri.tingkatan
                    },
                    'progress_summary': {
                        'total_penilaian': 0,
                        'rata_rata_nilai': 0,
                        'status_terakhir': 'Belum ada penilaian',
                        'surat_terakhir': '-',
                        'tanggal_terakhir': '-'
                    },
                    'recent_penilaian': []
                })
            
            # Hitung statistik
            total_penilaian = len(penilaian_list)
            total_nilai = sum(parse_float(p.hasil_naive_bayes) for p in penilaian_list if p.hasil_naive_bayes and p.hasil_naive_bayes != 'Belum Diprediksi')
            rata_rata_nilai = total_nilai / total_penilaian if total_penilaian > 0 else 0
            
            # Status terakhir
            penilaian_terakhir = penilaian_list[0]
            status_terakhir = 'LULUS' if parse_float(penilaian_terakhir.hasil_naive_bayes) >= 75 else 'TIDAK LULUS'
            
            # Data penilaian terbaru (5 terakhir)
            recent_penilaian = []
            for p in penilaian_list[:5]:
                recent_penilaian.append({
                    'surat': p.surat,
                    'dari_ayat': p.dari_ayat,
                    'sampai_ayat': p.sampai_ayat,
                    'nilai': p.hasil_naive_bayes,
                    'status': 'LULUS' if parse_float(p.hasil_naive_bayes) >= 75 else 'TIDAK LULUS',
                    'tanggal': p.tanggal_penilaian.strftime('%Y-%m-%d') if p.tanggal_penilaian else 'N/A',
                    'catatan': p.catatan if p.catatan else None
                })
            
            result = {
                'santri_info': {
                    'nama': santri.nama_lengkap,
                    'kode_santri': santri.kode_santri,
                    'tingkatan': santri.tingkatan
                },
                'progress_summary': {
                    'total_penilaian': total_penilaian,
                    'rata_rata_nilai': round(rata_rata_nilai, 2),
                    'status_terakhir': status_terakhir,
                    'surat_terakhir': penilaian_terakhir.surat,
                    'tanggal_terakhir': penilaian_terakhir.tanggal_penilaian.strftime('%Y-%m-%d') if penilaian_terakhir.tanggal_penilaian else 'N/A'
                },
                'recent_penilaian': recent_penilaian
            }
            
            print(f"Progress anak result: {result}")
            return jsonify(result)
            
        except Exception as e:
            print(f"Error in get_progress_anak: {e}")
            return jsonify({'error': str(e)}), 500

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

    @app.route('/upload_recording', methods=['POST'])
    def upload_recording():
        try:
            print("=== Upload Recording Request ===")
            print(f"Files: {list(request.files.keys())}")
            print(f"Form data: {list(request.form.keys())}")
            
            if 'recording' not in request.files:
                print("Error: No 'recording' file in request")
                return jsonify({'success': False, 'message': 'No file part'}), 400
            
            file = request.files['recording']
            kode_santri = request.form.get('kodeSantri')
            kode_guru = request.form.get('kodeGuru')
            
            print(f"File: {file.filename if file else 'None'}")
            print(f"Kode Santri: {kode_santri}")
            print(f"Kode Guru: {kode_guru}")
            
            if not file or file.filename == '':
                print("Error: No selected file")
                return jsonify({'success': False, 'message': 'No selected file'}), 400
            
            if not kode_santri:
                print("Error: Missing kodeSantri")
                return jsonify({'success': False, 'message': 'Missing kodeSantri'}), 400
            
            # Jika kodeGuru tidak ada, gunakan kodeSantri sebagai guru (self-recording)
            if not kode_guru:
                kode_guru = kode_santri
                print(f"Using kodeSantri as kodeGuru: {kode_guru}")
            
            if file and allowed_file(file.filename):
                base_filename = f"{kode_guru}_{kode_santri}_hafalan_recording_{int(datetime.datetime.now().timestamp() * 1000)}.wav"
                filename = secure_filename(base_filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                print(f"Saving file to: {save_path}")
                
                # Pastikan folder upload ada
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                file.save(save_path)
                print("File saved successfully")
                # TODO: Simpan info ke database jika perlu
                return jsonify({'success': True, 'message': 'File uploaded', 'filename': filename}), 200
            else:
                print(f"Error: File type not allowed. Filename: {file.filename}")
                return jsonify({'success': False, 'message': 'File type not allowed'}), 400
        except Exception as e:
            print(f"Error in upload_recording: {e}")
            return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

    @app.route('/api/rekaman_santri/<kode_santri>', methods=['GET'])
    def get_rekaman_santri(kode_santri):
        try:
            # Gunakan UPLOAD_FOLDER yang sama dengan endpoint upload
            rekaman_dir = UPLOAD_FOLDER
            files = []
            if os.path.exists(rekaman_dir):
                for filename in os.listdir(rekaman_dir):
                    # Format nama file: {kode_guru}_{kode_santri}_{original_filename}
                    parts = filename.split('_')
                    if len(parts) >= 3 and parts[1] == kode_santri:
                        files.append(filename)
            return jsonify({'files': files})
        except Exception as e:
            print(f"Error in get_rekaman_santri: {e}")
            return jsonify({'files': [], 'error': str(e)}), 500

    @app.route('/api/rekaman_guru/<kode_guru>', methods=['GET'])
    def get_rekaman_guru(kode_guru):
        try:
            kode_santri = request.args.get('kode_santri')
            print(f"=== Get Rekaman Guru ===")
            print(f"Kode Guru: {kode_guru}")
            print(f"Kode Santri (query param): {kode_santri}")
            print(f"Upload Folder: {UPLOAD_FOLDER}")
            print(f"Request URL: {request.url}")
            print(f"Request args: {request.args}")
            
            rekaman_dir = UPLOAD_FOLDER
            files = []
            if os.path.exists(rekaman_dir):
                all_files = os.listdir(rekaman_dir)
                print(f"All files in directory: {all_files}")
                for filename in all_files:
                    # Format nama file: {kode_guru}_{kode_santri}_{original_filename}
                    parts = filename.split('_')
                    print(f"File: {filename}, Parts: {parts}")
                    print(f"Checking if parts[0] == kode_guru: {parts[0]} == {kode_guru} -> {parts[0] == kode_guru}")
                    if len(parts) >= 3 and parts[0] == kode_guru:
                        print(f"File matches guru: {filename}")
                        # Jika ada kode_santri, filter berdasarkan santri
                        if kode_santri:
                            print(f"Filtering by santri: {kode_santri}")
                            print(f"Checking if parts[1] == kode_santri: {parts[1]} == {kode_santri} -> {parts[1] == kode_santri}")
                            if len(parts) >= 2 and parts[1] == kode_santri:
                                files.append(filename)
                                print(f"Added file (filtered by santri): {filename}")
                            else:
                                print(f"File does not match santri filter: {filename}")
                        else:
                            # Jika tidak ada kode_santri, tampilkan semua rekaman untuk guru tersebut
                            files.append(filename)
                            print(f"Added file (all for guru): {filename}")
                    else:
                        print(f"File does not match guru: {filename}")
            print(f"Final files list: {files}")
            return jsonify({'files': files})
        except Exception as e:
            print(f"Error in get_rekaman_guru: {e}")
            return jsonify({'files': [], 'error': str(e)}), 500

    # Endpoint test untuk debugging
    @app.route('/api/test_rekaman', methods=['GET'])
    def test_rekaman():
        try:
            print("=== Test Rekaman Endpoint ===")
            rekaman_dir = UPLOAD_FOLDER
            all_files = os.listdir(rekaman_dir) if os.path.exists(rekaman_dir) else []
            print(f"All files: {all_files}")
            
            # Test parsing
            for filename in all_files:
                parts = filename.split('_')
                print(f"File: {filename}, Parts: {parts}")
            
            return jsonify({
                'upload_folder': UPLOAD_FOLDER,
                'exists': os.path.exists(rekaman_dir),
                'all_files': all_files,
                'test_files': [f for f in all_files if f.endswith('.m4a')]
            })
        except Exception as e:
            print(f"Error in test_rekaman: {e}")
            return jsonify({'error': str(e)}), 500

    # Endpoint test koneksi sederhana
    @app.route('/api/test_connection', methods=['GET'])
    def test_connection():
        try:
            print("=== Test Connection Endpoint ===")
            return jsonify({
                'status': 'success',
                'message': 'Backend is running',
                'timestamp': datetime.datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error in test_connection: {e}")
            return jsonify({'error': str(e)}), 500

    # Endpoint untuk summary hafalan santri
    @app.route('/api/santri/<string:kode_santri>/summary', methods=['GET'])
    def get_summary_hafalan(kode_santri):
        try:
            print(f"=== Get Summary Hafalan for {kode_santri} ===")
            # Ambil data penilaian santri
            penilaian_list = PenilaianHafalan.query.filter_by(santri_id=kode_santri).all()
            
            if not penilaian_list:
                print("No penilaian data found")
                return jsonify({
                    'total_surat': 0,
                    'total_ayat': 0,
                    'rata_tajwid': 0,
                    'sesi_hari_ini': 0
                })
            
            # Hitung total surat unik
            surat_unik = set()
            total_ayat = 0
            total_tajwid = 0
            sesi_hari_ini = 0
            
            # Mapping nilai tajwid
            nilai_tajwid = {
                'Kurang': 1,
                'Cukup': 2,
                'Baik': 3,
                'Sangat Baik': 4
            }
            
            today = datetime.datetime.now().date()
            
            for penilaian in penilaian_list:
                surat_unik.add(penilaian.surat)
                total_ayat += (penilaian.sampai_ayat - penilaian.dari_ayat + 1)
                
                # Hitung nilai tajwid
                if penilaian.penilaian_tajwid in nilai_tajwid:
                    total_tajwid += nilai_tajwid[penilaian.penilaian_tajwid]
                
                # Hitung sesi hari ini
                if penilaian.tanggal_penilaian and penilaian.tanggal_penilaian.date() == today:
                    sesi_hari_ini += 1
            
            rata_tajwid = total_tajwid / len(penilaian_list) if penilaian_list else 0
            
            result = {
                'total_surat': len(surat_unik),
                'total_ayat': total_ayat,
                'rata_tajwid': round(rata_tajwid, 2),
                'sesi_hari_ini': sesi_hari_ini
            }
            
            print(f"Summary result: {result}")
            return jsonify(result)
            
        except Exception as e:
            print(f"Error in get_summary_hafalan: {e}")
            return jsonify({'error': str(e)}), 500

    # Endpoint untuk overview santri
    @app.route('/api/santri/<string:kode_santri>/overview', methods=['GET'])
    def get_overview_santri(kode_santri):
        try:
            print(f"=== Get Overview for {kode_santri} ===")
            from app.models import PenilaianHafalan, Santri
            
            # Ambil data santri
            santri = Santri.query.filter_by(nis=kode_santri).first()
            if not santri:
                return jsonify({'error': 'Santri not found'}), 404
            
            # Ambil data penilaian santri
            penilaian_list = PenilaianHafalan.query.filter_by(santri_id=kode_santri).order_by(PenilaianHafalan.tanggal_penilaian.desc()).all()
            
            # Hitung statistik
            total_surat = len(set([p.surat for p in penilaian_list])) if penilaian_list else 0
            total_ayat = sum([(p.sampai_ayat - p.dari_ayat + 1) for p in penilaian_list]) if penilaian_list else 0
            
            # Hitung rata-rata nilai
            total_nilai = 0
            nilai_count = 0
            for penilaian in penilaian_list:
                try:
                    nilai = int(penilaian.hasil_naive_bayes)
                    total_nilai += nilai
                    nilai_count += 1
                except (ValueError, TypeError):
                    continue
            
            rata_nilai = round(total_nilai / nilai_count, 1) if nilai_count > 0 else 0
            
            # Hitung sesi hari ini
            from datetime import datetime, date
            today = date.today()
            sesi_hari_ini = len([p for p in penilaian_list if p.tanggal_penilaian and p.tanggal_penilaian.date() == today])
            
            # Hitung progress percentage (contoh: berdasarkan jumlah surat)
            # Asumsikan target adalah 30 surat (bisa disesuaikan)
            target_surat = 30
            progress_percentage = min(total_surat / target_surat, 1.0) if target_surat > 0 else 0.0
            
            # Ambil surat terakhir
            surat_terakhir = penilaian_list[0].surat if penilaian_list else '-'
            
            # Hitung juz terakhir (contoh sederhana)
            juz_terakhir = 0
            if penilaian_list:
                # Mapping sederhana surat ke juz (bisa disesuaikan)
                surat_to_juz = {
                    'Al-Fatihah': 1, 'Al-Baqarah': 1, 'Al-Imran': 2, 'An-Nisa': 2,
                    'Al-Maidah': 3, 'Al-Anam': 3, 'Al-Araf': 4, 'Al-Anfal': 4,
                    # ... tambahkan mapping lainnya
                }
                juz_terakhir = surat_to_juz.get(surat_terakhir, 0)
            
            result = {
                'total_surat': total_surat,
                'total_ayat': total_ayat,
                'rata_nilai': rata_nilai,
                'sesi_hari_ini': sesi_hari_ini,
                'progress_percentage': progress_percentage,
                'surat_terakhir': surat_terakhir,
                'juz_terakhir': f'Juz {juz_terakhir}' if juz_terakhir > 0 else '-',
            }
            
            print(f"Overview result: {result}")
            return jsonify(result)
            
        except Exception as e:
            print(f"Error in get_overview_santri: {e}")
            return jsonify({'error': str(e)}), 500

    # Endpoint untuk log harian santri
    @app.route('/api/santri/<string:kode_santri>/log-harian', methods=['GET'])
    def get_log_harian(kode_santri):
        try:
            print(f"=== Get Log Harian for {kode_santri} ===")
            # Ambil data penilaian santri untuk log harian
            penilaian_list = PenilaianHafalan.query.filter_by(santri_id=kode_santri).order_by(PenilaianHafalan.tanggal_penilaian.desc()).limit(10).all()
            
            log_harian = []
            
            for penilaian in penilaian_list:
                log_entry = {
                    'jenis': 'penilaian',
                    'aktivitas': f'Hafalan {penilaian.surat} (Ayat {penilaian.dari_ayat}-{penilaian.sampai_ayat})',
                    'tanggal': penilaian.tanggal_penilaian.strftime('%Y-%m-%d') if penilaian.tanggal_penilaian else 'N/A',
                    'catatan': penilaian.catatan if penilaian.catatan else None
                }
                log_harian.append(log_entry)
            
            print(f"Log harian result: {len(log_harian)} entries")
            return jsonify(log_harian)
            
        except Exception as e:
            print(f"Error in get_log_harian: {e}")
            return jsonify({'error': str(e)}), 500

    # Endpoint login untuk aplikasi mobile
    @app.route('/api/login', methods=['POST'])
    def api_login():
        try:
            print("=== API Login Endpoint ===")
            data = request.get_json()
            
            if not data:
                return jsonify({'message': 'Data tidak valid'}), 400
            
            user_type = data.get('user_type')
            credential = data.get('credential')
            
            print(f"User Type: {user_type}")
            print(f"Credential: {credential}")
            
            if not user_type or not credential:
                return jsonify({'message': 'Tipe pengguna dan kredensial harus diisi'}), 400
            
            # Cari user berdasarkan tipe dan kredensial
            user = None
            display_name = None
            
            if user_type == 'Santri':
                user = Santri.query.filter_by(kode_santri=credential).first()
                if user:
                    display_name = user.nama_lengkap
            elif user_type == 'Guru':
                user = Guru.query.filter_by(kode_guru=credential).first()
                if user:
                    display_name = user.nama_lengkap
            elif user_type == 'Orang Tua Santri':
                user = OrangTuaSantri.query.filter_by(kode_orangtua=credential).first()
                if user:
                    display_name = user.nama
            elif user_type == 'Admin':
                user = Admin.query.filter_by(username=credential).first()
                if user:
                    display_name = user.username
            
            if user:
                print(f"User found: {display_name}")
                # Update last_login untuk user yang ditemukan
                user.last_login = datetime.datetime.now()
                db.session.commit()
                
                return jsonify({
                    'message': 'Login berhasil',
                    'user_type': user_type,
                    'credential': credential,
                    'display_name': display_name
                }), 200
            else:
                print(f"User not found for {user_type}: {credential}")
                return jsonify({'message': 'Kredensial tidak valid atau pengguna tidak ditemukan'}), 401
                
        except Exception as e:
            print(f"Error in api_login: {e}")
            return jsonify({'message': f'Terjadi kesalahan server: {str(e)}'}), 500