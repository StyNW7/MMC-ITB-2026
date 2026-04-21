# 📃 LISTING LENGKAP SEMUA MATHEMATICAL SOLUTION BAB 3

Berikut adalah **daftar lengkap dan terstruktur** semua solusi matematika yang kami buat pada bab 3:

---

### **MODEL / RUMUS 1 (Full Production Model P_out(t))**

**Lokasi:** Bab III, subbagian 3.2.2 (Perubahan Iklim dan Kejadian Ekstrem), hal. 16

## $P_{\rm out}(t) = P_{\rm src} \times \left( \frac{G_{\rm actual}(t) \times A_{\rm haze}(t)}{1000} \right) \times L_{\rm temp}(t) \times (1 - L_{\rm soiling}(t)) \times \eta_{\rm inv}$

**Komponen atau faktor:** Irradiansi aktual, attenuasi kabut asap (haze), loss temperatur, loss pengotoran, efisiensi inverter.

**Asumsi yang digunakan:** Haze di-modelkan dengan faktor attenuasi Beer-Lambert; soiling akumulatif harian; inverter loss konstan.

**Dataset atau sumber:** Data BMKG Tardamu 2025 + IPCC AR6 untuk proyeksi haze & cloud cover + model optik atmosfer (Beer-Lambert Law).

**Variabel:**  
- $P_{\rm src}$: daya sumber referensi (kW)  
- $G_{\rm actual}(t)$: irradiansi aktual (W/m²)  
- $A_{\rm haze}(t)$: faktor attenuasi haze  
- $L_{\rm temp}(t)$: loss temperatur  
- $L_{\rm soiling}(t)$: loss pengotoran  
- $\eta_{\rm inv}$: efisiensi inverter

**Hasil analisis:** Simulasi 50 tahun menghasilkan volatilitas produksi harian yang ekstrem (standar deviasi 10–25 kW).

**Insight:** **Climate Penalty** terbukti nyata; penalti termal konstan ~10% dan lonjakan intermitensi akibat haze membuat produksi PV jauh lebih tidak stabil daripada prediksi historis.

---

### **MODEL / RUMUS 2 (Two-State Markov Chain untuk Iklim)**

**Lokasi:** Bab III, subbagian 3.2 (Perubahan Iklim), hal. 15–16

## $p_L = 0{,}1053, \quad p_N = 0{,}8947$

dengan  

## $CF_L = 0{,}1342, \quad CF_N = 0{,}3333$

**Komponen atau faktor:** Dua kondisi surya (Low & Normal).

**Asumsi yang digunakan:** Kondisi cuaca mengikuti rantai Markov sederhana dua state; probabilitas di-estimasi dari data historis BMKG 2025.

**Dataset atau sumber:** Data empiris Lama Penyinaran Matahari (SS) Stasiun BMKG Tardamu tahun 2025.

**Variabel:**  
- $p_L$: probabilitas kondisi Low  
- $p_N$: probabilitas kondisi Normal  
- $CF_L$, $CF_N$: Capacity Factor masing-masing kondisi

**Hasil analisis:** Digunakan untuk menghasilkan skenario stokastik dalam simulasi 50 tahun.

**Insight:** Variabilitas intermitensi jauh lebih tinggi di masa depan karena perubahan pola tutupan awan dan haze.

---

### **MODEL / RUMUS 3 (Bellman Equation – SDP Optimisasi Kapasitas)**

**Lokasi:** Bab III, subbagian 3.3.2 (Perencanaan Kapasitas & Optimisasi), hal. 17–18

## $V_t(S_t) = \min_{a_t} \Bigl[ \mathbb{E}[C_t(S_t, a_t)] + \beta \mathbb{E}[V_{t+1}(S_{t+1})] \Bigr]$

dengan  

## $\beta = \frac{1}{1+r}$

**Komponen atau faktor:** Fungsi nilai (value function), biaya periode, faktor diskon, state transisi.

**Asumsi yang digunakan:** Two-layered SDP dengan dua kondisi surya; horizon 30–50 tahun; discount rate konstan.

**Dataset atau sumber:** Puterman (2014) – Stochastic Dynamic Programming; diterapkan pada data BMKG + estimasi biaya IESR/PLN.

