# ✅ LISTING LENGKAP SEMUA MATHEMATICAL FORMULA DALAM DOKUMEN SUBMISSION

## RUMUS 1

**Lokasi:** Bab II, subbab 2.1.1 (hal. 11)  

**Rumus:**  
$$
T_p(t) = T_{\text{avg}}(t) + \alpha \times G(t)
$$

**Asumsi:** NOCT = 44°C, α = 0,03 °C·m²/W (panel standar)  

**Sumber:** Model kesetimbangan energi NOCT (Nominal Operating Cell Temperature), standar industri PV  

**Variabel:**  
- $T_p(t)$: Suhu panel aktual (°C)  
- $T_{\text{avg}}(t)$: Suhu udara rata-rata (°C)  
- $\alpha$: Koefisien kenaikan suhu panel  
- $G(t)$: Irradiansi efektif (W/m²)  

**Hasil analisis:** Suhu panel selalu lebih tinggi daripada suhu udara karena radiasi matahari.  

**Insight:** Setiap kenaikan irradiansi meningkatkan suhu panel, yang langsung memengaruhi efisiensi (efek termal negatif).

---

## RUMUS 2

**Lokasi:** Bab II, subbab 2.1.1 (hal. 11)  

**Rumus:**  
$$
\eta_{T_p} = \eta_{\text{ref}} \times [1 - \beta (T_p - 25)] \quad \text{(2.2)}
$$

**Asumsi:** $\eta_{\text{ref}} = 0{,}20$, $\beta = 0{,}004/^\circ$C (silikon kristalin)  

**Sumber:** Koefisien Temperature Coefficient of Power (TCP) dari literatur Yusoff et al. (2018)  

**Variabel:**  
- $\eta_{T_p}$: Efisiensi efektif pada suhu panel  
- $\eta_{\text{ref}}$: Efisiensi referensi pada STC (25°C)  
- $\beta$: Koefisien penurunan efisiensi per °C  
- $T_p$: Suhu panel (°C)  

**Hasil analisis:** Penurunan efisiensi ≈ 0,4% per °C di atas 25°C.  

**Insight:** Penalti termal konstan ~10% pada kondisi Sabu Raijua (suhu tinggi).

---

## RUMUS 3

**Lokasi:** Bab II, subbab 2.1.2 (hal. 11)  

**Rumus:**  
$$
G(t) = \frac{SS(t)}{12} \times 1000 \quad \text{(2.3)}
$$

**Asumsi:** Model linearisasi foto-periode 12 jam (proxy irradiansi)  

**Sumber:** Pendekatan umum untuk stasiun tanpa pyranometer (BMKG Tardamu)  

**Variabel:**  
- $SS(t)$: Lama penyinaran matahari (jam/hari)  
- $G(t)$: Irradiansi (W/m²)  

**Hasil analisis:** Memberikan estimasi harian yang cukup akurat untuk daerah tropis.  

**Insight:** CF historis 0,13–0,33 dengan SS rata-rata 7,34 jam/hari.

---

## RUMUS 4 & 5

**Lokasi:** Bab II, subbab 2.1.2 (hal. 11)  

**Rumus:**  
$$
P(t) = G(t) \times A \times \eta_{T_p} \times PR \quad \text{(2.4)}
$$  
$$
E(t) = \frac{P(t) \times SS(t)}{1000} \quad \text{(2.5)}
$$

**Asumsi:** $A = 50$ m² (1 kWp), $PR = 0{,}8$ (agregat losses)  

**Sumber:** Standar IEC & IESR (2023) untuk sistem PV tropis  

**Variabel:**  
- $P(t)$: Daya (kW)  
- $E(t)$: Energi harian (kWh)  
- $PR$: Performance Ratio  

**Hasil analisis:** Produksi tahunan 1 kWp ≈ 11.811 kWh.  

**Insight:** Model ini mengintegrasikan variabilitas radiasi, suhu, dan losses sistem.

---

## RUMUS 6

**Lokasi:** Bab II, subbab 2.1.3 (hal. 12)  

**Rumus:**  
$$
D(y) = (1 - \delta_d)^y \quad \text{atau} \quad e^{-\lambda y} \quad \text{(2.6)}
$$

**Asumsi:** $\delta_d = 0{,}005{-}0{,}008$/tahun  

**Sumber:** Jordan & Kurtz (2013) – degradasi PV  

**Variabel:**  
- $D(y)$: Faktor degradasi tahun ke-$y$  

**Hasil analisis:** Degradasi 14–21% dalam 30 tahun.  

**Insight:** Degradasi linier/eksponensial harus dihitung setiap tahun dalam SDP.

