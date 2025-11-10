import streamlit as st
import pdfplumber
import pandas as pd
import io

def extract_tables_from_pdf(pdf_path):
    all_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                all_data.append(df)
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def make_columns_unique(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        dup_idx = cols[cols == dup].index
        for i, idx in enumerate(dup_idx[1:], 1):
            cols[idx] = f"{dup}_{i}"
    df.columns = cols
    return df

st.title("PDF Invoice to Excel Converter")

uploaded_file = st.file_uploader("Upload your PDF invoice file", type=["pdf"])

if uploaded_file:
    with open("temp_invoice.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("Extracting tables from PDF...")
    extracted_df = extract_tables_from_pdf("temp_invoice.pdf")

    if not extracted_df.empty:
        extracted_df = make_columns_unique(extracted_df)

        st.write("Extracted Data Preview (you can select and copy this data):")
        st.dataframe(extracted_df)

        st.text("Raw data (tab separated) for easy copy-paste:")
        st.text(extracted_df.to_csv(sep='\t', index=False))

        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            extracted_df.to_excel(writer, index=False)
        towrite.seek(0)

        st.download_button(
            label="Download Extracted Excel",
            data=towrite,
            file_name="Invoices_Extracted.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.write("No tables found in the PDF.")
