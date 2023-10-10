# -*- coding: utf-8 -*-
"""submission-dicoing-predictive-analytics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14YIMaSQZ9Z00QKeZUvkeVdGAAMtkYam9

Link download datasets: https://finance.yahoo.com/quote/BTC-USD/history?p=BTC-USD

# Import Library
"""

# Commented out IPython magic to ensure Python compatibility.
# Import Library yang dibutuhkan
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
# %matplotlib inline

"""# Data Loading"""

# Melihat datasets
df = pd.read_csv('/content/BTC-USD.csv')
df.head()

print(f'Data memiliki {df.shape[0]} data dan {df.shape[1]} kolom/fitur.')

"""# Exploratory Data Analysis

Dataset ini memiliki 1827 baris data dan 7 kolom :

1.   Date : Tanggal data tersebut direkam
2.   Open : Harga pembukaan pada hari tersebut
3.   High : Harga tertinggi pada hari tersebut
4.   Low : Harga terendah pada hari tersebut
5.   Close : Harga penutupan pada hari tersebut
6.   Adj Close (Adjusted Close) : Harga penutupan pada hari tersebut setelah disesuaikan dengan aksi korporasi seperti right issue, stock split atau stock reverse
7.   Volume : Banyaknya transaksi pada hari tersebut
"""

#Mengecek data apakah memiliki missing value atau tidak
print(df.isnull().sum())

col_with_missing = [col for col in df.columns if df[col].isnull().any()]
print('Kolom dengan missing value:', col_with_missing)

from sklearn.impute import SimpleImputer
imputer = SimpleImputer()
df[col_with_missing] = imputer.fit_transform(df[col_with_missing])

print('Total missing value dalam dataframe:', df.isnull().sum().sum(), 'records')

"""## Explore Statistic Information

Sebuah data pasti memiliki informasi statistik pada masing-masing kolom, antara lain:

1.   Count : Jumlah data pada setiap kolom
2.   Mean : Nilai rata-rata pada setiam kolom
3.   Std : Standar deviasi pada setiap kolom
4.   Min : Nilai minimum pada setiap kolom
5.   25% : Kuartil pertama
6.   50% : Kuartil kedua atau biasa juga disebut median (nilai tengah)
7.   75% : Kuartil ketiga
8.   Max : Nilai maksimum pada setiap kolom
"""

df.info()

df.describe()

"""## Data visualiation"""

# Mencari outlier pada sebuah data
numerical_col = [col for col in df.columns if df[col].dtypes == 'float64']
plt.figure(figsize=(15,8))
sns.boxplot(data=df[numerical_col])
plt.show()

"""Hal pertama yang perlu Anda lakukan adalah membuat batas bawah dan batas atas. Untuk membuat batas bawah, kurangi Q1 dengan 1,5 * IQR. Kemudian, untuk membuat batas atas, tambahkan 1.5 * IQR dengan Q3"""

Q1 = df.quantile(.25)
Q3 = df.quantile(.75)
IQR = Q3 - Q1
bottom = Q1 - 1.5 * IQR
top = Q3 + 1.5 * IQR
df = df[~((df < bottom) | (df > top)).any(axis=1)]
df.head()

# Cek ukuran dataset setelah kita drop outliers
df.shape

"""## Univariate Analysis

Fitur yang diprediksi adalah "Adj Close"
"""

cols = 3
rows = 2
fig = plt.figure(figsize=(cols * 5, rows * 5))

for i, col in enumerate(numerical_col):
  ax = fig.add_subplot(rows, cols, i + 1)
  sns.histplot(x=df[col], bins=30, kde=True, ax=ax)
fig.tight_layout()
plt.show()

"""## Multivariate Analysis

Selanjutnya kita akan menganalisis korelasi fitur "Adj Close" terhadap fitur lain. Dapat disimpulkan bahwa "Adj Close" memiliki korelasi positif yang kuat terhadap fitur "Open", "High", "Low" dan "Close", sedangkan untuk fitur "Volume" memiliki korelasi sedang terhadap fitur "Adj Close"
"""

