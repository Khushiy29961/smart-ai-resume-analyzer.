import streamlit as st
import requests
import PyPDF2
import os
import plotly.express as px
import pandas as pd

# Page config
st.set_page_config(page_title="Smart AI Resume Analyzer", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

# Glassmorphism & Custom Styling
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Force text color for all common elements */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: white !important;
    }
    
    /* Glowing Header */
    .glowing-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 15px rgba(79, 172, 254, 0.5);
        margin-bottom: 2rem;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(15, 32, 39, 0.6) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(45deg, #00f2fe, #4facfe);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.6);
    }
    
    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 15px;
        background: rgba(15, 32, 39, 0.8);
        backdrop-filter: blur(5px);
        border-top: 1px solid rgba(255,255,255,0.1);
        color: #8892b0;
        font-size: 0.9rem;
        z-index: 999;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">Developed by Khushi Yadav | GFG Campus Mantri</div>', unsafe_allow_html=True)

# Glowing Title
st.markdown('<div class="glowing-header">2026 Smart AI Resume Analyzer</div>', unsafe_allow_html=True)

# Fetch Backend URL from env var
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8080")

# Input Layout
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume in PDF format", type=["pdf"])

with col2:
    st.subheader("🎯 Job Description")
    job_description = st.text_area("Paste the job description here", height=150)
st.markdown('</div>', unsafe_allow_html=True)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

if st.button("🚀 Analyze Resume & Bridge the Semantic Gap"):
    if not uploaded_file or not job_description.strip():
        st.warning("⚠️ Please upload a resume and provide a job description.")
    else:
        with st.spinner("🤖 AI is analyzing context and identifying gaps..."):
            try:
                resume_text = extract_text_from_pdf(uploaded_file)
                
                # Make request to backend
                response = requests.post(
                    f"{BACKEND_URL}/analyze",
                    json={"resume_text": resume_text, "job_description": job_description}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✨ Analysis Complete!")
                    
                    st.markdown("---")
                    
                    # Top Metrics Row
                    met_col1, met_col2 = st.columns([1, 2])
                    
                    with met_col1:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        match_score = result.get("match_score", 0)
                        st.metric(label="🎯 ATS Match Score", value=f"{match_score}%")
                        st.progress(match_score / 100)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Skill Gap Radar
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader("Radar Chart")
                        radar_data = pd.DataFrame(dict(
                            r=[match_score, max(0, match_score-10), max(0, match_score-5), max(0, match_score-20), max(0, match_score-15)],
                            theta=['Technical', 'Soft Skills', 'Experience', 'Keywords', 'Education']
                        ))
                        fig = px.line_polar(radar_data, r='r', theta='theta', line_close=True)
                        fig.update_traces(fill='toself', fillcolor='rgba(0, 242, 254, 0.3)', line_color='#00f2fe')
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                    with met_col2:
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader("🔴 Identified Skill Gaps")
                        skill_gaps = result.get("skill_gaps", [])
                        if skill_gaps:
                            for skill in skill_gaps:
                                st.markdown(f"- ⚠️ {skill}")
                        else:
                            st.markdown("✅ No major skill gaps identified!")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader("✨ ATS Optimization (Impact Rewrites)")
                        impact_rewrites = result.get("impact_rewrites", [])
                        for i, rewrite in enumerate(impact_rewrites):
                            with st.expander(f"Suggestion {i+1}"):
                                st.write(rewrite)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                        st.subheader("📚 Learning Roadmap (GeeksforGeeks)")
                        learning_roadmap = result.get("learning_roadmap", [])
                        for topic in learning_roadmap:
                            st.markdown(f"- [📖 Learn {topic}](https://www.geeksforgeeks.org/search/?q={topic.replace(' ', '+')})")
                        st.markdown('</div>', unsafe_allow_html=True)

                else:
                    st.error(f"Backend Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
