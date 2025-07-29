# app/models.py
from app.extensions import db # Mengimpor objek db dari extensions.py
from werkzeug.security import generate_password_hash, check_password_hash

# Model Admin
class Admin(db.Model):
    __tablename__ = 'Admin'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    profile_picture = db.Column(db.String(255), nullable=True) # Tambahkan field ini

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'

# Model Guru
class Guru(db.Model):
    __tablename__ = 'Guru'
    guru_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    kode_guru = db.Column(db.String(20), unique=True, nullable=False)  # Ganti NIP dengan kode_guru
    status_pengajar = db.Column(db.String(50))  # Misal: ustadz, ustadzah, pembina, dll
    nomor_telepon = db.Column(db.String(15))
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    profile_picture = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Guru {self.nama_lengkap} (Kode: {self.kode_guru})>'

# Model Santri
class Santri(db.Model):
    __tablename__ = 'Santri'
    santri_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    kode_santri = db.Column(db.String(20), unique=True, nullable=False)  # ganti nis
    tingkatan = db.Column(db.String(50), nullable=False)  # ganti kelas
    alamat = db.Column(db.Text)
    nama_orang_tua = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    profile_picture = db.Column(db.String(255), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Santri {self.nama_lengkap} (Kode: {self.kode_santri})>'

# Model Hasil Prediksi
# class PredictionResult(db.Model):
#     __tablename__ = 'PredictionResult'
#     prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     santri_id = db.Column(db.Integer, db.ForeignKey('Santri.santri_id'), nullable=False)
#     tingkat_hafalan = db.Column(db.String(50), nullable=False)
#     jumlah_setoran = db.Column(db.Integer, nullable=False)
#     kehadiran = db.Column(db.Integer, nullable=False)
#     hasil_prediksi = db.Column(db.String(50), nullable=False)
#     predicted_at = db.Column(db.DateTime, default=db.func.current_timestamp())
#
#     # Relasi dengan model Santri
#     santri = db.relationship('Santri', backref=db.backref('predictions', lazy=True))
#
#     def __repr__(self):
#         return f'<PredictionResult {self.prediction_id} for Santri ID: {self.santri_id}>'

class OrangTuaSantri(db.Model):
    __tablename__ = 'OrangTuaSantri'
    ortu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.String(255), nullable=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('Santri.santri_id'), nullable=False)
    nomor_telepon = db.Column(db.String(20), nullable=True)

    santri = db.relationship('Santri', backref=db.backref('orangtua', lazy=True))

    def __repr__(self):
        return f'<OrangTuaSantri {self.nama}>'

class PenilaianHafalan(db.Model):
    __tablename__ = 'PenilaianHafalan'
    penilaian_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('Santri.santri_id'), nullable=False)
    surat = db.Column(db.String(50), nullable=False)
    dari_ayat = db.Column(db.Integer, nullable=False)
    sampai_ayat = db.Column(db.Integer, nullable=False)
    penilaian_tajwid = db.Column(db.Integer, nullable=False) # Diubah menjadi Integer
    kelancaran = db.Column(db.Integer, nullable=False) # Field baru
    kefasihan = db.Column(db.Integer, nullable=False) # Field baru
    catatan = db.Column(db.Text, nullable=True) # Field baru untuk catatan
    hasil_naive_bayes = db.Column(db.String(50), nullable=False, default='Belum Diprediksi') # Diubah menjadi not nullable dengan default
    tanggal_penilaian = db.Column(db.DateTime, default=db.func.current_timestamp())

    santri = db.relationship('Santri', backref=db.backref('penilaian_hafalan', lazy=True))

    def __repr__(self):
        return f'<PenilaianHafalan {self.penilaian_id} - Santri ID: {self.santri_id}>'