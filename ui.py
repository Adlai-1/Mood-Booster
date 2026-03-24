import streamlit as st

@st.cache_data(show_spinner=False)
def _get_css() -> str:
    return """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');
            html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

            .stApp {
                background: linear-gradient(135deg, #fef9f0 0%, #fde8d8 40%, #e8f4fd 100%);
                min-height: 100vh;
            }
            .hero-banner {
                background: linear-gradient(120deg, #ff7e5f, #feb47b, #86a8e7, #91eae4);
                background-size: 300% 300%;
                animation: gradientShift 6s ease infinite;
                border-radius: 20px;
                padding: 2rem 2.5rem;
                margin-bottom: 2rem;
                text-align: center;
                box-shadow: 0 8px 32px rgba(255,126,95,0.3);
            }
            @keyframes gradientShift {
                0%   { background-position: 0% 50%; }
                50%  { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            .hero-banner h1 { font-weight: 900; font-size: 2.4rem; color: white; text-shadow: 2px 3px 8px rgba(0,0,0,0.2); margin: 0; }
            .hero-banner p  { color: rgba(255,255,255,0.92); font-size: 1rem; font-weight: 600; margin: 0.4rem 0 0; }

            .card {
                background: white;
                border-radius: 18px;
                padding: 1.6rem 2rem;
                margin-bottom: 1.4rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.07);
                border: 1px solid rgba(255,255,255,0.8);
            }
            .card-title {
                font-size: 0.85rem; font-weight: 800; text-transform: uppercase;
                letter-spacing: 1.5px; color: #ff7e5f; margin-bottom: 0.9rem;
            }
            .suggestion-box {
                background: linear-gradient(135deg, #fff9f0, #ffe8d5);
                border-left: 5px solid #ff7e5f;
                border-radius: 14px;
                padding: 1.1rem 1.4rem;
                margin-top: 0.8rem;
                font-size: 1.05rem; font-weight: 700; color: #4a2e1a;
                box-shadow: 0 3px 12px rgba(255,126,95,0.15);
            }
            .dim-row { display: flex; gap: 0.7rem; flex-wrap: wrap; margin: 0.4rem 0 0.8rem; }
            .dim-badge {
                border-radius: 50px; padding: 0.25rem 0.85rem;
                font-size: 0.8rem; font-weight: 800; letter-spacing: 0.5px;
            }
            .dim-valence-pos  { background:#d4f5e9; color:#145a32; }
            .dim-valence-neg  { background:#fde8e8; color:#7b1c1c; }
            .dim-arousal-high { background:#fff3cd; color:#7d5a00; }
            .dim-arousal-low  { background:#e8f4fd; color:#154360; }
            .dim-pa           { background:#e8daef; color:#512e5f; }
            .dim-na           { background:#fde8d8; color:#6e2c00; }
            .dim-quad         { background:#f0f0ff; color:#2c2c7a; }

            .score-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.8rem; margin: 0.6rem 0; }
            .score-tile {
                background: linear-gradient(135deg, #f8f9ff, #eef2ff);
                border-radius: 14px; padding: 0.8rem 0.6rem; text-align: center;
                border: 1px solid #dde3f5;
            }
            .score-tile-val {
                font-family: 'Space Mono', monospace;
                font-size: 1.5rem; font-weight: 700; color: #2c3e7a;
            }
            .score-tile-lbl { font-size: 0.7rem; font-weight: 800; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

            .wbi-ring {
                width: 120px; height: 120px; border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                margin: 0 auto 0.6rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.12);
                font-family: 'Space Mono', monospace;
                font-size: 2rem; font-weight: 700; color: white;
            }
            .verdict {
                text-align: center; font-size: 1.4rem; font-weight: 900;
                padding: 0.9rem; border-radius: 14px; margin-top: 0.8rem;
            }
            .verdict-positive { background:#d4edda; color:#155724; }
            .verdict-negative { background:#f8d7da; color:#721c24; }
            .verdict-balanced { background:#d1ecf1; color:#0c5460; }

            .mood-pill {
                display: inline-block;
                background: linear-gradient(135deg, #86a8e7, #91eae4);
                color: #1a3a5c; border-radius: 50px;
                padding: 0.25rem 0.8rem; margin: 0.2rem;
                font-size: 0.8rem; font-weight: 700;
            }
            .info-box {
                background: #f0f4ff; border-left: 4px solid #86a8e7;
                border-radius: 10px; padding: 0.8rem 1rem;
                font-size: 0.82rem; color: #3a4a7a; line-height: 1.6;
            }
            .stButton > button {
                background: linear-gradient(135deg, #ff7e5f, #feb47b) !important;
                color: white !important; font-family: 'Nunito', sans-serif !important;
                font-weight: 800 !important; font-size: 0.95rem !important;
                border: none !important; border-radius: 50px !important;
                padding: 0.5rem 1.6rem !important;
                box-shadow: 0 4px 14px rgba(255,126,95,0.35) !important;
                transition: transform 0.15s ease !important;
            }
            .stButton > button:hover { transform: translateY(-2px) !important; }

            /* ── Motivational Quote Card ── */
            .quote-card {
                background: linear-gradient(160deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
                border-radius: 20px;
                padding: 2rem 2rem 1.6rem;
                box-shadow: 0 12px 40px rgba(0,0,0,0.25);
                font-family: 'Nunito', sans-serif;
            }
            .quote-section {
                position: relative;
                padding: 0 0.5rem;
                margin-bottom: 1.6rem;
            }
            .quote-mark {
                font-size: 4rem;
                line-height: 1;
                color: #ff7e5f;
                opacity: 0.6;
                font-family: Georgia, serif;
                display: block;
                margin-bottom: -1rem;
            }
            .quote-mark-close {
                text-align: right;
                margin-top: -1rem;
                margin-bottom: 0;
            }
            .quote-text {
                font-size: 1.15rem;
                font-weight: 700;
                color: #f0f0f0;
                line-height: 1.7;
                font-style: italic;
                text-align: center;
                padding: 0 0.5rem;
            }
            .author-section {
                border-top: 1px solid rgba(255,255,255,0.1);
                border-bottom: 1px solid rgba(255,255,255,0.1);
                padding: 1rem 0;
                margin-bottom: 1.4rem;
                text-align: center;
            }
            .author-name {
                font-size: 1.1rem;
                font-weight: 900;
                color: #feb47b;
                letter-spacing: 0.5px;
            }
            .author-meta {
                font-size: 0.78rem;
                color: rgba(255,255,255,0.45);
                font-weight: 600;
                margin-top: 0.25rem;
                letter-spacing: 0.3px;
            }
            .context-section {
                background: rgba(255,255,255,0.05);
                border-left: 3px solid #ff7e5f;
                border-radius: 0 12px 12px 0;
                padding: 0.85rem 1.1rem;
            }
            .context-label {
                font-size: 0.7rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                color: #ff7e5f;
                margin-bottom: 0.4rem;
            }
            .context-text {
                font-size: 0.88rem;
                color: rgba(255,255,255,0.7);
                font-weight: 600;
                line-height: 1.6;
            }
            </style>"""

def ui_style():
    st.markdown(_get_css(), unsafe_allow_html=True)