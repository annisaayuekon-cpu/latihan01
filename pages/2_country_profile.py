import streamlit as st
import pandas as pd
import plotly.express as px
import os

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

    df = pd.read_csv(
        path,
        sep=";",       # file pakai ;
        engine="python",
        decimal=",",   # desimal pakai koma
    )

    # Kolom tahun = kolom yang diawali angka (mis. "1995", "1995 [YR1995]")
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

    # Ambil 4 digit pertama sebagai tahun
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

    # Samakan rentang tahun (menyesuaikan maternal mortality, max 2023)
    all_df = all_df[(all_df["year"] >= 1995) & (all_df["year"] <= 2023)]

    return all_df


# =========================
# UI HALAMAN
# =========================
st.title("Country Profile – Women Indicators")

df = load_all_data()

if df.empty:
    st.error("Dataset kosong atau tidak berhasil dibaca. Periksa file di folder `data/`.")
    st.stop()

countries = sorted(df["country"].unique())

if not countries:
    st.error("Tidak ada negara dalam dataset.")
    st.stop()

default_country = "Indonesia" if "Indonesia" in countries else countries[0]

selected_country = st.selectbox(
    "Pilih Negara",
    options=countries,
    index=countries.index(default_country) if default_country in countries else 0,
)

df_c = df[df["country"] == selected_country].sort_values("year")

if df_c.empty:
    st.warning("Tidak ada data untuk negara ini.")
    st.stop()

st.subheader(f"Profil Indikator Perempuan – {selected_country}")

# =========================
# METRIC TERBARU PER INDIKATOR
# =========================
col1, col2, col3 = st.columns(3)

for indicator, col in zip(
    ["Female LFP", "Female Secondary Enrolment", "Maternal Mortality"],
    [col1, col2, col3],
):
    dfi = df_c[df_c["indicator"] == indicator].sort_values("year")
    if dfi.empty:
        col.info(f"Tidak ada data untuk {indicator}.")
        continue

    last_row = dfi.iloc[-1]
    value = last_row["value"]
    year = int(last_row["year"])

    if indicator == "Maternal Mortality":
        label = "Maternal Mortality (per 100.000 kelahiran)"
        display = f"{value:.0f}"
    elif indicator == "Female LFP":
        label = "Female Labor Force Participation (%)"
        display = f"{value:.1f} %"
    else:
        label = "Female Secondary Enrolment (%)"
        display = f"{value:.1f} %"

    col.metric(
        label=f"{label} – {year}",
        value=display,
    )

st.markdown("---")

# =========================
# GRAFIK TREN
# =========================
st.markdown("### Tren indikator dari waktu ke waktu")

indicator_configs = {
    "Female LFP": "Female Labor Force Participation (%)",
    "Female Secondary Enrolment": "Female Secondary Enrolment (%)",
    "Maternal Mortality": "Maternal Mortality (per 100.000 kelahiran)",
}

for indicator, y_label in indicator_configs.items():
    dfi = df_c[df_c["indicator"] == indicator].sort_values("year")
    if dfi.empty:
        continue

    st.markdown(f"**{y_label}**")

    fig = px.line(
        dfi,
        x="year",
        y="value",
        markers=True,
        labels={"year": "Tahun", "value": y_label},
    )
    st.plotly_chart(fig, use_container_width=True, key=f"{indicator}_line")

st.markdown("---")

# =========================
# DATA TABEL
# =========================
st.markdown("### Data mentah negara ini")

pivot = (
    df_c.pivot_table(
        index="year",
        columns="indicator",
        values="value",
    )
    .reset_index()
    .sort_values("year")
)

if pivot.empty:
    st.info("Tidak ada data tabel untuk negara ini.")
else:
    st.dataframe(pivot, use_container_width=True)

