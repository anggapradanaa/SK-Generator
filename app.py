import streamlit as st
from docxtpl import DocxTemplate
from datetime import datetime
from io import BytesIO
import base64
import re
import os
import tempfile
import subprocess

st.set_page_config(page_title="Generator SK Otomatis", layout="wide")
st.title("📄 Generator Surat Keputusan (SK) Otomatis")

# Fungsi kapitalisasi pintar (mempertahankan huruf besar dalam tanda kurung)
def kapital_awal_dengan_akronim(text):
    def smart_cap(word):
        if re.match(r"\(.*\)", word):
            return word.upper()
        return word.capitalize()
    return " ".join([smart_cap(w) for w in text.split()])

# Inisialisasi state untuk anggota
if "jumlah_anggota" not in st.session_state:
    st.session_state.jumlah_anggota = 3  # default 3 anggota
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
    st.markdown("*Nomor Surat*  \n<sub><i>Contoh: 118/33760/SK/TAHUN 2025</i></sub>", unsafe_allow_html=True)
    no_surat = st.text_input("", key="no_surat", label_visibility="collapsed")
    st.markdown("*Nama Tim (untuk kapitalisasi otomatis)*  \n<sub><i>Contoh: TIM KOORDINASI SISTEM PEMERINTAHAN BERBASIS ELEKTRONIK (SPBE)</i></sub>", unsafe_allow_html=True)
    nama_tim = st.text_input("", key="nama_tim", label_visibility="collapsed")
    st.markdown("*Sebutan Nama Tim*  \n<sub><i>Contoh: Tim Koordinasi SPBE</i></sub>", unsafe_allow_html=True)
    sebutan_nama_tim = st.text_input("", key="sebutan_nama_tim", label_visibility="collapsed")
    tahun = st.text_input("Tahun", value=str(datetime.today().year))
    st.markdown("*Nama Kegiatan*  \n<sub><i>Contoh: SPBE</i></sub>", unsafe_allow_html=True)
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

    st.success("✅ SK berhasil dibuat!")

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

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
        doc.save(tmp_docx.name)
        tmp_docx_path = tmp_docx.name

    # Konversi ke PDF menggunakan pandoc
    tmp_pdf_path = tmp_docx_path.replace(".docx", ".pdf")
    try:
        subprocess.run(['pandoc', tmp_docx_path, '-o', tmp_pdf_path], check=True)
    except subprocess.CalledProcessError as e:
        st.error("❌ Gagal mengonversi DOCX ke PDF. Pastikan `pandoc` telah terinstal di sistem.")
        st.stop()

    # Download link
    with open(tmp_pdf_path, "rb") as f:
        pdf_bytes = f.read()
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        file_name = f"SK_{nama_tim.replace(' ', '_')}.pdf"
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{file_name}">📥 Download SK (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)

    os.remove(tmp_docx_path)
    os.remove(tmp_pdf_path)
