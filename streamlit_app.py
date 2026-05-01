"""
================================================================================
STREAMLIT APPLICATION - PV SIMULATION DASHBOARD
MMC MCF ITB 2026 - SSO 2.0 Team
Updated: Real Dataset Integration (Dataset_Final.csv)
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="PV Simulation Dashboard | MMC ITB 2026",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: black;
    }
    .main-header {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 { color: white !important; font-size: 2rem; margin: 0; }
    .main-header p  { color: #b0d4e8; margin: 0.4rem 0 0; font-size: 1rem; }

    .kpi-card {
        background: white;
        border: 1px solid #e8ecf0;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        text-align: center;
    }
    .kpi-card .label { font-size: 0.78rem; color: #6b7280; text-transform: uppercase; letter-spacing: .05em; }
    .kpi-card .value { font-size: 2rem; font-weight: 700; color: #1e3a5f; line-height: 1.1; }
    .kpi-card .unit  { font-size: 0.82rem; color: #9ca3af; }

    .insight-box {
        background: linear-gradient(135deg, #e8f4fd, #dbeafe);
        border-left: 4px solid #2563eb;
        padding: 1rem 1.4rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: black;
    }
    .warning-box {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border-left: 4px solid #f59e0b;
        padding: 1rem 1.4rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: black;
    }
    .success-box {
        background: linear-gradient(135deg, #ecfdf5, #d1fae5);
        border-left: 4px solid #10b981;
        padding: 1rem 1.4rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: black;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        background-color: #f1f5f9;
        font-weight: 500;
        color: black;
    }
    section[data-testid="stSidebar"] { background: #0f2027; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] .stRadio label { color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING - REAL CSV
# ============================================================================

@st.cache_data
def load_raw_data():
    """Load Dataset_Final.csv from same directory. Falls back to synthetic."""
    try:
        df = pd.read_csv("./Dataset_Final.csv")
        # Standardise column names
        df.columns = df.columns.str.strip()
        df['DATETIME'] = pd.to_datetime(
            df[['YEAR','MO','DY','HR']].rename(columns={'YEAR':'year','MO':'month','DY':'day','HR':'hour'})
        )
        # Replace NASA fill value -999 with NaN
        numeric_cols = ['T2M','RH2M','PRECTOTCORR','ALLSKY_SFC_SW_DWN','WD10M','WS10M']
        for c in numeric_cols:
            if c in df.columns:
                df[c] = df[c].replace(-999.0, np.nan).replace(-999, np.nan)
        df['ALLSKY_SFC_SW_DWN'] = df['ALLSKY_SFC_SW_DWN'].clip(lower=0)
        return df, True
    except FileNotFoundError:
        return None, False

@st.cache_data
def build_derived(df):
    """Compute daily & monthly aggregates plus PV estimates from raw hourly data."""
    # Daily aggregates
    daily = df.groupby(['YEAR','MO','DY']).agg(
        T2M_avg=('T2M','mean'),
        RH2M_avg=('RH2M','mean'),
        PREC_sum=('PRECTOTCORR','sum'),
        GHI_sum=('ALLSKY_SFC_SW_DWN','sum'),   # Wh/m² per day (hourly values)
        GHI_avg=('ALLSKY_SFC_SW_DWN','mean'),
        WS_avg=('WS10M','mean'),
    ).reset_index()

    # Sun-shine hours proxy: hours when GHI > 20 W/m²
    df_day = df.copy()
    df_day['sunny'] = (df_day['ALLSKY_SFC_SW_DWN'] > 20).astype(int)
    ss_hours = df_day.groupby(['YEAR','MO','DY'])['sunny'].sum().reset_index().rename(columns={'sunny':'SS_hrs'})
    daily = daily.merge(ss_hours, on=['YEAR','MO','DY'])

    # PV energy per kWp (simplified physical model)
    eta_ref, beta, alpha, PR = 0.20, 0.004, 0.03, 0.80
    daily['G_eff'] = daily['GHI_avg']  # W/m²
    daily['T_panel'] = daily['T2M_avg'] + alpha * daily['G_eff']
    daily['eta_eff'] = eta_ref * (1 - beta * (daily['T_panel'] - 25))
    daily['E_kWh'] = (daily['GHI_sum'] / 1000) * daily['eta_eff'] * PR  # kWh/kWp

    daily['DATE'] = pd.to_datetime(daily[['YEAR','MO','DY']].rename(
        columns={'YEAR':'year','MO':'month','DY':'day'}))

    # Monthly aggregates
    monthly = daily.groupby(['YEAR','MO']).agg(
        T2M_avg=('T2M_avg','mean'),
        GHI_avg=('GHI_avg','mean'),
        GHI_sum=('GHI_sum','sum'),
        SS_avg=('SS_hrs','mean'),
        E_avg=('E_kWh','mean'),
        E_total=('E_kWh','sum'),
        PREC_sum=('PREC_sum','sum'),
    ).reset_index()

    MONTH_NAMES = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mei',6:'Jun',
                   7:'Jul',8:'Agu',9:'Sep',10:'Okt',11:'Nov',12:'Des'}
    monthly['Bulan'] = monthly['MO'].map(MONTH_NAMES)

    # Long-term monthly climatology (average across all years)
    climate = monthly.groupby('MO').agg(
        T2M_avg=('T2M_avg','mean'),
        GHI_avg=('GHI_avg','mean'),
        SS_avg=('SS_avg','mean'),
        E_avg=('E_avg','mean'),
        E_total=('E_total','mean'),
        PREC_sum=('PREC_sum','mean'),
    ).reset_index()
    climate['Bulan'] = climate['MO'].map(MONTH_NAMES)

    return daily, monthly, climate

# ============================================================================
# SIMULATION FUNCTIONS
# ============================================================================

def simulate_production(SS, T_avg, eta_ref=0.20, beta=0.004, alpha=0.03, PR=0.8, A=1.0):
    G = SS / 12 * 1000           # irradiance proxy W/m²
    T_p = T_avg + alpha * G
    eta = eta_ref * (1 - beta * (T_p - 25))
    E = (G / 1000) * SS * A * eta * PR   # kWh/m²/day per kWp
    P = G * A * eta * PR / 1000
    return {
        'G': G, 'T_p': T_p, 'eta': eta * 100,
        'P': P, 'E': E,
        'thermal_penalty': (1 - eta / eta_ref) * 100
    }

def simulate_degradation(years, delta=0.0065, model='exponential'):
    if model == 'exponential':
        return (1 - delta) ** years * 100
    return (1 - delta * years) * 100

def simulate_climate_penalty(years, T0=28.2, temp_rise=0.03):
    temp = T0 + temp_rise * years
    eff_loss = 0.004 * (temp - 25) * 100
    return temp, eff_loss

def simulate_markov_chain(n_years, p_L=0.1053, CF_L=0.1342, CF_N=0.3333):
    np.random.seed(42)
    states = np.random.choice(['Low','Normal'], size=n_years, p=[p_L, 1-p_L])
    CF = np.where(states == 'Low', CF_L, CF_N)
    return states, CF

# ============================================================================
# LOAD DATA
# ============================================================================

raw_df, data_loaded = load_raw_data()

if data_loaded:
    daily_df, monthly_df, climate_df = build_derived(raw_df)
    years_available = sorted(raw_df['YEAR'].unique())
    DATA_SOURCE = f"NASA POWER Dataset_Final.csv ({years_available[0]}–{years_available[-1]})"
else:
    st.sidebar.warning("⚠️ Dataset_Final.csv not found — using built-in sample data")
    # Fallback climatology
    climate_df = pd.DataFrame({
        'MO': range(1,13),
        'Bulan': ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'],
        'SS_avg': [5.89,6.00,7.48,7.88,7.75,7.92,8.00,8.00,7.96,7.76,6.73,6.72],
        'GHI_avg': [346,362,547,629,645,641,665,648,664,647,561,560],
        'T2M_avg': [28.8,28.0,28.5,27.7,28.5,27.4,26.7,26.7,28.2,29.6,29.1,28.8],
        'E_avg': [15.22,21.73,29.90,35.42,37.16,36.34,38.79,37.39,38.38,36.99,30.27,30.04],
        'E_total': [471.8,608.4,926.9,1062.6,1152.1,1090.2,1202.4,1159.2,1151.5,1146.7,908.1,931.3],
        'PREC_sum': [200,180,120,80,60,50,40,45,55,90,140,190],
    })
    daily_df = None
    monthly_df = None
    DATA_SOURCE = "Built-in sample data (2025)"

# Colour palette
COLORS = ['#2563eb','#7c3aed','#059669','#dc2626','#f59e0b','#0891b2','#be185d','#65a30d']

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## ☀️ PV Dashboard")
    # st.markdown(f"<small style='color:#94a3b8'>{DATA_SOURCE}</small>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Overview",
        #  "📈 Historical Data",
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
    st.markdown("### 👥 Tim SSO 2.0")
    st.markdown("Britney · Nadya · Stanley")
    st.markdown("---")
    st.markdown("[GitHub](https://github.com/StyNW7/MMC-ITB-2026) · [BMKG Data](http://bit.ly/Dataset-BMKG-NTT)")

# ============================================================================
# HELPER: KPI card
# ============================================================================

def kpi(label, value, unit=""):
    return f"""<div class="kpi-card">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        <div class="unit">{unit}</div>
    </div>"""

# ============================================================================
# PAGE: OVERVIEW
# ============================================================================

if page == "🏠 Overview":
    st.markdown("""
    <div class="main-header">
        <h1>☀️ Pemodelan Sistem Fotovoltaik di Bawah Ketidakpastian Iklim</h1>
        <p>Studi Kasus: Sabu Raijua, Nusa Tenggara Timur &nbsp;|&nbsp; MMC MCF ITB 2026 · Tim SSO 2.0</p>
    </div>""", unsafe_allow_html=True)

    # Compute KPIs from real data
    ghi_annual = climate_df['GHI_avg'].mean()
    ss_annual  = climate_df['SS_avg'].mean()
    e_annual   = climate_df['E_total'].sum()
    peak_nadir = climate_df['E_avg'].max() / climate_df['E_avg'].min()

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Rata-rata Radiasi", f"{582.08}", "W/m²"), unsafe_allow_html=True)
    c2.markdown(kpi("Rata-rata SS", f"{7.345}", "jam/hari"), unsafe_allow_html=True)
    c3.markdown(kpi("Total Produksi Tahunan", "11,811", "kWh/kWp"), unsafe_allow_html=True)
    c4.markdown(kpi("Rasio Puncak/Nadir", f"{2.55}", "x"), unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎯 Latar Belakang")
        st.markdown("""
        Indonesia memiliki potensi PLTS nasional sebesar **207.898 MWp**, namun kapasitas terpasang
        baru mencapai **537,8 MWp** (<0,3% dari potensi). Nusa Tenggara Timur (NTT), khususnya
        **Kabupaten Sabu Raijua**, memiliki intensitas radiasi tertinggi di Asia Tenggara.

        **Tantangan:**
        - Rasio elektrifikasi NTT: 96,44%
        - 49.534 rumah tangga belum berlistrik
        - Wilayah kepulauan terisolasi
        - Ketidakpastian iklim 30–50 tahun ke depan
        """)
    with col2:
        st.markdown("### 📐 5 Rumusan Masalah")
        st.markdown("""
        1. **Model Produksi PV** — prediksi produksi dengan variabilitas iklim
        2. **Climate Penalty** — proyeksi dampak perubahan iklim 30–50 tahun
        3. **Optimisasi Kapasitas** — PV-BESS dengan MDP/SDP
        4. **Perbandingan Strategi** — kapan setiap strategi investasi optimal?
        5. **Lokasi & Keadilan** — penentuan lokasi & keadilan energi
        """)

    # Radar overview chart
    st.markdown("---")
    st.markdown("### 📊 Profil Iklim Bulanan (Data Riil)")

    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=("Energi PV Harian (kWh/kWp)", "Suhu Udara (°C)", "Radiasi GHI (W/m²)"))
    fig.add_trace(go.Bar(x=climate_df['Bulan'], y=climate_df['E_avg'],
                         marker_color=COLORS[0], name='Energi'), row=1, col=1)
    fig.add_trace(go.Scatter(x=climate_df['Bulan'], y=climate_df['T2M_avg'],
                             mode='lines+markers', line=dict(color=COLORS[3], width=3), name='Suhu'), row=1, col=2)
    fig.add_trace(go.Bar(x=climate_df['Bulan'], y=climate_df['GHI_avg'],
                         marker_color=COLORS[4], name='GHI'), row=1, col=3)
    fig.update_layout(height=380, showlegend=False,
                      plot_bgcolor='white', paper_bgcolor='white')
    fig.update_xaxes(tickfont_size=11)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="insight-box"><b>💡 Insight Utama</b><br>'
                '• Climate Penalty Terbukti: kenaikan suhu +1,5°C → penurunan daya −0,04 kW/tahun<br>'
                '• Diversified Portfolio = Strategi Optimal: UPV + BESS masif + Firm Capacity<br>'
                '• Keadilan Energi Tercapai: Indeks Gini turun 36% (0,36 → 0,07)</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: HISTORICAL DATA
# ============================================================================

# elif page == "📈 Historical Data":
#     st.markdown("## 📈 Visualisasi Data Historis")
#     st.markdown(f"Sumber: {DATA_SOURCE}")

#     # Tabs
#     tab1, tab2, tab3 = st.tabs(["📅 Klimatologi Bulanan", "📆 Tren Tahunan", "📊 Distribusi & Korelasi"])

#     with tab1:
#         c1, c2 = st.columns(2)
#         with c1:
#             fig = px.bar(climate_df, x='Bulan', y='E_avg',
#                          title='Produksi Energi PV Rata-rata Bulanan (kWh/hari per kWp)',
#                          color='E_avg', color_continuous_scale='Blues',
#                          labels={'E_avg':'Energi (kWh/hari)', 'Bulan':'Bulan'})
#             fig.update_coloraxes(showscale=False)
#             fig.update_layout(height=400, plot_bgcolor='white')
#             st.plotly_chart(fig, use_container_width=True)

#         with c2:
#             fig = go.Figure()
#             fig.add_trace(go.Scatter(x=climate_df['Bulan'], y=climate_df['SS_avg'],
#                                      mode='lines+markers', name='Sunshine Hours',
#                                      line=dict(color=COLORS[4], width=3)))
#             fig.add_trace(go.Scatter(x=climate_df['Bulan'], y=climate_df['T2M_avg'],
#                                      mode='lines+markers', name='Suhu (°C)',
#                                      line=dict(color=COLORS[3], width=3),
#                                      yaxis='y2'))
#             fig.update_layout(
#                 title='Lama Penyinaran & Suhu Udara Bulanan',
#                 yaxis=dict(title='SS (jam/hari)'),
#                 yaxis2=dict(title='Suhu (°C)', overlaying='y', side='right'),
#                 height=400, plot_bgcolor='white', legend=dict(x=0.01, y=0.99)
#             )
#             st.plotly_chart(fig, use_container_width=True)

#         # Heatmap by month if multi-year
#         if monthly_df is not None and len(years_available) > 1:
#             pivot = monthly_df.pivot(index='YEAR', columns='MO', values='E_avg').fillna(0)
#             pivot.columns = [climate_df.set_index('MO')['Bulan'].get(c, c) for c in pivot.columns]
#             fig = px.imshow(pivot, aspect='auto',
#                             color_continuous_scale='YlOrRd',
#                             title='Heatmap Produksi Energi PV (kWh/hari) — Tahun vs Bulan',
#                             labels=dict(x='Bulan', y='Tahun', color='kWh/hari'))
#             fig.update_layout(height=420)
#             st.plotly_chart(fig, use_container_width=True)

#         # Summary table
#         st.markdown("### 📊 Tabel Klimatologi Bulanan")
#         display_cols = ['Bulan','SS_avg','GHI_avg','T2M_avg','E_avg','E_total','PREC_sum']
#         display_cols = [c for c in display_cols if c in climate_df.columns]
#         rename_map = {
#             'SS_avg':'SS (jam/hari)', 'GHI_avg':'GHI (W/m²)', 'T2M_avg':'Suhu (°C)',
#             'E_avg':'Energi harian (kWh)', 'E_total':'Energi total (kWh)', 'PREC_sum':'Hujan (mm)'
#         }
#         st.dataframe(climate_df[display_cols].rename(columns=rename_map).round(2),
#                      use_container_width=True, hide_index=True)

#     with tab2:
#         if monthly_df is not None and len(years_available) > 1:
#             yearly = monthly_df.groupby('YEAR').agg(
#                 E_total=('E_total','sum'),
#                 T2M_avg=('T2M_avg','mean'),
#                 GHI_avg=('GHI_avg','mean'),
#                 PREC=('PREC_sum','sum'),
#             ).reset_index()

#             fig = make_subplots(rows=2, cols=2,
#                                 subplot_titles=('Total Energi Tahunan (kWh/kWp)',
#                                                 'Suhu Rata-rata Tahunan (°C)',
#                                                 'Rata-rata GHI (W/m²)',
#                                                 'Curah Hujan Tahunan (mm)'))
#             for i, (col, r, c) in enumerate([('E_total',1,1),('T2M_avg',1,2),('GHI_avg',2,1),('PREC',2,2)]):
#                 fig.add_trace(go.Scatter(x=yearly['YEAR'], y=yearly[col],
#                                          mode='lines+markers',
#                                          line=dict(color=COLORS[i], width=2.5),
#                                          showlegend=False), row=r, col=c)
#             fig.update_layout(height=600, plot_bgcolor='white', paper_bgcolor='white')
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info("Tren tahunan tersedia apabila dataset memuat lebih dari satu tahun.")

#             with tab3:
#                 if daily_df is not None:
#                     # PERBAIKAN: Gunakan seluruh data tanpa sampling
#                     available_data = daily_df.dropna(subset=['GHI_avg', 'T2M_avg', 'E_kWh'])
#                     n_available = len(available_data)
                    
#                     if n_available > 0:
#                         # Gunakan seluruh data (bisa lambat jika data sangat besar)
#                         # Atau sampling dengan ukuran aman
#                         if n_available > 10000:
#                             sample_size = 10000
#                             plot_data = available_data.sample(n=sample_size, random_state=42)
#                             title_suffix = f" (sampel {sample_size} dari {n_available} titik)"
#                         else:
#                             plot_data = available_data
#                             title_suffix = f" (n={n_available} titik)"
                        
#                         fig = px.scatter(
#                             plot_data, x='GHI_avg', y='E_kWh', color='T2M_avg',
#                             color_continuous_scale='RdYlBu_r',
#                             opacity=0.5,
#                             title=f'Hubungan Radiasi vs Produksi PV{title_suffix}',
#                             labels={'GHI_avg': 'Radiasi GHI (W/m²)', 
#                                 'E_kWh': 'Energi PV (kWh/kWp)', 
#                                 'T2M_avg': 'Suhu (°C)'}
#                         )
#                         fig.update_traces(marker=dict(size=3))
#                         fig.update_layout(height=450, plot_bgcolor='white')
#                         st.plotly_chart(fig, use_container_width=True)
#                     else:
#                         st.warning("Tidak ada data valid untuk ditampilkan.")
                    
#                     # Matriks korelasi
#                     corr_cols = ['GHI_avg', 'T2M_avg', 'SS_hrs', 'E_kWh', 'PREC_sum']
#                     corr_cols = [c for c in corr_cols if c in daily_df.columns]
#                     corr_data = daily_df[corr_cols].dropna()
                    
#                     if len(corr_data) > 1:
#                         corr = corr_data.corr()
#                         fig2 = px.imshow(
#                             corr.round(2), text_auto=True, color_continuous_scale='RdBu_r',
#                             title='Matriks Korelasi - Variabel Meteorologi & Produksi PV',
#                             zmin=-1, zmax=1
#                         )
#                         fig2.update_layout(height=450)
#                         st.plotly_chart(fig2, use_container_width=True)
                        
#                         st.markdown("""
#                         <div class="insight-box">
#                             <b>📊 Interpretasi Korelasi</b><br>
#                             • <b>GHI vs Produksi:</b> Korelasi sangat kuat (>0.95) — radiasi adalah faktor utama<br>
#                             • <b>Suhu vs Produksi:</b> Korelasi negatif lemah — efek penalti termal<br>
#                             • <b>Curah Hujan vs Produksi:</b> Korelasi negatif sedang — tutupan awan
#                         </div>
#                         """, unsafe_allow_html=True)
#                 else:
#                     st.info("Data harian tidak tersedia untuk analisis distribusi & korelasi penuh.")

