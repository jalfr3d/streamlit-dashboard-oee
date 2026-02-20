import streamlit as st
import json
import bcrypt
from pathlib import Path

USERS_FILE = Path("users.json")


def load_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def login(username, password):
    users = load_users()
    user = users.get(username)

    if user and verify_password(password, user["password"]):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.role = user["role"]
        return True

    return False


def logout():
    for key in ["authenticated", "username", "role"]:
        if key in st.session_state:
            del st.session_state[key]


def require_role(allowed_roles):
    if "authenticated" not in st.session_state:
        st.error("Please login first.")
        st.stop()

    if st.session_state.role not in allowed_roles:
        st.error("Access denied.")
        st.stop()