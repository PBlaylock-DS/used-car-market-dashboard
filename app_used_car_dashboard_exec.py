import streamlit as st
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

    st.markdown("---")

    exposure_by_age = (
        df.groupby("age_band", observed=False)["outstanding_loan_balance"]
        .sum()
        .reset_index()
    )
    fig_exposure = px.bar(
        exposure_by_age,
        x="age_band",
        y="outstanding_loan_balance",
        title="Total Exposure by Vehicle Age Band",
        labels={"age_band": "Vehicle Age Band", "outstanding_loan_balance": "Total Exposure ($)"},
        color_discrete_sequence=[BLUE_PRIMARY],
    )
    apply_exec_style(fig_exposure)

    value_by_age = (
        df.groupby("age_band", observed=False)["estimated_market_value"]
        .mean()
        .reset_index()
    )
    fig_value = px.line(
        value_by_age,
        x="age_band",
        y="estimated_market_value",
        markers=True,
        title="Average Market Value by Vehicle Age Band",
        labels={"age_band": "Vehicle Age Band", "estimated_market_value": "Average Market Value ($)"},
        color_discrete_sequence=[BLUE_PRIMARY],
    )
    fig_value.update_traces(line=dict(width=3), marker=dict(size=8, color=BLUE_PRIMARY))
    apply_exec_style(fig_value)

    compare_df = (
        df.groupby("age_band", observed=False)[["estimated_market_value", "outstanding_loan_balance"]]
        .mean()
        .reset_index()
    )
    compare_long = compare_df.melt(
        id_vars="age_band",
        value_vars=["estimated_market_value", "outstanding_loan_balance"],
        var_name="metric",
        value_name="amount",
    )
    compare_long["metric"] = compare_long["metric"].replace({
        "estimated_market_value": "Market Value",
        "outstanding_loan_balance": "Loan Balance",
    })
    fig_compare = px.line(
        compare_long,
        x="age_band",
        y="amount",
        color="metric",
        markers=True,
        title="Average Market Value vs Loan Balance by Age Band",
        labels={"age_band": "Vehicle Age Band", "amount": "Average Amount ($)", "metric": "Metric"},
        color_discrete_sequence=[BLUE_PRIMARY, BLUE_LIGHT],
    )
    fig_compare.update_traces(line=dict(width=3), marker=dict(size=8))
    apply_exec_style(fig_compare, legend_title="Metric")

    neg_df = (
        df.groupby("age_band", observed=False)["negative_equity"]
        .mean()
        .reset_index()
    )
    neg_df["negative_equity_pct"] = neg_df["negative_equity"] * 100
    fig_negative = px.bar(
        neg_df,
        x="age_band",
        y="negative_equity_pct",
        title="Negative Equity Rate by Age Band",
        labels={"age_band": "Vehicle Age Band", "negative_equity_pct": "Negative Equity Rate (%)"},
        color_discrete_sequence=[BLUE_MID],
    )
    apply_exec_style(fig_negative)

    c_left, c_right = st.columns(2)
    with c_left:
        st.plotly_chart(fig_exposure, use_container_width=True)
        st.plotly_chart(fig_compare, use_container_width=True)
    with c_right:
        st.plotly_chart(fig_value, use_container_width=True)
        st.plotly_chart(fig_negative, use_container_width=True)

    st.markdown("---")
    st.write(
        "This overview highlights total exposure, market value, depreciation patterns, "
        "and negative equity risk across the synthetic used car portfolio."
    )


