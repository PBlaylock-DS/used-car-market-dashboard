import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from pathlib import Path

# -------------------------------------------------------
# Executive-style dashboard theme
# -------------------------------------------------------
BLUE_PRIMARY = "#1f4e79"
BLUE_MID = "#2f6fa5"
BLUE_LIGHT = "#7fb3d5"
BLUE_DARK = "#12344d"
BG = "#f7f9fc"
CARD = "#ffffff"
GRID = "#d9e6f2"

pio.templates.default = "plotly_white"

st.set_page_config(
    page_title="Used Car Market Dashboard",
    page_icon="🚗",
    layout="wide"
)

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
    }}
    div[data-testid="stMetric"] {{
        background-color: {CARD};
        border: 1px solid {GRID};
        padding: 12px 16px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(18, 52, 77, 0.06);
    }}
    div[data-testid="stMetricLabel"] {{
        color: {BLUE_DARK};
        font-weight: 600;
    }}
    div[data-testid="stMetricValue"] {{
        color: {BLUE_PRIMARY};
    }}
    h1, h2, h3 {{
        color: {BLUE_DARK};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🚗 Used Car Market Dashboard")
st.caption("Executive-style portfolio analytics for synthetic used car financial assets")


@st.cache_data
def load_data(source):
    df = pd.read_csv(source)

    expected_cols = [
        "asset_id",
        "vehicle_age_years",
        "mileage",
        "outstanding_loan_balance",
        "estimated_market_value",
    ]
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        raise ValueError(f"The dataset is missing required columns: {missing}")

    df = df.copy()
    numeric_cols = [
        "vehicle_age_years",
        "mileage",
        "outstanding_loan_balance",
        "estimated_market_value",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=numeric_cols)

    df["negative_equity"] = df["outstanding_loan_balance"] > df["estimated_market_value"]
    df["equity_gap"] = df["outstanding_loan_balance"] - df["estimated_market_value"]
    df["ltv_ratio"] = np.where(
        df["estimated_market_value"] > 0,
        df["outstanding_loan_balance"] / df["estimated_market_value"],
        np.nan,
    )

    age_bins = [0, 3, 5, 7, 10, 15, 20]
    age_labels = ["0-3", "4-5", "6-7", "8-10", "11-15", "16-20"]
    df["age_band"] = pd.cut(
        df["vehicle_age_years"],
        bins=age_bins,
        labels=age_labels,
        include_lowest=True,
        right=True,
    )

    mileage_bins = [0, 30000, 60000, 90000, 120000, 180000, 300000]
    mileage_labels = ["0-30K", "30K-60K", "60K-90K", "90K-120K", "120K-180K", "180K+"]
    df["mileage_band"] = pd.cut(
        df["mileage"],
        bins=mileage_bins,
        labels=mileage_labels,
        include_lowest=True,
        right=False,
    )

    return df


def apply_exec_style(fig, legend_title=None):
    fig.update_layout(
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(color=BLUE_DARK),
        title_font=dict(color=BLUE_DARK, size=20),
        legend_title_text=legend_title,
        margin=dict(l=30, r=30, t=60, b=30),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID)
    return fig


def show_overview(df: pd.DataFrame) -> None:
    st.subheader("Overview")
    total_assets = len(df)
    total_exposure = df["outstanding_loan_balance"].sum()
    total_market_value = df["estimated_market_value"].sum()
    avg_market_value = df["estimated_market_value"].mean()
    negative_equity_rate = df["negative_equity"].mean() * 100

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Assets", f"{total_assets:,}")
    c2.metric("Total Exposure", f"${total_exposure:,.0f}")
    c3.metric("Total Market Value", f"${total_market_value:,.0f}")
    c4.metric("Avg Market Value", f"${avg_market_value:,.0f}")
    c5.metric("Negative Equity Rate", f"{negative_equity_rate:.1f}%")

def show_drilldown(df: pd.DataFrame) -> None:
    st.subheader("Drill-Down")
    st.write("Use your existing drill-down code here.")


# -------------------------------------------------------
# App execution and after-caching timing display
# -------------------------------------------------------
app_start = time.perf_counter()

st.sidebar.header("Dashboard Setup")
page = st.sidebar.radio("Go to", ["Overview", "Drill-Down"])

default_path = Path("used_car_financial_assets_800k.csv")

try:
    load_start = time.perf_counter()
    df = load_data(default_path)
    load_time = time.perf_counter() - load_start
    app_elapsed = time.perf_counter() - app_start

    if "after_cache_timing_log" not in st.session_state:
        st.session_state.after_cache_timing_log = []
    st.session_state.after_cache_timing_log.append(app_elapsed)

    st.subheader("Performance Metrics After Caching")
    col1, col2 = st.columns(2)
    col1.metric("Data Load Time (sec)", f"{load_time:.4f}")
    col2.metric("App Refresh Time (sec)", f"{app_elapsed:.4f}")

    if len(st.session_state.after_cache_timing_log) > 1:
        timing_df = pd.DataFrame({
            "run_number": range(1, len(st.session_state.after_cache_timing_log) + 1),
            "refresh_time_sec": st.session_state.after_cache_timing_log
        })
        st.dataframe(timing_df, use_container_width=True, hide_index=True)

    st.caption("These timings are displayed in the app after applying st.cache_data.")
    st.sidebar.success(f"Using local file: {default_path.name}")

except Exception as exc:
    st.error(f"Unable to load the dataset: {exc}")
    st.stop()

if page == "Overview":
    show_overview(df)
else:
    show_drilldown(df)