# 📃 LISTING LENGKAP SEMUA HASIL SIMULASI DARI SOLUSI MATEMATIKA

Berikut adalah **daftar lengkap semua hasil simulasi** yang disebutkan pada dokumen kami (Bab III & Ringkasan). Kami kelompokkan berdasarkan bagian simulasi agar mudah dipahami:

---

## 1. Hasil Simulasi Model Produksi PV Harian (Bab III.3.1 – hal. 14–15)

$1.$ **Analisis Data Historis (Tabel 3.1 – Produksi PV Bulanan 1 kWp, Stasiun Tardamu 2025)**:
  - Rata-rata lama penyinaran matahari ($SS_{\text{avg}}$): **7,34 jam/hari**
  - Rata-rata irradiansi ($G(t)_{\text{avg}}$): **582 W/m²**
  - Rata-rata produksi harian ($E_{\text{avg}}$): **32,30 kWh/hari** (untuk 1 kWp)
  - Total produksi tahunan: **11.811 kWh/kWp/tahun**

$2.$ **Variasi musiman sangat besar**: 
  - Produksi tertinggi di bulan Juli (**~38,79 kWh/hari**)
  - Produksi terendah di bulan Januari (**~15,22 kWh/hari**)
  - Rasio **2,55 kali lipat** antara produksi tertinggi dan terendah.

$3.$ **Variabilitas Musiman**:
  - Coefficient of Variation (CV) energi bulanan: **22,8%**
  - Ini mendukung perlunya sistem penyimpanan energi (BESS) untuk menjamin keandalan sepanjang tahun.

$4.$ **Penalti Efisiensi Termal**:
  - Contoh bulan Oktober: $G(t)$ rata-rata 647 W/m², $T_{\text{avg}} = 29,6^\circ$C → suhu panel $T_p = 49,01^\circ$C
  - Penalti efisiensi rata-rata: **9,6%** terhadap kondisi STC (25°C).

$5.$ **Diagram Alur Pemodelan (Gambar 1)**:
  - Flowchart lengkap proses pemodelan produksi PV harian untuk satu hari pada tahun ke-$y$, yang mencakup:
    - Input data meteorologi ($SS$, $T_{\text{avg}}$, dll.)
    - Perhitungan irradiansi $G(t)$
    - Koreksi suhu panel $T_p(t)$ dan efisiensi $\eta_{T_p}$
    - Perhitungan daya $P(t)$ dan energi $E(t)$
    - Integrasi faktor degradasi $D(y)$
  - Diagram ini menggambarkan alur komputasi terintegrasi dari data mentah hingga output produksi harian.

![alt text](<../list-gambar/Gambar 3.1. Diagram Alur Pemodelan Produksi Energi PV Harian .png>)

---

## 2. Hasil Simulasi Produksi PV & Climate Penalty (Bab III.3.2 – hal. 16–17 & Gambar 2)

$1.$ **Fenomena Climate Penalty** terbukti secara empiris melalui simulasi deret waktu 50 tahun (2024–2074):
  - Penurunan daya keluaran PV secara **linear sebesar -0.04 kW/tahun**.
  - Penalti efisiensi termal konstan **~10%**.
  - Tren produksi rata-rata: dari **14.5 kW** (awal simulasi) menjadi **sekitar 12.5 kW** (akhir simulasi) → penurunan total **~14%** dari kapasitas awal.

$2.$ **Volatilitas produksi harian**: standar deviasi **10–25 kW** akibat haze, cloud cover, dan suhu ekstrem.

$3.$ **Capacity Factor (CF)** historis vs proyeksi:
  - Historis (data BMKG Tardamu 2025): **0.13 – 0.33**
  - Kondisi Low (Markov Chain): **$CF_L = 0.1342$** (probabilitas $p_L = 0.1053$)
  - Kondisi Normal: **$CF_N = 0.3333$** (probabilitas $p_N = 0.8947$)

