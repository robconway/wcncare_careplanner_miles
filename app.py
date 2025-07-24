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

    lines = text.splitlines()
    results = []
    current_name = None
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect name after Payroll ID
        if "Payroll ID" in line:
            for j in range(i + 1, min(i + 6, len(lines))):
                if re.match(r"^(Mr|Mrs|Miss|Ms)\b", lines[j]):
                    current_name = lines[j].strip()
                    break

        # Detect TRAVEL MILEAGE followed by TOTAL
        if "TRAVEL MILEAGE" in line.upper():
            for j in range(i + 1, min(i + 6, len(lines))):
                if "TOTAL" in lines[j].upper():
                    monetary_values = []
                    for k in range(j + 1, min(j + 10, len(lines))):
                        money_match = re.findall(r"£\s?[\d,]+\.\d{2}", lines[k])
                        if money_match:
                            monetary_values.extend(money_match)
                        if len(monetary_values) >= 2:
                            break
                    if len(monetary_values) >= 2 and current_name:
                        mileage_str = monetary_values[1].replace("£", "").replace(",", "").strip()
                        try:
                            mileage = float(mileage_str)
                        except ValueError:
                            mileage = 0.0
                        results.append({"name": current_name, "mileage": mileage})
                    break
        i += 1

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
