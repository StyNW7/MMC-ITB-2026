from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "Dataset_MMC - Data BMKG NTT.csv"
LIST_DIR = BASE_DIR / "list"
IMAGE_DIR = BASE_DIR / "list-gambar"


@dataclass
class ModelParameters:
    eta_ref: float
    temp_coeff: float
    alpha: float
    pr: float
    area_m2_per_kwp: float
    pv_degradation: float
    bess_degradation: float
    firm_degradation: float
    inverter_efficiency: float
    haze_tau: float
    path_length: float
    cleaning_loss_monthly: float
    annual_temp_increase: float
    discount_rate: float
    low_state_threshold: float
    monte_carlo_runs: int
    planning_horizon: int
    peak_demand_mw: float
    annual_demand_growth: float
    bess_roundtrip_eff: float
    value_of_lost_load: float
    pv_capex_per_mw: float
    bess_capex_per_mwh: float
    firm_capex_per_mw: float
    pv_opex_ratio: float
    bess_opex_ratio: float
    firm_opex_ratio: float
    plant_size_mw: float
    oversizing_pct: float


def inject_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

            :root {
                --bg: #f4efe6;
                --card: rgba(255, 250, 242, 0.92);
                --ink: #14211d;
                --muted: #5f6b68;
                --accent: #0f766e;
                --accent-2: #d97706;
                --line: rgba(20, 33, 29, 0.09);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(15, 118, 110, 0.10), transparent 28%),
                    radial-gradient(circle at top right, rgba(217, 119, 6, 0.10), transparent 22%),
                    linear-gradient(180deg, #fbf7f0 0%, #f1ebe2 100%);
                color: var(--ink);
                font-family: 'IBM Plex Sans', sans-serif;
            }

            h1, h2, h3, h4 {
                font-family: 'Space Grotesk', sans-serif !important;
                color: var(--ink);
                letter-spacing: -0.02em;
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 3rem;
                max-width: 1450px;
            }

            .hero {
                padding: 1.6rem 1.8rem;
                border-radius: 26px;
                background:
                    linear-gradient(135deg, rgba(15, 118, 110, 0.92) 0%, rgba(13, 52, 55, 0.94) 62%, rgba(217, 119, 6, 0.88) 100%);
                color: #fffaf3;
                box-shadow: 0 24px 80px rgba(15, 118, 110, 0.18);
                border: 1px solid rgba(255, 255, 255, 0.10);
                margin-bottom: 1rem;
            }

            .hero h1, .hero h3, .hero p {
                color: #fffaf3 !important;
            }

            .metric-card {
                background: var(--card);
                border: 1px solid var(--line);
                padding: 1rem 1.1rem;
                border-radius: 20px;
                box-shadow: 0 18px 45px rgba(21, 31, 29, 0.06);
                min-height: 120px;
            }

            .metric-card .label {
                color: var(--muted);
                font-size: 0.90rem;
                margin-bottom: 0.2rem;
            }

            .metric-card .value {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.8rem;
                font-weight: 700;
                color: var(--ink);
            }

            .metric-card .sub {
                color: var(--muted);
                font-size: 0.92rem;
            }

            .section-card {
                background: var(--card);
                border-radius: 24px;
                border: 1px solid var(--line);
                padding: 1rem 1.1rem;
                box-shadow: 0 18px 45px rgba(21, 31, 29, 0.06);
            }

            .small-note {
                color: var(--muted);
                font-size: 0.90rem;
            }

            div[data-testid="stMetric"] {
                background: var(--card);
                border: 1px solid var(--line);
                border-radius: 18px;
                padding: 0.9rem 1rem;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
            }

            .stTabs [data-baseweb="tab"] {
                background: rgba(255,255,255,0.55);
                border-radius: 999px;
                padding: 0.55rem 1rem;
                border: 1px solid rgba(20,33,29,0.08);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def read_markdown_file(path: Path) -> str:
    if not path.exists():
        return f"Missing file: {path.name}"
    return path.read_text(encoding="utf-8", errors="ignore")


def clean_numeric(value: object) -> float:
    if value is None:
        return np.nan
    text = str(value).strip().replace('"', "")
    if not text:
        return np.nan
    text = text.replace("%", "")
    text = text.replace(".", "").replace(",", ".") if text.count(",") == 1 and text.count(".") > 1 else text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return np.nan


def preprocess_csv_text(raw_text: str) -> str:
    processed_lines: List[str] = []
    for idx, line in enumerate(raw_text.splitlines()):
        if idx == 0 or not line.strip():
            processed_lines.append(line)
            continue
        fixed = line
        fixed = fixed.replace("\ufeff", "")
        fixed = fixed.replace('""', '"')
        fixed = fixed.replace(',""', ',"')
        if fixed.startswith('"') and len(fixed) > 12:
            fixed = fixed[1:]
        fixed = fixed.replace('",', ',', 1)
        processed_lines.append(fixed)
    return "\n".join(processed_lines)


@st.cache_data(show_spinner=False)
def load_bmkg_dataset() -> pd.DataFrame:
    raw_text = DATASET_PATH.read_text(encoding="utf-8", errors="ignore")
    cleaned_text = preprocess_csv_text(raw_text)
    reader = csv.reader(io.StringIO(cleaned_text))
    rows = list(reader)
    header = rows[0]
    data_rows = [row for row in rows[1:] if row]
    normalized_rows = []
    for row in data_rows:
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        normalized_rows.append(row[: len(header)])

    df = pd.DataFrame(normalized_rows, columns=header)
    df.columns = [col.strip() for col in df.columns]
    df["TANGGAL"] = df["TANGGAL"].astype(str).str.replace('"', "").str.strip()
    df["Date"] = pd.to_datetime(df["TANGGAL"], format="%d-%m-%Y", errors="coerce")

    numeric_cols = [col for col in df.columns if col not in {"TANGGAL", "DDD_CAR", "Date"}]
    for col in numeric_cols:
        df[col] = df[col].apply(clean_numeric)

    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    df["Month"] = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.strftime("%b")
    df["Year"] = df["Date"].dt.year
    return df


def compute_physical_model(df: pd.DataFrame, params: ModelParameters) -> pd.DataFrame:
    model = df.copy()
    model["G_model"] = (model["SS"] / 12.0) * 1000.0
    model["Tp_model"] = model["TAVG"] + params.alpha * model["G_model"]
    model["eta_model"] = params.eta_ref * (1.0 - params.temp_coeff * (model["Tp_model"] - 25.0))
    model["eta_model"] = model["eta_model"].clip(lower=0.05)
    model["P_w_model"] = model["G_model"] * params.area_m2_per_kwp * model["eta_model"] * params.pr
    model["P_kw_model"] = model["P_w_model"] / 1000.0
    model["E_kwh_model"] = model["P_kw_model"] * model["SS"]
    model["CF_daily"] = model["SS"] / 24.0
    model["thermal_penalty_pct"] = (1.0 - (model["eta_model"] / params.eta_ref)) * 100.0
    return model


def monthly_summary(model_df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        model_df.groupby(["Month", "MonthName"], as_index=False)
        .agg(
            SS_avg=("SS", "mean"),
            G_avg=("G_model", "mean"),
            Tavg_avg=("TAVG", "mean"),
            Tp_avg=("Tp_model", "mean"),
            Eta_avg=("eta_model", "mean"),
            P_kw_avg=("P_kw_model", "mean"),
            E_kwh_daily_avg=("E_kwh_model", "mean"),
            E_kwh_total=("E_kwh_model", "sum"),
            CV_energy=("E_kwh_model", lambda s: 100.0 * s.std(ddof=0) / s.mean() if s.mean() else np.nan),
        )
        .sort_values("Month")
    )
    return grouped


def annual_baseline_metrics(model_df: pd.DataFrame) -> Dict[str, float]:
    return {
        "ss_avg": model_df["SS"].mean(),
        "g_avg": model_df["G_model"].mean(),
        "tavg_avg": model_df["TAVG"].mean(),
        "tp_avg": model_df["Tp_model"].mean(),
        "eta_avg": model_df["eta_model"].mean(),
        "p_kw_avg": model_df["P_kw_model"].mean(),
        "e_daily_avg": model_df["E_kwh_model"].mean(),
        "e_annual_total": model_df["E_kwh_model"].sum(),
        "cv_energy": 100.0 * model_df["E_kwh_model"].std(ddof=0) / model_df["E_kwh_model"].mean(),
    }


def build_climate_projection(
    model_df: pd.DataFrame,
    params: ModelParameters,
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(random_seed)
    monthly_base = (
        model_df.groupby("Month", as_index=False)
        .agg(
            SS=("SS", "mean"),
            TAVG=("TAVG", "mean"),
            RH_AVG=("RH_AVG", "mean"),
            Rain=("RR", "mean"),
        )
        .sort_values("Month")
    )

    years = np.arange(2024, 2024 + params.planning_horizon + 1)
    periods = []
    for year in years:
        year_offset = year - years[0]
        climate_temp_shift = params.annual_temp_increase * year_offset
        trend_factor = 1.0 - 0.0015 * year_offset
        for _, row in monthly_base.iterrows():
            month = int(row["Month"])
            month_phase = 2 * np.pi * (month - 1) / 12.0

            clear_sky = max(250.0, (row["SS"] / 12.0) * 1000.0)
            cloud_cover = np.clip(
                0.24
                + 0.08 * np.sin(month_phase + 0.5)
                + 0.0012 * year_offset
                + rng.normal(0, 0.035),
                0.05,
                0.82,
            )

            pm25 = np.clip(
                22.0
                + 7.0 * np.sin(month_phase - 0.3)
                + 0.18 * year_offset
                + rng.normal(0, 2.4),
                8.0,
                80.0,
            )

            haze_event = rng.random() < min(0.04 + 0.0015 * year_offset, 0.16)
            if haze_event:
                pm25 *= rng.uniform(1.35, 1.9)

            haze_att = math.exp(-params.haze_tau * pm25 * params.path_length)
            haze_att = np.clip(haze_att, 0.72, 0.995)

            g_actual = clear_sky * (1.0 - cloud_cover) * haze_att * trend_factor
            tavg = row["TAVG"] + climate_temp_shift + rng.normal(0, 0.45)
            tp = tavg + params.alpha * g_actual
            eta = max(0.05, params.eta_ref * (1.0 - params.temp_coeff * (tp - 25.0)))
            temp_loss = eta / params.eta_ref
            soiling_loss = np.clip(params.cleaning_loss_monthly + 0.002 * max(0.0, 40.0 - row["Rain"]) / 40.0, 0.01, 0.08)

            p_out_kw = (
                params.plant_size_mw
                * 1000.0
                * (g_actual / 1000.0)
                * temp_loss
                * (1.0 - soiling_loss)
                * params.inverter_efficiency
            )

            energy_mwh = p_out_kw * (30.42 * row["SS"]) / 1000.0

            periods.append(
                {
                    "Year": year,
                    "Month": month,
                    "Date": pd.Timestamp(year=year, month=month, day=1),
                    "Tavg_projected": tavg,
                    "Cloud_cover": cloud_cover,
                    "PM25": pm25,
                    "Haze_att": haze_att,
                    "Clear_sky_G": clear_sky,
                    "G_actual": g_actual,
                    "Tp": tp,
                    "Eta": eta,
                    "Temp_loss_factor": temp_loss,
                    "Soiling_loss": soiling_loss,
                    "Power_kw": p_out_kw,
                    "Energy_mwh": energy_mwh,
                    "Haze_event": int(haze_event),
                }
            )

    climate_df = pd.DataFrame(periods)
    climate_df["Decade"] = (climate_df["Year"] // 10) * 10

    annual_df = (
        climate_df.groupby("Year", as_index=False)
        .agg(
            Mean_power_kw=("Power_kw", "mean"),
            Total_energy_mwh=("Energy_mwh", "sum"),
            Mean_temp=("Tavg_projected", "mean"),
            Mean_haze_att=("Haze_att", "mean"),
            Mean_temp_loss=("Temp_loss_factor", "mean"),
            Mean_cloud_cover=("Cloud_cover", "mean"),
            Haze_events=("Haze_event", "sum"),
        )
    )

    baseline = annual_df.loc[annual_df["Year"].between(years[0], years[0] + 4), "Mean_power_kw"].mean()
    annual_df["Production_change_pct"] = ((annual_df["Mean_power_kw"] / baseline) - 1.0) * 100.0

    run_summaries = []
    for run in range(params.monte_carlo_runs):
        run_df, _, _ = build_climate_projection_single_run(model_df, params, random_seed + 1000 + run)
        run_summary = run_df.groupby("Year", as_index=False)["Mean_power_kw"].mean()
        run_summary["Run"] = run
        run_summaries.append(run_summary)
    uncertainty_df = pd.concat(run_summaries, ignore_index=True)
    return climate_df, annual_df, uncertainty_df


def build_climate_projection_single_run(
    model_df: pd.DataFrame,
    params: ModelParameters,
    random_seed: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, None]:
    rng = np.random.default_rng(random_seed)
    monthly_base = (
        model_df.groupby("Month", as_index=False)
        .agg(SS=("SS", "mean"), TAVG=("TAVG", "mean"), Rain=("RR", "mean"))
        .sort_values("Month")
    )
    years = np.arange(2024, 2024 + params.planning_horizon + 1)
    periods = []
    for year in years:
        year_offset = year - years[0]
        for _, row in monthly_base.iterrows():
            month_phase = 2 * np.pi * (int(row["Month"]) - 1) / 12.0
            cloud_cover = np.clip(0.24 + 0.08 * np.sin(month_phase + 0.5) + 0.0012 * year_offset + rng.normal(0, 0.045), 0.05, 0.82)
            pm25 = np.clip(22.0 + 7.0 * np.sin(month_phase - 0.3) + 0.18 * year_offset + rng.normal(0, 3.0), 8.0, 85.0)
            if rng.random() < min(0.04 + 0.0015 * year_offset, 0.16):
                pm25 *= rng.uniform(1.35, 1.9)
            haze_att = np.clip(math.exp(-params.haze_tau * pm25 * params.path_length), 0.72, 0.995)
            g_actual = max(180.0, (row["SS"] / 12.0) * 1000.0) * (1.0 - cloud_cover) * haze_att * (1.0 - 0.0015 * year_offset)
            tavg = row["TAVG"] + params.annual_temp_increase * year_offset + rng.normal(0, 0.55)
            tp = tavg + params.alpha * g_actual
            eta = max(0.05, params.eta_ref * (1.0 - params.temp_coeff * (tp - 25.0)))
            soiling_loss = np.clip(params.cleaning_loss_monthly + 0.002 * max(0.0, 40.0 - row["Rain"]) / 40.0, 0.01, 0.08)
            p_out_kw = params.plant_size_mw * 1000.0 * (g_actual / 1000.0) * (eta / params.eta_ref) * (1.0 - soiling_loss) * params.inverter_efficiency
            periods.append({"Year": year, "Mean_power_kw": p_out_kw})
    monthly = pd.DataFrame(periods)
    annual = monthly.groupby("Year", as_index=False)["Mean_power_kw"].mean()
    return annual, monthly, None


def estimate_markov_chain(model_df: pd.DataFrame, threshold: float) -> Tuple[pd.DataFrame, np.ndarray]:
    daily = model_df[["Date", "CF_daily"]].copy()
    daily["State"] = np.where(daily["CF_daily"] < threshold, "Low", "Normal")
    daily["NextState"] = daily["State"].shift(-1)
    transitions = pd.crosstab(daily["State"], daily["NextState"], normalize="index").reindex(index=["Low", "Normal"], columns=["Low", "Normal"]).fillna(0.0)
    matrix = transitions.to_numpy()
    return daily, matrix


def simulate_markov_states(
    transition_matrix: np.ndarray,
    horizon_years: int,
    threshold: float,
    random_seed: int = 10,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_seed)
    states = ["Low", "Normal"]
    cf_map = {"Low": 0.1342, "Normal": 0.3333}
    current = 0 if threshold > 0.30 else 1
    periods = []
    for year in range(2024, 2024 + horizon_years + 1):
        for month in range(1, 13):
            current_state = states[current]
            periods.append(
                {
                    "Date": pd.Timestamp(year=year, month=month, day=1),
                    "Year": year,
                    "Month": month,
                    "State": current_state,
                    "CF": cf_map[current_state],
                }
            )
            probs = transition_matrix[current]
            if probs.sum() <= 0:
                probs = np.array([0.1053, 0.8947])
            current = rng.choice([0, 1], p=probs / probs.sum())
    return pd.DataFrame(periods)


def build_strategy_table(params: ModelParameters, annual_df: pd.DataFrame) -> pd.DataFrame:
    years = annual_df["Year"].to_numpy()
    climate_factor = (annual_df["Mean_power_kw"] / annual_df["Mean_power_kw"].iloc[0]).clip(lower=0.72)
    demand = params.peak_demand_mw * (1.0 + params.annual_demand_growth) ** (years - years[0])

    strategies = {
        "Rapid Distributed PV": {"pv": 1.10, "bess_h": 1.5, "firm": 0.08, "equity": 0.58},
        "Utility-scale PV": {"pv": 1.32, "bess_h": 2.2, "firm": 0.12, "equity": 0.73},
        "Storage-led": {"pv": 1.18, "bess_h": 4.6, "firm": 0.16, "equity": 0.77},
        "Diversified Portfolio": {"pv": 1.38, "bess_h": 3.8, "firm": 0.22, "equity": 0.86},
    }

    rows = []
    for name, spec in strategies.items():
        pv_mw = params.peak_demand_mw * (1.0 + params.oversizing_pct) * spec["pv"]
        bess_mwh = params.peak_demand_mw * spec["bess_h"]
        firm_mw = params.peak_demand_mw * spec["firm"]

        pv_generation = pv_mw * climate_factor * 24.0
        firm_generation = firm_mw * 24.0 * (1.0 - params.firm_degradation) ** (years - years[0])
        storage_support = bess_mwh * params.bess_roundtrip_eff * 0.45
        demand_energy = demand * 24.0

        unserved = np.maximum(0.0, demand_energy - (pv_generation + firm_generation + storage_support))
        eens = unserved.mean()
        resilience = 1.0 - min(1.0, eens / max(demand_energy.mean(), 1e-9))

        capex = (
            pv_mw * params.pv_capex_per_mw
            + bess_mwh * params.bess_capex_per_mwh
            + firm_mw * params.firm_capex_per_mw
        )

        yearly_opex = (
            pv_mw * params.pv_capex_per_mw * params.pv_opex_ratio
            + bess_mwh * params.bess_capex_per_mwh * params.bess_opex_ratio
            + firm_mw * params.firm_capex_per_mw * params.firm_opex_ratio
        )

        discounted_opex = 0.0
        discounted_unserved = 0.0
        for offset, loss in enumerate(unserved):
            factor = 1.0 / ((1.0 + params.discount_rate) ** offset)
            discounted_opex += yearly_opex * factor
            discounted_unserved += loss * 365.0 * params.value_of_lost_load * factor

        total_cost = capex + discounted_opex + discounted_unserved
        lcoe = total_cost / max((pv_generation.mean() + firm_generation.mean()) * 365.0 * len(years), 1e-9)
        gini_energy = 1.0 - spec["equity"]

        rows.append(
            {
                "Strategy": name,
                "PV_MW": pv_mw,
                "BESS_MWh": bess_mwh,
                "Firm_MW": firm_mw,
                "EENS_MWh_per_day": eens,
                "Total_discounted_cost_usd": total_cost,
                "LCOE_usd_per_MWh": lcoe,
                "Resilience_score": resilience * 100.0,
                "Equity_score": spec["equity"] * 100.0,
                "Energy_Gini": gini_energy,
            }
        )

    result = pd.DataFrame(rows)
    result["Rank_score"] = (
        0.35 * (1.0 - (result["Total_discounted_cost_usd"] / max(result["Total_discounted_cost_usd"].max(), 1e-9)))
        + 0.30 * (1.0 - (result["EENS_MWh_per_day"] / max(result["EENS_MWh_per_day"].max(), 1e-9)))
        + 0.20 * (result["Resilience_score"] / 100.0)
        + 0.15 * (result["Equity_score"] / 100.0)
    )
    result = result.sort_values("Rank_score", ascending=False).reset_index(drop=True)
    return result


def build_investment_path(best_strategy: pd.Series, annual_df: pd.DataFrame, params: ModelParameters) -> pd.DataFrame:
    years = annual_df["Year"].to_numpy()
    growth = np.linspace(0.32, 1.0, len(years))
    path_df = pd.DataFrame(
        {
            "Year": years,
            "PV_MW": best_strategy["PV_MW"] * growth,
            "BESS_MWh": best_strategy["BESS_MWh"] * np.sqrt(growth),
            "Firm_MW": best_strategy["Firm_MW"] * np.minimum(1.0, growth * 1.08),
        }
    )
    path_df["Demand_MW"] = params.peak_demand_mw * (1.0 + params.annual_demand_growth) ** (path_df["Year"] - years[0])
    return path_df


def build_location_candidates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Candidate": "North-Central Grid Ring",
                "Available_ha": 104,
                "Potential_MWp": 104,
                "Slope_deg": 7.2,
                "Distance_to_grid_km": 1.6,
                "Land_status": "Open dry land",
                "Suitability_score": 91,
            },
            {
                "Candidate": "West Coastal Plateau",
                "Available_ha": 86,
                "Potential_MWp": 86,
                "Slope_deg": 9.1,
                "Distance_to_grid_km": 2.1,
                "Land_status": "Shrub / non-forest",
                "Suitability_score": 87,
            },
            {
                "Candidate": "South-East Expansion Block",
                "Available_ha": 75,
                "Potential_MWp": 75,
                "Slope_deg": 11.8,
                "Distance_to_grid_km": 2.8,
                "Land_status": "Mixed open land",
                "Suitability_score": 82,
            },
        ]
    )


