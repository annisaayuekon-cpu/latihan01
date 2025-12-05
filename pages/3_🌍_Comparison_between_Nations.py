import streamlit as st
import pandas as pd
import plotly.express as px
import os

 =========================
# TEMA PINK
# =========================
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
    separator ; dan desimal ,
    lalu ubah ke long format:
    country | country_code | year | value | indicator
    """
    path = os.path.join("data", filename)

    if not os.path.exists(path):
        st.error(f"File tidak ditemukan: {path}")
        return pd.DataFrame(columns=["country", "country_code", "year", "value", "indicator"])

    df = pd.read_csv(
        path,
        sep=";",       # file memakai ;
        engine="python",
        decimal=",",   # desimal memakai koma
    )

    # Kolom tahun = kolom yang diawali angka (mis "1995" atau "1995 [YR1995]")
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

    # Ambil empat digit pertama sebagai tahun
    df_long["year"] = df_long["year"].astype(str).str.slice(0, 4)
    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce")
    df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

    df_long["indicator"] = indicator_label
    df_long = df_long.rename(
        columns={"Country Name": "country", "Country Code": "country_code"}
    )

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

    # Samakan rentang tahun, mengikuti ketersediaan Maternal Mortality
    all_df = all_df[(all_df["year"] >= 1995) & (all_df["year"] <= 2023)]

    return all_df


# =========================
# UI HALAMAN
# =========================
st.title("Country Comparison – Women Indicators")

df = load_all_data()

if df.empty:
    st.error("Dataset kosong atau tidak berhasil dibaca. Periksa file di folder `data/`.")
    st.stop()

available_years = sorted(df["year"].unique())

if not available_years:
    st.error("Tidak ada tahun yang tersedia dalam data.")
    st.stop()

default_year = max(available_years)

indicator_options = {
    "Female Labor Force Participation (%)": "Female LFP",
    "Female Secondary Enrolment (%)": "Female Secondary Enrolment",
    "Maternal Mortality (per 100.000 births)": "Maternal Mortality",
}

col1, col2 = st.columns(2)

with col1:
    selected_year = st.selectbox(
        "Pilih Tahun",
        options=available_years,
        index=available_years.index(default_year),
    )

with col2:
    indicator_label = st.selectbox(
        "Pilih Indikator",
        options=list(indicator_options.keys()),
    )

indicator = indicator_options[indicator_label]

df_year = df[(df["year"] == selected_year) & (df["indicator"] == indicator)]

if df_year.empty:
    st.warning("Tidak ada data untuk kombinasi tahun dan indikator ini.")
    st.stop()

st.subheader(f"Perbandingan Negara – {indicator_label} ({selected_year})")

# Pilih banyak negara yang ingin ditampilkan
all_countries = sorted(df_year["country"].unique())
selected_countries = st.multiselect(
    "Filter negara tertentu (kosongkan bila ingin memakai semua negara)",
    options=all_countries,
)

if selected_countries:
    df_year = df_year[df_year["country"].isin(selected_countries)]

if df_year.empty:
    st.warning("Tidak ada data setelah filter negara diterapkan.")
    st.stop()

# Pilihan jumlah negara yang ditampilkan
# Hitung jumlah negara setelah filter
n_countries = len(df_year)

# Kalau negara sedikit, tidak usah slider ribet
if n_countries <= 5:
    top_n = n_countries
    st.caption(f"Menampilkan semua {n_countries} negara yang tersedia.")
else:
    max_allowed = min(50, n_countries)
    top_n = st.slider(
        "Tampilkan berapa negara di grafik",
        min_value=5,
        max_value=max_allowed,
        value=min(20, max_allowed),
    )

# Untuk maternal mortality, nilai lebih rendah berarti kinerja lebih baik
if indicator == "Maternal Mortality":
    df_sorted = df_year.sort_values("value", ascending=True).head(top_n)
    note_text = "Untuk maternal mortality, nilai yang lebih rendah berarti kinerja lebih baik."
else:
    df_sorted = df_year.sort_values("value", ascending=False).head(top_n)
    note_text = "Untuk indikator ini, nilai yang lebih tinggi berarti kinerja lebih baik."

st.caption(note_text)

fig_bar = px.bar(
    df_sorted,
    x="country",
    y="value",
    labels={"country": "Negara", "value": indicator_label},
)

st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{indicator}_{selected_year}")

st.markdown("### Data tabel")

table = df_sorted[["country", "value"]].rename(
    columns={"country": "Negara", "value": indicator_label}
)

st.dataframe(table, use_container_width=True)