sns.pairplot(df[numerical_col], diag_kind='kde')
plt.show()

"""Untuk melihat korelasi lebih jelas, kita dapat menggunakan heatmap dari library seaborn"""

plt.figure(figsize=(15,8))
corr = df[numerical_col].corr().round(2)
sns.heatmap(data=corr, annot=True, vmin=-1, vmax=1, cmap='coolwarm', linewidth=1)
plt.title('Correlation matrix for numerical feature', size=15)
plt.show()

"""# Data Preparation

Data pada kolom "Date", "Volume", dan "Close" akan dihapus dikarenakan tidak diperlukan oleh model.
"""

# library for data preprocessing
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV, train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer

df = df.drop(['Date', 'Volume', 'Close'], axis=1)
df.head()

"""## Splitting Dataset"""

X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

# Split dat menjadi data latih dan uji
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42)

print('Total X_train:', len(X_train), 'records')
print('Total y_train:', len(y_train), 'records')
print('Total X_test:', len(X_test), 'records')
print('Total y_test:', len(y_test), 'records')

"""## Data Normalization

Proses normalisasi menggunakan library MinMaxScaler. Fungsi normalisasi diterapkan agar model lebih cepat dalam mempelajari data karena data telah diubah pada rentang tertentu seperti antara 0 dan 1
"""

scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

#models = pd.DataFrame(columns=['train_mse', 'test_mse'], index=['SVR', 'KNN', 'GradientBoosting'])

# Siapkan dataframe untuk analisis model
models = pd.DataFrame(index=['train_mse', 'test_mse'],
                      columns=['KNN', 'RandomForest', 'Boosting'])

"""# Modeling"""

from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.metrics import mean_squared_error

knn = KNeighborsRegressor(n_neighbors=10)
knn.fit(X_train, y_train)

models.loc['train_mse','knn'] = mean_squared_error(y_pred = knn.predict(X_train), y_true=y_train)

# buat model prediksi
RF = RandomForestRegressor(n_estimators=50, max_depth=16, random_state=55, n_jobs=-1)
RF.fit(X_train, y_train)

models.loc['train_mse','RandomForest'] = mean_squared_error(y_pred=RF.predict(X_train), y_true=y_train)

boosting = AdaBoostRegressor(learning_rate=0.05, random_state=55)
boosting.fit(X_train, y_train)
models.loc['train_mse','Boosting'] = mean_squared_error(y_pred=boosting.predict(X_train), y_true=y_train)

"""# Model Evaluation"""

# Buat variabel mse yang isinya adalah dataframe nilai mse data train dan test pada masing-masing algoritma
mse = pd.DataFrame(columns=['train', 'test'], index=['KNN','RF','Boosting'])

# Buat dictionary untuk setiap algoritma yang digunakan
model_dict = {'KNN': knn, 'RF': RF, 'Boosting': boosting}

# Hitung Mean Squared Error masing-masing algoritma pada data train dan test
for name, model in model_dict.items():
    mse.loc[name, 'train'] = mean_squared_error(y_true=y_train, y_pred=model.predict(X_train))/1e3
    mse.loc[name, 'test'] = mean_squared_error(y_true=y_test, y_pred=model.predict(X_test))/1e3

# Panggil mse
mse

fig, ax = plt.subplots()
mse.sort_values(by='test', ascending=False).plot(kind='barh', ax=ax, zorder=3)
ax.grid(zorder=0)

"""Dari gambar di atas, terlihat bahwa, model Random Forest (RF) memberikan nilai eror yang paling kecil. Sedangkan model dengan algoritma Boosting memiliki eror yang paling besar (berdasarkan grafik, angkanya di atas 2500). Model inilah yang akan kita pilih sebagai model terbaik untuk melakukan prediksi harga bitcoin."""