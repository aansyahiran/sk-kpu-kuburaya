import os
import streamlit as st
from pypdf import PdfReader
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Asisten SK KPU Kubu Raya", page_icon="📄", layout="centered")
st.title("📄 Asisten Pencari & Tanya Jawab SK")
st.write("Analisis dokumen SK JDIH KPU Kubu Raya secara instan.")

full_text = ""

# 1. Otomatis baca dari folder lokal "folder_sk" jika ada
pdf_folder = "./folder_sk"
if os.path.exists(pdf_folder):
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(pdf_folder, file))
            for i, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    full_text += f"\n--- [{file} - Hal {i+1}] ---\n" + extracted

# 2. Opsional: Tambahan uploader jika ingin tambah file baru lewat web
uploaded_files = st.file_uploader("Atau upload dokumen PDF tambahan di sini (Opsional):", type=["pdf"], accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        reader = PdfReader(uploaded_file)
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                full_text += f"\n--- [{uploaded_file.name} - Hal {i+1}] ---\n" + extracted

if not full_text:
    st.warning("⚠️ Belum ada file PDF SK di dalam folder server maupun yang di-upload.")
else:
    st.success("✅ Dokumen SK berhasil dimuat dan siap dianalisis oleh AI!")

query = st.text_input("Tulis pertanyaan tentang SK Anda di sini (Contoh: rekap PDPB TW III 2025):")

if query and full_text:
    with st.spinner("AI sedang membaca dan menganalisis seluruh isi SK..."):
        context = full_text[:100000]
        
        prompt = f"""Anda adalah asisten ahli analisis dokumen Surat Keputusan (SK) KPU. 
Baca seluruh isi teks dokumen SK di bawah ini dengan sangat teliti, lalu jawab pertanyaan pengguna secara rinci, akurat, dan sebutkan data atau angka aslinya jika ada di dalam dokumen.

Isi Dokumen SK:
{context}

Pertanyaan: {query}
"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        answer = completion.choices[0].message.content

    st.markdown("### 🤖 Jawaban AI:")
    st.write(answer)