def energy_benefit_curve(strategy_name: str) -> pd.DataFrame:
    incomes = np.array([1, 2, 3, 4, 5], dtype=float)
    if strategy_name == "Rapid Distributed PV":
        benefits = np.array([4, 7, 14, 26, 49], dtype=float)
    elif strategy_name == "Utility-scale PV":
        benefits = np.array([10, 13, 18, 26, 33], dtype=float)
    elif strategy_name == "Storage-led":
        benefits = np.array([11, 14, 19, 25, 31], dtype=float)
    else:
        benefits = np.array([13, 15, 19, 24, 29], dtype=float)

    population_share = incomes / incomes.sum()
    benefit_share = benefits / benefits.sum()
    curve = pd.DataFrame(
        {
            "IncomeGroup": ["Q1 Lowest", "Q2", "Q3", "Q4", "Q5 Highest"],
            "PopulationShare": population_share,
            "BenefitShare": benefit_share,
        }
    )
    curve["CumPopulation"] = curve["PopulationShare"].cumsum()
    curve["CumBenefit"] = curve["BenefitShare"].cumsum()
    return curve


def gini_from_curve(curve_df: pd.DataFrame) -> float:
    x = np.concatenate([[0.0], curve_df["CumPopulation"].to_numpy()])
    y = np.concatenate([[0.0], curve_df["CumBenefit"].to_numpy()])
    area = np.trapz(y, x)
    return 1.0 - 2.0 * area


