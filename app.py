import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd

def extract_mileage_data(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    sections = re.split(r"Timesheet\\s+number:\\s*\\d+", full_text)
    records = []

    name_pattern = re.compile(r"(Mr|Mrs|Miss|Ms)\\s+[A-Z][a-z]+\\s+[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)?")
    mileage_pattern = re.compile(r"MILEAGE\\s+TOTAL.*?£[\\d,]+\\.\\d{2}\\s+£[\\d,]+\\.\\d{2}\\s+£([\\d,]+\\.\\d{2})", re.DOTALL)

    for section in sections:
        name_match = name_pattern.search(section)
        mileage_match = mileage_pattern.search(section)
        if name_match and mileage_match:
            name = name_match.group().strip()
            mileage = float(mileage_match.group(1).replace(",", ""))
            if mileage > 0:
                records.append({ "Name": name, "Mileage": mileage })

    return pd.DataFrame(records)

st.title("Mileage Extractor from PDF Timesheets")

uploaded_files = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    all_data = pd.DataFrame()
    for file in uploaded_files:
        df = extract_mileage_data(file)
        df["Source File"] = file.name
        all_data = pd.concat([all_data, df], ignore_index=True)

    if not all_data.empty:
        st.dataframe(all_data)
        csv = all_data.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "mileage_summary.csv", "text/csv")
    else:
        st.info("No mileage data found in the uploaded PDFs.")
