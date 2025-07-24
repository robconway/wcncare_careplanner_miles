import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd

def extract_mileage_data_from_pdf(file):
    # Open the PDF file
    doc = fitz.open(stream=file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Split the document into sections by timesheet number
    sections = re.split(r"Timesheet\\s+number:\\s*\\d+", full_text)

    # Patterns to extract name and mileage
    name_pattern = re.compile(r"(Mr|Mrs|Miss|Ms)\\s+[A-Z][a-z]+\\s+[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)?")
    mileage_pattern = re.compile(r"TRAVEL\\s+MILEAGE\\s+TOTAL.*?£[\\d,]+\\.\\d{2}\\s+£[\\d,]+\\.\\d{2}\\s+£([\\d,]+\\.\\d{2})", re.DOTALL)

    records = []
    for section in sections:
        name_match = name_pattern.search(section)
        mileage_match = mileage_pattern.search(section)
        if name_match and mileage_match:
            name = name_match.group().strip()
            mileage = float(mileage_match.group(1).replace(",", ""))
            if mileage > 0:
                records.append({"Name": name, "Mileage": mileage})

    return pd.DataFrame(records)

# Streamlit UI
st.title("Mileage Extractor from PDF Timesheets")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    df = extract_mileage_data_from_pdf(uploaded_file)
    if not df.empty:
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "mileage_summary.csv", "text/csv")
    else:
        st.warning("No mileage data found in the uploaded PDF.")