def show_drilldown(df: pd.DataFrame) -> None:
    st.subheader("Drill-Down")

    st.sidebar.header("Filter Options")

    age_options = [x for x in df["age_band"].dropna().unique().tolist()]
    selected_age_bands = st.sidebar.multiselect(
        "Select Age Band(s)",
        options=age_options,
        default=age_options,
    )

    mileage_range = st.sidebar.slider(
        "Select Mileage Range",
        min_value=int(df["mileage"].min()),
        max_value=int(df["mileage"].max()),
        value=(int(df["mileage"].min()), int(df["mileage"].max())),
    )

    market_value_range = st.sidebar.slider(
        "Select Market Value Range",
        min_value=float(df["estimated_market_value"].min()),
        max_value=float(df["estimated_market_value"].max()),
        value=(float(df["estimated_market_value"].min()), float(df["estimated_market_value"].max())),
    )

    negative_equity_filter = st.sidebar.selectbox(
        "Negative Equity",
        options=["All", "Yes", "No"],
    )

    filtered_df = df[df["age_band"].isin(selected_age_bands)].copy()
    filtered_df = filtered_df[
        (filtered_df["mileage"] >= mileage_range[0]) &
        (filtered_df["mileage"] <= mileage_range[1])
    ]
    filtered_df = filtered_df[
        (filtered_df["estimated_market_value"] >= market_value_range[0]) &
        (filtered_df["estimated_market_value"] <= market_value_range[1])
    ]

    if negative_equity_filter == "Yes":
        filtered_df = filtered_df[filtered_df["negative_equity"]]
    elif negative_equity_filter == "No":
        filtered_df = filtered_df[~filtered_df["negative_equity"]]

    total_assets = len(filtered_df)
    total_exposure = filtered_df["outstanding_loan_balance"].sum() if total_assets else 0
    avg_market_value = filtered_df["estimated_market_value"].mean() if total_assets else 0
    avg_ltv = filtered_df["ltv_ratio"].mean() * 100 if total_assets else 0
    negative_equity_rate = filtered_df["negative_equity"].mean() * 100 if total_assets else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filtered Assets", f"{total_assets:,}")
    c2.metric("Filtered Exposure", f"${total_exposure:,.0f}")
    c3.metric("Avg Market Value", f"${avg_market_value:,.0f}")
    c4.metric("Avg LTV / Neg. Equity", f"{avg_ltv:.1f}% / {negative_equity_rate:.1f}%")

    st.markdown("---")

    if total_assets == 0:
        st.warning("No records match the selected filters. Adjust the filters and try again.")
        return

    scatter_source = filtered_df.sample(min(len(filtered_df), 10000), random_state=42)
    scatter_fig = px.scatter(
        scatter_source,
        x="estimated_market_value",
        y="outstanding_loan_balance",
        color="age_band",
        hover_data=["asset_id", "vehicle_age_years", "mileage"],
        title="Loan Balance vs Market Value",
        labels={
            "estimated_market_value": "Estimated Market Value ($)",
            "outstanding_loan_balance": "Outstanding Loan Balance ($)",
            "age_band": "Age Band",
        },
        color_discrete_sequence=[BLUE_PRIMARY, BLUE_MID, BLUE_LIGHT, "#6c9bcf", "#98c1e3", "#c7ddf2"],
        opacity=0.65,
    )
    apply_exec_style(scatter_fig, legend_title="Age Band")

    hist_fig = px.histogram(
        filtered_df,
        x="vehicle_age_years",
        nbins=20,
        title="Distribution of Vehicle Age",
        labels={"vehicle_age_years": "Vehicle Age (Years)"},
        color_discrete_sequence=[BLUE_PRIMARY],
    )
    apply_exec_style(hist_fig)

    equity_gap_fig = px.box(
        filtered_df,
        x="age_band",
        y="equity_gap",
        title="Equity Gap by Age Band",
        labels={"age_band": "Vehicle Age Band", "equity_gap": "Loan Balance - Market Value ($)"},
        color="age_band",
        color_discrete_sequence=[BLUE_PRIMARY, BLUE_MID, BLUE_LIGHT, "#6c9bcf", "#98c1e3", "#c7ddf2"],
    )
    equity_gap_fig.update_layout(showlegend=False)
    apply_exec_style(equity_gap_fig)

    exposure_by_mileage = (
        filtered_df.groupby("mileage_band", observed=False)["outstanding_loan_balance"]
        .sum()
        .reset_index()
    )
    mileage_fig = px.bar(
        exposure_by_mileage,
        x="mileage_band",
        y="outstanding_loan_balance",
        title="Exposure by Mileage Band",
        labels={"mileage_band": "Mileage Band", "outstanding_loan_balance": "Total Exposure ($)"},
        color_discrete_sequence=[BLUE_MID],
    )
    apply_exec_style(mileage_fig)

    c_left, c_right = st.columns(2)
    with c_left:
        st.plotly_chart(scatter_fig, use_container_width=True)
        st.plotly_chart(hist_fig, use_container_width=True)
    with c_right:
        st.plotly_chart(equity_gap_fig, use_container_width=True)
        st.plotly_chart(mileage_fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Filtered Asset Detail")

    display_df = filtered_df.copy()
    display_df["ltv_ratio_pct"] = display_df["ltv_ratio"] * 100

    display_cols = [
        "asset_id",
        "vehicle_age_years",
        "mileage",
        "outstanding_loan_balance",
        "estimated_market_value",
        "negative_equity",
        "equity_gap",
        "ltv_ratio_pct",
    ]

    st.dataframe(
        display_df[display_cols].head(500),
        use_container_width=True,
        hide_index=True,
    )

    csv = display_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_used_car_assets.csv",
        mime="text/csv",
    )


st.sidebar.header("Dashboard Setup")
page = st.sidebar.radio("Go to", ["Overview", "Drill-Down"])

uploaded_file = st.sidebar.file_uploader("Upload used car CSV (optional)", type=["csv"])
default_path = Path("used_car_financial_assets_800k.csv")

try:
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.sidebar.success("Using uploaded CSV file")
    elif default_path.exists():
        df = load_data(default_path)
        st.sidebar.success(f"Using local file: {default_path.name}")
    else:
        st.info("Upload `used_car_financial_assets_800k.csv` from the sidebar to run this dashboard.")
        st.stop()
except Exception as exc:
    st.error(f"Unable to load the dataset: {exc}")
    st.stop()

if page == "Overview":
    show_overview(df)
else:
    show_drilldown(df)
