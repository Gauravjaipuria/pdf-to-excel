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
        # Concatenate and drop fully empty columns
        df = pd.concat(all_data, ignore_index=True)
        df = df.loc[:,~df.columns.duplicated()].copy()
        # Make columns unique
        cols = pd.Series([str(c).strip() if c and str(c).strip() != '' else "column" for c in df.columns])
        for dup in cols[cols.duplicated()].unique():
            dup_idx = cols[cols == dup].index
            for i, idx in enumerate(dup_idx[1:], 1):
                cols[idx] = f"{dup}_{i}"
        df.columns = cols
        return df
    else:
        return pd.DataFrame()

st.title("PDF Invoice to Table & Excel")

uploaded_file = st.file_uploader("Upload invoice PDF", type=["pdf"])
if uploaded_file:
    with open("temp_invoice.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    df = extract_tables_from_pdf("temp_invoice.pdf")
    if not df.empty:
        st.write("Extracted Item Table (copy from here):")
        st.dataframe(df)
        st.text("Tab-separated for easy copying:")
        st.text(df.to_csv(sep='\t', index=False))
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        towrite.seek(0)
        st.download_button(
            label="Download Extracted Excel",
            data=towrite,
            file_name="Invoice_Extracted.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.write("No tables found in this PDF.")