---

## RUMUS 7

**Lokasi:** Bab II, subbab 2.1.3 (hal. 12)  

**Rumus:**  
$$
T_{\text{avg}}(t,y) = T_{\text{avg hist}}(t) + \Delta T(y) \quad \text{(2.7)}
$$

**Asumsi:** $\Delta T(y) = +1{,}0{-}1{,}5^\circ$C pada 2050 (SSP2-4.5)  

**Sumber:** IPCC AR6 + tren BMKG  

**Variabel:**  
- $\Delta T(y)$: Kenaikan suhu proyeksi  

**Hasil analisis:** Climate Penalty linear -0,04 kW/tahun.  

**Insight:** Fenomena **Climate Penalty** terbukti secara empiris.

---

## RUMUS 8–10

**Lokasi:** Bab II, 2.1.7–2.1.8 & Bab III, 3.3.2 (hal. 12–13, 17–18)  

**Rumus utama:**  

Objective:  
$$
\min \sum_{t=1}^T \frac{1}{(1+r)^t} C_t \quad \text{(2.8)}
$$

State transition:  
$$
S_{t+1} = f(S_t, a_t) \quad \text{(2.9)}
$$

Bellman equation:  
$$
V_t(S_t) = \min_{a_t} \left[ \mathbb{E}[C_t(S_t,a_t)] + \beta \mathbb{E}[V_{t+1}(S_{t+1})] \right] \quad \text{(2.10)}
$$  
dengan $\beta = \frac{1}{1+r}$

**Asumsi:** Dua state surya (Low/Normal) dengan probabilitas $p_L = 0{,}1053$, $p_N = 0{,}8947$; CF_Low = 0,1342, CF_Normal = 0,3333  

**Sumber:** Puterman (2014) – Markov Decision Process & Stochastic Dynamic Programming  

**Variabel:**  
- $S_t$: state kapasitas  
- $a_t$: keputusan investasi  
- $C_t$: biaya periode $t$  

**Hasil analisis:** Model two-layered SDP.  

**Insight:** Portofolio campuran (UPV + BESS + Firm) adalah solusi optimal.

---

## RUMUS 11

**Lokasi:** Bab II, 2.1.9 (hal. 13)  

**Rumus:**  
$$
g_t^{PV}(\omega) = CF_\omega \cdot K_t^{PV} \quad \text{(2.11)}
$$

**Asumsi:** Dua kondisi surya (Low/Normal)  

**Sumber:** Duffie & Beckman (2013)  

**Variabel:**  
- $CF_\omega$: Capacity Factor kondisi $\omega$  

**Hasil analisis:** Digunakan dalam energy balance SDP.  

**Insight:** Menyederhanakan variabilitas tanpa simulasi hourly.

---

## RUMUS 12

**Lokasi:** Bab II, 2.1.10 (hal. 13)  

**Rumus:**  
$$
EENS_t = \mathbb{E}_\omega [LS_t(\omega)] \quad \text{(2.12)}
$$

**Asumsi:** Load shedding $LS_t$ ketika supply < demand  

**Sumber:** Billinton & Allan (1996)  

**Variabel:**  
- $EENS_t$: Expected Energy Not Served  

**Hasil analisis:** Metrik keandalan utama dalam SDP.  

**Insight:** Strategi yang baik menekan EENS mendekati nol.

---

## RUMUS TAMBAHAN (Bab III – 1B)

**Lokasi:** Bab III, 3.2.2 (hal. 16)  

**Rumus:**  
$$
P_{\text{out}}(t) = P_{\text{src}} \times \left( \frac{G_{\text{actual}}(t) \times A_{\text{haze}}(t)}{1000} \right) \times L_{\text{temp}}(t) \times (1 - L_{\text{soiling}}(t)) \times \eta_{\text{inv}}
$$

**Asumsi:** Termasuk haze (Beer-Lambert), cloud cover, soiling  

**Sumber:** Kombinasi model fisik + optik atmosfer  

**Variabel:**  
- $A_{\text{haze}}$: attenuasi haze  
- $L_{\text{temp}}$: loss temperatur  
- dll.  

**Hasil analisis:** Volatilitas 10–25 kW.  

**Insight:** Climate Penalty + ekstrem weather sangat signifikan.

---

## 📘 Catatan Tambahan

- Semua rumus di atas sudah tercakup dan konsisten antar bab.  
- Model inti adalah **integrasi fisika PV + stokastik iklim + SDP optimisasi**.  
- Tidak ada rumus baru yang signifikan di Bab III bagian lokasi/keadilan (lebih ke filtering GIS dan indeks Gini).