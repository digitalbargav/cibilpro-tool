import streamlit as st
import google.generativeai as genai
import pdfplumber
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="CibilPro V3.0", layout="wide")

# --- CSS TO FIX LAYOUT & DOWNLOADS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Make the entire app scrollable */
    .main {
        overflow: visible;
    }
    /* Style the download button to be green and big */
    .stDownloadButton button {
        background-color: #28a745; 
        color: white;
        width: 100%;
        padding: 15px;
        font-weight: bold;
        border: none;
        border-radius: 8px;
    }
    .stDownloadButton button:hover {
        background-color: #218838;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- API CHECK ---
api_key = st.secrets.get("GEMINI_KEY")
if not api_key:
    st.error("⚠️ CRITICAL ERROR: API Key is missing in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=api_key)

# --- HEADER (LOOK FOR THE V3.0 TAG) ---
st.title("📊 CibilPro Analyzer (v3.0)")
st.caption("If you see 'v3.0', the update worked!")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload CIBIL PDF", type="pdf")

# --- MAIN LOGIC ---
if uploaded_file:
    # 1. READ PDF
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        st.error(f"❌ Error reading PDF: {e}")
        st.stop()

    # 2. RUN AI (Only if not already in memory)
    # We use a unique key combining filename and 'v3' to force a fresh check
    state_key = f"analysis_v3_{uploaded_file.name}"
    
    if state_key not in st.session_state:
        status_box = st.info("🤖 AI is reading your report... Please wait...")
        try:
            prompt = f"""
            You are a Credit Expert. Analyze this CIBIL report.
            REPORT TEXT: {text[:25000]}
            
            OUTPUT FORMAT (Markdown):
            # 🚦 VERDICT: [SAFE / RISKY]
            
            ## 🚩 CRITICAL PROBLEMS
            * List specific accounts (Bank Name, Amount) that are 'Suit Filed', 'Written Off', or Overdue.
            
            ## 🛠️ RECOVERY STEPS
            1. [Immediate Action]
            2. [Short Term Plan]
            
            ## 📈 SCORE PREDICTION
            * Estimated Increase: +[Points]
            * Timeline: [Months]
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            # Save result to memory
            st.session_state[state_key] = response.text
            status_box.empty() # Remove loading message
            
        except Exception as e:
            st.error(f"AI Connection Error: {e}")
            st.stop()

    # 3. SHOW RESULTS (Always runs if state exists)
    if state_key in st.session_state:
        report_content = st.session_state[state_key]
        
        st.success("✅ Analysis Complete!")
        
        # DOWNLOAD BUTTON (Top priority placement)
        st.download_button(
            label="📥 DOWNLOAD FULL REPORT NOW",
            data=report_content,
            file_name="CibilPro_Analysis.md",
            mime="text/markdown"
        )
        
        st.markdown("---")
        st.markdown("### 📝 Full Report Preview:")
        # Use a container to ensure text wraps correctly
        with st.container():
            st.markdown(report_content)
