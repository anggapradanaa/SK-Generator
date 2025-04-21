import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
from io import BytesIO
import re

st.set_page_config(page_title="Generator SK Otomatis BPS Kota Tegal", layout="wide")
st.title("📄 Generator Surat Keputusan (SK) Otomatis BPS Kota Tegal")

def kapital_awal_dengan_akronim(text):
    def smart_cap(word):
        if re.match(r"\(.*\)", word):
            return word.upper()
        return word.capitalize()
    return " ".join([smart_cap(w) for w in text.split()])

# Inisialisasi session state
if "jumlah_anggota" not in st.session_state:
    st.session_state.jumlah_anggota = 3
if "anggota_nama" not in st.session_state:
    st.session_state.anggota_nama = [""] * st.session_state.jumlah_anggota

def tambah_anggota():
    st.session_state.jumlah_anggota += 1
    st.session_state.anggota_nama.append("")

def hapus_anggota():
    if st.session_state.jumlah_anggota > 1:
        st.session_state.jumlah_anggota -= 1
        st.session_state.anggota_nama.pop()

with st.form("form_sk"):
    st.subheader("📝 Informasi Umum")
    st.markdown("Nomor Surat  \n<sub><i>Contoh: 118/33760/SK/TAHUN 2025</i></sub>", unsafe_allow_html=True)
    no_surat = st.text_input("", key="no_surat", label_visibility="collapsed")
    st.markdown("Nama Tim (untuk kapitalisasi otomatis)  \n<sub><i>Contoh: TIM KOORDINASI SISTEM PEMERINTAHAN BERBASIS ELEKTRONIK (SPBE)</i></sub>", unsafe_allow_html=True)
    nama_tim = st.text_input("", key="nama_tim", label_visibility="collapsed")
    st.markdown("Sebutan Nama Tim  \n<sub><i>Contoh: Tim Koordinasi SPBE</i></sub>", unsafe_allow_html=True)
    sebutan_nama_tim = st.text_input("", key="sebutan_nama_tim", label_visibility="collapsed")
    tahun = st.text_input("Tahun", value=str(datetime.today().year))
    st.markdown("Nama Kegiatan  \n<sub><i>Contoh: SPBE</i></sub>", unsafe_allow_html=True)
    nama_kegiatan = st.text_input("", key="nama_kegiatan", label_visibility="collapsed")
    tanggal = st.date_input("Tanggal SK", value=datetime.today())

    st.subheader("👤 Penanggung Jawab & Koordinator")
    nama_pj = st.text_input("Nama Penanggung Jawab")
    nama_kor = st.text_input("Nama Koordinator")

    st.subheader("👥 Daftar Anggota")
    for i in range(st.session_state.jumlah_anggota):
        st.session_state.anggota_nama[i] = st.text_input(
            f"Nama Anggota {i+1}", value=st.session_state.anggota_nama[i], key=f"anggota_{i}"
        )

    col1, col2 = st.columns(2)
    with col1:
        st.form_submit_button("➕ Tambah Anggota", on_click=tambah_anggota)
    with col2:
        st.form_submit_button("➖ Hapus Anggota", on_click=hapus_anggota)

    submitted = st.form_submit_button("📄 Buat SK")

if submitted:
    anggota_list = []
    for i, nama in enumerate(st.session_state.anggota_nama):
        if nama.strip():
            anggota_list.append({
                "nama": nama.strip(),
                "jabatan": "Anggota",
                "index": i + 1
            })

    context = {
        "NO_SURAT": no_surat,
        "NAMA_TIM_KAPITAL": nama_tim.upper(),
        "TAHUN": tahun,
        "NAMA_KEGIATAN": nama_kegiatan,
        "NAMA_TIM_KAPITAL_Setiap_Awal_Kata": kapital_awal_dengan_akronim(nama_tim),
        "SEBUTAN_NAMA_TIM": sebutan_nama_tim,
        "TANGGAL": tanggal.strftime("%d %B %Y"),
        "NAMA_PENANGGUNG_JAWAB": nama_pj,
        "NAMA_KOORDINATOR": nama_kor,
        "anggota": anggota_list
    }

    doc = DocxTemplate("template_sk.docx")
    doc.render(context)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    file_name = f"SK_{nama_tim.replace(' ', '_')}.docx"
    st.download_button(
        label="📥 Download SK (Word)",
        data=output,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
