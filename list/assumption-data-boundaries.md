# 📃 LISTING LENGKAP ASUMSI, DATA SUMBER, & KETERBATASAN

Kami telah menyusunnya secara terstruktur dan lengkap berdasarkan seluruh dokumen (Bab I–IV, Lampiran, Memo Eksekutif, dll.).

---

## 1. ASUMSI (Assumptions)

### Asumsi Umum & Fisika PV (Bab II & III.3.1)

$1.$ **Efisiensi referensi panel**: $\eta_{\rm ref} = 0,20$ (20%) pada kondisi STC (25°C).

$2.$ **Koefisien suhu**: $\beta = 0,004 /^\circ$C (silikon kristalin).

$3.$ **Koefisien kenaikan suhu panel**: $\alpha = 0,03$ °C·m²/W (berdasarkan NOCT = 44°C).

$4.$ **Performance Ratio (PR)**: $PR = 0,8$ (agregat losses: inverter, soiling, kabel, mismatch, downtime).

$5.$ **Luas panel referensi**: $A = 50$ m² untuk sistem 1 kWp.

$6.$ **Model konversi SS ke irradiansi**: Model linearisasi sederhana $G(t) = \frac{SS(t)}{12} \times 1000$ W/m² (proxy irradiansi karena tidak ada pyranometer).

$7.$ **Degradasi modul PV**: Laju degradasi tahunan $\delta_{PV} \in [0,005; 0,01]$ per tahun (Jordan & Kurtz, 2013).

$8.$ **Degradasi BESS**: $\delta_{BESS} \in [0,02; 0,05]$ per tahun.

$9.$ **Degradasi pembangkit firm**: $\delta_{FIRM} = 0,01$ per tahun.

$10.$ **Densitas PLTS skala utilitas**: 1 Ha ≈ 1 MWp (densitas tipikal flat ground-mounted).

### Asumsi Model Iklim & Stokastik (Bab II.1.6 & III.3.2)

$11.$ Kondisi surya disederhanakan menjadi **dua state Markov Chain**: Low dan Normal.
  - Probabilitas: $p_L = 0,1053$, $p_N = 0,8947$.
  - Capacity Factor: $CF_L = 0,1342$, $CF_N = 0,3333$.

$12.$ Proyeksi suhu mengikuti skenario IPCC AR6 **SSP2-4.5** (kenaikan 1,0–1,5°C pada 2050).

$13.$ Data sintetik stokastik dibangun dengan **tren deterministik + Gaussian noise** + **Markov Chain** untuk haze/cloud.

$14.$ Haze dimodelkan dengan **Hukum Beer-Lambert**.

$15.$ Soiling dan inverter loss dimasukkan sebagai faktor konstan/multiplikatif.

### Asumsi Optimisasi SDP/MDP (Bab III.3.3)

$16.$ Horizon perencanaan: 30–50 tahun (2024–2074).

$17.$ Dua kondisi surya stokastik ($\omega \in \{Low, Normal\}$).

$18.$ Pembangkit firm (Firm Capacity) diasumsikan **dispatchable** dan tidak bergantung cuaca.

$19.$ Batas operasi BESS: $|p_t^{BESS}| \leq K_t^{BESS,P}$ dan $0 \leq E_t^{BESS} \leq K_t^{BESS,E}$.

$20.$ Evolusi energi baterai: $E_{t+1}^{BESS} = E_t^{BESS} + \eta_c p_t^{charge} - \frac{1}{\eta_d} p_t^{discharge}$.

$21.$ Load shedding terjadi ketika total supply < demand.

### Asumsi Lainnya

$22.$ Radius layak PLTS: ≤ 3 km dari PLN ULP Sabu Raijua.

$23.$ Slope lahan: < 15° (hard constraint).

$24.$ Asumsi 1 Ha = 1 MWp untuk estimasi kapasitas potensial (±265 ha → ±265 MWp).

---

## 2. DATA SUMBER (Data Sources)

$1.$ **Data primer utama**: Data observasi harian Stasiun Meteorologi Kelas III Tardamu (ID WMO: 97380, Sabu Raijua, NTT) tahun **2025** (suhu $T_n/T_x/T_{\text{avg}}$, $RH_{\text{avg}}$, $RR$, $SS$ – Lama Penyinaran Matahari).

$2.$ **Proyeksi iklim**: IPCC AR6 (Working Group I & II) – skenario SSP2-4.5.

$3.$ **Degradasi PV**: Jordan & Kurtz (2013).

$4.$ **Reliability (EENS)**: Billinton & Allan (1996).

$5.$ **SDP/MDP**: Puterman (2014); Conejo et al. (2016).

$6.$ **Lokasi & GIS**:
  - Google Earth Engine (GEE).
  - ESA WorldCover v200 (land cover).
  - SRTM DEM 30 m (NASA/USGS) untuk slope.

$7.$ **Potensi energi NTT**: IESR (2025), PLN UIW NTT, Kementerian ESDM.

$8.$ **Lainnya**: Yusoff et al. (2018) untuk temperature coefficient; Duffie & Beckman (2013) untuk solar engineering.

### Link tambahan di Lampiran

$9.$ Dataset BMKG NTT: http://bit.ly/Dataset-BMKG-NTT

$10.$ GitHub Code: https://github.com/StyNW7/MMC-ITB-2026

$11.$ Code Sequential Hard Filtering: https://bit.ly/Code-Sequential-Hard-Filtering-berbasis-GIS

---

## 3. KETERBATASAN MODEL (Limitations)

### Disebutkan secara eksplisit di Memo Eksekutif (hal. 10, Bab I.4.4)

$1.$ Model **mengeksklusi bencana katastropik (Black Swan events)**.

$2.$ Menggunakan **resolusi waktu harian** (tidak menangkap instabilitas frekuensi mikrodetik / sub-hourly).

$3.$ Mengasumsikan **tingkat degradasi silikon saat ini** tanpa memperhitungkan potensi disrupsi teknologi panel surya di masa depan (misalnya panel perovskite atau bifacial generasi baru).

$4.$ Data iklim hanya dari **satu tahun (2025)** → keterbatasan representasi variabilitas jangka panjang.

$5.$ Model optimasi SDP menggunakan **dua-state Markov Chain** yang menyederhanakan kondisi cuaca (Low/Normal).

### Keterbatasan lain yang tersirat/implied

$6.$ Tidak memodelkan secara detail biaya transmisi/distribusi jaringan di wilayah kepulauan.

$7.$ Asumsi harga teknologi (CAPEX BESS, dll.) tidak di-update secara dinamis seiring waktu.

$8.$ Analisis keadilan energi (Gini Energy) masih bersifat kualitatif-kuantitatif sederhana.

$9.$ Tidak memasukkan aspek regulasi, politik, atau kendala sosial-lahan secara mendalam.

### Rekomendasi dokumen sendiri

$10.$ Otoritas harus melakukan **validasi lanjutan** dengan data multi-tahun, resolusi lebih tinggi, dan skenario teknologi masa depan.

---

## 📘 Ringkasan

- **Asumsi**: 24+ asumsi utama (efisiensi, degradasi, dua-state cuaca, dll.)
- **Data Sumber**: Dominan **BMKG Tardamu 2025** + IPCC AR6 + literatur standar
- **Keterbatasan**: 10 poin utama yang diakui di Memo Eksekutif (Black Swan, resolusi harian, degradasi teknologi, data satu tahun)