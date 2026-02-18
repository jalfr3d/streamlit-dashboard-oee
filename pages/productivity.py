import streamlit as st
from pages.oee import load_data, build_model
import plotly.express as px

st.set_page_config(page_title="📊 Productivity",layout="wide")

def render_prod(df):
    # Daily chart
    daily = df.groupby(df["Date"].dt.date).agg({
        "Hours": "sum",
        "QtyProduced": "sum"
    }).reset_index()

    st.subheader("Qty by day", anchor=False)
    fig = px.line(daily, x="Date", y="QtyProduced", markers=True)
    st.plotly_chart(fig, width="stretch")

# ===============================
# MAIN APP
# ===============================
st.title("Productivity", anchor=False)

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

select_all_p = st.checkbox("Select All Months", value=True, key="productivity")

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

render_prod(df_filtered)

st.divider()
col1, col2 = st.columns([0.9,0.1])
with col2:
    st.write("2025 [**jalfr3d**](https://github.com/jalfr3d)")
