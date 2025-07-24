import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from io import BytesIO

def extract_mileage_data_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # Find all name blocks and mileage values
    name_blocks = re.findall(
        r"((Mr|Mrs|Miss|Ms)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+).*?TOTAL.*?£[\\d,]+\\.\\d{2}\\s+£[\\d,]+\\.\\d{2}\\s+£([\\d,]+\\.\\d{2})",
        text, re.DOTALL
    )

    data = []
    for block in name_blocks:
        name = block[0].strip()
        mileage = float(block[2].replace(',', ''))
        if mileage > 0:
            data.append({
                "Name": name,
                "Mileage": mileage,
                "Source File": file.name
            })

    return data

# Streamlit UI
st.title("Mileage Extractor from PDF Timesheets")

uploaded_files = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for file in uploaded_files:
        extracted = extract_mileage_data_from_pdf(file)
        all_data.extend(extracted)

    if all_data:
        df = pd.DataFrame(all_data)
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "mileage_summary.csv", "text/csv")
    else:
        st.info("No mileage data found in the uploaded PDFs.")
