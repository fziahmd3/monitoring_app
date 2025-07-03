import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle

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

print("Model dan encoder berhasil disimpan.")
