import streamlit as st
import pdfplumber
import pandas as pd
import io

def extract_tables_from_pdf(pdf_path):
    tables_extracted = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for t, table in enumerate(tables):
                # Skip tables with less than 2 columns
                if table and len(table[0]) >= 2:
                    # Reformat: Clean header, fill Nones, strip whitespace
                    header = [str(col or f"Column_{idx}").strip() for idx, col in enumerate(table[0])]
                    df = pd.DataFrame(table[1:], columns=header)
                    # Remove empty columns and fill NaN
                    df = df.dropna(axis=1, how='all').fillna('')
                    tables_extracted.append(df)
    return tables_extracted

def display_tables(tables):
    for idx, df in enumerate(tables):
        st.subheader(f"Table {idx+1}")
        st.dataframe(df, use_container_width=True)
        st.text("Tab-separated values for easy copying:")
        st.text(df.to_csv(sep='\t', index=False))

        # Download Excel button for each table
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=f'Table{idx+1}')
        towrite.seek(0)
        st.download_button(
            label=f"Download Table {idx+1} as Excel",
            data=towrite,
            file_name=f"Invoice_Table{idx+1}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.set_page_config(page_title="Invoice PDF Table Extractor", layout="centered")

st.title("Invoice PDF to Table & Excel Converter")
st.markdown("""
Upload a PDF invoice containing tables. This app will extract all tables (including item/product details and payment summaries) and display them below for easy reading, copying, and downloading.  
- Supports GST, retail, jewelry, and standard invoice templates  
- Download each table as Excel (multi-table export for complex invoices)  
- Easily copy tabular data  
""")

uploaded_file = st.file_uploader("Upload invoice PDF", type=["pdf"], help="Works best with invoices containing clearly formatted tables.")

if uploaded_file:
    st.info("Processing your PDF. Extraction may take a few seconds...")
    temp_path = "temp_invoice.pdf"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    tables = extract_tables_from_pdf(temp_path)
    if tables:
        display_tables(tables)
    else:
        st.error("No tables were found. Please make sure your PDF has readable tables (not just images). For image invoices, OCR tools will be required.")
else:
    st.caption("Accepts any invoice PDF with tables. If your invoices are scanned images, contact us for OCR support.")