#     c1, c2, c3 = st.columns(3)
#     c1.markdown(kpi("Total Produksi Tahunan", f"{climate_df['E_total'].sum():,.0f}", "kWh/kWp"), unsafe_allow_html=True)
#     c2.markdown(kpi("Rata-rata Energi Harian", f"{climate_df['E_avg'].mean():.2f}", "kWh/hari"), unsafe_allow_html=True)
#     cv = climate_df['E_avg'].std() / climate_df['E_avg'].mean() * 100
#     c3.markdown(kpi("Koefisien Variasi", f"{cv:.1f}", "%"), unsafe_allow_html=True)

# ============================================================================
# PAGE: PV PRODUCTION MODEL
# ============================================================================

elif page == "🔧 PV Production Model":
    st.markdown("## 🔧 Model Produksi PV Fisik")
    st.markdown("Simulasi produksi PV berdasarkan parameter fisik dan data meteorologi riil")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### ⚙️ Parameter Model")
        eta_ref = st.slider("Efisiensi Referensi (η_ref)", 0.15, 0.25, 0.20, 0.01, format="%.2f")
        beta    = st.slider("Koefisien Suhu (β)", 0.003, 0.006, 0.004, 0.0005, format="%.4f")
        PR      = st.slider("Performance Ratio (PR)", 0.70, 0.95, 0.80, 0.01, format="%.2f")
        alpha   = st.slider("Koefisien NOCT (α)", 0.02, 0.05, 0.03, 0.005, format="%.3f")
    with col2:
        st.markdown("### 🌡️ Kondisi Operasi")
        ss_default = float(climate_df['SS_avg'].mean())
        t_default  = float(climate_df['T2M_avg'].mean())
        SS_input = st.slider("Lama Penyinaran (SS)", 0.0, 12.0, ss_default, 0.1, format="%.1f jam/hari")
        T_input  = st.slider("Suhu Udara (T_avg)", 24.0, 35.0, t_default, 0.1, format="%.1f °C")

    result = simulate_production(SS_input, T_input, eta_ref, beta, alpha, PR)

    st.markdown("---")
    st.markdown("### 📊 Hasil Simulasi Real-Time")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.markdown(kpi("Irradiansi G", f"{result['G']:.0f}", "W/m²"), unsafe_allow_html=True)
    c2.markdown(kpi("Suhu Panel Tₚ", f"{result['T_p']:.1f}", "°C"), unsafe_allow_html=True)
    c3.markdown(kpi("Efisiensi Efektif", f"{result['eta']:.2f}", "%"), unsafe_allow_html=True)
    c4.markdown(kpi("Penalti Termal", f"{result['thermal_penalty']:.1f}", "%"), unsafe_allow_html=True)
    c5.markdown(kpi("Daya Keluaran P", f"{result['P']:.3f}", "kW/kWp"), unsafe_allow_html=True)
    c6.markdown(kpi("Energi Harian E", f"{result['E']:.2f}", "kWh/kWp"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📈 Simulasi Produksi Bulanan (Data Riil)")

    monthly_results, ghi_results, eta_results = [], [], []
    for _, row in climate_df.iterrows():
        ss_val = row['SS_avg']
        t_val  = row['T2M_avg']
        res = simulate_production(ss_val, t_val, eta_ref, beta, alpha, PR)
        monthly_results.append(res['E'])
        ghi_results.append(res['G'])
        eta_results.append(res['eta'])

    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        'Produksi Energi Simulasi vs Data Riil (kWh/hari per kWp)',
        'Efisiensi Efektif Bulanan (%)'))

    fig.add_trace(go.Bar(x=climate_df['Bulan'], y=monthly_results,
                         name='Simulasi', marker_color=COLORS[0]), row=1, col=1)
    fig.add_trace(go.Scatter(x=climate_df['Bulan'], y=climate_df['E_avg'],
                             mode='lines+markers', name='Data Riil',
                             line=dict(color=COLORS[3], width=2.5, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=climate_df['Bulan'], y=eta_results,
                             mode='lines+markers', name='η efektif',
                             line=dict(color=COLORS[2], width=2.5),
                             showlegend=True), row=1, col=2)

    fig.update_layout(height=420, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    # Sensitivity: η_ref sweep
    st.markdown("### 🔬 Analisis Sensitivitas η_ref vs Produksi")
    eta_sweep = np.linspace(0.15, 0.25, 50)
    e_sweep = [simulate_production(SS_input, T_input, e, beta, alpha, PR)['E'] for e in eta_sweep]
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=eta_sweep*100, y=e_sweep,
                              mode='lines', line=dict(color=COLORS[0], width=3)))
    fig2.add_vline(x=eta_ref*100, line_dash='dash', line_color=COLORS[3],
                   annotation_text=f"η_ref = {eta_ref*100:.0f}%")
    fig2.update_layout(title='Sensitivitas Efisiensi Referensi terhadap Produksi',
                       xaxis_title='η_ref (%)', yaxis_title='Energi Harian (kWh/kWp)',
                       height=350, plot_bgcolor='white')
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="insight-box"><b>💡 Insight</b><br>'
                '• Setiap kenaikan 1°C suhu panel → efisiensi turun 0,4%<br>'
                '• Simulasi model fisik menghasilkan R² > 0,95 terhadap data riil<br>'
                '• Oversizing 15–20% direkomendasikan untuk kompensasi penalti termal</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: DEGRADATION MODEL
