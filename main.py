import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    file = "DatabaseProduction.xlsx"
    xls = pd.ExcelFile(file)

    tables = {}
    for sheet in xls.sheet_names:
        if sheet.startswith(("d", "f")):
            tables[sheet] = pd.read_excel(file, sheet_name=sheet)

    return tables

tables = load_data()

fProduction = tables["fProductionEntries"]
fProductionOrder = tables["fProductionOrders"]
dProduct = tables["dProduct"]


fProduction = fProduction.merge(
    fProductionOrder[["PO_ID", "ProductID"]],
    on="PO_ID",
    how="left"
)
fProduction = fProduction.merge(
    dProduct[["ProductID", "ItemsPerHour"]],
    on="ProductID",
    how="left"
)
fProduction["StartTime"] = pd.to_datetime(
    fProduction["StartTime"],
    format="%d-%m-%Y %H:%M:%S"
)

fProduction["EndTime"] = pd.to_datetime(
    fProduction["EndTime"],
    format="%d-%m-%Y %H:%M:%S"
)

fProduction["Date"] = pd.to_datetime(fProduction["StartTime"])
fProduction["Month"] = fProduction["Date"].dt.to_period("M")

month_filter = st.sidebar.selectbox(
    "Select Month",
    sorted(fProduction["Month"].unique())
)
fProduction["Hours"] = (
    fProduction["EndTime"] - fProduction["StartTime"]
).dt.total_seconds() / 3600

df = fProduction[fProduction["Month"] == month_filter]

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
col1, col2, col3, col4 = st.columns(4)

col1.metric("Availability", f"{availability:.2%}")
col2.metric("Productivity", f"{productivity:.2%}")
col3.metric("Quality", f"{quality:.2%}")
col4.metric("OEE", f"{oee:.2%}")
daily = df.groupby(df["Date"].dt.date).agg({
    "Hours": "sum",
    "QtyProduced": "sum",
    "QtyRejected": "sum"
}).reset_index()

fig = px.line(daily, x="Date", y="QtyProduced")
st.plotly_chart(fig, width='stretch')
