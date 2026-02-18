import streamlit as st

st.set_page_config(layout="wide")
st.logo("images/logo.png", size="large")
pages = {
    "Dashboard": [
        st.Page("pages/oee.py", title="📈 OEE"),
        st.Page("pages/hours.py", title="⏳ Hours"),
        st.Page("pages/productivity.py", title="📊 Productivity")
    ],
    "\u200b": [
        st.Page("pages/account.py", title="🙋‍♂️ Account Settings"),
        st.Page("pages/contact.py", title="✉️ Contact"),
    ],
}
pg = st.navigation(pages)
pg.run()