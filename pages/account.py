import streamlit as st
from utils.auth import require_role
require_role(["admin", "manager", "analyst", "viewer"])

st.set_page_config(page_title="🙋‍♂️ Account Settings",layout="wide")