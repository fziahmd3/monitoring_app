import pandas as pd
from sklearn.naive_bayes import MultinomialNB, GaussianNB # Tambahkan GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import numpy as np # Tambahkan numpy

# --- Bagian untuk model Penilaian Hafalan (Gaussian Naive Bayes) dengan skala 1-100 ---
# Contoh data pelatihan dengan skala 1-100
# Data ini akan digunakan untuk memprediksi nilai akhir (1-100)
X_train_nb = np.array([
    # Tajwid, Kelancaran, Kefasihan (semua dalam skala 1-100)
    [95, 95, 95], # Nilai tinggi
    [90, 95, 90], # Nilai tinggi
    [95, 90, 95], # Nilai tinggi
    [85, 90, 85], # Nilai baik
    [80, 85, 80], # Nilai baik
    [85, 80, 85], # Nilai baik
    [75, 80, 75], # Nilai cukup (KKM)
    [75, 80, 75], # Nilai cukup (KKM)
    [70, 75, 70], # Nilai cukup
    [75, 70, 75], # Nilai cukup
    [65, 70, 65], # Nilai kurang
    [60, 65, 60], # Nilai kurang
    [70, 60, 70], # Nilai kurang
    [55, 60, 55], # Nilai sangat kurang
    [50, 55, 50], # Nilai sangat kurang
    [45, 50, 45], # Nilai sangat kurang
    [40, 45, 40], # Nilai sangat kurang
    [35, 40, 35], # Nilai sangat kurang
    [30, 35, 30], # Nilai sangat kurang
    [25, 30, 25], # Nilai sangat kurang
    [20, 25, 20], # Nilai sangat kurang
    [15, 20, 15], # Nilai sangat kurang
    [10, 15, 10], # Nilai sangat kurang
    [5, 10, 5],   # Nilai sangat kurang
    [1, 5, 1],    # Nilai sangat kurang
])

# Target: nilai akhir (1-100) yang diprediksi berdasarkan rata-rata dari 3 komponen
y_train_nb = np.array([
    95, 92, 93,  # Nilai tinggi (lulus)
    87, 82, 83,  # Nilai baik (lulus)
    77, 75,  # Nilai cukup (lulus)
    72, 73, 67, # Nilai kurang (tidak lulus)
    62, 67,  # Nilai kurang (tidak lulus)
    57, 52, 47,  # Nilai sangat kurang (tidak lulus)
    42, 37, 32,  # Nilai sangat kurang (tidak lulus)
    27, 22, 17,  # Nilai sangat kurang (tidak lulus)
    12, 7, 2,    # Nilai sangat kurang (tidak lulus)
])

# Untuk model ini, kita tidak perlu LabelEncoder karena target adalah nilai numerik
# Kita akan menggunakan model regresi atau tetap menggunakan GaussianNB untuk klasifikasi nilai

naive_bayes_model = GaussianNB()
naive_bayes_model.fit(X_train_nb, y_train_nb)

# Simpan model untuk penilaian hafalan
with open('output/naive_bayes_model.pkl', 'wb') as f_nb_model:
    pickle.dump(naive_bayes_model, f_nb_model)

# Simpan KKM sebagai konstanta
kkm = 75
with open('output/kkm.pkl', 'wb') as f_kkm:
    pickle.dump(kkm, f_kkm)

print("Model Naive Bayes untuk penilaian hafalan dengan skala 1-100 dan KKM berhasil disimpan.")
