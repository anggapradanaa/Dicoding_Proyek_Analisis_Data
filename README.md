# 🌫️ Beijing Air Quality Analysis Project

Proyek analisis kualitas udara di Beijing menggunakan data dari 12 stasiun monitoring (2013-2017) dengan fokus pada PM2.5 sebagai indikator utama polusi udara.

## 📋 Deskripsi Proyek

Proyek ini menganalisis kualitas udara di Beijing untuk menjawab 4 pertanyaan bisnis utama:

1. **Station mana yang memiliki rata-rata PM2.5 tertinggi selama periode pengamatan?**
2. **Bagaimana pola musiman PM2.5 di Beijing selama periode 2013-2017, dan bulan apa yang konsisten menunjukkan konsentrasi tertinggi dan terendah?**
3. **Bagaimana pengelompokan stasiun monitoring berdasarkan tingkat rata-rata PM2.5 selama periode 2013-2017, dan karakteristik polusi apa yang membedakan setiap kelompok?**

---

## 🎯 Fitur Utama

### 📓 Notebook Analysis
- ✅ Data wrangling lengkap (gathering, assessing, cleaning)
- ✅ Exploratory Data Analysis (EDA) komprehensif
- ✅ Visualisasi profesional dengan matplotlib & seaborn
- ✅ Analisis lanjutan: clustering manual & correlation analysis
- ✅ Kesimpulan mendalam untuk setiap pertanyaan bisnis

### 📊 Interactive Dashboard
- ✅ Filter interaktif (station & date range)
- ✅ Real-time metric cards
- ✅ Tren PM2.5 dinamis
- ✅ Perbandingan antar station
- ✅ Clustering tingkat polusi
- ✅ Correlation heatmap antar variabel

---

## 🚀 Cara Menjalankan

### 1. Persiapan Environment

```bash
# Clone atau download project
# Pastikan folder PRSA_Data_20130301-20170228 ada di direktori yang sama

# Install dependencies
pip install -r requirements.txt
```

### 2. Menjalankan Notebook Analysis

```bash
# Buka Jupyter Notebook
jupyter notebook analysis_notebook.ipynb

# Atau gunakan JupyterLab
jupyter lab analysis_notebook.ipynb
```

### 3. Menjalankan Dashboard

```bash
# Jalankan Streamlit dashboard
streamlit run dashboard.py

# Dashboard akan terbuka di browser (default: http://localhost:8501)
```

## 📊 Dataset Information

### Sumber Data
- **Dataset**: PRSA Air Quality Dataset
- **Periode**: 1 Maret 2013 - 28 Februari 2017
- **Stations**: 12 stasiun monitoring di Beijing
- **Total Records**: ~420,000 entries (setelah cleaning)

### Variabel Utama
- `PM2.5`: Particulate Matter 2.5 (µg/m³) - **Fokus utama**
- `PM10`: Particulate Matter 10 (µg/m³)
- `SO2`: Sulfur Dioxide (µg/m³)
- `NO2`: Nitrogen Dioxide (µg/m³)
- `CO`: Carbon Monoxide (µg/m³)
- `O3`: Ozone (µg/m³)
- `TEMP`: Temperature (°C)
- `PRES`: Pressure (hPa)
- `DEWP`: Dew Point (°C)
- `RAIN`: Rainfall (mm)
- `WSPM`: Wind Speed (m/s)

### Daftar Station
1. Aotizhongxin
2. Changping
3. Dingling
4. Dongsi
5. Guanyuan
6. Gucheng
7. Huairou
8. Nongzhanguan
9. Shunyi
10. Tiantan
11. Wanliu
12. Wanshouxigong

## 🔍 Metodologi Analisis

### 1. Data Wrangling
- **Gathering**: Menggabungkan 12 file CSV
- **Assessing**: Identifikasi missing values, outliers, dan inkonsistensi
- **Cleaning**: Remove missing PM2.5, drop duplikasi

### 2. Exploratory Data Analysis
- Analisis distribusi PM2.5
- Pola temporal (tahunan, bulanan, musiman)
- Perbandingan antar stasiun

### 3. Advanced Analysis
- **Clustering Manual**: Klasifikasi stasiun berdasarkan tingkat polusi
  - Rendah: < 50 µg/m³
  - Sedang: 50-75 µg/m³
  - Tinggi: 75-100 µg/m³
  - Sangat Tinggi: > 100 µg/m³

- **Correlation Analysis**: Hubungan antar polutan dan faktor meteorologi

### 4. Visualization
- Line charts untuk tren temporal
- Bar charts untuk perbandingan stasiun
- Heatmaps untuk korelasi
- Horizontal bar chart untuk clustering

## 📈 Hasil Utama

### Key Findings

1. **Polusi Tertinggi**: Beberapa stasiun menunjukkan rata-rata PM2.5 > 85 µg/m³ (jauh di atas standar WHO: 35 µg/m³)

2. **Pola Musiman yang Jelas**:
   - Musim Dingin: PM2.5 tertinggi (85-100 µg/m³)
   - Musim Panas: PM2.5 terendah (50-60 µg/m³)

3. **Kelompok Polusi Berbeda**: Terdapat 4 cluster stasiun berdasarkan karakteristik tingkat polusi.

## 🛠️ Teknologi yang Digunakan

- **Python 3.8+**
- **Libraries**:
  - `pandas` - Data manipulation
  - `numpy` - Numerical operations
  - `matplotlib` - Visualization
  - `seaborn` - Statistical visualization
  - `streamlit` - Interactive dashboard
  - `scikit-learn` - Data preprocessing (StandardScaler)

## 📄 License

Proyek ini dibuat untuk keperluan edukasi dan analisis data.

---
