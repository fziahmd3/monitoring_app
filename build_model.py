import pandas as pd
from sklearn.naive_bayes import MultinomialNB, GaussianNB # Tambahkan GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import numpy as np # Tambahkan numpy

# 1. Dummy dataset
data = {
    'tingkat_hafalan': ['tinggi', 'rendah', 'sedang', 'tinggi', 'sedang', 'rendah'],
    'jumlah_setoran': [15, 5, 10, 18, 9, 4],
    'kehadiran': [95, 60, 80, 100, 85, 55],
    'kemajuan': ['baik', 'kurang', 'cukup', 'baik', 'cukup', 'kurang']
}
df = pd.DataFrame(data)

# 2. Encode fitur kategorikal
le_tingkat = LabelEncoder()
df['tingkat_hafalan'] = le_tingkat.fit_transform(df['tingkat_hafalan'])

# 3. Fitur dan target
X = df[['tingkat_hafalan', 'jumlah_setoran', 'kehadiran']]
y = df['kemajuan']

# 4. Encode target
le_kemajuan = LabelEncoder()
y_encoded = le_kemajuan.fit_transform(y)

# 5. Split data dan latih model
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
model = MultinomialNB()
model.fit(X_train, y_train)

# 6. Simpan model dan encoder
with open('output/model.pkl', 'wb') as f_model:
    pickle.dump(model, f_model)

with open('output/encoder.pkl', 'wb') as f_enc:
    pickle.dump({
        'tingkat_hafalan': le_tingkat,
        'kemajuan': le_kemajuan
    }, f_enc)

# Simpan juga model dan encoder untuk penilaian (Gaussian Naive Bayes)
# Jika ada model Gaussian Naive Bayes terpisah yang dilatih di sini
# Periksa apakah ada inisialisasi model GaussianNB di build_model.py yang terlewat
# Jika tidak ada, bagian ini tidak diperlukan di build_model.py, hanya di app/routes.py
# Namun, jika Anda ingin menyertakan model yang dilatih di build_model.py, maka tambahkan kode berikut
# Untuk saat ini, asumsikan model Naive Bayes yang digunakan di app/routes.py dilatih secara terpisah dari model ini.
# Jika Anda ingin model di app/routes.py memuat model yang dilatih di build_model.py, 
# maka kita harus mengganti model.pkl dan encoder.pkl dengan model dan encoder yang digunakan untuk prediksi di routes.py
# Berdasarkan app/routes.py, ada 2 set model: satu untuk 'predict_web' (model, le_tingkat, le_kemajuan) 
# dan satu lagi untuk '/api/penilaian' (naive_bayes_model, le_hasil_penilaian).
# build_model.py saat ini melatih model untuk 'predict_web'.
# Jadi, kita hanya perlu memastikan model.pkl dan encoder.pkl terbuat dengan benar.
# Jika model naive_bayes_model dan le_hasil_penilaian juga dilatih secara terpisah 
# (seperti di contoh data pelatihan di app/routes.py), 
# maka kita tidak perlu menyimpannya dari build_model.py.
# Namun, jika Anda ingin menyimpannya dari build_model.py, Anda perlu melatihnya di sini juga.

print("Model dan encoder berhasil disimpan.")

# --- Bagian untuk model Penilaian Hafalan (Gaussian Naive Bayes) ---
# Contoh data pelatihan (X: tajwid, kelancaran, kefasihan; y: hasil penilaian)
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

# Simpan model dan encoder untuk penilaian hafalan
with open('output/naive_bayes_model.pkl', 'wb') as f_nb_model:
    pickle.dump(naive_bayes_model, f_nb_model)

with open('output/naive_bayes_encoder.pkl', 'wb') as f_nb_enc:
    pickle.dump(le_hasil_penilaian, f_nb_enc)

print("Model Naive Bayes untuk penilaian hafalan dan encoder berhasil disimpan.")
