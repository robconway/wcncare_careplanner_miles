import streamlit as st
import fitz  # PyMuPDF
import re
import csv
import io

st.title("Travel Mileage Extractor (Under £200)")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in pdf_doc:
        text += page.get_text()

    sections = re.split(r"(?=Payroll\\s+ID:\\s*\\d+)", text)
    results = []

    for section in sections:
        # Extract name
        name_match = re.search(r"Payroll\\s+ID:\\s*\\d+\\s+(Mr|Mrs|Miss|Ms)\\s+[A-Za-z]+\\s+[A-Za-z]+", section)
        if name_match:
            name = name_match.group(0).split("Payroll ID:")[1].strip()
        else:
            continue

        # Look for 'BASIC PAY' followed by 4 £ values
        lines = section.splitlines()
        for i in range(len(lines)):
            if lines[i].strip().upper() == "BASIC PAY":
                pound_values = []
                for j in range(i + 1, i + 10):
                    if j < len(lines):
                        matches = re.findall(r"£\\s?([\\d,]+\\.\\d{2})", lines[j])
                        for match in matches:
                            pound_values.append(match.replace(",", ""))
                    if len(pound_values) >= 4:
                        break
                if len(pound_values) >= 3:
                    mileage = float(pound_values[2])
                    if mileage < 200:
                        results.append({"name": name, "mileage": mileage})
                break

    st.subheader("Filtered Travel Mileage (Under £200)")
    if results:
        for entry in results:
            st.write(f"{entry['name']} — £{entry['mileage']:.2f}")
    else:
        st.write("No valid travel mileage data found.")

    # CSV download
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["name", "mileage"])
    writer.writeheader()
    writer.writerows(results)

    st.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name="filtered_travel_mileage_under_200.csv",
        mime="text/csv"
    )
