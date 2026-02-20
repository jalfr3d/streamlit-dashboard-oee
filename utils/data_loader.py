import pandas as pd
import streamlit as st


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