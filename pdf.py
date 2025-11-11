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
                if table and len(table[0]) > 1:  # Avoid empty tables
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_data.append(df)
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
        df = df.loc[:,~df.columns.duplicated()].copy()
        # Unique, readable columns
        cols = pd.Series([str(c).strip() if c and str(c).strip() != '' else "Column" for c in df.columns])
        for dup in cols[cols.duplicated()].unique():
            dup_idx = cols[cols == dup].index
            for i, idx in enumerate(dup_idx[1:], 1):
                cols[idx] = f"{dup}_{i}"
        df.columns = cols
        return df
    else:
        return pd.DataFrame()

st.set_page_config(page_title="PDF Invoice Table Extractor", layout="centered")
st.markdown(
    """
    <style>
    .main { background-color: #faf6f0; }
    .css-1v0mbdj { background-color: #ece6f0; }
    .stButton button { background-color: #a698ed; color: white; font-weight: bold; border-radius: 4px; }
    .stTextArea textarea { background: #fff8f0; }
    .stDataFrame { background: #ffffff; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True
)

st.title("🧾 PDF Invoice Table Extractor")
st.subheader("Turn Invoices into Editable Excel and Shareable Tables")
st.write(
    "Upload any PDF invoice containing tables (GST, retail, jewelry, services, etc.). "
    "Extracted table data will appear below and can be easily copied or downloaded. "
    "Useful for accountants, finance professionals, and business owners!"
)

uploaded_file = st.file_uploader("📤 Upload invoice PDF", type=["pdf"])
if uploaded_file:
    with st.spinner("Extracting tables... Please wait."):
        temp_path = "temp_invoice.pdf"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        df = extract_tables_from_pdf(temp_path)
        if not df.empty:
            st.success("✅ Table extracted successfully!")
            st.markdown("### Preview & Copy")
            st.dataframe(df, use_container_width=True)
            st.markdown("#### Tab-separated table (easy to copy):")
            st.text_area("Tab-separated Data", df.to_csv(sep='\t', index=False), height=200)
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            towrite.seek(0)
            st.download_button(
                label="⬇️ Download Excel",
                data=towrite,
                file_name="Invoice_Extracted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.caption("Tip: Use the table preview for quick analysis or copy tabular values for spreadsheet apps.")
        else:
            st.error("⚠️ No tables found in this PDF. Make sure your invoice is not just an image. For scanned images, OCR may be required.")
else:
    st.info("Please upload an invoice PDF above to begin extracting tables.")

st.markdown("---")
st.caption("Powered by pdfplumber, pandas, and Streamlit. Designed for modern business users.")
