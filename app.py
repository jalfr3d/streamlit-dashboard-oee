import streamlit as st

st.set_page_config(layout="wide")
st.sidebar.image("images/logo.jpg")
pages = {
    "Dashboard": [
        st.Page("pages/oee.py", title="📈 OEE"),
        st.Page("pages/hours.py", title="⏳ Hours"),
        st.Page("pages/productivity.py", title="📊 Productivity")
    ],
    "\u200b": [
        st.Page("pages/account.py", title="⚙️ Settings"),
        st.Page("pages/contact.py", title="✉️ Contact"),
    ],
}
pg = st.navigation(pages)
pg.run()