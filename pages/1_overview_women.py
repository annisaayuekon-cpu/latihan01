import streamlit as st
import pandas as pd
import plotly.express as px
import os
from typing import Dict

# nama file sesuai data kamu
FEMALE_EDU_FILE = "FEMALE SECONDARY.csv"
FEMALE_LFP_FILE = "FLFP.csv"
MATERNAL_MORT_FILE = "MATERNAL MORTALITY.csv"


def load_wb_indicator(filename: str, indicator_label: str) -> pd.DataFrame:
    """
    Baca file CSV World Bank versi kamu:
    - separator pakai ; (semicolon)
    - desimal pakai , (comma)
    Lalu diubah ke long format:
    country | country_code | year | value | indicator
    """
    path = os.path.join("data", filename)

    # sep=';' dan decimal=',' penting supaya angka terbaca float
    df = pd.read_csv(
        path,
        sep=";",
        engine="python",
        decimal=",",
    )

    # kolom tahun = semua kolom selain Country Name dan Country Code
    year_cols = [c for c in df.columns if c not in ["Country Name", "Country Code"]]

    df_long = df.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=year_cols,
        var_name="year",
        value_name="value",
    )

    df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce")
    df_long["indicator"] = indicator_label
    df_long = df_long.rename(
        columns={"Country Name": "country", "Country Code": "country_code"}
    )
    df_long = df_long.dropna(subset=["value", "year"])

    return df_long


@st.cache_data
def load_all_data() -> pd.DataFrame:
    lfp = load_wb_indicator(FEMALE_LFP_FILE, "Female LFP")
    edu = load_wb_indicator(FEMALE_EDU_FILE, "Female Secondary Enrolment")
    mort = load_wb_indicator(MATERNAL_MORT_FILE, "Maternal Mortality")

    all_df = pd.concat([lfp, edu, mort], ignore_index=True)
    all_df = all_df[all_df["year"] >= 1995]
    return all_df


st.title("Overview – Women & Development")

df = load_all_data()

available_years = sorted(df["year"].unique())
default_year = max(available_years) if available_years else None

selected_year = st.sidebar.selectbox(
    "Pilih Tahun",
    options=available_years,
    index=available_years.index(default_year) if default_year in available_years else 0,
)

df_year = df[df["year"] == selected_year]

st.subheader(f"Ringkasan Global Indikator Perempuan – {selected_year}")

# ringkasan global per indikator
summary = (
    df_year.groupby("indicator")["value"]
    .agg(["mean", "min", "max"])
    .reset_index()
)

col1, col2, col3 = st.columns(3)

lfp_row = summary[summary["indicator"] == "Female LFP"]
if not lfp_row.empty:
    col1.metric(
        "Rata-rata Female Labor Force Participation (%)",
        f"{lfp_row['mean'].iloc[0]:.1f}",
    )

edu_row = summary[summary["indicator"] == "Female Secondary Enrolment"]
if not edu_row.empty:
    col2.metric(
        "Rata-rata Female Secondary Enrolment (%)",
        f"{edu_row['mean'].iloc[0]:.1f}",
    )

mort_row = summary[summary["indicator"] == "Maternal Mortality"]
if not mort_row.empty:
    col3.metric(
        "Rata-rata Maternal Mortality\n(per 100.000 kelahiran)",
        f"{mort_row['mean'].iloc[0]:.0f}",
    )

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