**Variabel:**  
- $V_t(S_t)$: value function pada waktu $t$  
- $S_t$: state vector (kapasitas PV terdistribusi, utilitas, BESS, firm capacity)  
- $a_t$: aksi keputusan investasi  
- $C_t$: total biaya periode $t$  
- $\beta$: discount factor  
- $r$: discount rate

**Hasil analisis:** Model two-layered SDP menghasilkan lintasan investasi optimal.

**Insight:** Strategi **Diversified Portfolio** (UPV + BESS masif + oversizing 15–20%) adalah solusi optimal yang meminimalkan biaya siklus hidup dan EENS.

---

### **MODEL / RUMUS 4 (EENS – Expected Energy Not Served)**

**Lokasi:** Bab III, subbagian 3.3 (Perencanaan Kapasitas), hal. 18

## $EENS_t = \mathbb{E}_\omega [LS_t(\omega)]$

**Komponen atau faktor:** Ekspektasi load shedding di seluruh skenario cuaca $\omega$.

**Asumsi yang digunakan:** Load shedding terjadi ketika total supply < demand pada setiap periode.

**Dataset atau sumber:** Billinton & Allan (1996) – reliability engineering; diterapkan pada simulasi stokastik SDP.

**Variabel:**  
- $EENS_t$: Expected Energy Not Served pada periode $t$  
- $LS_t(\omega)$: load shedding pada skenario $\omega$

**Hasil analisis:** Metrik ini menjadi bagian dari fungsi tujuan SDP.

**Insight:** Strategi campuran mampu menekan EENS mendekati nol, menjamin keandalan pasokan 24 jam.

---

### **MODEL / RUMUS 5 (Sequential Hard Filtering untuk Penentuan Lokasi)**

**Lokasi:** Bab III, subbagian 3.5 (Penentuan Lokasi), hal. 19–20

## $\text{Sequential Hard Filtering (Algoritma GIS multi-kriteria)}$

**Langkah-langkah filter:**  
1. Filter radiasi $>$ threshold  
2. Slope $<$ 15°  
3. Jarak ke grid $<$ radius tertentu  
4. Lahan terbuka (bukan hutan lindung)

**Komponen atau faktor:** Kualitas sumber daya surya, ketersediaan lahan, kedekatan jaringan, kendala lingkungan.

**Asumsi yang digunakan:** Radius 3 km dari PLN ULP Sabu Raijua; data satelit/Google Earth Engine.

**Dataset atau sumber:** Data GIS dari Google Earth Engine + peta lahan KLHK.

**Variabel:** Tidak ada rumus tunggal, melainkan urutan filter spasial.

**Hasil analisis:** Menghasilkan ±265 ha lahan potensial (~265 MWp).

**Insight:** Tiga lokasi kandidat optimal yang memenuhi semua kriteria teknis dan sosial.

---

### **MODEL / RUMUS 6 (Indeks Gini Energi – Keadilan)**

**Lokasi:** Bab III, subbagian 3.6 (Keadilan dan Akses Energi), hal. 21

## $\text{Indeks Gini Energi (variasi dari Gini coefficient standar)}$

**Komponen atau faktor:** Distribusi akses PV antar kelompok pendapatan.

**Asumsi yang digunakan:** Data pendapatan rumah tangga di NTT + skenario penetrasi PV atap vs utilitas.

**Dataset atau sumber:** Data BPS NTT + model distribusi manfaat energi.

**Variabel:** $\text{Gini Energy}$ (nilai antara 0–1, semakin rendah = semakin adil)

**Hasil analisis:** Strategi UPV + BESS memberikan distribusi manfaat yang lebih merata daripada hanya PV terdistribusi.

**Insight:** Portofolio campuran menurunkan indeks Gini Energi secara signifikan, memastikan keadilan akses di wilayah kepulauan terisolasi.

---

## 📘 Catatan Akhir Bab 3

- Bab 3 lebih banyak **menerapkan** dan **menyelesaikan** model dari Bab II daripada menciptakan rumus baru.
- Inti solusi adalah **integrasi $P_{\rm out}(t)$ + Markov Chain + SDP + Sequential Hard Filtering + Gini Energy**.
- Tidak ada rumus matematika tambahan yang signifikan di subbagian 3.4 (Strategi Jangka Pendek & Panjang) selain perbandingan 4 strategi menggunakan metrik dari SDP.