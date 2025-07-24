import streamlit as st
import fitz  # PyMuPDF
import re
import csv
import io

st.title("Travel Mileage Extractor")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in pdf_doc:
        text += page.get_text()

    # Split into sections per person
    sections = re.split(r"(?=Payroll\s+ID:\s*\d+)", text)
    results = []

    for section in sections:
        # Extract name
        name_match = re.search(r"Payroll\s+ID:\s*\d+\s+(Mr|Mrs|Miss|Ms)\s+[A-Za-z]+\s+[A-Za-z]+", section)
        name = name_match.group(0).split("Payroll ID:")[1].strip() if name_match else "Unknown"

        # Extract travel mileage total
        mileage_match = re.search(r"TRAVEL\s+MILEAGE.*?£\s?([\d,]+\.\d{2})", section, re.IGNORECASE)
        if mileage_match:
            mileage_str = mileage_match.group(1).replace(",", "")
            try:
                mileage = float(mileage_str)
            except ValueError:
                mileage = 0.0
            results.append({"name": name, "mileage": mileage})

    st.subheader("Extracted Travel Mileage")
    if results:
        for entry in results:
            st.write(f"{entry['name']} — £{entry['mileage']:.2f}")
    else:
        st.write("No travel mileage data found.")

    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["name", "mileage"])
    writer.writeheader()
    writer.writerows(results)

    st.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name="travel_mileage.csv",
        mime="text/csv"
    )