def confidence_band(uncertainty_df: pd.DataFrame) -> pd.DataFrame:
    band = (
        uncertainty_df.groupby("Year")["Mean_power_kw"]
        .agg(
            Mean="mean",
            P05=lambda s: np.quantile(s, 0.05),
            P25=lambda s: np.quantile(s, 0.25),
            P75=lambda s: np.quantile(s, 0.75),
            P95=lambda s: np.quantile(s, 0.95),
        )
        .reset_index()
    )
    return band


def recommendation_text(strategy_table: pd.DataFrame, annual_df: pd.DataFrame, params: ModelParameters) -> List[str]:
    best = strategy_table.iloc[0]
    decline = abs((annual_df["Mean_power_kw"].iloc[-1] / annual_df["Mean_power_kw"].iloc[0] - 1.0) * 100.0)
    temp_rise = annual_df["Mean_temp"].iloc[-1] - annual_df["Mean_temp"].iloc[0]
    return [
        f"Primary portfolio: {best['Strategy']} because it leads the composite score with the lowest combined cost-risk profile.",
        f"Oversize PV by {params.oversizing_pct * 100:.0f}% to absorb the modeled climate penalty, which reaches roughly {decline:.1f}% by the end of the horizon.",
        f"Scale storage toward {best['BESS_MWh']:.1f} MWh equivalent to smooth the modeled inter-seasonal volatility and load-risk tail.",
        f"Retain at least {best['Firm_MW']:.2f} MW of firm capacity for essential services and deep low-solar events.",
        f"Plan for a mean temperature increase of about {temp_rise:.2f} degC and keep module temperature coefficient below -0.3%/degC where procurement allows.",
        "Use utility-scale deployment near the filtered grid-adjacent sites first, then layer inclusive access programs such as Solar-as-a-Service to improve equity.",
    ]


