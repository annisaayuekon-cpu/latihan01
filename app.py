import streamlit as st

st.set_page_config(
    page_title="Women & Development Dashboard",
    layout="wide",
    page_icon="👩",
)

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
            .stDataFrame thead tr th {
                background-color: #f8bbd0 !important;
                color: #880e4f !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_pink_theme()

st.title("Women & Development Dashboard")

st.markdown(
    """
Dashboard ini menggunakan data World Bank terkait perempuan:

- **Partisipasi angkatan kerja perempuan**
- **Pendidikan menengah perempuan**
- **Kesehatan ibu (maternal mortality)**

---

### 🎯 Tujuan Dashboard

Dashboard ini disusun untuk:

1. **Memberikan gambaran ringkas** perkembangan indikator utama perempuan lintas negara dan lintas tahun.
2. **Mempermudah analisis komparatif** antara negara, tanpa perlu mengunduh dan mengolah data World Bank berulang kali.
3. **Mendukung diskusi kebijakan** terkait kesetaraan gender, akses pendidikan, dan kualitas layanan kesehatan ibu.
4. **Mendukung kebutuhan akademik** (tugas kuliah, riset skripsi/tesis, policy brief) dengan visualisasi yang cepat dan intuitif.

---

### 📊 Definisi Indikator (berdasarkan World Bank)

1. **Female Labor Force Participation Rate (FLFP)**  
   Proporsi perempuan usia kerja yang **bekerja atau aktif mencari pekerjaan**
   dibandingkan dengan total populasi perempuan usia kerja (biasanya 15 tahun ke atas).

2. **Female Secondary School Enrolment**  
   Persentase pendaftaran perempuan pada jenjang **pendidikan menengah**  
   (secondary education) terhadap populasi perempuan pada kelompok umur resmi
   sekolah menengah di suatu negara.

3. **Maternal Mortality Ratio (MMR)**  
   Jumlah kematian ibu terkait kehamilan, persalinan, atau masa nifas  
   **per 100.000 kelahiran hidup** dalam satu periode tertentu.

Indikator-indikator ini saling melengkapi: partisipasi kerja perempuan
mencerminkan **keterlibatan ekonomi**, pendidikan menengah perempuan
berkaitan dengan **kapasitas manusia & peluang ekonomi**, sedangkan maternal
mortality menggambarkan **kualitas sistem kesehatan dan perlindungan ibu**.

---

### 🗺️ Cara Menggunakan Dashboard

Gunakan menu **Pages** di sidebar kiri untuk:

1. **📚 Overview of Womens Data**  
   Ringkasan global tiap indikator, termasuk **top/bottom negara** per tahun.

2. **🧑‍🍼 Country Profile**  
   Profil lengkap satu negara, berisi tren waktu dan ringkasan angka terbaru.

3. **🌍 Comparison between Nations**  
   Perbandingan beberapa negara dalam satu indikator dan satu tahun tertentu,
   untuk membantu membaca **kesenjangan dan kemajuan relatif** antar negara.
"""
)
