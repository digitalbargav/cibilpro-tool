import streamlit as st
import google.generativeai as genai
import pdfplumber
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="CibilPro Analyzer", layout="wide")

# --- HIDE STREAMLIT BRANDING ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDownloadButton button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- API SETUP ---
api_key = st.secrets.get("GEMINI_KEY")
if not api_key:
    st.error("⚠️ System Error: API Key missing. Please set it in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- APP HEADER ---
st.title("📊 CibilPro.ai Report Analyzer")
st.write("Upload your PDF to see the full problems, solutions, and score analysis.")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload CIBIL Report (PDF)", type="pdf")

# --- MAIN LOGIC ---
if uploaded_file is not None:
    # 1. READ PDF
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        st.stop()

    # 2. ANALYZE WITH AI (Only runs once per file)
    # We use a unique key for session state based on filename to avoid re-running
    if "analysis_result" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        
        with st.spinner("🤖 AI is analyzing 200+ credit factors... (Wait 10s)"):
            try:
                # The Prompt
                prompt = f"""
                You are a Senior Credit Officer. Analyze this CIBIL report.
                
                REPORT DATA: 
                {text[:20000]}

                OUTPUT INSTRUCTIONS:
                Provide a detailed Markdown report.
                
                Structure:
                ## 1. 🚦 Executive Summary
                * **Estimated Score:** (Extract or Estimate)
                * **Verdict:** (Safe / Caution / Risk)
                
                ## 2. 🚩 Critical Issues (The "Why")
                * List exactly which accounts are overdue, written off, or suit filed.
                * Show the bank name and amount for each.

                ## 3. 🛠️ Step-by-Step Fix Plan
                * **Immediate Action:** What to pay today.
                * **Dispute Strategy:** If any errors exist.
                * **Wait Period:** How long until score increases.

                ## 4. 📈 Projected Growth
                * "If you follow this plan, your score could rise by +X points in Y months."
                """
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                # Save to "Memory" (Session State)
                st.session_state.analysis_result = response.text
                st.session_state.current_file = uploaded_file.name
                
            except Exception as e:
                st.error(f"AI Error: {e}")

    # 3. DISPLAY RESULTS (This runs every time, even after clicking download)
    if "analysis_result" in st.session_state:
        report_text = st.session_state.analysis_result
        
        # --- DASHBOARD SECTION ---
        st.success("Analysis Success!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("👇 **Scroll Down for Full Report**")
        with col2:
            # --- THE WORKING DOWNLOAD BUTTON ---
            # Using data=report_text from session state fixes the "Stuck" issue
            st.download_button(
                label="📥 Download Full Report",
                data=report_text,
                file_name=f"Cibil_Analysis_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

        st.divider()
        
        # --- FULL REPORT DISPLAY ---
        st.markdown("### 📝 Detailed Analysis")
        st.markdown(report_text)
