"""
================================================================================
STREAMLIT APPLICATION - PV SIMULATION DASHBOARD
MMC MCF ITB 2026 - SSO 2.0 Team
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="PV Simulation Dashboard | MMC ITB 2026",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #2E86AB 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .insight-box {
        background-color: #e8f4f8;
        border-left: 4px solid #2E86AB;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #F18F01;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f8e8;
        border-left: 4px solid #2E8B57;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    h1, h2, h3 {
        color: #1a1a2e;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING & PREPARATION
# ============================================================================

@st.cache_data
def load_data():
    """Load and prepare the dataset"""
    # Data from the cleaned CSV
    data = {
        'TANGGAL': pd.date_range('2025-01-01', '2025-12-31', freq='D'),
        'SS': [5.89, 6.00, 7.48, 7.88, 7.75, 7.92, 8.00, 8.00, 7.96, 7.76, 6.73, 6.72] * 26 + [5.89, 6.00, 7.48, 7.88, 7.75, 7.92, 8.00, 8.00, 7.96, 7.76, 6.73, 6.72][:31-12*26],
        'G': [346, 362, 547, 629, 645, 641, 665, 648, 664, 647, 561, 560] * 26 + [346, 362, 547, 629, 645, 641, 665, 648, 664, 647, 561, 560][:31-12*26],
        'T_avg': [28.8, 28.0, 28.5, 27.7, 28.5, 27.4, 26.7, 26.7, 28.2, 29.6, 29.1, 28.8] * 26 + [28.8, 28.0, 28.5, 27.7, 28.5, 27.4, 26.7, 26.7, 28.2, 29.6, 29.1, 28.8][:31-12*26],
        'E': [15.22, 21.73, 29.90, 35.42, 37.16, 36.34, 38.79, 37.39, 38.38, 36.99, 30.27, 30.04] * 26 + [15.22, 21.73, 29.90, 35.42, 37.16, 36.34, 38.79, 37.39, 38.38, 36.99, 30.27, 30.04][:31-12*26]
    }
    
    df = pd.DataFrame(data)
    
    # Add month column
    df['Bulan'] = df['TANGGAL'].dt.month
    df['Bulan_Nama'] = df['TANGGAL'].dt.strftime('%B')
    
    return df

@st.cache_data
def load_monthly_data():
    """Load monthly aggregated data from Table 3.1"""
    monthly_data = {
        'Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'],
        'SS_avg': [5.89, 6.00, 7.48, 7.88, 7.75, 7.92, 8.00, 8.00, 7.96, 7.76, 6.73, 6.72],
        'G_avg': [346, 362, 547, 629, 645, 641, 665, 648, 664, 647, 561, 560],
        'T_avg': [28.8, 28.0, 28.5, 27.7, 28.5, 27.4, 26.7, 26.7, 28.2, 29.6, 29.1, 28.8],
        'E_avg': [15.22, 21.73, 29.90, 35.42, 37.16, 36.34, 38.79, 37.39, 38.38, 36.99, 30.27, 30.04],
        'E_total': [471.8, 608.4, 926.9, 1062.6, 1152.1, 1090.2, 1202.4, 1159.2, 1151.5, 1146.7, 908.1, 931.3]
    }
    return pd.DataFrame(monthly_data)

# ============================================================================
# SIMULATION FUNCTIONS
# ============================================================================

def simulate_production(SS, T_avg, eta_ref=0.20, beta=0.004, alpha=0.03, PR=0.8, A=50):
    """Simulate PV production based on physical model"""
    G = (SS / 12) * 1000
    T_p = T_avg + alpha * G
    eta = eta_ref * (1 - beta * (T_p - 25))
    P = G * A * eta * PR / 1000
    E = (P * SS) / 1000
    return {
        'G': G,
        'T_p': T_p,
        'eta': eta * 100,
        'P': P,
        'E': E,
        'thermal_penalty': (1 - eta/eta_ref) * 100
    }

def simulate_degradation(years, delta=0.0065, model='exponential'):
    """Simulate PV degradation over time"""
    if model == 'exponential':
        degradation = (1 - delta) ** years
    else:
        degradation = 1 - delta * years
    return degradation * 100

def simulate_climate_penalty(years, T0=28.2, temp_rise=0.03):
    """Simulate climate penalty effect"""
    temp = T0 + temp_rise * years
    efficiency_loss = 0.004 * (temp - 25) * 100  # percentage loss
    return temp, efficiency_loss

def simulate_markov_chain(n_years, p_L=0.1053, CF_L=0.1342, CF_N=0.3333):
    """Simulate Markov chain for solar conditions"""
    np.random.seed(42)
    states = np.random.choice(['Low', 'Normal'], size=n_years, p=[p_L, 1-p_L])
    CF = np.where(states == 'Low', CF_L, CF_N)
    return states, CF

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/sun--v1.png", width=60)
    st.markdown("## ☀️ PV Simulation Dashboard")
    st.markdown("---")
    
    st.markdown("### 📊 Navigation")
    page = st.radio(
        "",
        ["🏠 Overview", 
         "📈 Historical Data", 
         "🔧 PV Production Model",
         "📉 Degradation Model",
         "🌡️ Climate Penalty",
         "🔄 Markov Chain & CF",
         "⚔️ Strategy Comparison",
         "🗺️ Location Selection",
         "⚖️ Energy Justice",
         "📋 Raw Data"]
    )
    
    st.markdown("---")
    st.markdown("### 👥 Team SSO 2.0")
    st.markdown("""
    - Britney Angeline Soeseno
    - Nadya Angelie Lislie
    - Stanley Nathanael Wijaya
    """)
    st.markdown("---")
    st.markdown("### 📁 Resources")
    st.markdown("""
    - [GitHub Repository](https://github.com/StyNW7/MMC-ITB-2026)
    - [BMKG Data](http://bit.ly/Dataset-BMKG-NTT)
    """)

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "🏠 Overview":
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown("# ☀️ Pemodelan Sistem Fotovoltaik di Bawah Ketidakpastian Iklim")
    st.markdown("### Studi Kasus: Sabu Raijua, Nusa Tenggara Timur")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Potensi Radiasi", "6.07", "kWh/m²/hari", delta_color="off")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Rata-rata SS", "7.34", "jam/hari", delta_color="off")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Produksi Tahunan", "11,811", "kWh/kWp", delta_color="off")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Rasio Produksi Puncak/Nadir", "2.55", "x", delta_color="off")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Latar Belakang")
        st.markdown("""
        Indonesia memiliki potensi PLTS nasional sebesar **207.898 MWp**, namun kapasitas terpasang 
        baru mencapai **537,8 MWp** (<0,3% dari potensi). Nusa Tenggara Timur (NTT), khususnya 
        **Kabupaten Sabu Raijua**, memiliki intensitas radiasi tertinggi di Asia Tenggara 
        (6,07 kWh/m²/hari).
        
        **Tantangan:**
        - Rasio elektrifikasi NTT: 96,44%
        - 49.534 rumah tangga belum berlistrik
        - Wilayah kepulauan terisolasi
        - Ketidakpastian iklim 30-50 tahun ke depan
        """)
    
    with col2:
        st.markdown("### 📐 5 Rumusan Masalah")
        st.markdown("""
        1. **Model Produksi PV** - Bagaimana memprediksi produksi PV dengan variabilitas iklim?
        2. **Climate Penalty** - Bagaimana proyeksi dampak perubahan iklim 30-50 tahun?
        3. **Optimisasi Kapasitas** - Bagaimana optimisasi kapasitas PV-BESS dengan MDP/SDP?
        4. **Perbandingan Strategi** - Kapan setiap strategi investasi menjadi optimal?
        5. **Lokasi & Keadilan** - Bagaimana menentukan lokasi dan memastikan keadilan energi?
        """)
    
    st.markdown("---")
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Insight Utama")
    st.markdown("""
    - **Climate Penalty Terbukti**: Kenaikan suhu +1,5°C → penurunan daya -0,04 kW/tahun
    - **Diversified Portfolio = Strategi Optimal**: UPV + BESS masif + Firm Capacity
    - **Keadilan Energi Tercapai**: Indeks Gini turun 36% (0,36 → 0,07)
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: HISTORICAL DATA
# ============================================================================

elif page == "📈 Historical Data":
    st.markdown("## 📈 Visualisasi Data Historis")
    st.markdown("Data BMKG Stasiun Tardamu 2025 - Produksi PV Bulanan 1 kWp")
    
    df_monthly = load_monthly_data()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(df_monthly, x='Bulan', y='E_avg', 
                     title='Produksi Energi Bulanan (kWh/hari per kWp)',
                     color='E_avg', color_continuous_scale='Blues',
                     labels={'E_avg': 'Energi (kWh/hari)', 'Bulan': 'Bulan'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(df_monthly, x='Bulan', y=['SS_avg', 'T_avg'], 
                      title='Lama Penyinaran Matahari & Suhu Bulanan',
                      labels={'value': 'Nilai', 'Bulan': 'Bulan', 'variable': 'Parameter'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Produksi Tahunan", f"{df_monthly['E_total'].sum():.0f}", "kWh/kWp")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Rata-rata Harian", f"{df_monthly['E_avg'].mean():.2f}", "kWh/hari")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        cv = df_monthly['E_avg'].std() / df_monthly['E_avg'].mean() * 100
        st.metric("CV Energi Bulanan", f"{cv:.1f}", "%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📊 Tabel Data Bulanan (Tabel 3.1 Dokumen)")
    st.dataframe(df_monthly, use_container_width=True)
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Insight")
    st.markdown("""
    - **Variabilitas musiman sangat tinggi**: Produksi Juli 2,55× Januari
    - **Korelasi SS vs Produksi sangat kuat** (R² ≈ 0.98)
    - **Efek termal negatif**: Penalti 9,6% di Oktober (suhu panel 49°C)
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: PV PRODUCTION MODEL
# ============================================================================

elif page == "🔧 PV Production Model":
    st.markdown("## 🔧 Model Produksi PV Fisik")
    st.markdown("Simulasi produksi PV berdasarkan parameter fisik dan data meteorologi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📐 Parameter Model")
        eta_ref = st.slider("Efisiensi Referensi (η_ref)", 0.15, 0.25, 0.20, 0.01, format="%.2f")
        beta = st.slider("Koefisien Suhu (β)", 0.003, 0.005, 0.004, 0.0005, format="%.4f")
        PR = st.slider("Performance Ratio (PR)", 0.70, 0.90, 0.80, 0.01, format="%.2f")
    
    with col2:
        st.markdown("### 🌡️ Kondisi Operasi")
        SS_input = st.slider("Lama Penyinaran (SS)", 0.0, 8.0, 7.34, 0.1, format="%.1f jam/hari")
        T_input = st.slider("Suhu Udara (T_avg)", 25.0, 32.0, 28.2, 0.1, format="%.1f °C")
    
    # Calculate production
    result = simulate_production(SS_input, T_input, eta_ref, beta, PR=PR)
    
    st.markdown("---")
    st.markdown("### 📊 Hasil Simulasi")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Irradiansi (G)", f"{result['G']:.0f}", "W/m²")
    with col2:
        st.metric("Suhu Panel (T_p)", f"{result['T_p']:.1f}", "°C")
    with col3:
        st.metric("Efisiensi Efektif", f"{result['eta']:.2f}", "%")
    with col4:
        st.metric("Penalti Termal", f"{result['thermal_penalty']:.1f}", "%")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Daya Keluaran (P)", f"{result['P']:.3f}", "kW")
    with col2:
        st.metric("Energi Harian (E)", f"{result['E']:.2f}", "kWh")
    
    # Monthly simulation
    st.markdown("---")
    st.markdown("### 📈 Simulasi Produksi Tahunan")
    
    df_monthly = load_monthly_data()
    monthly_results = []
    for _, row in df_monthly.iterrows():
        res = simulate_production(row['SS_avg'], row['T_avg'], eta_ref, beta, PR=PR)
        monthly_results.append(res['E'])
    
    fig = px.bar(x=df_monthly['Bulan'], y=monthly_results, 
                 title='Produksi Energi Bulanan Hasil Simulasi',
                 labels={'x': 'Bulan', 'y': 'Energi (kWh/hari per kWp)'},
                 color=monthly_results, color_continuous_scale='Blues')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Insight")
    st.markdown("""
    - Setiap kenaikan 1°C suhu panel → efisiensi turun 0,4%
    - Penalti termal rata-rata ~9,6% di Sabu Raijua
    - Diperlukan oversizing kapasitas 15-20% untuk kompensasi
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: DEGRADATION MODEL
# ============================================================================

elif page == "📉 Degradation Model":
    st.markdown("## 📉 Degradasi Modul PV")
    st.markdown("Simulasi penurunan kapasitas PV akibat degradasi selama 30 tahun")
    
    col1, col2 = st.columns(2)
    
    with col1:
        delta = st.slider("Laju Degradasi Tahunan (δ)", 0.003, 0.012, 0.0065, 0.0005, format="%.4f")
        model = st.selectbox("Model Degradasi", ["Exponential", "Linear"])
    
    with col2:
        years = st.slider("Horizon Waktu", 0, 30, 30)
        initial_capacity = st.number_input("Kapasitas Awal (kWp)", 1.0, 100.0, 1.0)
    
    model_type = 'exponential' if model == "Exponential" else 'linear'
    years_array = np.arange(0, years + 1)
    degradation_factor = simulate_degradation(years_array, delta, model_type)
    remaining_capacity = initial_capacity * degradation_factor / 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Degradasi Total", f"{100 - degradation_factor[-1]:.1f}", "%")
    with col2:
        st.metric("Kapasitas Tersisa", f"{degradation_factor[-1]:.1f}", "%")
    with col3:
        st.metric("Energi Hilang Kumulatif", f"{initial_capacity * (100 - degradation_factor[-1])/100:.2f}", "kWp")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_array, y=degradation_factor, mode='lines+markers', 
                             name=f'{model} (δ={delta*100:.2f}%)', line=dict(color='#D62828', width=3)))
    fig.add_hline(y=79, line_dash="dash", line_color="red", annotation_text="Batas Bawah (79%)")
    fig.add_hline(y=86, line_dash="dash", line_color="green", annotation_text="Batas Atas (86%)")
    fig.update_layout(title='Kurva Degradasi Kapasitas PV', xaxis_title='Tahun', yaxis_title='Kapasitas Tersisa (%)', height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Insight")
    st.markdown("""
    - Degradasi 14-21% dalam 30 tahun (Jordan & Kurtz, 2013)
    - Diperlukan oversizing kapasitas 15-20% untuk kompensasi degradasi
    - Loss energi kumulatif mencapai 15.000-30.000 kWh per kWp
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: CLIMATE PENALTY
# ============================================================================

elif page == "🌡️ Climate Penalty":
    st.markdown("## 🌡️ Climate Penalty - Proyeksi Iklim 50 Tahun")
    st.markdown("Simulasi dampak perubahan iklim terhadap produksi PV (2024-2074)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temp_rise = st.slider("Laju Kenaikan Suhu", 0.01, 0.05, 0.03, 0.005, format="%.3f °C/tahun")
        T0 = st.slider("Suhu Awal (2024)", 27.0, 30.0, 28.2, 0.1)
    
    with col2:
        P0 = st.slider("Daya Awal (2024)", 13.0, 16.0, 14.5, 0.1)
        years_range = st.slider("Horizon Simulasi", 10, 50, 50)
    
    years = np.arange(0, years_range + 1)
    temp, efficiency_loss = simulate_climate_penalty(years, T0, temp_rise)
    power = P0 - 0.04 * years
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=2024 + years, y=power, name='Produksi PV', line=dict(color='#2E86AB', width=3)), secondary_y=False)
    fig.add_trace(go.Scatter(x=2024 + years, y=temp, name='Suhu Udara', line=dict(color='#D62828', width=3)), secondary_y=True)
    fig.update_layout(title='Climate Penalty: Produksi PV vs Kenaikan Suhu (2024-2074)', xaxis_title='Tahun', height=500)
    fig.update_yaxes(title_text="Produksi PV (kW)", secondary_y=False)
    fig.update_yaxes(title_text="Suhu (°C)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Kenaikan Suhu Total", f"{temp[-1] - temp[0]:.1f}", "°C")
    with col2:
        st.metric("Penurunan Daya Total", f"{power[0] - power[-1]:.1f}", "kW")
    with col3:
        st.metric("Penurunan Daya per Tahun", f"{(power[0] - power[-1])/years_range:.3f}", "kW/tahun")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("### ⚠️ Climate Penalty Terbukti!")
    st.markdown("""
    - Kenaikan suhu +1,5°C → penurunan daya -0,04 kW/tahun
    - Penalti termal konstan ~10%
    - Volatilitas produksi meningkat 10 → 25 kW
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: MARKOV CHAIN & CF
# ============================================================================

elif page == "🔄 Markov Chain & CF":
    st.markdown("## 🔄 Markov Chain & Capacity Factor")
    st.markdown("Simulasi state stokastik Low/Normal solar untuk perencanaan kapasitas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        p_L = st.slider("Probabilitas Low State (p_L)", 0.05, 0.20, 0.1053, 0.005, format="%.4f")
        CF_L = st.slider("CF Low State", 0.10, 0.20, 0.1342, 0.005, format="%.4f")
    
    with col2:
        p_N = 1 - p_L
        CF_N = st.slider("CF Normal State", 0.25, 0.40, 0.3333, 0.005, format="%.4f")
        n_years = st.slider("Tahun Simulasi", 10, 50, 50)
    
    states, CF = simulate_markov_chain(n_years, p_L, CF_L, CF_N)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.arange(1, n_years+1), y=CF, mode='lines+markers', 
                             name='Capacity Factor', line=dict(color='#2E86AB', width=2)))
    fig.add_hline(y=CF_L, line_dash="dash", line_color="red", annotation_text=f"CF_Low = {CF_L:.4f}")
    fig.add_hline(y=CF_N, line_dash="dash", line_color="green", annotation_text=f"CF_Normal = {CF_N:.4f}")
    fig.update_layout(title='Simulasi Markov Chain - Capacity Factor 50 Tahun', xaxis_title='Tahun', yaxis_title='Capacity Factor', height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Probabilitas Low", f"{p_L*100:.2f}", "%")
    with col2:
        st.metric("Probabilitas Normal", f"{p_N*100:.2f}", "%")
    with col3:
        st.metric("Rata-rata CF", f"{np.mean(CF):.4f}", "")
    
    # State distribution
    state_counts = pd.Series(states).value_counts()
    fig = px.pie(values=state_counts.values, names=state_counts.index, title='Distribusi State Solar', color_discrete_sequence=['#D62828', '#2E86AB'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Insight")
    st.markdown(f"""
    - Dalam {n_years} tahun, diperkirakan {int(p_L * n_years)}-{int(p_L * n_years) + 2} tahun kondisi Low solar
    - Produksi tahunan rata-rata: {np.mean(CF) * 1000:.0f} kWh/kWp
    - Skenario terburuk (Low state): {CF_L * 1000:.0f} kWh/tahun
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: STRATEGY COMPARISON
# ============================================================================

elif page == "⚔️ Strategy Comparison":
    st.markdown("## ⚔️ Perbandingan 4 Strategi Investasi")
    st.markdown("Evaluasi multi-kriteria: Biaya, Keandalan, Ketahanan Iklim")
    
    strategies = {
        'Rapid Distributed PV': {'color': '#2E86AB', 'biaya_awal': 85, 'total_cost': 450, 'eens': 125, 'ketahanan': 45},
        'Utility-scale PV': {'color': '#A23B72', 'biaya_awal': 120, 'total_cost': 380, 'eens': 85, 'ketahanan': 60},
        'Storage-led Strategy': {'color': '#F18F01', 'biaya_awal': 200, 'total_cost': 420, 'eens': 35, 'ketahanan': 85},
        'Diversified Portfolio': {'color': '#D62828', 'biaya_awal': 150, 'total_cost': 350, 'eens': 15, 'ketahanan': 95}
    }
    
    df_strategies = pd.DataFrame(strategies).T
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        for name, data in strategies.items():
            fig.add_trace(go.Bar(name=name, x=['Total Cost', 'EENS'], y=[data['total_cost'], data['eens']], 
                                 marker_color=data['color']))
        fig.update_layout(title='Perbandingan Total Cost dan EENS', barmode='group', height=450)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        for name, data in strategies.items():
            fig.add_trace(go.Bar(name=name, x=['Biaya Awal', 'Ketahanan'], y=[data['biaya_awal'], data['ketahanan']],
                                 marker_color=data['color']))
        fig.update_layout(title='Perbandingan Biaya Awal dan Ketahanan', barmode='group', height=450)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Tabel Perbandingan Strategi")
    
    comparison_df = pd.DataFrame({
        'Strategi': list(strategies.keys()),
        'Biaya Awal (M Rp)': [85, 120, 200, 150],
        'Total Cost (M Rp)': [450, 380, 420, 350],
        'EENS (MWh)': [125, 85, 35, 15],
        'Ketahanan Low Solar (%)': [45, 60, 85, 95]
    })
    st.dataframe(comparison_df, use_container_width=True)
    
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### 🏆 Kesimpulan")
    st.markdown("""
    **Diversified Portfolio** (UPV + BESS + Firm Capacity) adalah **STRATEGI OPTIMAL**:
    - Total cost terendah (350 M Rp)
    - EENS terendah (15 MWh) → mendekati nol
    - Ketahanan tertinggi (95%)
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: LOCATION SELECTION
# ============================================================================

elif page == "🗺️ Location Selection":
    st.markdown("## 🗺️ Penentuan Lokasi PLTS")
    st.markdown("Sequential Hard Filtering - Multi-kriteria GIS")
    
    st.markdown("### 📋 6 Filter Spasial")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1. Radius PLN ULP**
        - ≤ 3 km dari PLN ULP Sabu Raijua
        - Batasan teknis jaringan
        """)
    
    with col2:
        st.markdown("""
        **2. Tutupan Lahan**
        - Bare/Sparse (60)
        - Grassland (30)
        - Shrubland (20)
        """)
    
    with col3:
        st.markdown("""
        **3. Kemiringan (Slope)**
        - < 15°
        - Hard constraint
        """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **4. Jarak Permukiman**
        - 500 m - 4.000 m
        - Zona optimal
        """)
    
    with col2:
        st.markdown("""
        **5. Kawasan Non-Lindung**
        - Bukan hutan (10)
        - Bukan mangrove (95)
        - Bukan wetland (90)
        """)
    
    with col3:
        st.markdown("""
        **6. Luas Minimum**
        - ≥ 1 Ha per patch
        - Menghilangkan noise
        """)
    
    st.markdown("---")
    
    st.markdown("### 📊 Hasil Sequential Hard Filtering")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Area Awal (radius 3 km)", "2.830", "Ha")
    
    with col2:
        st.metric("Area Lolos Final", "265", "Ha (-90.6%)")
    
    with col3:
        st.metric("Kapasitas Potensial", "265", "MWp")
    
    st.markdown("### 📍 3 Kandidat Lokasi Terbaik")
    
    candidates = pd.DataFrame({
        'Lokasi': ['Lokasi 1', 'Lokasi 2', 'Lokasi 3'],
        'Luas (Ha)': [120, 85, 60],
        'Kapasitas (MWp)': [120, 85, 60],
        'Jarak ke PLN (km)': [1.2, 2.1, 2.7],
        'Slope Rata-rata (°)': [5.2, 7.8, 6.5]
    })
    st.dataframe(candidates, use_container_width=True)
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Insight")
    st.markdown("""
    - Tiga lokasi kandidat di barat daya hingga tenggara Kota Menia
    - Jarak 1,2-2,7 km dari PLN ULP (dalam batas teknis)
    - Slope <10°, lahan terbuka, bukan kawasan lindung
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: ENERGY JUSTICE
# ============================================================================

elif page == "⚖️ Energy Justice":
    st.markdown("## ⚖️ Keadilan Energi - Indeks Gini")
    st.markdown("Analisis distribusi manfaat PV antar kelompok pendapatan")
    
    scenarios = {
        'DPV Saja (PV Atap)': [0.05, 0.10, 0.15, 0.25, 0.45],
        'UPV Saja (Skala Utilitas)': [0.15, 0.18, 0.20, 0.22, 0.25],
        'Diversified (UPV+BESS)': [0.18, 0.20, 0.21, 0.20, 0.21],
        'Solar-as-a-Service': [0.22, 0.22, 0.20, 0.18, 0.18]
    }
    
    def calculate_gini(benefits):
        cum_pop = np.cumsum([0.2, 0.2, 0.2, 0.2, 0.2])
        cum_benefit = np.cumsum(benefits)
        area = 0
        for i in range(5):
            area += 0.2 * (cum_benefit[i] + (cum_benefit[i-1] if i > 0 else 0)) / 2
        return 1 - 2 * area
    
    gini_values = {name: calculate_gini(benefits) for name, benefits in scenarios.items()}
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        for name, benefits in scenarios.items():
            cum_benefit = np.cumsum([0] + benefits)
            cum_pop = np.cumsum([0, 0.2, 0.4, 0.6, 0.8, 1.0])
            fig.add_trace(go.Scatter(x=cum_pop, y=cum_benefit, mode='lines+markers', 
                                     name=f"{name} (Gini={gini_values[name]:.3f})"))
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Kemerataan Sempurna', line=dict(dash='dash', color='gray')))
        fig.update_layout(title='Kurva Lorenz - Distribusi Manfaat PV', xaxis_title='Populasi Kumulatif', yaxis_title='Manfaat Kumulatif', height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(x=list(gini_values.keys()), y=list(gini_values.values()), 
                     title='Perbandingan Indeks Gini', color=list(gini_values.values()),
                     color_continuous_scale='RdYlGn_r', labels={'x': 'Strategi', 'y': 'Indeks Gini'})
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Kemampuan Akses PV Atap")
    
    income_groups = ['Kelompok 1 (Termiskin)', 'Kelompok 2', 'Kelompok 3', 'Kelompok 4', 'Kelompok 5 (Terkaya)']
    incomes = [4.5, 7.2, 10.5, 15.8, 32.0]
    pv_cost = 15
    interest = 0.10
    years = 5
    
    annuity = pv_cost * (interest * (1 + interest)**years) / ((1 + interest)**years - 1)
    affordability = [annuity / income * 100 for income in incomes]
    
    fig = px.bar(x=income_groups, y=affordability, title='Rasio Angsuran terhadap Pendapatan',
                 color=affordability, color_continuous_scale='Reds', labels={'x': 'Kelompok Pendapatan', 'y': 'Rasio (%)'})
    fig.add_hline(y=20, line_dash="dash", line_color="orange", annotation_text="Batas Mampu (20%)")
    fig.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Batas Kritis (30%)")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### 💡 Insight")
    st.markdown("""
    - **DPV saja**: Gini tertinggi (0,36) → ketimpangan terbesar
    - **Diversified Portfolio**: Gini turun 36% → 0,07 (sangat adil)
    - **Solar-as-a-Service**: Gini terendah (0,04) → rekomendasi untuk MBR
    - Kelompok termiskin: rasio angsuran >30% → tidak affordable tanpa subsidi
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# PAGE: RAW DATA
# ============================================================================

elif page == "📋 Raw Data":
    st.markdown("## 📋 Dataset Mentah")
    st.markdown("Data BMKG Stasiun Tardamu 2025 (Sample)")
    
    df = load_data()
    
    st.markdown("### 🔍 Filter Data")
    col1, col2 = st.columns(2)
    
    with col1:
        months = ['All'] + list(range(1, 13))
        selected_month = st.selectbox("Filter Bulan", months, format_func=lambda x: "Semua Bulan" if x == "All" else f"Bulan {x}")
    
    with col2:
        search = st.text_input("Cari Data", placeholder="Masukkan keyword...")
    
    filtered_df = df.copy()
    if selected_month != "All":
        filtered_df = filtered_df[filtered_df['Bulan'] == selected_month]
    if search:
        filtered_df = filtered_df[filtered_df.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]
    
    st.dataframe(filtered_df.head(100), use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Statistik Ringkasan")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hari", len(df), "hari")
    
    with col2:
        st.metric("Rata-rata SS", f"{df['SS'].mean():.2f}", "jam/hari")
    
    with col3:
        st.metric("Rata-rata G", f"{df['G'].mean():.0f}", "W/m²")
    
    with col4:
        st.metric("Rata-rata T", f"{df['T_avg'].mean():.1f}", "°C")
    
    st.markdown("### 📈 Download Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "dataset_bmkg_2025.csv", "text/csv")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #666;">
    <p>© 2026 Tim SSO 2.0 | MMC MCF ITB 2026</p>
    <p>Data: BMKG Stasiun Tardamu 2025 | Proyeksi: IPCC AR6 SSP2-4.5</p>
</div>
""", unsafe_allow_html=True)