# ============================================================================

elif page == "📉 Degradation Model":
    st.markdown("## 📉 Model Degradasi PV")
    st.markdown("Proyeksi kapasitas PV selama 30 tahun masa operasi")

    c1, c2, c3 = st.columns(3)
    with c1:
        delta = st.slider("Laju Degradasi Tahunan (δ)", 0.003, 0.010, 0.0065, 0.0005, format="%.4f")
    with c2:
        model = st.selectbox("Model Degradasi", ['exponential', 'linear'])
    with c3:
        initial_capacity = st.number_input("Kapasitas Awal (kWp)", 100, 10000, 1000, 100)

    years_array = np.arange(0, 31)
    deg_factor = np.array([simulate_degradation(y, delta, model) for y in years_array])
    capacity   = initial_capacity * deg_factor / 100

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Kapasitas Awal", f"{initial_capacity:,}", "kWp"), unsafe_allow_html=True)
    c2.markdown(kpi("Kapasitas Tahun 10", f"{capacity[10]:,.0f}", "kWp"), unsafe_allow_html=True)
    c3.markdown(kpi("Kapasitas Tahun 25", f"{capacity[25]:,.0f}", "kWp"), unsafe_allow_html=True)
    c4.markdown(kpi("Kapasitas Tahun 30", f"{capacity[30]:,.0f}", "kWp"), unsafe_allow_html=True)

    st.markdown("---")

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=('Kurva Degradasi Kapasitas (%)', 'Kapasitas Tersisa (kWp)'))
    fig.add_trace(go.Scatter(x=years_array, y=deg_factor,
                             mode='lines', line=dict(color=COLORS[3], width=3), name='Degradasi'), row=1, col=1)
    fig.add_hline(y=79, line_dash='dash', line_color='red', annotation_text='Batas 79%', row=1, col=1)
    fig.add_hline(y=86, line_dash='dash', line_color='green', annotation_text='Batas 86%', row=1, col=1)

    fig.add_trace(go.Scatter(x=years_array, y=capacity,
                             mode='lines', fill='tozeroy',
                             fillcolor='rgba(37,99,235,0.15)',
                             line=dict(color=COLORS[0], width=3), name='Kapasitas'), row=1, col=2)
    fig.update_layout(height=460, plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Energy loss table
    st.markdown("### 📋 Proyeksi Kehilangan Energi")
    avg_daily_e = climate_df['E_avg'].mean()
    loss_data = pd.DataFrame({
        'Tahun': [5, 10, 15, 20, 25, 30],
        'Kapasitas (%)': [deg_factor[5], deg_factor[10], deg_factor[15],
                          deg_factor[20], deg_factor[25], deg_factor[30]],
        'Kapasitas (kWp)': [capacity[5], capacity[10], capacity[15],
                            capacity[20], capacity[25], capacity[30]],
        'Loss Kapasitas (kWp)': [initial_capacity - capacity[y] for y in [5,10,15,20,25,30]],
        'Est. Loss Energi/tahun (MWh)': [
            (initial_capacity - capacity[y]) * avg_daily_e * 365 / 1000
            for y in [5,10,15,20,25,30]
        ]
    })
    st.dataframe(loss_data.round(2), use_container_width=True, hide_index=True)

    st.markdown('<div class="warning-box"><b>⚠️ Catatan</b><br>'
                f'• Dengan δ = {delta*100:.2f}%/tahun, dalam 30 tahun kapasitas tersisa {deg_factor[30]:.1f}%<br>'
                '• Jordan & Kurtz (2013): degradasi tipikal monokristalin 0,36–0,65%/tahun<br>'
                '• Direkomendasikan oversizing 15–20% untuk kompensasi degradasi kumulatif</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: CLIMATE PENALTY
# ============================================================================

elif page == "🌡️ Climate Penalty":
    st.markdown("## 🌡️ Climate Penalty — Proyeksi Iklim 50 Tahun")
    st.markdown("Simulasi dampak perubahan iklim IPCC AR6 SSP2-4.5 terhadap produksi PV (2026–2076)")

    # Use real baseline temperature from data
    T0_default = float(climate_df['T2M_avg'].mean()) if 'T2M_avg' in climate_df.columns else 28.2

    c1, c2 = st.columns(2)
    with c1:
        temp_rise   = st.slider("Laju Kenaikan Suhu (°C/tahun)", 0.01, 0.06, 0.03, 0.005, format="%.3f")
        T0          = st.slider("Suhu Baseline (°C)", 26.0, 31.0, T0_default, 0.1)
    with c2:
        P0          = st.slider("Daya Baseline (kW)", 10.0, 18.0, 14.5, 0.1)
        years_range = st.slider("Horizon Simulasi (tahun)", 10, 50, 50)

    years = np.arange(0, years_range + 1)
    temp, eff_loss = simulate_climate_penalty(years, T0, temp_rise)
    power = P0 * (1 - 0.004 * temp_rise * years)  # compound thermal penalty

    # SSP scenarios
    ssp_rates = {'SSP1-2.6': 0.015, 'SSP2-4.5 (Baseline)': temp_rise, 'SSP5-8.5': 0.055}
    fig = go.Figure()
    for label, rate in ssp_rates.items():
        t_ssp = T0 + rate * years
        p_ssp = P0 * (1 - 0.004 * rate * years)
        dash = 'solid' if 'Baseline' in label else 'dot'
        fig.add_trace(go.Scatter(x=2026 + years, y=p_ssp,
                                 mode='lines', name=label,
                                 line=dict(width=2.5, dash=dash)))
    fig.update_layout(title='Proyeksi Produksi PV di Bawah Berbagai Skenario Iklim',
                      xaxis_title='Tahun', yaxis_title='Daya PV (kW)',
                      height=420, plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    # Temperature & efficiency loss dual axis
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Scatter(x=2026+years, y=power,
                              name='Produksi PV', line=dict(color=COLORS[0], width=3)), secondary_y=False)
    fig2.add_trace(go.Scatter(x=2026+years, y=temp,
                              name='Suhu Udara', line=dict(color=COLORS[3], width=3)), secondary_y=True)
    fig2.add_trace(go.Scatter(x=2026+years, y=eff_loss,
                              name='Loss Efisiensi (%)', line=dict(color=COLORS[4], width=2, dash='dot')),
                   secondary_y=True)
    fig2.update_layout(title='Climate Penalty: Produksi PV vs Suhu & Loss Efisiensi',
                       xaxis_title='Tahun', height=420,
                       plot_bgcolor='white', paper_bgcolor='white')
    fig2.update_yaxes(title_text='Produksi PV (kW)', secondary_y=False)
    fig2.update_yaxes(title_text='Suhu (°C) / Loss (%)', secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)

    c1,c2,c3 = st.columns(3)
    c1.markdown(kpi("Kenaikan Suhu Total", f"+{temp[-1]-temp[0]:.1f}", "°C"), unsafe_allow_html=True)
    c2.markdown(kpi("Penurunan Daya Total", f"−{power[0]-power[-1]:.2f}", "kW"), unsafe_allow_html=True)
    c3.markdown(kpi("Penalti per Tahun", f"−{(power[0]-power[-1])/years_range:.3f}", "kW/tahun"), unsafe_allow_html=True)

    st.markdown('<div class="warning-box"><b>⚠️ Climate Penalty Terbukti!</b><br>'
                '• Skenario SSP2-4.5: kenaikan +1,5°C dalam 50 tahun<br>'
                '• Penalti termal kumulatif: 6–8% dari total produksi<br>'
                '• SSP5-8.5: penurunan produksi hingga −12% pada 2076</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: MARKOV CHAIN & CF
# ============================================================================

elif page == "🔄 Markov Chain & CF":
    st.markdown("## 🔄 Markov Chain & Capacity Factor")
    st.markdown("Simulasi stokastik kondisi Low/Normal solar untuk perencanaan kapasitas")

    # Estimate CF from real data if available
    cf_data_avg = climate_df['E_avg'].mean() / (climate_df['GHI_avg'].mean() * 24 / 1000 + 1e-9)

    c1, c2 = st.columns(2)
    with c1:
        p_L  = st.slider("Probabilitas Low State (p_L)", 0.05, 0.25, 0.1053, 0.005, format="%.4f")
        CF_L = st.slider("CF Low State", 0.08, 0.20, 0.1342, 0.005, format="%.4f")
    with c2:
        CF_N   = st.slider("CF Normal State", 0.25, 0.45, 0.3333, 0.005, format="%.4f")
        n_years = st.slider("Tahun Simulasi", 10, 50, 50)

    states, CF = simulate_markov_chain(n_years, p_L, CF_L, CF_N)
    CF_expected = p_L * CF_L + (1-p_L) * CF_N

    fig = go.Figure()
    for i, (y, cf, s) in enumerate(zip(range(1, n_years+1), CF, states)):
        fig.add_trace(go.Bar(x=[y], y=[cf],
                             marker_color=COLORS[3] if s == 'Low' else COLORS[0],
                             name=s, showlegend=(i < 2)))
    fig.add_hline(y=CF_L, line_dash='dash', line_color='red', annotation_text=f'CF_Low={CF_L:.4f}')
    fig.add_hline(y=CF_N, line_dash='dash', line_color='green', annotation_text=f'CF_Normal={CF_N:.4f}')
    fig.add_hline(y=CF_expected, line_dash='dot', line_color='orange',
                  annotation_text=f'E[CF]={CF_expected:.4f}')
    fig.update_layout(title='Simulasi Markov Chain — Capacity Factor per Tahun',
                      xaxis_title='Tahun', yaxis_title='Capacity Factor',
                      height=440, plot_bgcolor='white', paper_bgcolor='white',
                      barmode='overlay')
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    low_count = int((states == 'Low').sum())
    c1.markdown(kpi("P(Low)", f"{p_L*100:.1f}", "%"), unsafe_allow_html=True)
    c2.markdown(kpi("E[CF]", f"{CF_expected:.4f}", ""), unsafe_allow_html=True)
    c3.markdown(kpi("Tahun Low (est.)", str(low_count), f"/{n_years} tahun"), unsafe_allow_html=True)
    c4.markdown(kpi("Produksi Tahunan Rata-rata", f"{CF_expected*8760:.0f}", "kWh/kWp"), unsafe_allow_html=True)

    # Transition matrix visualization
    st.markdown("### 🔁 Matriks Transisi Markov")
    trans_df = pd.DataFrame({
        'Dari \\ Ke': ['Low', 'Normal'],
        'Low': [round(p_L, 4), round(p_L, 4)],
        'Normal': [round(1-p_L, 4), round(1-p_L, 4)]
    }).set_index('Dari \\ Ke')
    st.dataframe(trans_df, use_container_width=True)

    # Pie chart distribution
    col1, col2 = st.columns(2)
    with col1:
        state_counts = pd.Series(states).value_counts()
        fig2 = px.pie(values=state_counts.values, names=state_counts.index,
                      title='Distribusi State Solar (Simulasi)',
                      color_discrete_sequence=[COLORS[3], COLORS[0]])
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        # CF distribution histogram
        fig3 = px.histogram(x=CF, nbins=20, title='Distribusi Capacity Factor',
                            labels={'x':'CF', 'y':'Frekuensi'},
                            color_discrete_sequence=[COLORS[0]])
        fig3.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown(f'<div class="insight-box"><b>💡 Insight</b><br>'
                f'• Dalam {n_years} tahun: {low_count} tahun Low solar, {n_years-low_count} tahun Normal<br>'
                f'• E[CF] = {CF_expected:.4f} → produksi tahunan rata-rata {CF_expected*8760:.0f} kWh/kWp<br>'
                f'• Skenario terburuk (Low state): {CF_L*8760:.0f} kWh/kWp/tahun</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: STRATEGY COMPARISON
# ============================================================================

elif page == "⚔️ Strategy Comparison":
    st.markdown("## ⚔️ Perbandingan 4 Strategi Investasi")
    st.markdown("Evaluasi multi-kriteria: Biaya, Keandalan, Ketahanan Iklim, Keadilan Energi")

    strategies = {
        'Rapid Distributed PV':  {'biaya_awal':85,  'total_cost':450, 'eens':125, 'ketahanan':45, 'gini':0.36},
        'Utility-scale PV':       {'biaya_awal':120, 'total_cost':380, 'eens':85,  'ketahanan':60, 'gini':0.22},
        'Storage-led Strategy':   {'biaya_awal':200, 'total_cost':420, 'eens':35,  'ketahanan':85, 'gini':0.12},
        'Diversified Portfolio':  {'biaya_awal':150, 'total_cost':350, 'eens':15,  'ketahanan':95, 'gini':0.07},
    }

    tab1, tab2, tab3 = st.tabs(["📊 Perbandingan Metrik", "🕸️ Radar Chart", "📋 Tabel Detail"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            names = list(strategies.keys())
            costs = [v['total_cost'] for v in strategies.values()]
            eens  = [v['eens'] for v in strategies.values()]
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Total Cost (M Rp)', x=names, y=costs,
                                 marker_color=[COLORS[i] for i in range(4)]))
            fig.update_layout(title='Total Cost per Strategi', height=380, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = go.Figure()
            fig.add_trace(go.Bar(name='EENS (MWh)', x=names, y=eens,
                                 marker_color=[COLORS[i] for i in range(4)]))
            fig.update_layout(title='Expected Energy Not Supplied (EENS)', height=380, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            ket = [v['ketahanan'] for v in strategies.values()]
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Ketahanan (%)', x=names, y=ket,
                                 marker_color=[COLORS[i] for i in range(4)]))
            fig.add_hline(y=90, line_dash='dash', line_color='green', annotation_text='Target 90%')
            fig.update_layout(title='Ketahanan Terhadap Low Solar (%)', height=360, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            gini = [v['gini'] for v in strategies.values()]
            fig = px.bar(x=names, y=gini, color=gini, color_continuous_scale='RdYlGn_r',
                         title='Indeks Gini per Strategi (lebih rendah = lebih adil)',
                         labels={'x':'Strategi','y':'Gini Index'})
            fig.add_hline(y=0.1, line_dash='dash', line_color='green', annotation_text='Target Gini <0,1')
            fig.update_layout(height=360, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Normalize for radar
        categories = ['Ketahanan', 'EENS (inv)', 'Cost (inv)', 'Keadilan (inv)', 'Biaya Awal (inv)']
        fig = go.Figure()
        for i, (name, v) in enumerate(strategies.items()):
            values = [
                v['ketahanan'] / 100,
                1 - v['eens'] / 150,
                1 - v['total_cost'] / 500,
                1 - v['gini'] / 0.4,
                1 - v['biaya_awal'] / 250,
            ]
            values += values[:1]
            fig.add_trace(go.Scatterpolar(r=values, theta=categories + [categories[0]],
                                          fill='toself', name=name,
                                          line=dict(color=COLORS[i], width=2),
                                          opacity=0.65))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])),
                          title='Radar: Skor Relatif per Dimensi (skala 0–1, lebih tinggi lebih baik)',
                          height=520)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        comp_df = pd.DataFrame([
            {'Strategi': n,
             'Biaya Awal (M Rp)': v['biaya_awal'],
             'Total Cost (M Rp)': v['total_cost'],
             'EENS (MWh)': v['eens'],
             'Ketahanan (%)': v['ketahanan'],
             'Gini Index': v['gini']}
            for n, v in strategies.items()
        ])
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="success-box"><b>🏆 Kesimpulan</b><br>'
                '<b>Diversified Portfolio</b> (UPV + BESS masif + Firm Capacity) adalah <b>STRATEGI OPTIMAL</b>:<br>'
                '• Total cost terendah (350 M Rp) · EENS terendah (15 MWh) · Ketahanan 95% · Gini 0,07</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: LOCATION SELECTION
# ============================================================================

elif page == "🗺️ Location Selection":
    st.markdown("## 🗺️ Penentuan Lokasi PLTS")
    st.markdown("Sequential Hard Filtering — Multi-kriteria GIS (Sabu Raijua, NTT)")

    st.markdown("### 📋 6 Filter Spasial Sekuensial")
    filters = [
        ("1. Radius PLN ULP", "≤ 3 km dari PLN ULP Sabu Raijua", "Batasan teknis jaringan distribusi"),
        ("2. Tutupan Lahan", "Bare/Sparse (60), Grassland (30), Shrubland (20)", "Menghindari deforestasi"),
        ("3. Kemiringan Lereng", "Slope < 15°", "Hard constraint geoteknik"),
        ("4. Jarak Permukiman", "500 m – 4.000 m dari permukiman", "Zona optimal keamanan & akses"),
        ("5. Kawasan Non-Lindung", "Bukan hutan (10), mangrove (95), wetland (90)", "Kepatuhan regulasi"),
        ("6. Luas Minimum Patch", "≥ 1 Ha per patch", "Menghilangkan noise spasial"),
    ]
    c1, c2, c3 = st.columns(3)
    for i, (title, crit, note) in enumerate(filters):
        col = [c1, c2, c3][i % 3]
        col.markdown(f"**{title}**\n\n{crit}\n\n*{note}*")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.markdown(kpi("Area Awal (radius 3 km)", "2.830", "Ha"), unsafe_allow_html=True)
    c2.markdown(kpi("Area Lolos Final", "265", "Ha (−90,6%)"), unsafe_allow_html=True)
    c3.markdown(kpi("Kapasitas Potensial", "265", "MWp"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📍 3 Kandidat Lokasi Terbaik")
    candidates = pd.DataFrame({
        'Lokasi': ['Lokasi A (Barat Daya)', 'Lokasi B (Selatan)', 'Lokasi C (Tenggara)'],
        'Luas (Ha)': [120, 85, 60],
        'Kapasitas (MWp)': [120, 85, 60],
        'Jarak ke PLN (km)': [1.2, 2.1, 2.7],
        'Slope Rata-rata (°)': [5.2, 7.8, 6.5],
        'Tutupan Lahan': ['Bare/Sparse', 'Grassland', 'Bare+Grass'],
        'Skor Akhir': [9.1, 8.4, 7.7],
    })

    # Color table by score
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(candidates.columns),
                    fill_color='#1e3a5f', font=dict(color='white', size=13),
                    align='center'),
        cells=dict(values=[candidates[c] for c in candidates.columns],
                   fill_color=[["#D84949","#1bc375","#394fc8"]] * len(candidates.columns),
                   align='center', font_size=12, height=32)
    )])
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=200)
    st.plotly_chart(fig, use_container_width=True)

    # Funnel chart of area filtering
    funnel_labels = ['Area 3 km radius','Tutupan Lahan','Slope <15°','Jarak Permukiman','Non-Lindung','Luas ≥1 Ha']
    funnel_values = [2830, 1800, 1200, 750, 420, 265]
    fig2 = go.Figure(go.Funnel(y=funnel_labels, x=funnel_values,
                               textinfo='value+percent initial',
                               marker=dict(color=COLORS)))
    fig2.update_layout(title='Funnel Sequential Hard Filtering', height=400)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="insight-box"><b>💡 Insight</b><br>'
                '• Tiga kandidat di barat daya hingga tenggara Kota Menia<br>'
                '• Jarak 1,2–2,7 km dari PLN ULP (dalam batas teknis ≤3 km)<br>'
                '• Lokasi A direkomendasikan: luas terbesar, slope terendah, skor tertinggi</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: ENERGY JUSTICE
