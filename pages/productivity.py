import streamlit as st
from utils.data_loader import load_data, build_model, calculate_oee
import plotly.express as px
import pandas as pd
from utils.auth import require_role
require_role(["admin", "manager"])

st.set_page_config(page_title="📊 Productivity",layout="wide")

def calculate_productivity_over_time(df):

    monthly = []

    grouped = df.groupby(["MonthLabel", "MonthSort"])

    for (label, sort), group in grouped:
        metrics = calculate_oee(group)

        monthly.append({
            "MonthLabel": label,
            "MonthSort": sort,
            "Productivity": metrics["productivity"]
        })

    monthly_df = pd.DataFrame(monthly)
    monthly_df = monthly_df.sort_values("MonthSort")

    return monthly_df


def render_qty_by_machine(df):

    df_machine = df[
        (df["MachineID"].notna())]

    machine_qty = (
        df_machine
        .groupby("Machine", as_index=False)["QtyProduced"]
        .sum()
        .sort_values("QtyProduced", ascending=True)
    )

    fig = px.bar(
        machine_qty,
        x="QtyProduced",
        y="Machine",
        orientation="h",
    )
    fig.update_traces(
        texttemplate="%{x:.2s}",
        textposition="outside"
    )

    fig.update_layout(
        title="Qty Produced by Machine"
    )

    st.plotly_chart(fig, width='stretch')

def render_qty_by_operator(df):

    df_operators = df[
        (df["OperatorID"].notna())]

    operator_qty = (
        df_operators
        .groupby("Operator", as_index=False)["QtyProduced"]
        .sum()
        .sort_values("QtyProduced", ascending=True)
    )

    fig = px.bar(
        operator_qty,
        x="QtyProduced",
        y="Operator",
        orientation="h",
    )
    fig.update_traces(
        texttemplate="%{x:.2s}",
        textposition="outside",
        textfont_size=244
    )

    fig.update_layout(
        title="Qty Produced by Operator"
    )

    st.plotly_chart(fig, width='stretch')

def render_productivity(df):
    monthly_df = calculate_productivity_over_time(df)

    fig = px.line(
        monthly_df,
        x="MonthLabel",
        y="Productivity",
        text="Productivity",
        markers=True
    )

    fig.update_layout(
        yaxis_tickformat=".0%",
        xaxis_title="Month",
        yaxis_title="Productivity",
        title="Productivity Over Time",
        yaxis=dict(
            range=[0.5,1]
        )
    )

    fig.update_traces(text=monthly_df["Productivity"].map(lambda x: f"{x:.1%}"),
                      textposition="top center",texttemplate="%{text}")

    st.plotly_chart(fig, width="stretch")


def render_prod(df):
    # Daily chart
    daily = df.groupby(df["Date"].dt.date).agg({
        "Hours": "sum",
        "QtyProduced": "sum"
    }).reset_index()

    st.subheader("QtyProduced by day", anchor=False)
    fig = px.line(daily, x="Date", y="QtyProduced", markers=True)
    st.plotly_chart(fig, width="stretch")

def render_dash_prod(df):

    col1, col2, col3 = st.columns(3)

    with col1:
        render_qty_by_operator(df)
    with col2:
        render_productivity(df)
    with col3:
        render_qty_by_machine(df)

    render_prod(df)
# ===============================
# MAIN APP
# ===============================
st.title("Productivity Analysis", anchor=False)

df = load_data()
fProduction = build_model(df)
# Month Filter
months = (
    fProduction[["MonthLabel", "MonthSort"]]
    .drop_duplicates()
    .sort_values("MonthSort")
)
month_labels = months["MonthLabel"].tolist()

select_all_p = st.checkbox("Select All Months", value=True, key="prod_page")

if select_all_p:
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

render_dash_prod(df_filtered)

st.divider()
col1, col2 = st.columns([0.9,0.1])
with col2:
    st.write("2025 [**jalfr3d**](https://github.com/jalfr3d)")
