import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard",page_icon="📊",layout="wide")

# ===============================
# DATA LOADING
# ===============================

KPI_INFO = {
    "Availability": "Availability = Productive Hours / (Productive Hours + Outage Hours)",
    "Productivity": "Productivity = Qty Produced / Qty Planned",
    "Quality": "Quality = Qty Produced / (Qty Produced + Qty Rejected)",
    "OEE": "OEE = Availability × Productivity × Quality",
    "Qty Produced": "Total sum of produced units",
    "Qty Planned": "Sum of (ItemsPerHour × Hours) for productive records",
    "Qty Rejected": "Total rejected units"
}

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
    fProduction["Year"] = fProduction["Date"].dt.year
    fProduction["MonthNumber"] = fProduction["Date"].dt.month
    fProduction["MonthName"] = fProduction["Date"].dt.month_name(locale="en_US.utf8")

    fProduction["MonthLabel"] = (
            fProduction["MonthName"] + " " + fProduction["Year"].astype(str)
    )
    fProduction["MonthSort"] = (
            fProduction["Year"] * 100 + fProduction["MonthNumber"]
    )

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

    return {
        "availability": availability,
        "productivity": productivity,
        "quality": quality,
        "oee": oee,
        "qty_produced": qty_produced,
        "qty_planned": qty_planned,
        "qty_rejected": qty_rejected
    }


# ===============================
# KPI RENDER
# ===============================

def render_kpi(label, value, threshold=None, is_percentage=True):
    help_text = KPI_INFO.get(label, "")

    if threshold is not None:
        color = "green" if value >= threshold else "red"
        arrow = "▲" if value >= threshold else "▼"

        st.metric(
            label,
            f"{value:.2%}" if is_percentage else f"{value:,.0f}",
            delta=f"{arrow} Target {threshold:.0%}",
            delta_color=color,
            border=True,
            help=help_text
        )
    else:
        st.metric(
            label,
            f"{value:.2%}" if is_percentage else f"{value:,.0f}",
            border=True,
            help=help_text
        )


def render_dashboard(df):

    st.header("KPI", anchor=False)
    metrics = calculate_oee(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi("Availability", metrics["availability"], 0.90)

    with col2:
        render_kpi("Productivity", metrics["productivity"], 0.95)

    with col3:
        render_kpi("Quality", metrics["quality"], 0.99)

    with col4:
        render_kpi("OEE", metrics["oee"], 0.85)

    col5, col6, col7 = st.columns(3)

    col5.metric("Qty Produced", f"{metrics['qty_produced']:,.0f}", border=True)
    col6.metric("Qty Planned", f"{metrics['qty_planned']:,.0f}", border=True)
    col7.metric("Qty Rejected", f"{metrics['qty_rejected']:,.0f}", border=True)

    # Daily chart
    daily = df.groupby(df["Date"].dt.date).agg({
        "Hours": "sum",
        "QtyProduced": "sum"
    }).reset_index()

    st.divider()

    st.subheader("Production by Day", anchor=False)
    fig = px.line(daily, x="Date", y="QtyProduced", markers=True)
    st.plotly_chart(fig, width="stretch")


# ===============================
# MAIN APP
# ===============================

tables = load_data()
fProduction = build_model(tables)

# Sidebar Month Filter
months = (
    fProduction[["MonthLabel", "MonthSort"]]
    .drop_duplicates()
    .sort_values("MonthSort")
)
month_labels = months["MonthLabel"].tolist()

select_all = st.sidebar.checkbox("Select All Months", value=True)

if select_all:
    selected_months = month_labels
else:
    selected_months = st.sidebar.multiselect(
        "Select Month(s)",
        options=month_labels,
        default=month_labels
    )

df_filtered = fProduction[
    fProduction["MonthLabel"].isin(selected_months)
]

#st.subheader(f"Selected Months: {', '.join(map(str, selected_months))}", anchor=False)
st.title("DASHBOARD", anchor=False)
render_dashboard(df_filtered)
