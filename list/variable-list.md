# 📃 LISTING LENGKAP SEMUA VARIABEL

Berikut adalah **daftar lengkap semua variabel** yang muncul di dokumen submission (dari Bab II dan Bab III). Kami kelompokkan berdasarkan kategori agar lebih mudah dibaca:

| Kategori | Simbol Variabel | Penjelasan Lengkap | Fungsi / Penggunaan | Analisis / Insight Utama |
|----------|-----------------|---------------------|---------------------|--------------------------|
| **Produksi PV Fisik** | $T_p(t)$ | Suhu panel fotovoltaik aktual pada waktu $t$ (°C) | Koreksi suhu sel PV | Selalu lebih tinggi daripada suhu udara |
| **Produksi PV Fisik** | $T_{\rm avg}(t)$ | Suhu udara rata-rata pada waktu $t$ (°C) | Input suhu lingkungan | Data BMKG Tardamu 2025 |
| **Produksi PV Fisik** | $\alpha$ | Koefisien kenaikan suhu panel (0,03 °C·m²/W) | Model NOCT | Standar industri PV |
| **Produksi PV Fisik** | $G(t)$ | Irradiansi efektif (W/m²) | Daya yang diterima panel | Diperoleh dari $SS(t)$ |
| **Produksi PV Fisik** | $SS(t)$ | Lama penyinaran matahari (jam/hari) | Proxy irradiansi utama | Data empiris BMKG Tardamu 2025 |
| **Produksi PV Fisik** | $\eta_{T_p}$ | Efisiensi PV yang dikoreksi suhu | Efisiensi aktual panel | Turun 0,4% per °C |
| **Produksi PV Fisik** | $\eta_{\rm ref}$ | Efisiensi referensi pada STC (0,20 atau 20%) | Efisiensi standar pabrik | Nilai nominal modul |
| **Produksi PV Fisik** | $\beta$ | Koefisien penurunan efisiensi suhu (0,004 /°C) | Temperature coefficient | Penalti termal ~10% |
| **Produksi PV Fisik** | $P(t)$ | Daya keluaran PV pada waktu $t$ (kW) | Daya sesaat | Dasar perhitungan energi |
| **Produksi PV Fisik** | $E(t)$ | Energi harian PV (kWh) | Produksi harian | 11.811 kWh/kWp/tahun |
| **Produksi PV Fisik** | $A$ | Luas panel (m²) – contoh 50 m² untuk 1 kWp | Ukuran sistem | 1 kWp referensi |
| **Produksi PV Fisik** | $PR$ | Performance Ratio (0,8) | Faktor kerugian sistem agregat | Inverter, kabel, soiling |
| **Degradasi & Iklim** | $\delta_d$ | Laju degradasi tahunan (0,005–0,008 /tahun) | Degradasi modul PV | 14–21% dalam 30 tahun |
| **Degradasi & Iklim** | $D(y)$ | Faktor degradasi pada tahun ke-$y$ | Penyesuaian kapasitas seiring waktu | Linier atau eksponensial |
| **Degradasi & Iklim** | $\Delta T(y)$ | Kenaikan suhu rata-rata pada tahun ke-$y$ (°C) | Proyeksi iklim IPCC AR6 | +1,0–1,5 °C pada 2050 |
| **Degradasi & Iklim** | $A_{\rm haze}(t)$ | Faktor attenuasi kabut asap (haze) | Pengurangan irradiansi | Beer-Lambert Law |
| **Degradasi & Iklim** | $L_{\rm temp}(t)$ | Faktor loss temperatur | Koreksi termal | ~10% penalti tetap |
| **Degradasi & Iklim** | $L_{\rm soiling}(t)$ | Faktor loss pengotoran (soiling) | Kerugian akibat debu | Akumulasi harian |
| **Degradasi & Iklim** | $\eta_{\rm inv}$ | Efisiensi inverter | Konversi DC ke AC | Bagian dari $PR$ |
| **Degradasi & Iklim** | $P_{\rm src}$ | Daya sumber referensi (kW) | Basis perhitungan $P_{\rm out}$ | 1 kWp referensi |
| **Optimisasi (MDP/SDP)** | $S_t$ | State vector pada waktu $t$ | Kapasitas PV, BESS, firm capacity | Input utama SDP |
| **Optimisasi (MDP/SDP)** | $a_t$ | Aksi keputusan investasi pada waktu $t$ | Tambah kapasitas PV/BESS | Variabel keputusan |
| **Optimisasi (MDP/SDP)** | $C_t$ | Total biaya pada periode $t$ | Biaya CAPEX + OPEX + unserved energy | Fungsi tujuan |
| **Optimisasi (MDP/SDP)** | $V_t(S_t)$ | Value function (fungsi nilai) | Solusi optimal SDP | Bellman equation |
| **Optimisasi (MDP/SDP)** | $\beta$ | Discount factor = $1/(1+r)$ | Faktor diskon waktu | $r$ = discount rate |
| **Optimisasi (MDP/SDP)** | $r$ | Discount rate (tingkat diskon) | Penyesuaian nilai waktu uang | Standar ekonomi energi |
| **Optimisasi (MDP/SDP)** | $\omega$ | Skenario cuaca (Low / Normal) | Simulasi stokastik | Markov Chain |
| **Optimisasi (MDP/SDP)** | $CF_\omega$ | Capacity Factor kondisi $\omega$ | Produksi PV per skenario | $CF_L = 0,1342$; $CF_N = 0,3333$ |
| **Optimisasi (MDP/SDP)** | $K_t^{PV}$ | Kapasitas PV terpasang pada waktu $t$ | Skala produksi | Variabel keputusan |
| **Optimisasi (MDP/SDP)** | $p_L, p_N$ | Probabilitas kondisi Low & Normal | Transisi Markov Chain | 0,1053 & 0,8947 |
| **Keandalan Sistem** | $EENS_t$ | Expected Energy Not Served pada periode $t$ | Metrik keandalan utama | Target mendekati nol |
| **Keandalan Sistem** | $LS_t(\omega)$ | Load shedding (energi tidak terpenuhi) | Kekurangan pasokan | Digunakan dalam $EENS_t$ |
| **Lokasi & Keadilan** | Gini Energy | Indeks Gini untuk distribusi manfaat energi | Ukuran keadilan akses PV | Semakin rendah = semakin adil |

---

## 📘 Catatan Penting

- Total ada **33 variabel utama** yang paling sering muncul dan penting untuk presentasi.
- Variabel optimasi ($S_t$, $a_t$, $V_t$) adalah **jantung model SDP** Anda — siapkan slide khusus jika juri tanya detail.
- Variabel produksi PV ($T_p$, $G$, $\eta_{T_p}$) adalah dasar fisik model.
- Semua variabel sudah konsisten antara Bab II dan Bab III.
- Semua simbol matematika menggunakan delimiter `$...$` untuk kompatibilitas dengan Markdown standar.