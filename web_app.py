import os
import streamlit as st
from pypdf import PdfReader
from groq import Groq

# Mengambil API Key secara aman dari Secrets Streamlit Cloud
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="Asisten SK KPU Kubu Raya", page_icon="📄", layout="centered")
st.title("📄 Asisten Pencari & Tanya Jawab SK")
st.write("Analisis dokumen SK JDIH KPU Kubu Raya secara instan.")

@st.cache_data
def load_all_pdfs():
    text_data = ""
    pdf_folder = "./folder_sk"
    if os.path.exists(pdf_folder):
        for file in os.listdir(pdf_folder):
            if file.endswith(".pdf"):
                reader = PdfReader(os.path.join(pdf_folder, file))
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_data += extracted + "\n"
    return text_data

with st.spinner("Memuat dokumen SK..."):
    full_text = load_all_pdfs()

if not full_text:
    st.warning("⚠️ Belum ada file PDF SK di dalam folder proyek.")
else:
    st.success("✅ Dokumen SK Berhasil Dimuat dan Siap Dianalisis!")

query = st.text_input("Tulis pertanyaan tentang SK Anda di sini (Contoh: rekap PDPB TW III 2025):")

if query and full_text:
    with st.spinner("AI sedang menganalisis dokumen..."):
        context = full_text[:150000]
        
        prompt = f"""Jawab pertanyaan berikut secara akurat berdasarkan isi dokumen SK yang diberikan di bawah ini.

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
