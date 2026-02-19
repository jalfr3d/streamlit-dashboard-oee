import streamlit as st
from pages.oee import load_data, build_model, calculate_oee
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="⏳ Hours",layout="wide")

def calculate_availa_over_time(df):

    monthly = []

    grouped = df.groupby(["MonthLabel", "MonthSort"])

    for (label, sort), group in grouped:
        metrics = calculate_oee(group)

        monthly.append({
            "MonthLabel": label,
            "MonthSort": sort,
            "Availability": metrics["availability"]
        })

    monthly_df = pd.DataFrame(monthly)
    monthly_df = monthly_df.sort_values("MonthSort")

    return monthly_df


def render_hours_by_incident(df):

    df_incidents = df[df["IncidentID"].notna()]

    incident_hours = (
        df_incidents
        .groupby("Incident", as_index=False)["Hours"]
        .sum()
        .sort_values("Hours", ascending=True)
    )

    fig = px.bar(
        incident_hours,
        x="Hours",
        y="Incident",
        orientation="h",
    )
    fig.update_traces(
        texttemplate="%{x:.1f}",
        textposition="outside"
    )
    fig.update_xaxes(tickformat=".1f")
    fig.update_layout(
        title="Outage Hours by Incident"
    )



    st.plotly_chart(fig, width='stretch')


def render_availa(df):
    monthly_df = calculate_availa_over_time(df)

    fig = px.line(
        monthly_df,
        x="MonthLabel",
        y="Availability",
        markers=True
    )

    fig.update_layout(
        yaxis_tickformat=".0%",
        xaxis_title="Month",
        yaxis_title="Availability",
        title="Availability Over Time"
    )

    fig.update_traces(text=monthly_df["Availability"].map(lambda x: f"{x:.1%}"),
                      textposition="top center")

    st.plotly_chart(fig, width="stretch")

def render_dash(df):
    metrics = calculate_oee(df)

    col1, col2, col3, col4 = st.columns(4)

    col2.metric("Productive Hours",f"{metrics['total_hours']}", border=True, format="compact")
    col3.metric("Outage Hours", f"{metrics['outage_hours']}", border=True, format="compact")

    col5, col6, col7 = st.columns(3)

    with col5:
        pass
    with col6:
        render_availa(df)
    with col7:
        render_hours_by_incident(df)
# ===============================
# MAIN APP
# ===============================
st.title("Hours", anchor=False)

st.divider()

df = load_data()
fProduction = build_model(df)
# Month Filter
months = (
    fProduction[["MonthLabel", "MonthSort"]]
    .drop_duplicates()
    .sort_values("MonthSort")
)
month_labels = months["MonthLabel"].tolist()

select_all_h = st.checkbox("Select All Months", value=True, key="hours_page")

if select_all_h:
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

render_dash(df_filtered)

st.divider()
col1, col2 = st.columns([0.9,0.1])
with col2:
    st.write("2025 [**jalfr3d**](https://github.com/jalfr3d)")
