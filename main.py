import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ===============================
# DATA LOADING
# ===============================

@st.cache_data
def load_data():
    file = "DatabaseProduction.xlsx"
    xls = pd.ExcelFile(file)

    tables = {}
    for sheet in xls.sheet_names:
        if sheet.startswith(("d", "f")):
            tables[sheet] = pd.read_excel(file, sheet_name=sheet)

    return tables


# ===============================
# DATA MODEL
# ===============================

def build_model(tables):

    fProduction = tables["fProductionEntries"]
    fProductionOrder = tables["fProductionOrders"]
    dProduct = tables["dProduct"]

    # Merge ProductID
    fProduction = fProduction.merge(
        fProductionOrder[["PO_ID", "ProductID"]],
        on="PO_ID",
        how="left"
    )

    # Merge ItemsPerHour
    fProduction = fProduction.merge(
        dProduct[["ProductID", "ItemsPerHour"]],
        on="ProductID",
        how="left"
    )

    # Datetime conversion
    fProduction["StartTime"] = pd.to_datetime(
        fProduction["StartTime"],
        format="%d-%m-%Y %H:%M:%S"
    )

    fProduction["EndTime"] = pd.to_datetime(
        fProduction["EndTime"],
        format="%d-%m-%Y %H:%M:%S"
    )

    # Hours calculation
    fProduction["Hours"] = (
        fProduction["EndTime"] - fProduction["StartTime"]
    ).dt.total_seconds() / 3600

    # Date columns
    fProduction["Date"] = fProduction["StartTime"]
    fProduction["Month"] = fProduction["Date"].dt.to_period("M")

    return fProduction


# ===============================
# CALCULATIONS
# ===============================

def calculate_oee(df):

    total_hours = df["Hours"].sum()
    outage_hours = df[df["IncidentID"].notna()]["Hours"].sum()
    productive_hours = df[df["IncidentID"].isna()]["Hours"].sum()

    availability = (
        productive_hours / (productive_hours + outage_hours)
        if (productive_hours + outage_hours) > 0 else 0
    )

    df_productive = df[df["IncidentID"].isna()].copy()
    df_productive["Planned"] = (
        df_productive["ItemsPerHour"] * df_productive["Hours"]
    )

    qty_planned = df_productive["Planned"].sum()
    qty_produced = df["QtyProduced"].sum()
    qty_rejected = df["QtyRejected"].sum()

    productivity = qty_produced / qty_planned if qty_planned > 0 else 0

    quality = (
        qty_produced / (qty_produced + qty_rejected)
        if (qty_produced + qty_rejected) > 0 else 0
    )

    oee = availability * productivity * quality

    return availability, productivity, quality, oee


# ===============================
# KPI RENDER
# ===============================

def render_kpi(label, value, threshold):
    color = "green" if value >= threshold else "red"
    arrow = "▲" if value >= threshold else "▼"

    st.metric(
        label,
        f"{value:.2%}",
        delta=f"{arrow} Target {threshold:.0%}",
        delta_color=color
    )


def render_dashboard(df):

    availability, productivity, quality, oee = calculate_oee(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi("Availability", availability, 0.90)

    with col2:
        render_kpi("Productivity", productivity, 0.95)

    with col3:
        render_kpi("Quality", quality, 0.99)

    with col4:
        render_kpi("OEE", oee, 0.85)

    # Daily chart
    daily = df.groupby(df["Date"].dt.date).agg({
        "Hours": "sum",
        "QtyProduced": "sum"
    }).reset_index()

    fig = px.line(daily, x="Date", y="QtyProduced")
    st.plotly_chart(fig, width="stretch")


# ===============================
# MAIN APP
# ===============================

tables = load_data()
fProduction = build_model(tables)

# Sidebar Month Filter
months = sorted(fProduction["Month"].unique())

select_all = st.sidebar.checkbox("Select All Months", value=True)

if select_all:
    selected_months = months
else:
    selected_months = st.sidebar.multiselect(
        "Select Month(s)",
        options=months,
        default=months
    )

df_filtered = fProduction[fProduction["Month"].isin(selected_months)]

st.subheader(f"Selected Months: {', '.join(map(str, selected_months))}")

render_dashboard(df_filtered)
