# app/models.py
from app.extensions import db # Mengimpor objek db dari extensions.py
from werkzeug.security import generate_password_hash, check_password_hash

# Model Admin
class Admin(db.Model):
    __tablename__ = 'Admin'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nama_lengkap = db.Column(db.String(100))
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
    nip = db.Column(db.String(20), unique=True, nullable=False)
    pendidikan_terakhir = db.Column(db.String(50))
    nomor_telepon = db.Column(db.String(15))
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    profile_picture = db.Column(db.String(255), nullable=True) # Tambahkan field ini

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Guru {self.nama_lengkap} (NIP: {self.nip})>'

# Model Santri
class Santri(db.Model):
    __tablename__ = 'Santri'
    santri_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    nis = db.Column(db.String(20), unique=True, nullable=False)
    kelas = db.Column(db.String(50), nullable=False)
    alamat = db.Column(db.Text)
    nama_orang_tua = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    profile_picture = db.Column(db.String(255), nullable=True) # Tambahkan field ini

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Santri {self.nama_lengkap} (NIS: {self.nis})>'

# Model Hasil Prediksi
class PredictionResult(db.Model):
    __tablename__ = 'PredictionResult'
    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('Santri.santri_id'), nullable=False)
    tingkat_hafalan = db.Column(db.String(50), nullable=False)
    jumlah_setoran = db.Column(db.Integer, nullable=False)
    kehadiran = db.Column(db.Integer, nullable=False)
    hasil_prediksi = db.Column(db.String(50), nullable=False)
    predicted_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relasi dengan model Santri
    santri = db.relationship('Santri', backref=db.backref('predictions', lazy=True))

    def __repr__(self):
        return f'<PredictionResult {self.prediction_id} for Santri ID: {self.santri_id}>'

class OrangTuaSantri(db.Model):
    __tablename__ = 'OrangTuaSantri'
    ortu_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.String(255), nullable=True)
    nama_santri = db.Column(db.String(100), nullable=False)
    nomor_telepon = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<OrangTuaSantri {self.nama}>'