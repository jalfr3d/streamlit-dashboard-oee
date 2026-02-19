import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="📈 Dashboard OEE",layout="wide")

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

    dMachine = tables["dMachine"]
    dIncident = tables["dIncident"]
    dOperator = tables["dOperator"]
    # Merge Machine Name
    fProduction = fProduction.merge(
        dMachine[["MachineID", "Machine"]],
        on="MachineID",
        how="left"
    )

    fProduction = fProduction.merge(
        dIncident[["IncidentID","Incident"]],
        on="IncidentID",
        how="left"
    )

    fProduction = fProduction.merge(
        dOperator[["OperatorID","Operator"]],
        on="OperatorID",
        how="left"
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
        "qty_rejected": qty_rejected,
        "total_hours": productive_hours,
        "outage_hours": outage_hours,
    }


def calculate_oee_over_time(df):

    monthly = []

    grouped = df.groupby(["MonthLabel", "MonthSort"])

    for (label, sort), group in grouped:
        metrics = calculate_oee(group)

        monthly.append({
            "MonthLabel": label,
            "MonthSort": sort,
            "OEE": metrics["oee"]
        })

    monthly_df = pd.DataFrame(monthly)
    monthly_df = monthly_df.sort_values("MonthSort")

    return monthly_df


def calculate_oee_by_machine(df):

    machine_list = []

    grouped = df.groupby(["MachineID", "Machine"])

    for (machine_id, machine_name), group in grouped:
        metrics = calculate_oee(group)

        machine_list.append({
            "MachineID": machine_id,
            "Machine": machine_name,
            "OEE": metrics["oee"]
        })

    machine_df = pd.DataFrame(machine_list)
    machine_df = machine_df.sort_values("OEE", ascending=True)

    return machine_df



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


def render_oee_over_time(df):

    monthly_df = calculate_oee_over_time(df)

    fig = px.line(
        monthly_df,
        x="MonthLabel",
        y="OEE",
        text="OEE",
        markers=True
    )

    fig.update_layout(
        yaxis_tickformat=".0%",
        xaxis_title="Month",
        yaxis_title="OEE",
        title="OEE Over Time"
    )

    fig.update_traces(text=monthly_df["OEE"].map(lambda x: f"{x:.1%}"),
                      textposition="top center", texttemplate="%{text}")

    st.plotly_chart(fig, width="stretch")


def render_oee_by_machine(df):

    machine_df = calculate_oee_by_machine(df)
    machine_df["DisplayName"] = (
            machine_df["Machine"] + " (" + machine_df["MachineID"].astype(str) + ")"
    )

    fig = px.bar(
        machine_df,
        x="OEE",
        y="DisplayName",
        orientation="h"
    )

    fig.update_layout(
        xaxis_tickformat=".0%",
        title="OEE by Machine",
        dragmode='pan',
        xaxis=dict(
            range=[0, 1]  # Show only the first 10 values initially
        )
    )

    fig.add_vline(
        x=OEE_TARGET,
        line_dash="dash",
        line_color="black",
        annotation_text="Target 85%",
        annotation_position="top"
    )

    fig.update_traces(
        text=machine_df["OEE"].map(lambda x: f"{x:.1%}"),
        textposition="outside"
    )

    st.plotly_chart(fig,
                    width="stretch")


def render_dashboard(df):

    st.header("KPIs", anchor=False)
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

    col8, col9 = st.columns(2)
    with col8:
        render_oee_over_time(df)
    with col9:
        render_oee_by_machine(df)

# ===============================
# MAIN APP
# ===============================
st.title("Production Analytical Dashboard", anchor=False)
OEE_TARGET = 0.85
tables = load_data()
fProduction = build_model(tables)

# Month Filter
months = (
    fProduction[["MonthLabel", "MonthSort"]]
    .drop_duplicates()
    .sort_values("MonthSort")
)
month_labels = months["MonthLabel"].tolist()

select_all = st.checkbox("Select All Months", value=True, key="oee_page")

if select_all:
    selected_months = month_labels
else:
    selected_months = st.multiselect(
        "Select Month(s)",
        options=month_labels,
        default=month_labels
    )

df_filtered = fProduction[
    fProduction["MonthLabel"].isin(selected_months)
]

render_dashboard(df_filtered)
st.divider()
col1, col2 = st.columns([0.9,0.1])
with col2:
    st.write("2025 [**jalfr3d**](https://github.com/jalfr3d)")