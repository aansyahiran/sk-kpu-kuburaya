import os
import streamlit as st
from pypdf import PdfReader
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Asisten SK KPU Kubu Raya", page_icon="📄", layout="centered")
st.title("📄 Asisten Pencari & Tanya Jawab SK")
st.write("Analisis dokumen SK JDIH KPU Kubu Raya secara instan.")

full_text = ""

uploaded_files = st.file_uploader("Upload dokumen PDF SK di sini:", type=["pdf"], accept_multiple_files=True)
if uploaded_files:
    for uploaded_file in uploaded_files:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"

if not full_text.strip():
    st.warning("⚠️ Silakan upload file PDF SK terlebih dahulu melalui tombol di atas.")
else:
    st.success("✅ Dokumen SK berhasil dimuat!")

query = st.text_input("Tulis pertanyaan tentang SK Anda di sini (Contoh: rekap PDPB TW III 2025):")

if query and full_text.strip():
    with st.spinner("AI sedang menganalisis dokumen..."):
        # Pangkas teks secara ketat maksimal 2.500 karakter agar aman dari limit gratis TPM Groq
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
