# run.py
import os
from app.data_migration import create_app, db, migrate # Import the factory
from app.models import Admin, Guru, Santri # Impor model-model Anda

# Create the app instance for running the development server
app = create_app()

# Set environment variable for Flask
os.environ['FLASK_APP'] = 'run:app'

# ===============================================
# Main Block untuk Menjalankan Aplikasi
# ===============================================
print("Flask app created and db initialized.")

print("Flask app running. Endpoints:")
print(app.url_map)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
