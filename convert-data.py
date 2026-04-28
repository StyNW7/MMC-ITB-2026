import pandas as pd
import numpy as np

# Baca file (asumsi nama file: 'Dataset_MMC - Data BMKG NTT.csv')
file_path = 'Dataset_MMC - Data BMKG NTT.csv'
df = pd.read_csv(file_path, thousands=None, decimal=',')

# Bersihkan nama kolom (opsional)
df.columns = df.columns.str.strip()

# Fungsi untuk membersihkan kolom numerik yang masih error
def clean_numeric(col):
    # Jika kolom bertipe object (string), bersihkan
    if df[col].dtype == 'object':
        # Ganti koma dengan titik untuk desimal
        df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
        # Ganti nilai 8888, 9999, dan sejenisnya dengan NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # Nilai 8888, 9999 yang mungkin tersisa jadi NaN
        df[col] = df[col].replace([8888, 9999, 8888.0, 9999.0], np.nan)
    else:
        # Jika sudah numeric, tetap cek 8888/9999
        df[col] = df[col].replace([8888, 9999], np.nan)
    return df[col]

# Daftar kolom yang perlu dibersihkan. 
# Berdasarkan isi file, semua kolom kecuali TANGGAL, mungkin perlu dibersihkan 
# karena berisi koma dan 8888/9999.
# Tapi beberapa kolom seperti G(t), Tp, dll sudah dihitung? Lebih aman bersihkan semua kolom numerik potensial.
numeric_columns = ['TN', 'TX', 'TAVG', 'RH_AVG', 'RR', 'SS', 'FF_X', 'DDD_X', 'FF_AVG', 
                   'DDD_CAR', 'G(t)', 'Tp', 'ηref', 'A', 'P', 'Energi/hari', 'SSavg', 
                   'Gavg', 'Tavg', 'Eavg', 'Etotal']

# Kolom yang mungkin tidak ada di file asli tapi ada di dataframe? Cek dulu.
existing_numeric_cols = [col for col in numeric_columns if col in df.columns]

for col in existing_numeric_cols:
    df[col] = clean_numeric(col)

# Konversi kolom tanggal
if 'TANGGAL' in df.columns:
    # Ganti format tanggal dari "01-01-2025" ke datetime
    df['TANGGAL'] = pd.to_datetime(df['TANGGAL'], format='%d-%m-%Y', errors='coerce')
    # Atau biarkan sebagai string jika tidak perlu datetime, tapi lebih baik datetime
    pass

# Urutkan berdasarkan tanggal jika perlu
if 'TANGGAL' in df.columns:
    df = df.sort_values('TANGGAL').reset_index(drop=True)

# Simpan ke CSV baru dengan pemisah koma dan titik untuk desimal (standar internasional)
output_path = 'Dataset_MMC_Cleaned.csv'
# Menggunakan titik sebagai desimal (standard CSV)
df.to_csv(output_path, index=False, sep=',', decimal='.')

print(f"File telah dibersihkan dan disimpan sebagai: {output_path}")
print("\n5 baris pertama dari data yang telah dibersihkan:")
print(df.head())
print("\nInfo tipe data setelah pembersihan:")
print(df.info())
print("\nStatistik deskriptif kolom numerik:")
print(df[existing_numeric_cols].describe())