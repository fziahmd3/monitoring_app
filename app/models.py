# app/models.py
from app.__init__ import db # Mengimpor objek db dari __init__.py
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Santri {self.nama_lengkap} (NIS: {self.nis})>'