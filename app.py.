import streamlit as st
import google.generativeai as genai
import pdfplumber

# 1. CONFIGURATION
st.set_page_config(page_title="CibilPro Analyst", layout="wide")

# 2. HIDE MENU STYLE
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. API KEY SETUP
api_key = st.secrets.get("GEMINI_KEY")
if not api_key:
    st.error("⚠️ Server Error: API Key missing. Please contact admin.")
    st.stop()

genai.configure(api_key=api_key)

# 4. APP INTERFACE
st.title("📊 CibilPro Report Analyzer")
st.write("Upload your CIBIL PDF to get a free, instant recovery plan.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with st.spinner("Analyzing report..."):
        try:
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            # AI PROMPT
            prompt = f"""
            Analyze this CIBIL report.
            Identify: Total Overdue, 'Suit Filed' accounts, and DPD > 0.
            Provide a step-by-step recovery plan.
            
            Report Data: {text[:15000]}
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            st.success("Analysis Complete!")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Error: {e}")
