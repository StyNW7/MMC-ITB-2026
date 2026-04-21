## 📌 DAFTAR LENGKAP SIMULASI YANG DAPAT DIBUAT DENGAN PYTHON

*(Berdasarkan dokumen submission Anda – Bab II, Bab III, & Lampiran)*

---

### **BAGIAN 1 – MODEL PRODUKSI PV FISIK (Bab III.3.1)**

| No | Nama Simulasi | Formula / Model | Output / Grafik yang Dihasilkan |
|----|---------------|----------------|--------------------------------|
| 1.1 | Konversi SS ke Irradiansi | $G(t) = \frac{SS(t)}{12} \times 1000$ | Grafik time series $G(t)$ harian vs $SS(t)$ |
| 1.2 | Koreksi suhu panel $T_p(t)$ | $T_p(t) = T_{\text{avg}}(t) + 0.03 \times G(t)$ | Grafik $T_p(t)$ vs $T_{\text{avg}}(t)$ |
| 1.3 | Efisiensi vs suhu $\eta(T_p)$ | $\eta(T_p) = 0.20 \times [1 - 0.004 \times (T_p - 25)]$ | Grafik penurunan efisiensi terhadap suhu |
| 1.4 | Daya keluaran $P(t)$ | $P(t) = G(t) \times A \times \eta(T_p) \times PR$ | Grafik $P(t)$ harian (kW) |
| 1.5 | Energi harian $E(t)$ | $E(t) = \frac{P(t) \times SS(t)}{1000}$ | Grafik produksi energi harian (kWh) |
| 1.6 | Produksi bulanan & tahunan | Agregasi $E(t)$ ke bulan/tahun | Bar chart produksi per bulan, total tahunan |
| 1.7 | Variabilitas musiman (CV) | $CV = \frac{\sigma}{\mu} \times 100\%$ | Tabel & visualisasi CV per musim |
| 1.8 | Penalti termal contoh bulan Oktober | $T_p$, $\eta$, penalti = $1 - \eta/\eta_{\text{ref}}$ | Grafik perbandingan produksi vs STC |

---

### **BAGIAN 2 – DEGRADASI MODUL (Bab II.2.1.3)**

| No | Nama Simulasi | Formula / Model | Output / Grafik |
|----|---------------|----------------|----------------|
| 2.1 | Degradasi eksponensial $D(y)$ | $D(y) = (1 - \delta_d)^y$ dengan $\delta_d = 0.005, 0.008, 0.01$ | Grafik degradasi 30 tahun (3 skenario) |
| 2.2 | Kapasitas tersisa vs waktu | $K(y) = K_0 \times D(y)$ | Grafik penurunan kapasitas seiring waktu |

---

### **BAGIAN 3 – PROYEKSI IKLIM (Bab III.3.2)**

| No | Nama Simulasi | Formula / Model | Output / Grafik |
|----|---------------|----------------|----------------|
| 3.1 | Tren kenaikan suhu | $T_{\text{avg}}(t,y) = T_{\text{hist}}(t) + \Delta T(y)$ dengan $\Delta T(y) = +0.03^\circ C$/tahun | Grafik linear trend suhu 2024–2074 |
| 3.2 | Produksi dengan Climate Penalty | $P_{\text{out}}(t) = P_{\text{src}} \times \frac{G_{\text{actual}} \times A_{\text{haze}}}{1000} \times L_{\text{temp}} \times (1 - L_{\text{soiling}}) \times \eta_{\text{inv}}$ | Grafik produksi 50 tahun dengan tren menurun |
| 3.3 | Simulasi volatilitas (Gaussian noise) | $G_s(t) = G(t) \times [1 + \varepsilon(t)], \quad \varepsilon \sim N(0, \sigma^2)$ | Grafik produksi dengan confidence band |
| 3.4 | Haze attenuation (Beer-Lambert) | $A_{\text{haze}}(t) = \exp(-\tau \cdot PM_{2.5}(t) \cdot L_{\text{path}})$ | Grafik redaman akibat PM2.5 |
| 3.5 | Cloud cover effect | $G_{\text{actual}}(t) = G_{\text{clear}}(t) \times (1 - C_f(t))$ | Grafik fluktuasi akibat tutupan awan |

---

### **BAGIAN 4 – MARKOV CHAIN & CAPACITY FACTOR (Bab III.3.3.1 & Lampiran 5)**

| No | Nama Simulasi | Formula / Model | Output / Grafik |
|----|---------------|----------------|----------------|
| 4.1 | Distribusi CF dari data SS | $CF = SS / 24$ | Histogram CF, distribusi empiris |
| 4.2 | Klasifikasi dua state (Low/Normal) | Threshold CF < 0.30 → Low | Pie chart probabilitas $p_L$, $p_N$ |
| 4.3 | Simulasi rantai Markov 50 tahun | Transisi state $\omega_t \in \{L, N\}$ dengan probabilitas tetap | Grafik state evolution 50 tahun |
| 4.4 | Produksi PV stokastik | $g_t^{PV} = CF_\omega \times K_t^{PV}$ | Grafik produksi tahunan dengan 2 skenario |

