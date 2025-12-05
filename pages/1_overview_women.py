import streamlit as st
import pandas as pd
import plotly.express as px
import os
from typing import Dict

def apply_pink_theme():
    st.markdown(
        """
        <style>
            .stApp {
                background: radial-gradient(circle at top left, #ffe6f2 0%, #ffffff 40%, #ffd6eb 100%);
            }
            section[data-testid="stSidebar"] {
                background-color: #ffe6f2 !important;
            }
            h1, h2, h3 {
                color: #c2185b !important;
            }
            [data-testid="stMetric"] {
                background-color: #ffffff !important;
                border-radius: 12px !important;
                border: 1px solid #f48fb1 !important;
                padding: 12px 16px !important;
            }
            [data-baseweb="slider"] > div {
                background-color: #f8bbd0 !important;
            }
            .stButton > button {
                background-color: #f06292 !important;
                color: white !important;
                border-radius: 20px !important;
                border: none !important;
            }
            .stButton > button:hover {
                background-color: #ec407a !important;
            }
            .stDataFrame thead tr th {
                background-color: #f8bbd0 !important;
                color: #880e4f !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_pink_theme()

# =========================
# KONFIGURASI FILE DATA
# =========================
FEMALE_EDU_FILE = "FEMALE SECONDARY.csv"
FEMALE_LFP_FILE = "FLFP.csv"
MATERNAL_MORT_FILE = "MATERNAL MORTALITY.csv"


# =========================
# FUNGSI BACA DATA
# =========================
def load_wb_indicator(filename: str, indicator_label: str) -> pd.DataFrame:
    """
    Membaca file CSV World Bank versi kamu:
    - Separator ; (semicolon)
    - Desimal , (comma)
    Lalu ubah ke long format:
    country | country_code | year | value | indicator
    """
    path = os.path.join("data", filename)

    if not os.path.exists(path):
        st.error(f"File tidak ditemukan: {path}")
        return pd.DataFrame(columns=["country", "country_code", "year", "value", "indicator"])

    # Baca CSV
    df = pd.read_csv(
        path,
        sep=";",       # penting, karena file kamu pakai ;
        engine="python",
        decimal=",",   # angka desimal pakai koma
    )

    # Deteksi kolom tahun: kolom yang diawali angka (misal "1990", "1990 [YR1990]")
    year_cols = [
        c for c in df.columns
        if str(c).strip()[:4].isdigit()
    ]

    if "Country Name" not in df.columns or "Country Code" not in df.columns:
        st.error(f"Kolom 'Country Name' / 'Country Code' tidak ditemukan di {filename}")
        return pd.DataFrame(columns=["country", "country_code", "year", "value", "indicator"])

    df_long = df.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    )

    # Bersihkan kolom tahun (ambil 4 digit pertama)
    df_long["year"] = df_long["year"].astype(str).str.slice(0, 4)
    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce")
    df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

    df_long["indicator"] = indicator_label
    df_long = df_long.rename(
        columns={"Country Name": "country", "Country Code": "country_code"}
    )

    # Buang baris tanpa tahun atau nilai
    df_long = df_long.dropna(subset=["year", "value"])

    return df_long


@st.cache_data
def load_all_data() -> pd.DataFrame:
    lfp = load_wb_indicator(FEMALE_LFP_FILE, "Female LFP")
    edu = load_wb_indicator(FEMALE_EDU_FILE, "Female Secondary Enrolment")
    mort = load_wb_indicator(MATERNAL_MORT_FILE, "Maternal Mortality")

    all_df = pd.concat([lfp, edu, mort], ignore_index=True)

    if all_df.empty:
        return all_df

    # Batasi tahun yang dipakai supaya konsisten (menyesuaikan maternal mortality, max 2023)
    all_df = all_df[(all_df["year"] >= 1995) & (all_df["year"] <= 2023)]

    return all_df


# =========================
# UI HALAMAN
# =========================
st.title("Overview – Women & Development")

df = load_all_data()

# Kalau data benar-benar kosong
if df.empty:
    st.error("Dataset kosong atau tidak berhasil dibaca. Periksa file di folder `data/`.")
    st.stop()

available_years = sorted(df["year"].unique())

if not available_years:
    st.error("Tidak ada tahun yang tersedia dalam data.")
    st.stop()

default_year = max(available_years)

selected_year = st.sidebar.selectbox(
    "Pilih Tahun",
    options=available_years,
    index=available_years.index(default_year),
)

df_year = df[df["year"] == selected_year]

st.subheader(f"Ringkasan Global Indikator Perempuan – {selected_year}")

# Ringkasan global per indikator
summary = (
    df_year.groupby("indicator")["value"]
    .agg(["mean", "min", "max"])
    .reset_index()
)

col1, col2, col3 = st.columns(3)

# Female LFP
lfp_row = summary[summary["indicator"] == "Female LFP"]
if not lfp_row.empty:
    col1.metric(
        "Rata-rata Female Labor Force Participation (%)",
        f"{lfp_row['mean'].iloc[0]:.1f}",
    )
else:
    col1.info("Tidak ada data LFP untuk tahun ini.")

# Female Secondary Enrolment
edu_row = summary[summary["indicator"] == "Female Secondary Enrolment"]
if not edu_row.empty:
    col2.metric(
        "Rata-rata Female Secondary Enrolment (%)",
        f"{edu_row['mean'].iloc[0]:.1f}",
    )
else:
    col2.info("Tidak ada data Secondary Enrolment untuk tahun ini.")

# Maternal Mortality
mort_row = summary[summary["indicator"] == "Maternal Mortality"]
if not mort_row.empty:
    col3.metric(
        "Rata-rata Maternal Mortality\n(per 100.000 kelahiran)",
        f"{mort_row['mean'].iloc[0]:.0f}",
    )
else:
    col3.info("Tidak ada data Maternal Mortality untuk tahun ini.")

st.markdown("---")

indicator_labels: Dict[str, str] = {
    "Female Labor Force Participation (%)": "Female LFP",
    "Female Secondary Enrolment (%)": "Female Secondary Enrolment",
    "Maternal Mortality (per 100.000 births)": "Maternal Mortality",
}

chosen_label = st.selectbox(
    "Pilih indikator untuk melihat Top/Bottom negara",
    options=list(indicator_labels.keys()),
)

chosen_indicator = indicator_labels[chosen_label]

df_ind = df_year[df_year["indicator"] == chosen_indicator].copy()

st.markdown(f"Distribusi Negara – {chosen_label}")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("Top 10 Negara")
    if chosen_indicator == "Maternal Mortality":
        # untuk mortality, nilai rendah = lebih baik
        top10 = df_ind.sort_values("value", ascending=True).head(10)
    else:
        top10 = df_ind.sort_values("value", ascending=False).head(10)

    if not top10.empty:
        fig_top = px.bar(
            top10,
            x="country",
            y="value",
            labels={"country": "Negara", "value": chosen_label},
        )
        st.plotly_chart(fig_top, use_container_width=True, key="top_chart")
    else:
        st.info("Tidak ada data untuk ditampilkan.")

with col_right:
    st.markdown("Bottom 10 Negara")
    if chosen_indicator == "Maternal Mortality":
        bottom10 = df_ind.sort_values("value", ascending=False).head(10)
    else:
        bottom10 = df_ind.sort_values("value", ascending=True).head(10)

    if not bottom10.empty:
        fig_bottom = px.bar(
            bottom10,
            x="country",
            y="value",
            labels={"country": "Negara", "value": chosen_label},
        )
        st.plotly_chart(fig_bottom, use_container_width=True, key="bottom_chart")
    else:
        st.info("Tidak ada data untuk ditampilkan.")