def render_metric_cards(metrics: List[Tuple[str, str, str]]) -> None:
    cols = st.columns(len(metrics))
    for col, (label, value, sub) in zip(cols, metrics):
        col.markdown(
            f"""
            <div class="metric-card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
                <div class="sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    st.set_page_config(
        page_title="MMC ITB 2026 | Mathematical Model Simulator",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    st.markdown(
        """
        <div class="hero">
            <h1>Climate-Resilient PV Planning Simulator</h1>
            <p>Interactive Streamlit dashboard for the MMC ITB 2026 mathematical model. It combines BMKG-based PV physics, climate penalty projection, Markov-chain solar states, strategy comparison, location screening, energy equity, and policy recommendations in one application.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Simulation Controls")
        plant_size_mw = st.slider("Reference utility-scale plant (MW)", 1.0, 60.0, 15.0, 0.5)
        planning_horizon = st.slider("Planning horizon (years)", 20, 50, 50, 5)
        monte_carlo_runs = st.slider("Monte Carlo runs", 50, 400, 160, 10)
        peak_demand_mw = st.slider("Peak demand served (MW)", 2.0, 50.0, 12.0, 0.5)
        oversizing_pct = st.slider("Oversizing ratio", 0.00, 0.35, 0.18, 0.01)
        annual_temp_increase = st.slider("Annual temperature increase (degC/year)", 0.015, 0.040, 0.028, 0.001)
        pv_degradation = st.slider("PV degradation per year", 0.003, 0.012, 0.006, 0.001)
        discount_rate = st.slider("Discount rate", 0.03, 0.14, 0.08, 0.01)
        annual_demand_growth = st.slider("Annual demand growth", 0.00, 0.08, 0.025, 0.005)
        low_state_threshold = st.slider("Low-solar state threshold (CF)", 0.10, 0.35, 0.30, 0.01)

        st.header("Physical Assumptions")
        eta_ref = st.slider("Reference efficiency", 0.14, 0.26, 0.20, 0.01)
        temp_coeff = st.slider("Temperature coefficient", 0.002, 0.006, 0.004, 0.001)
        alpha = st.slider("Panel temperature rise alpha", 0.01, 0.05, 0.03, 0.005)
        pr = st.slider("Performance ratio", 0.65, 0.90, 0.80, 0.01)
        inverter_efficiency = st.slider("Inverter efficiency", 0.88, 0.99, 0.96, 0.01)

    params = ModelParameters(
        eta_ref=eta_ref,
        temp_coeff=temp_coeff,
        alpha=alpha,
        pr=pr,
        area_m2_per_kwp=50.0,
        pv_degradation=pv_degradation,
        bess_degradation=0.03,
        firm_degradation=0.01,
        inverter_efficiency=inverter_efficiency,
        haze_tau=0.00095,
        path_length=1.8,
        cleaning_loss_monthly=0.022,
        annual_temp_increase=annual_temp_increase,
        discount_rate=discount_rate,
        low_state_threshold=low_state_threshold,
        monte_carlo_runs=monte_carlo_runs,
        planning_horizon=planning_horizon,
        peak_demand_mw=peak_demand_mw,
        annual_demand_growth=annual_demand_growth,
        bess_roundtrip_eff=0.90,
        value_of_lost_load=1200.0,
        pv_capex_per_mw=670000.0,
        bess_capex_per_mwh=260000.0,
        firm_capex_per_mw=930000.0,
        pv_opex_ratio=0.018,
        bess_opex_ratio=0.022,
        firm_opex_ratio=0.040,
        plant_size_mw=plant_size_mw,
        oversizing_pct=oversizing_pct,
    )

    model_df = compute_physical_model(load_bmkg_dataset(), params)
    monthly_df = monthly_summary(model_df)
    baseline = annual_baseline_metrics(model_df)
    climate_df, annual_df, uncertainty_df = build_climate_projection(model_df, params)
    uncertainty_band = confidence_band(uncertainty_df)
    markov_daily, transition_matrix = estimate_markov_chain(model_df, params.low_state_threshold)
    markov_sim = simulate_markov_states(transition_matrix, params.planning_horizon, params.low_state_threshold)
    strategy_table = build_strategy_table(params, annual_df)
    best_strategy = strategy_table.iloc[0]
    path_df = build_investment_path(best_strategy, annual_df, params)
    locations_df = build_location_candidates()
    recommendation_lines = recommendation_text(strategy_table, annual_df, params)

    page = st.radio(
        "Navigation",
        [
            "Executive Overview",
            "Historical Data & Physics",
            "Climate Penalty Projection",
            "Markov Chain & Reliability",
            "Strategy Optimization",
            "Site Screening & Equity",
            "Model Library",
        ],
        horizontal=True,
    )

    if page == "Executive Overview":
        render_metric_cards(
            [
                ("Historical annual production", f"{baseline['e_annual_total']:,.0f} kWh", "Modeled from BMKG 2025 daily records"),
                ("Average thermal penalty", f"{(1 - baseline['eta_avg']/params.eta_ref) * 100:,.1f}%", "Efficiency loss relative to STC"),
                ("End-horizon production change", f"{annual_df['Production_change_pct'].iloc[-1]:,.1f}%", "Compared with 2024-2028 baseline"),
                ("Best strategy", best_strategy["Strategy"], "Highest combined score"),
            ]
        )

        left, right = st.columns([1.45, 1.0], gap="large")
        with left:
            st.subheader("System Storyline")
            overview_fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Historical Monthly Energy",
                    "Mean Annual Climate-Affected Power",
                    "Strategy Cost vs Reliability",
                    "Candidate Site Potential",
                ),
            )
            overview_fig.add_trace(
                go.Bar(x=monthly_df["MonthName"], y=monthly_df["E_kwh_total"], marker_color="#0f766e"),
                row=1,
                col=1,
            )
            overview_fig.add_trace(
                go.Scatter(x=annual_df["Year"], y=annual_df["Mean_power_kw"], mode="lines", line=dict(color="#d97706", width=3)),
                row=1,
                col=2,
            )
            overview_fig.add_trace(
                go.Scatter(
                    x=strategy_table["Total_discounted_cost_usd"] / 1e6,
                    y=strategy_table["EENS_MWh_per_day"],
                    mode="markers+text",
                    text=strategy_table["Strategy"],
                    textposition="top center",
                    marker=dict(size=16, color=strategy_table["Equity_score"], colorscale="Tealgrn"),
                ),
                row=2,
                col=1,
            )
            overview_fig.add_trace(
                go.Bar(x=locations_df["Candidate"], y=locations_df["Potential_MWp"], marker_color="#1f2937"),
                row=2,
                col=2,
            )
            overview_fig.update_layout(height=760, margin=dict(l=10, r=10, t=60, b=10), showlegend=False)
            st.plotly_chart(overview_fig, use_container_width=True)

        with right:
            st.subheader("Decision Highlights")
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            for line in recommendation_lines:
                st.write(f"- {line}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.subheader("Model Anchors")
            st.dataframe(
                pd.DataFrame(
                    {
                        "Metric": [
                            "Average sunshine duration",
                            "Average irradiance proxy",
                            "Average daily energy",
                            "Climate state probabilities",
                            "Potential screened utility land",
                        ],
                        "Value": [
                            f"{baseline['ss_avg']:.2f} hours/day",
                            f"{baseline['g_avg']:.0f} W/m^2",
                            f"{baseline['e_daily_avg']:.2f} kWh/day",
                            "Low 0.1053 | Normal 0.8947",
                            "~ 265 ha / 265 MWp",
                        ],
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            image_path = IMAGE_DIR / "Gambar 3.2. Simulasi Climate Change Impact on PV Production.png"
            if image_path.exists():
                st.image(str(image_path), caption="Original supporting figure from the project assets", use_container_width=True)

    elif page == "Historical Data & Physics":
        st.subheader("Historical BMKG Data Pipeline")
        tab1, tab2, tab3 = st.tabs(["Raw & Cleaned Data", "Physical Model", "Monthly Diagnostics"])

        with tab1:
            c1, c2 = st.columns([1.1, 1.0], gap="large")
            with c1:
                st.dataframe(
                    model_df[["Date", "TN", "TX", "TAVG", "RH_AVG", "RR", "SS", "G_model", "Tp_model", "eta_model", "E_kwh_model"]].head(20),
                    use_container_width=True,
                )
            with c2:
                fig = px.scatter(
                    model_df,
                    x="SS",
                    y="E_kwh_model",
                    color="TAVG",
                    trendline="ols",
                    color_continuous_scale="Tealgrn",
                    labels={"SS": "Sunshine duration (hours/day)", "E_kwh_model": "Energy (kWh/day)"},
                )
                fig.update_layout(height=460, margin=dict(l=10, r=10, t=40, b=10))
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = make_subplots(rows=2, cols=2, subplot_titles=("Irradiance Proxy", "Panel vs Ambient Temperature", "Efficiency Response", "Daily Power Output"))
            fig.add_trace(go.Scatter(x=model_df["Date"], y=model_df["G_model"], mode="lines", line=dict(color="#d97706")), row=1, col=1)
            fig.add_trace(go.Scatter(x=model_df["Date"], y=model_df["TAVG"], mode="lines", name="Ambient", line=dict(color="#475569")), row=1, col=2)
            fig.add_trace(go.Scatter(x=model_df["Date"], y=model_df["Tp_model"], mode="lines", name="Panel", line=dict(color="#0f766e")), row=1, col=2)
            fig.add_trace(go.Scatter(x=model_df["Tp_model"], y=model_df["eta_model"] * 100, mode="markers", marker=dict(color=model_df["thermal_penalty_pct"], colorscale="YlOrBr", size=7)), row=2, col=1)
            fig.add_trace(go.Scatter(x=model_df["Date"], y=model_df["P_kw_model"], mode="lines", line=dict(color="#111827")), row=2, col=2)
            fig.update_layout(height=780, margin=dict(l=10, r=10, t=60, b=10))
            st.plotly_chart(fig, use_container_width=True)

            render_metric_cards(
                [
                    ("Average panel temperature", f"{baseline['tp_avg']:.1f} degC", "Higher than ambient due to irradiance loading"),
                    ("Average efficiency", f"{baseline['eta_avg'] * 100:.2f}%", "Temperature-corrected module efficiency"),
                    ("Average daily output", f"{baseline['p_kw_avg']:.2f} kW", "1 kWp reference equivalent"),
                    ("Energy CV", f"{baseline['cv_energy']:.1f}%", "Seasonal variability indicator"),
                ]
            )

        with tab3:
            c1, c2 = st.columns([1.0, 1.15], gap="large")
            with c1:
                st.dataframe(monthly_df, use_container_width=True, hide_index=True)
            with c2:
                fig = px.bar(
                    monthly_df,
                    x="MonthName",
                    y=["E_kwh_daily_avg", "CV_energy"],
                    barmode="group",
                    color_discrete_sequence=["#0f766e", "#d97706"],
                )
                fig.update_layout(height=480, margin=dict(l=10, r=10, t=40, b=10), yaxis_title="Value")
                st.plotly_chart(fig, use_container_width=True)

    elif page == "Climate Penalty Projection":
        st.subheader("2024-2074 Climate Penalty and Production Risk")
        upper, lower = st.columns([1.4, 1.0], gap="large")

        with upper:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=uncertainty_band["Year"], y=uncertainty_band["P95"], mode="lines", line=dict(width=0), showlegend=False))
            fig.add_trace(
                go.Scatter(
                    x=uncertainty_band["Year"],
                    y=uncertainty_band["P05"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(15,118,110,0.12)",
                    name="90% band",
                )
            )
            fig.add_trace(go.Scatter(x=uncertainty_band["Year"], y=uncertainty_band["P75"], mode="lines", line=dict(width=0), showlegend=False))
            fig.add_trace(
                go.Scatter(
                    x=uncertainty_band["Year"],
                    y=uncertainty_band["P25"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor="rgba(217,119,6,0.18)",
                    name="50% band",
                )
            )
            fig.add_trace(go.Scatter(x=annual_df["Year"], y=annual_df["Mean_power_kw"], mode="lines", name="Mean power", line=dict(color="#0f766e", width=3)))
            fig.update_layout(height=520, margin=dict(l=10, r=10, t=35, b=10), yaxis_title="Power (kW)")
            st.plotly_chart(fig, use_container_width=True)

            factor_fig = make_subplots(specs=[[{"secondary_y": True}]])
            factor_fig.add_trace(go.Scatter(x=annual_df["Year"], y=annual_df["Mean_temp_loss"], name="Temperature factor", line=dict(color="#d97706", width=3)), secondary_y=False)
            factor_fig.add_trace(go.Scatter(x=annual_df["Year"], y=annual_df["Mean_haze_att"], name="Haze transmission", line=dict(color="#111827", width=3)), secondary_y=False)
            factor_fig.add_trace(go.Bar(x=annual_df["Year"], y=annual_df["Haze_events"], name="Haze events", marker_color="#0f766e", opacity=0.4), secondary_y=True)
            factor_fig.update_layout(height=420, margin=dict(l=10, r=10, t=35, b=10))
            factor_fig.update_yaxes(title_text="Loss / transmission factor", secondary_y=False)
            factor_fig.update_yaxes(title_text="Event count", secondary_y=True)
            st.plotly_chart(factor_fig, use_container_width=True)

        with lower:
            st.markdown("#### Quantitative Interpretation")
            decadal = (
                climate_df.groupby("Decade", as_index=False)
                .agg(
                    Mean_power_kw=("Power_kw", "mean"),
                    Mean_temp=("Tavg_projected", "mean"),
                    Temp_loss=("Temp_loss_factor", "mean"),
                    Haze_trans=("Haze_att", "mean"),
                    Haze_events=("Haze_event", "sum"),
                )
            )
            baseline_power = annual_df.loc[annual_df["Year"].between(2024, 2028), "Mean_power_kw"].mean()
            decadal["Change_pct"] = (decadal["Mean_power_kw"] / baseline_power - 1.0) * 100.0
            st.dataframe(decadal, use_container_width=True, hide_index=True)

            render_metric_cards(
                [
                    ("Mean production decline", f"{abs(annual_df['Mean_power_kw'].pct_change().mean()) * 100:.2f}%/yr", "Average annual climate-adjusted decline"),
                    ("Temperature rise by horizon", f"{annual_df['Mean_temp'].iloc[-1] - annual_df['Mean_temp'].iloc[0]:.2f} degC", "Relative to simulation start"),
                    ("Mean haze events", f"{annual_df['Haze_events'].mean():.1f}/yr", "Modeled monthly extreme episodes"),
                ]
            )

            st.markdown("#### Planning Notes")
            st.write("- Climate penalty is driven by the interaction of rising ambient temperature, panel heat loading, cloud attenuation, and haze transmission loss.")
            st.write("- Confidence bands are generated from repeated stochastic climate runs using the same structural assumptions and randomized extreme-event paths.")
            st.write("- The dashboard intentionally exposes volatility and uncertainty, not only average trends, because capacity planning fails when tails are ignored.")

    elif page == "Markov Chain & Reliability":
        st.subheader("Solar State Modeling and Reliability Signals")
        c1, c2 = st.columns([1.0, 1.15], gap="large")
        with c1:
            state_prob = markov_daily["State"].value_counts(normalize=True).rename_axis("State").reset_index(name="Probability")
            fig = px.pie(state_prob, names="State", values="Probability", color="State", color_discrete_map={"Low": "#d97706", "Normal": "#0f766e"})
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig, use_container_width=True)

            trans_df = pd.DataFrame(transition_matrix, index=["Low", "Normal"], columns=["Low", "Normal"])
            st.markdown("#### Transition Matrix")
            st.dataframe(trans_df.style.format("{:.3f}"), use_container_width=True)

        with c2:
            sample_markov = markov_sim.head(180).copy()
            fig = px.line(sample_markov, x="Date", y="CF", color="State", color_discrete_map={"Low": "#d97706", "Normal": "#0f766e"})
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=35, b=10), yaxis_title="Capacity factor")
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Reliability Translation")
        markov_annual = markov_sim.groupby("Year", as_index=False).agg(Low_months=("State", lambda s: int((s == "Low").sum())), Mean_CF=("CF", "mean"))
        reliability_fig = make_subplots(rows=1, cols=2, subplot_titles=("Low-Solar Months per Year", "Mean Annual CF"))
        reliability_fig.add_trace(go.Bar(x=markov_annual["Year"], y=markov_annual["Low_months"], marker_color="#d97706"), row=1, col=1)
        reliability_fig.add_trace(go.Scatter(x=markov_annual["Year"], y=markov_annual["Mean_CF"], mode="lines", line=dict(color="#0f766e", width=3)), row=1, col=2)
        reliability_fig.update_layout(height=430, margin=dict(l=10, r=10, t=45, b=10), showlegend=False)
        st.plotly_chart(reliability_fig, use_container_width=True)

        render_metric_cards(
            [
                ("Low-state probability", f"{state_prob.loc[state_prob['State'] == 'Low', 'Probability'].iloc[0] * 100:.1f}%", "Empirical share below selected CF threshold"),
                ("Normal-state probability", f"{state_prob.loc[state_prob['State'] == 'Normal', 'Probability'].iloc[0] * 100:.1f}%", "Empirical share above selected CF threshold"),
                ("Expected low months", f"{markov_annual['Low_months'].mean():.1f}", "Per projected year"),
                ("Implication", "BESS + firm backup", "Needed to control EENS tails"),
            ]
        )

    elif page == "Strategy Optimization":
        st.subheader("SDP-Inspired Strategy Comparison and Capacity Path")
        c1, c2 = st.columns([1.1, 1.2], gap="large")

        with c1:
            styled = strategy_table.copy()
            styled["Total_discounted_cost_usd"] = styled["Total_discounted_cost_usd"] / 1e6
            styled = styled.rename(columns={"Total_discounted_cost_usd": "Total_discounted_cost_usd_million"})
            st.dataframe(styled, use_container_width=True, hide_index=True)

            radar = go.Figure()
            categories = ["Cost efficiency", "Reliability", "Resilience", "Equity"]
            for _, row in strategy_table.iterrows():
                radar.add_trace(
                    go.Scatterpolar(
                        r=[
                            100.0 - 100.0 * row["Total_discounted_cost_usd"] / strategy_table["Total_discounted_cost_usd"].max(),
                            100.0 - 100.0 * row["EENS_MWh_per_day"] / max(strategy_table["EENS_MWh_per_day"].max(), 1e-9),
                            row["Resilience_score"],
                            row["Equity_score"],
                        ],
                        theta=categories,
                        fill="toself",
                        name=row["Strategy"],
                    )
                )
            radar.update_layout(height=500, margin=dict(l=10, r=10, t=35, b=10), polar=dict(radialaxis=dict(range=[0, 100])))
            st.plotly_chart(radar, use_container_width=True)

        with c2:
            path_long = path_df.melt(id_vars="Year", value_vars=["PV_MW", "BESS_MWh", "Firm_MW"], var_name="Asset", value_name="Capacity")
            fig = px.area(path_long, x="Year", y="Capacity", color="Asset", color_discrete_sequence=["#0f766e", "#d97706", "#111827"])
            fig.update_layout(height=500, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig, use_container_width=True)

            pareto = px.scatter(
                strategy_table,
                x="Total_discounted_cost_usd",
                y="EENS_MWh_per_day",
                size="Resilience_score",
                color="Equity_score",
                text="Strategy",
                color_continuous_scale="Tealgrn",
            )
            pareto.update_traces(textposition="top center")
            pareto.update_layout(height=430, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(pareto, use_container_width=True)

        render_metric_cards(
            [
                ("Optimal portfolio", best_strategy["Strategy"], "Top score among four strategies"),
                ("Estimated EENS", f"{best_strategy['EENS_MWh_per_day']:.2f} MWh/day", "Lower is better"),
                ("Discounted cost", f"${best_strategy['Total_discounted_cost_usd'] / 1e6:,.1f}M", "CAPEX + OPEX + reliability penalty"),
                ("Equity score", f"{best_strategy['Equity_score']:.1f}/100", "Distributional benefit proxy"),
            ]
        )

        st.markdown("#### Interpretation")
        st.write("- This layer is a practical planning engine built from the project formulas, climate output, and strategy assumptions. It is Bellman-inspired, but streamlined for interactive dashboard use.")
        st.write("- The result is intended for comparative planning, not as a regulatory-grade production dispatch model.")
        st.write("- The winning diversified portfolio is consistent with the written project recommendations: utility PV plus strong BESS plus retained firm support.")

    elif page == "Site Screening & Equity":
        st.subheader("Sequential Hard Filtering, Land Potential, and Energy Justice")
        tab1, tab2 = st.tabs(["Location Screening", "Energy Equity"])

        with tab1:
            left, right = st.columns([1.0, 1.15], gap="large")
            with left:
                st.dataframe(locations_df, use_container_width=True, hide_index=True)
                st.write("- Hard filters encoded in the dashboard: high solar resource, slope below 15 deg, grid distance below 3 km, and open non-protected land.")
                st.write("- The 265 ha total is preserved from the project summary and distributed into three candidate zones for interactive planning.")
            with right:
                fig = px.bar(
                    locations_df,
                    x="Candidate",
                    y=["Potential_MWp", "Available_ha"],
                    barmode="group",
                    color_discrete_sequence=["#0f766e", "#d97706"],
                )
                fig.update_layout(height=480, margin=dict(l=10, r=10, t=35, b=10))
                st.plotly_chart(fig, use_container_width=True)

                bubble = px.scatter(
                    locations_df,
                    x="Distance_to_grid_km",
                    y="Slope_deg",
                    size="Potential_MWp",
                    color="Suitability_score",
                    text="Candidate",
                    color_continuous_scale="Tealgrn",
                )
                bubble.update_traces(textposition="top center")
                bubble.update_layout(height=380, margin=dict(l=10, r=10, t=35, b=10))
                st.plotly_chart(bubble, use_container_width=True)

        with tab2:
            selected_strategy = st.selectbox("Strategy for Lorenz analysis", strategy_table["Strategy"].tolist(), index=0)
            curve = energy_benefit_curve(selected_strategy)
            gini = gini_from_curve(curve)

            c1, c2 = st.columns([1.15, 1.0], gap="large")
            with c1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Equality line", line=dict(color="#94a3b8", dash="dash")))
                fig.add_trace(
                    go.Scatter(
                        x=np.concatenate([[0.0], curve["CumPopulation"].to_numpy()]),
                        y=np.concatenate([[0.0], curve["CumBenefit"].to_numpy()]),
                        mode="lines+markers",
                        name=selected_strategy,
                        line=dict(color="#0f766e", width=4),
                    )
                )
                fig.update_layout(height=430, margin=dict(l=10, r=10, t=35, b=10), xaxis_title="Cumulative population share", yaxis_title="Cumulative energy benefit share")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.dataframe(curve, use_container_width=True, hide_index=True)
                render_metric_cards(
                    [
                        ("Energy Gini", f"{gini:.3f}", "Lower means more equitable benefit distribution"),
                        ("Equity interpretation", "Solar-as-a-Service", "Best complement for lower-income groups"),
                    ]
                )
                st.write("- Strategies concentrated in distributed self-financed rooftop access tend to shift benefits upward to higher-income households.")
                st.write("- Utility-scale PV integrated with storage improves service equity because benefits arrive through system reliability, not only capital ownership.")

    else:
        st.subheader("Model Library and Source Notes")
        doc_tab1, doc_tab2, doc_tab3, doc_tab4 = st.tabs(["Formula List", "Variables", "Assumptions", "Recommendations"])
        with doc_tab1:
            st.markdown(read_markdown_file(LIST_DIR / "formula-bab-2.md"))
            st.markdown(read_markdown_file(LIST_DIR / "formula-bab-3.md"))
        with doc_tab2:
            st.markdown(read_markdown_file(LIST_DIR / "variable-list.md"))
        with doc_tab3:
            st.markdown(read_markdown_file(LIST_DIR / "assumption-data-boundaries.md"))
        with doc_tab4:
            st.markdown(read_markdown_file(LIST_DIR / "recommendation-insight-list.md"))
            st.markdown(read_markdown_file(LIST_DIR / "simulation-results.md"))
            st.markdown(read_markdown_file(BASE_DIR / "simulation" / "simulation-list.md"))

        st.markdown("#### Export-Ready Tables")
        export_col1, export_col2 = st.columns(2)
        with export_col1:
            st.download_button(
                "Download monthly historical summary CSV",
                monthly_df.to_csv(index=False).encode("utf-8"),
                file_name="monthly_historical_summary.csv",
                mime="text/csv",
            )
        with export_col2:
            st.download_button(
                "Download strategy comparison CSV",
                strategy_table.to_csv(index=False).encode("utf-8"),
                file_name="strategy_comparison.csv",
                mime="text/csv",
            )

    st.caption(
        "Built from the local project folders: `list`, `simulation`, `list-gambar`, and the BMKG dataset. Interactive outputs are derived from the formulas and assumptions documented in those project assets."
    )


if __name__ == "__main__":
    main()
