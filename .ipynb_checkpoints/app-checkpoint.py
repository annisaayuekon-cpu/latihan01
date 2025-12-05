import streamlit as st

st.set_page_config(
    page_title="Women & Development Dashboard",
    layout="wide",
    page_icon="👩",
)

st.title("Women & Development Dashboard")

st.markdown(
    """
Dashboard ini menggunakan data World Bank terkait perempuan:
- Partisipasi angkatan kerja perempuan
- Pendidikan menengah perempuan
- Kesehatan ibu (maternal mortality)

Gunakan menu **Pages** di sidebar kiri untuk:
1. Overview Women
2. Country Profile
3. Comparison
"""
)