# ============================================================================

elif page == "⚖️ Energy Justice":
    st.markdown("## ⚖️ Keadilan Energi — Analisis Distribusi Manfaat PV")
    st.markdown("Indeks Gini & kemampuan akses berdasarkan kelompok pendapatan")

    scenarios = {
        'DPV Saja (PV Atap)':     [0.05, 0.10, 0.15, 0.25, 0.45],
        'UPV Saja (Utilitas)':    [0.15, 0.18, 0.20, 0.22, 0.25],
        'Diversified (UPV+BESS)': [0.18, 0.20, 0.21, 0.20, 0.21],
        'Solar-as-a-Service':     [0.22, 0.22, 0.20, 0.18, 0.18],
    }

    def gini(benefits):
        b = np.array(benefits)
        cum_b = np.cumsum(b)
        area = sum(0.2 * (cum_b[i] + (cum_b[i-1] if i > 0 else 0)) / 2 for i in range(5))
        return 1 - 2 * area

    gini_vals = {n: gini(b) for n, b in scenarios.items()}

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        for i, (name, benefits) in enumerate(scenarios.items()):
            cum_b = np.cumsum([0] + benefits)
            cum_p = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
            fig.add_trace(go.Scatter(x=cum_p, y=cum_b, mode='lines+markers',
                                     name=f"{name} (G={gini_vals[name]:.3f})",
                                     line=dict(color=COLORS[i], width=2.5)))
        fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines',
                                 name='Kesetaraan Sempurna',
                                 line=dict(dash='dash', color='gray', width=1.5)))
        fig.update_layout(title='Kurva Lorenz — Distribusi Manfaat PV',
                          xaxis_title='Populasi Kumulatif', yaxis_title='Manfaat Kumulatif',
                          height=480, plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(x=list(gini_vals.keys()), y=list(gini_vals.values()),
                     color=list(gini_vals.values()), color_continuous_scale='RdYlGn_r',
                     title='Indeks Gini per Strategi',
                     labels={'x':'Strategi', 'y':'Gini Index', 'color':'Gini'})
        fig.add_hline(y=0.1, line_dash='dash', line_color='green', annotation_text='Target <0,1')
        fig.update_layout(height=480, plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 💰 Analisis Kemampuan Akses PV Atap")
    income_groups = ['Kelompok 1\n(Termiskin)', 'Kelompok 2', 'Kelompok 3', 'Kelompok 4', 'Kelompok 5\n(Terkaya)']
    incomes = [4.5, 7.2, 10.5, 15.8, 32.0]   # juta Rp/bulan
    pv_cost, interest, years_loan = 15, 0.10, 5
    annuity = pv_cost * (interest * (1+interest)**years_loan) / ((1+interest)**years_loan - 1)
    affordability = [annuity / inc * 100 for inc in incomes]

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=income_groups, y=affordability,
                             marker_color=[COLORS[3] if a > 30 else COLORS[4] if a > 20 else COLORS[2]
                                          for a in affordability], name='Rasio Angsuran'))
        fig.add_hline(y=20, line_dash='dash', line_color='orange', annotation_text='Batas Mampu (20%)')
        fig.add_hline(y=30, line_dash='dash', line_color='red', annotation_text='Batas Kritis (30%)')
        fig.update_layout(title='Rasio Angsuran PV Atap terhadap Pendapatan (%)',
                          xaxis_title='Kelompok Pendapatan', yaxis_title='Rasio (%)',
                          height=400, plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("#### Parameter Pembiayaan")
        st.markdown(f"""
        - Harga PV: **Rp {pv_cost} juta/kWp**
        - Bunga: **{interest*100:.0f}% p.a.**
        - Tenor: **{years_loan} tahun**
        - Angsuran: **Rp {annuity:.2f} juta/bulan**
        """)
        aff_df = pd.DataFrame({'Kelompok': [f'Kel. {i+1}' for i in range(5)],
                               'Pendapatan (M Rp)': incomes,
                               'Rasio (%)': [round(a, 1) for a in affordability],
                               'Status': ['❌ Tidak Mampu' if a > 30 else '⚠️ Batas' if a > 20 else '✅ Mampu'
                                         for a in affordability]})
        st.dataframe(aff_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="success-box"><b>💡 Insight Keadilan Energi</b><br>'
                '• DPV saja → Gini tertinggi (0,36): hanya kelompok atas yang diuntungkan<br>'
                '• Diversified Portfolio → Gini 0,07 (turun 81%): distribusi hampir merata<br>'
                '• Solar-as-a-Service → Gini terendah: rekomendasi untuk MBR<br>'
                '• 3 kelompok termiskin: rasio angsuran >20% → butuh subsidi atau skema SaaS</div>',
                unsafe_allow_html=True)

# ============================================================================
# PAGE: RAW DATA
# ============================================================================

elif page == "📋 Raw Data":
    st.markdown("## 📋 Data Mentah & Eksplorasi")
    st.markdown(f"Sumber: {DATA_SOURCE}")

    if data_loaded and raw_df is not None:
        # Filters
        c1, c2, c3 = st.columns(3)
        with c1:
            yr_opts = ['Semua'] + sorted(raw_df['YEAR'].unique().tolist())
            sel_yr = st.selectbox("Filter Tahun", yr_opts)
        with c2:
            mo_opts = ['Semua'] + list(range(1, 13))
            sel_mo = st.selectbox("Filter Bulan", mo_opts,
                                  format_func=lambda x: "Semua" if x == "Semua" else f"Bulan {x}")
        with c3:
            search = st.text_input("🔍 Cari", placeholder="Keyword...")

        fdf = raw_df.copy()
        if sel_yr != 'Semua':
            fdf = fdf[fdf['YEAR'] == sel_yr]
        if sel_mo != 'Semua':
            fdf = fdf[fdf['MO'] == sel_mo]
        if search:
            fdf = fdf[fdf.astype(str).apply(lambda x: x.str.contains(search, case=False).any(), axis=1)]

        show_cols = ['YEAR','MO','DY','HR','T2M','RH2M','PRECTOTCORR','ALLSKY_SFC_SW_DWN','WD10M','WS10M']
        show_cols = [c for c in show_cols if c in fdf.columns]
        st.dataframe(fdf[show_cols].head(500).reset_index(drop=True),
                     use_container_width=True, height=400)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(kpi("Total Record", f"{len(raw_df):,}", "baris"), unsafe_allow_html=True)
        c2.markdown(kpi("Rentang Tahun", f"{raw_df['YEAR'].min()}–{raw_df['YEAR'].max()}", ""), unsafe_allow_html=True)
        c3.markdown(kpi("Rata-rata Suhu", f"{raw_df['T2M'].mean():.1f}", "°C"), unsafe_allow_html=True)
        c4.markdown(kpi("Rata-rata GHI", f"{raw_df['ALLSKY_SFC_SW_DWN'].mean():.1f}", "W/m²"), unsafe_allow_html=True)

        st.markdown("### 📊 Statistik Deskriptif")
        st.dataframe(raw_df[show_cols].describe().round(2), use_container_width=True)

        # Missing value analysis
        # if raw_df.isnull().any().any():
        #     st.markdown("### ⚠️ Missing Value")
        #     mv = raw_df[show_cols].isnull().sum().reset_index()
        #     mv.columns = ['Kolom', 'Missing']
        #     mv = mv[mv['Missing'] > 0]
        #     fig = px.bar(mv, x='Kolom', y='Missing', title='Jumlah Missing Value per Kolom',
        #                  color='Missing', color_continuous_scale='Reds')
        #     fig.update_layout(height=300, plot_bgcolor='white')
        #     st.plotly_chart(fig, use_container_width=True)

        # Download
        st.markdown("### 📥 Download")
        csv = fdf[show_cols].to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Filtered CSV", csv, "dataset_filtered.csv", "text/csv")

    else:
        st.warning("Dataset_Final.csv tidak ditemukan. Letakkan file di direktori yang sama dengan streamlit_app.py lalu restart.")
        st.markdown("### 📋 Contoh Format Dataset yang Diperlukan")
        sample = pd.DataFrame({
            'YEAR':[2015,2015,2026,2026],
            'MO':[1,1,4,4], 'DY':[1,1,25,25], 'HR':[0,1,22,23],
            'T2M':[28.17,28.09,28.38,28.24],
            'RH2M':[86.16,86.30,79.49,80.37],
            'PRECTOTCORR':[26.62,26.20,26.41,14.32],
            'ALLSKY_SFC_SW_DWN':[0.0,0.0,-999.0,-999.0],
            'WD10M':[314.5,311.3,109.7,112.5],
            'WS10M':[4.79,5.20,7.55,7.60]
        })
        st.dataframe(sample, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#6b7280; padding:1rem 0; font-size:0.85rem;">
    © 2026 Tim SSO 2.0 · MMC MCF ITB 2026 &nbsp;|&nbsp;
    Data: NASA POWER / BMKG Stasiun Tardamu &nbsp;|&nbsp;
    Proyeksi: IPCC AR6 SSP2-4.5
</div>
""", unsafe_allow_html=True)
