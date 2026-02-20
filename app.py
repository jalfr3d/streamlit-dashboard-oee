import streamlit as st
from utils.auth import login, logout

st.set_page_config(initial_sidebar_state="collapsed")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# ---------------- LOGIN SCREEN ----------------

if not st.session_state.authenticated:
    st.title("Login", anchor=False)

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(username, password):
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()


# ---------------- AUTHENTICATED AREA ----------------

st.sidebar.image("images/logo.jpg", caption="Company Name")
st.sidebar.write(f"Logged in as: {st.session_state.username}")
st.sidebar.write(f"Role: {st.session_state.role}")

if st.sidebar.button("Logout"):
    logout()
    st.rerun()


# Role-based navigation
role = st.session_state.role

if role in ["admin", "manager"]:
    pages = {
        "Dashboard": [
            st.Page("pages/oee.py", title="📈 OEE"),
            st.Page("pages/hours.py", title="⏳ Hours"),
            st.Page("pages/productivity.py", title="📊 Productivity"),
        ],
        " ": [
            st.Page("pages/account.py", title="⚙ Settings"),
            st.Page("pages/contact.py", title="✉️ Contact"),
        ],
    }

elif role == "analyst":
    pages = {
        "Dashboard": [
            st.Page("pages/oee.py", title="📈 OEE"),
        ],
        " ": [
            st.Page("pages/account.py", title="⚙ Settings"),
            st.Page("pages/contact.py", title="✉️ Contact"),
        ],
    }

elif role == "viewer":
    pages = {
        "Dashboard": [
            st.Page("pages/hours.py", title="⏳ Hours"),
        ],
        " ": [
            st.Page("pages/account.py", title="⚙ Settings"),
            st.Page("pages/contact.py", title="✉️ Contact"),
        ],
    }

pg = st.navigation(pages)
pg.run()