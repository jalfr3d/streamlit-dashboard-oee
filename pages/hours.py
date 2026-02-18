import streamlit as st
from pages.oee import load_data

st.set_page_config(page_title="⏳ Hours",layout="wide")

df = load_data()

