import streamlit as st

st.set_page_config(
    page_title="Women & Development Dashboard",
    layout="wide",
    page_icon="👩",
)

# ========== THEME PINK ==========
st.markdown(
    """
    <style>
        /* Background utama app */
        .stApp {
            background: radial-gradient(circle at top left, #ffe6f2 0%, #ffffff 40%, #ffd6eb 100%);
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #ffe6f2 !important;
        }

        /* Judul utama */
        h1, h2, h3 {
            color: #c2185b !important;
        }

        /* Subheader dan teks penting */
        .css-10trblm, .css-1v0mbdj {
            color: #c2185b !important;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            border: 1px solid #f48fb1 !important;
            padding: 12px 16px !important;
        }

        /* Slider handle dan track (kira-kira) */
        [data-baseweb="slider"] > div {
            background-color: #f8bbd0 !important;
        }

        /* Tombol */
        .stButton > button {
            background-color: #f06292 !important;
            color: white !important;
            border-radius: 20px !important;
            border: none !important;
        }

        .stButton > button:hover {
            background-color: #ec407a !important;
        }

        /* Dataframe header */
        .stDataFrame thead tr th {
            background-color: #f8bbd0 !important;
            color: #880e4f !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
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