---

### **BAGIAN 5 – OPTIMISASI SDP / MDP (Bab III.3.3.2 & Lampiran 5)**

| No | Nama Simulasi | Formula / Model | Output / Grafik |
|----|---------------|----------------|----------------|
| 5.1 | Value iteration (Bellman) | $V_t(S_t) = \min_{a_t} [\mathbb{E}[C_t] + \beta \mathbb{E}[V_{t+1}(S_{t+1})]]$ | Kurva konvergensi value function |
| 5.2 | Lintasan investasi optimal | $a_t = (x_t^{DPV}, x_t^{UPV}, x_t^{BESS,P}, x_t^{BESS,E}, x_t^{FIRM})$ | Grafik akumulasi kapasitas per teknologi (50 tahun) |
| 5.3 | Perbandingan 4 strategi | Rapid DPV, Utility-scale, Storage-led, Diversified | Bar chart perbandingan biaya, EENS, risiko |
| 5.4 | EENS simulasi | $EENS_t = p_L \cdot LS_t^{Low} + p_N \cdot LS_t^{Normal}$ | Grafik EENS per tahun per strategi |
| 5.5 | Evolusi energi BESS | $E_{t+1}^{BESS} = E_t^{BESS} + \eta_c p_t^{charge} - \frac{1}{\eta_d} p_t^{discharge}$ | Grafik state of charge (SoC) baterai |
| 5.6 | Load shedding event | $LS_t = \max(0, D_t - \text{supply}_t)$ | Grafik frekuensi & durasi load shedding |

---

### **BAGIAN 6 – PENENTUAN LOKASI (Bab III.3.5)**

| No | Nama Simulasi | Formula / Model | Output / Grafik |
|----|---------------|----------------|----------------|
| 6.1 | Sequential Hard Filtering (simulasi) | Filter: radius, slope, land cover, jarak permukiman, RTRW, luas minimum | Visualisasi hasil filter (peta konseptual) |
| 6.2 | Estimasi kapasitas potensial | Luas lahan (Ha) × 1 MWp/Ha | Bar chart potensi per kandidat lokasi |

---

### **BAGIAN 7 – KEADILAN ENERGI (Bab III.3.6)**

| No | Nama Simulasi | Formula / Model | Output / Grafik |
|----|---------------|----------------|----------------|
| 7.1 | Indeks Gini Energi | Kurva Lorenz untuk distribusi manfaat PV | Kurva Lorenz + nilai Gini (0–1) |
| 7.2 | Perbandingan Gini antar strategi | DPV saja vs UPV+BESS | Bar chart perbandingan keadilan |

---

### **BAGIAN 8 – PERBANDINGAN STRATEGI (Bab III.3.4 & Tabel hal. 19)**

| No | Nama Simulasi | Output / Grafik |
|----|---------------|----------------|
| 8.1 | Radar chart 4 strategi | Dimensi: Biaya awal, Total cost jangka panjang, EENS, Ketahanan Low Solar |
| 8.2 | Biaya vs Keandalan (Pareto frontier) | Scatter plot: Total cost vs EENS untuk berbagai skenario investasi |

---

### **BAGIAN 9 – VISUALISASI DATA HISTORIS (Bab III.3.1 Tabel 3.1)**

| No | Nama Simulasi | Output / Grafik |
|----|---------------|----------------|
| 9.1 | Produksi bulanan 1 kWp | Bar chart 12 bulan (kWh/bulan) |
| 9.2 | SS, G, Tavg per bulan | Line chart multi-axis |
| 9.3 | Korelasi SS vs produksi | Scatter plot + regresi linier |

---

## 🧠 REKOMENDASI UTAMA UNTUK SIMULASI PYTHON

| Prioritas | Simulasi | Kegunaan untuk Presentasi |
|-----------|----------|---------------------------|
| **Tertinggi** | 1.6, 3.2, 5.3, 5.4 | Climate Penalty, perbandingan strategi, EENS |
| **Tinggi** | 4.3, 5.2, 5.5 | Markov Chain, lintasan investasi, BESS SoC |
| **Sedang** | 1.1–1.5, 2.1, 7.1 | Fisik PV, degradasi, Gini |
| **Pelengkap** | 6.1, 8.1, 9.1 | Peta konseptual, radar chart, data historis |

---

## 🛠️ TEKNIS SIMULASI

- **Bahasa:** Python 3.9+
- **Library utama:** NumPy, Pandas, Matplotlib, Seaborn, SciPy
- **Struktur kode:** Saya sarankan membuat 1 Jupyter Notebook dengan **9 bagian** sesuai daftar di atas
- **Data input:** Gunakan data historis dari Tabel 3.1 (produksi bulanan) dan data SS harian (dapat disintetis ulang dari statistik yang diberikan)