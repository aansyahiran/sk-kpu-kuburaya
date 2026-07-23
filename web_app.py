import os
import streamlit as st
from pypdf import PdfReader
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Asisten SK KPU Kubu Raya", page_icon="📄", layout="centered")
st.title("📄 Asisten Pencari & Tanya Jawab SK")
st.write("Analisis dokumen SK JDIH KPU Kubu Raya secara instan.")

uploaded_files = st.file_uploader("Upload dokumen PDF SK di sini:", type=["pdf"], accept_multiple_files=True)

full_text = ""

if uploaded_files:
    for uploaded_file in uploaded_files:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                full_text += extracted + "\n"
    st.success(f"✅ Berhasil memuat {len(uploaded_files)} dokumen PDF!")
else:
    pdf_folder = "./folder_sk"
    if os.path.exists(pdf_folder):
        for file in os.listdir(pdf_folder):
            if file.endswith(".pdf"):
                reader = PdfReader(os.path.join(pdf_folder, file))
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        full_text += extracted + "\n"

if not full_text:
    st.warning("⚠️ Silakan upload file PDF SK terlebih dahulu melalui tombol di atas.")

query = st.text_input("Tulis pertanyaan tentang SK Anda di sini (Contoh: rekap PDPB TW III 2025):")

if query and full_text:
    with st.spinner("AI sedang menganalisis dokumen..."):
        # Batasi konteks maksimal 15.000 karakter agar tidak overload/error API Status
        context = full_text[:15000]
        
        prompt = f"""Jawab pertanyaan berikut secara akurat berdasarkan ringkasan isi dokumen SK di bawah ini.

Dokumen SK:
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
