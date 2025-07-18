from app.data_migration import create_app, db
from app.models import Admin

# Inisialisasi Flask app
app = create_app()

# Data akun admin
USERNAME = "monitoring1"
PASSWORD = "monitoring1"

with app.app_context():
    # Cek apakah username sudah ada
    existing = Admin.query.filter_by(username=USERNAME).first()
    if existing:
        print(f"Akun admin dengan username '{USERNAME}' sudah ada.")
    else:
        admin = Admin(username=USERNAME)
        admin.set_password(PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Akun admin '{USERNAME}' berhasil dibuat.") 