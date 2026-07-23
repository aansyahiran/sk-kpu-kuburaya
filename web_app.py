import os
import streamlit as st
from pypdf import PdfReader
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Asisten SK KPU Kubu Raya", page_icon="📄", layout="centered")
st.title("📄 Asisten Pencari & Tanya Jawab SK")
st.write("Analisis dokumen SK JDIH KPU Kubu Raya secara instan.")

full_text = ""

# 1. Otomatis ambil teks dari folder server
pdf_folder = "./folder_sk"
if os.path.exists(pdf_folder):
    for file in os.listdir(pdf_folder):
        if file.endswith(".pdf"):
            try:
                reader = PdfReader(os.path.join(pdf_folder, file))
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        full_text += extracted + "\n"
            except Exception:
                pass

# 2. Opsional tambahan uploader
uploaded_files = st.file_uploader("Atau upload dokumen PDF tambahan (Opsional):", type=["pdf"], accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"

if not full_text.strip():
    st.warning("⚠️ Belum ada file SK di dalam folder server.")
else:
    st.success("✅ Dokumen SK kantor sudah siap dan aktif otomatis!")

query = st.text_input("Tulis pertanyaan tentang SK Anda di sini (Contoh: rekap PDPB TW III 2025):")

if query and full_text.strip():
    with st.spinner("AI sedang menganalisis dokumen..."):
        context = full_text[:2500]
        
        prompt = f"""Jawab pertanyaan berikut secara akurat berdasarkan ringkasan dokumen SK ini:

Dokumen SK:
{context}

Pertanyaan: {query}
"""

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            answer = completion.choices[0].message.content
            st.markdown("### 🤖 Jawaban AI:")
            st.write(answer)
        except Exception as e:
            st.error(f"Terjadi kesalahan pada koneksi AI: {e}")
