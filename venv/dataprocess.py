import pandas as pd

# Ganti 'dataset-ayam.csv' dengan nama file CSV yang akan Anda cek
df = pd.read_csv('dataset-udang.csv')
print("Kolom dalam CSV:", df.columns.tolist())
print("\nContoh 5 baris pertama:\n", df.head())