$4.$ Produksi tahunan referensi 1 kWp: **11.811 kWh/tahun** (sebelum degradasi & iklim).

![alt text](<../list-gambar/Gambar 3.2. Simulasi Climate Change Impact on PV Production.png>)

---

## 3. Hasil Simulasi Optimisasi Kapasitas (SDP/MDP – Bab III.3.3, hal. 17–19)

$1.$ **Model two-layered SDP** (50 tahun horizon) menghasilkan strategi optimal: **Diversified Portfolio** (UPV + BESS masif + Firm Capacity).

$2.$ **Metrik utama yang dicapai**:
  - **Expected Energy Not Served (EENS)** → **mendekati nol** (jaminan pasokan 24 jam).
  - **Levelized Cost of Energy (LCOE)** → ditekan seminimal mungkin.
  - Total discounted cost → paling rendah dibandingkan 4 strategi lain.

$3.$ **Perbandingan 4 strategi** (tabel simulasi di dokumen):

| Strategi | Fokus Investasi Awal | Total Cost Jangka Panjang | EENS | Ketahanan Low Solar | Prioritas |
|----------|----------------------|---------------------------|------|---------------------|-----------|
| Rapid Distributed PV | DPV tinggi | Sedang | Sedang | Rendah | Jangka pendek |
| Utility-scale PV | UPV tinggi | Rendah | Sedang | Rendah | Jangka sedang |
| Storage-led | BESS masif | Tinggi awal | Rendah | Tinggi | Jangka panjang |
| **Diversified Portfolio** | UPV + BESS + Firm | **Terendah** | **Mendekati 0** | **Tertinggi** | **Optimal** |

---

## 4. Hasil Simulasi Penentuan Lokasi (Sequential Hard Filtering – Bab III.3.5, hal. 19–20 & Gambar 3)

$1.$ Penerapan 6 filter GIS (radiasi, slope $<$ 15°, jarak grid $<$ 3 km, lahan terbuka, dll.) menghasilkan:
  - **±265 ha lahan potensial** di radius 3 km dari PLN ULP Sabu Raijua.
  - Kapasitas terpasang potensial: **~265 MWp**.

$2.$ Terdapat **tiga lokasi kandidat optimal** yang memenuhi semua kriteria teknis, lingkungan, dan sosial.

---

## 5. Hasil Simulasi Keadilan Energi (Bab III.3.6, hal. 21)

$1.$ **Indeks Gini Energi**:
  - Strategi PV terdistribusi saja → Gini lebih tinggi (kurang adil).
  - **Portofolio campuran (UPV + BESS)** → menurunkan indeks Gini secara signifikan → distribusi manfaat lebih merata antar kelompok pendapatan.

$2.$ Rekomendasi **Solar-as-a-Service** lebih efektif untuk masyarakat berpenghasilan rendah di kepulauan.

---

## 6. Hasil Simulasi Keseluruhan (Ringkasan & Bab IV, hal. 3, 7, 9, 22)

$1.$ Simulasi stokastik Monte Carlo + Markov Chain (50 tahun) mengonfirmasi:
  - Climate Penalty adalah **paradoks fundamental** yang harus diantisipasi.
  - Tanpa intervensi (oversizing + BESS), volatilitas dan EENS akan meningkat drastis.
  - Dengan strategi optimal, sistem mencapai **keandalan tinggi + biaya kompetitif + keadilan energi**.

---

## 📘 Catatan Tambahan

- Semua hasil di atas berasal dari **simulasi stokastik 50 tahun (2024–2074)** menggunakan data BMKG Tardamu 2025 + proyeksi IPCC AR6.
- Gambar kunci: Gambar 1 (Diagram Alur Pemodelan), Gambar 2 (Simulasi Climate Change Impact), Gambar 3 (Peta Lokasi Potensial), dan tabel perbandingan strategi.
- Tidak ada hasil numerik tambahan yang disebutkan di luar poin-poin di atas.