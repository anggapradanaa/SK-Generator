import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
from io import BytesIO
import base64
import re

st.set_page_config(page_title="Generator SK Otomatis", layout="wide")
st.title("📄 Generator Surat Keputusan (SK) Otomatis")

# Fungsi kapitalisasi pintar (mempertahankan huruf besar dalam tanda kurung)
def kapital_awal_dengan_akronim(text):
    def smart_cap(word):
        if re.match(r"\(.*\)", word):
            return word.upper()  # huruf besar untuk konten dalam tanda kurung
        return word.capitalize()
    return " ".join([smart_cap(w) for w in text.split()])

with st.form("form_sk"):
    st.subheader("📝 Informasi Umum")
    st.markdown("**Nomor Surat**  \n<sub><i>Contoh: 118/33760/SK/TAHUN 2025</i></sub>", unsafe_allow_html=True)
    no_surat = st.text_input("", key="no_surat", label_visibility="collapsed")
    st.markdown("**Nama Tim (untuk kapitalisasi otomatis)**  \n<sub><i>Contoh: TIM KOORDINASI SISTEM PEMERINTAHAN BERBASIS ELEKTRONIK (SPBE)</i></sub>", unsafe_allow_html=True)
    nama_tim = st.text_input(label="", key="nama_tim", label_visibility="collapsed")
    st.markdown("**Sebutan Nama Tim**  \n<sub><i>Contoh: Tim Koordinasi SPBE</i></sub>", unsafe_allow_html=True)
    sebutan_nama_tim = st.text_input("", key="sebutan_nama_tim", label_visibility="collapsed")
    tahun = st.text_input("Tahun", value=str(datetime.today().year))
    st.markdown("**Nama Kegiatan**  \n<sub><i>Contoh: SPBE</i></sub>", unsafe_allow_html=True)
    nama_kegiatan = st.text_input("", key="nama_kegiatan", label_visibility="collapsed")
    tanggal = st.date_input("Tanggal SK", value=datetime.today())

    st.subheader("👤 Penanggung Jawab & Koordinator")
    nama_pj = st.text_input("Nama Penanggung Jawab")
    nama_kor = st.text_input("Nama Koordinator")

    st.subheader("👥 Daftar Anggota")
    jml_anggota = st.number_input("Jumlah Anggota", min_value=1, max_value=20, value=3)
    anggota_list = []

    for i in range(jml_anggota):
        nama = st.text_input(f"Nama Anggota {i+1}", key=f"nama_{i}")
        if nama.strip():  # hanya tambahkan anggota jika nama tidak kosong atau hanya spasi
            anggota_list.append({"nama": nama, "jabatan": "Anggota"})

    submitted = st.form_submit_button("📄 Buat SK")

if submitted:
    st.success("✅ SK berhasil dibuat!")

    # Siapkan data untuk template
    context = {
        "NO_SURAT": no_surat,
        "NAMA_TIM_KAPITAL": nama_tim.upper(),
        "TAHUN": tahun,
        "NAMA_KEGIATAN": nama_kegiatan,
        "NAMA_TIM_KAPITAL_Setiap_Awal_Kata": kapital_awal_dengan_akronim(nama_tim),
        "SEBUTAN_NAMA_TIM": sebutan_nama_tim,  # input mandiri
        "TANGGAL": tanggal.strftime("%d %B %Y"),
        "NAMA_PENANGGUNG_JAWAB": nama_pj,
        "NAMA_KOORDINATOR": nama_kor,
        "anggota": [{"nama": person['nama'], "jabatan": person['jabatan'], "index": i+1} for i, person in enumerate(anggota_list)]
    }

    # Load dan render template
    doc = DocxTemplate("template_sk.docx")
    doc.render(context)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    # Buat tombol download
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64}" download="SK_{nama_tim.replace(" ", "_")}.docx">📥 Download SK</a>'
    st.markdown(href, unsafe_allow_html=True)