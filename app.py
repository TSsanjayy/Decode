import streamlit as st
import os
import json
import re
from dotenv import load_dotenv

# Universal SDK Handler
USE_NEW_SDK = False
try:
    from google import genai
    from google.genai import types
    USE_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as legacy_genai
        USE_NEW_SDK = False
    except ImportError:
        pass

load_dotenv()

st.set_page_config(
    page_title="Decode — Know What You Code.",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── API SETUP ──────────────────────────────────────────────
env_api_key = os.getenv("GEMINI_API_KEY", "")

with st.sidebar:
    st.markdown('<div class="sidebar-eyebrow">Configuration</div><div class="sidebar-title">⚙️ Engine Settings</div>', unsafe_allow_html=True)
    user_api_key = st.text_input("Gemini API Key", value=env_api_key, type="password")
    selected_model = st.selectbox(
        "Model Version",
        ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash"],
        index=0
    )
    _key_live = user_api_key.strip() if user_api_key else env_api_key.strip()
    if _key_live:
        st.markdown(
            f'<div class="status-chip online"><span class="status-dot"></span>API Key Connected</div>'
            f'<div class="status-chip" style="background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.4);color:#93C5FD;">'
            f'<span class="status-dot"></span>{selected_model}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="status-chip offline"><span class="status-dot"></span>No API Key</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-eyebrow" style="margin-bottom:8px;">Decode Features</div>', unsafe_allow_html=True)
    _features = [
        ("🚨", "Instant Bug / Error Detection & Fix"),
        ("📊", "Deep Time & Space Complexity Breakdown"),
        ("🧩", "Smart Functional Segments"),
        ("🧠", "Simple Purpose & Logic Explanations"),
        ("📖", "Line-by-Line Logic Breakdown"),
        ("⚡", "Code Optimizer & Comparison"),
        ("💬", "Contextual Code Tutor"),
    ]
    for _icon, _label in _features:
        st.markdown(
            f'<div class="sidebar-feature-row"><span class="sidebar-feature-icon">{_icon}</span><span>{_label}</span></div>',
            unsafe_allow_html=True
        )

ACTIVE_API_KEY = user_api_key.strip() if user_api_key else env_api_key.strip()

client = None
legacy_model = None

if ACTIVE_API_KEY:
    try:
        if USE_NEW_SDK:
            client = genai.Client(api_key=ACTIVE_API_KEY)
        else:
            legacy_genai.configure(api_key=ACTIVE_API_KEY)
            legacy_model = legacy_genai.GenerativeModel(selected_model)
    except Exception as e:
        st.sidebar.error(f"Error initializing client: {e}")

# ── CSS & CUSTOM TYPOGRAPHY ────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700;800;900&family=Orbitron:wght@700;800;900&display=swap');

html, body, [class*="css"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
}
code, pre { 
    font-family: 'JetBrains Mono', monospace !important; 
}

.stApp {
    background:
        radial-gradient(circle at 10% 15%, rgba(124,58,237,0.16), transparent 40%),
        radial-gradient(circle at 90% 15%, rgba(217,119,6,0.11), transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(236,72,153,0.08), transparent 45%),
        repeating-linear-gradient(0deg, rgba(255,255,255,0.014) 0px, rgba(255,255,255,0.014) 1px, transparent 1px, transparent 46px),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.014) 0px, rgba(255,255,255,0.014) 1px, transparent 1px, transparent 46px),
        #030204;
    color: #F1F5F9;
}
.block-container { padding-top: 0.6rem; padding-bottom: 2rem; max-width: 100%; }

/* Gradient dividers instead of plain gray lines */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(168,85,247,0.5), rgba(244,114,182,0.4), transparent) !important;
    margin: 14px 0 !important;
}

/* Streamlit button polish: rounded pill, subtle lift on hover */
.stButton button {
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    transition: border-color 0.18s ease, background 0.18s ease !important;
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: #E2E8F0 !important;
}
.stButton button:hover {
    border-color: rgba(59,130,246,0.5) !important;
    background: rgba(59,130,246,0.08) !important;
}
.stButton button[kind="primary"] {
    background: rgba(59,130,246,0.16) !important;
    border: 1px solid rgba(59,130,246,0.6) !important;
    color: #BFDBFE !important;
    box-shadow: none !important;
}
.stButton button[kind="primary"]:hover {
    background: rgba(59,130,246,0.25) !important;
    border-color: rgba(59,130,246,0.85) !important;
}

[data-testid="stHorizontalBlock"] > div:first-child {
    position: sticky !important;
    top: 60px !important;
    align-self: flex-start !important;
    height: fit-content !important;
}

/* ── SCROLLBARS ── */
.scroll-container {
    max-height: 74vh;
    overflow-y: auto;
    padding-right: 8px;
    scrollbar-width: thin;
    scrollbar-color: rgba(139,92,246,0.5) rgba(16,15,19,0.6);
}
.scroll-container::-webkit-scrollbar { width: 6px; }
.scroll-container::-webkit-scrollbar-track { background: rgba(16,15,19,0.6); border-radius: 10px; }
.scroll-container::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #A855F7, #F472B6); border-radius: 10px; }

.inspect-box {
    background: rgba(3,3,6,0.95);
    border: 1px solid rgba(139,92,246,0.35);
    border-radius: 14px;
    padding: 14px;
    margin-top: 10px;
    margin-bottom: 14px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.5);
}
.inspect-scroll {
    max-height: 240px;
    overflow-y: auto;
    padding-right: 6px;
    scrollbar-width: thin;
    scrollbar-color: rgba(139,92,246,0.5) rgba(16,15,19,0.6);
}
.inspect-scroll::-webkit-scrollbar { width: 5px; }
.inspect-scroll::-webkit-scrollbar-track { background: rgba(16,15,19,0.6); border-radius: 8px; }
.inspect-scroll::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #A855F7, #F472B6); border-radius: 8px; }

/* ── HERO BANNER ── */
.hero-header {
    position: relative;
    padding: 20px 32px;
    border-radius: 18px;
    background:
        radial-gradient(circle at 88% -25%, rgba(59,130,246,0.18), transparent 55%),
        radial-gradient(circle at 8% 130%, rgba(96,165,250,0.10), transparent 55%),
        linear-gradient(135deg, rgba(7,7,9,0.99) 0%, rgba(5,5,7,0.99) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
    box-shadow: 0 14px 38px rgba(0,0,0,0.65), 0 0 0 1px rgba(59,130,246,0.06), inset 0 1px 0 rgba(255,255,255,0.04);
    overflow: hidden;
}
.hero-header::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #3B82F6, #60A5FA, #3B82F6, transparent);
    opacity: 0.9;
}
.hero-left {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.hero-brand-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 10px;
}
.hero-brand-dash {
    display: inline-block;
    width: 16px;
    height: 3px;
    border-radius: 2px;
    background: #60A5FA;
    box-shadow: 0 0 8px rgba(96,165,250,0.7);
}
.hero-brand {
    font-size: 46px;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
    letter-spacing: 4px;
    text-transform: uppercase;
    font-family: 'Orbitron', 'Space Grotesk', sans-serif;
    color: #E8ECF1;
    text-shadow: 0 0 1px rgba(232,236,241,0.6), 0 0 16px rgba(148,163,184,0.2);
    display: inline-block;
    transform: scaleY(1.2);
    transform-origin: center;
}
.hero-tagline {
    color: #94A3B8;
    font-size: 13.5px;
    font-weight: 800;
    letter-spacing: 2.8px;
    text-transform: uppercase;
    margin-top: 8px;
    font-family: 'Space Grotesk', sans-serif;
}
.tagline-code {
    font-weight: 900;
    color: #60A5FA;
    text-shadow: 0 0 10px rgba(96,165,250,0.45);
}
.hero-right {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    position: relative;
    z-index: 1;
}
.hero-badge {
    position: relative;
    background: rgba(59,130,246,0.10);
    border: 1px solid rgba(96,165,250,0.4);
    padding: 9px 20px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 700;
    color: #93C5FD;
    font-family: 'Space Grotesk', sans-serif;
    white-space: nowrap;
}
.hero-chip-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(118px, 1fr));
    gap: 8px;
}
.hero-chip {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    color: #CBD5E1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 7px 12px;
    border-radius: 9px;
    white-space: nowrap;
    text-align: center;
}


.glass-card {
    background: rgba(4,4,7,0.94);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
    backdrop-filter: blur(10px);
    transition: border-color 0.2s ease;
}
.glass-card:hover {
    border-color: rgba(168,85,247,0.35);
}
.panel-heading {
    font-size: 18px;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 10px;
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: 0.3px;
}

/* ── EXACT IMAGE PILL HEADER ── */
.segment-header-card {
    width: 100%;
    border-radius: 14px;
    padding: 12px 18px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    transition: all 0.2s ease;
}
.segment-header-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
}
.segment-header-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #94A3B8;
}

/* ── ERROR DISPLAY ── */
.error-box {
    background: linear-gradient(135deg, rgba(220,38,38,0.18), rgba(153,27,27,0.28));
    border: 1px solid rgba(239,68,68,0.5);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 8px 25px rgba(239,68,68,0.15);
}
.error-title {
    color: #F87171;
    font-size: 18px;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── COMPLEXITY BOXES ── */
/* ── UNIFIED STAT CARD (like reference "141 MODULES | 1872 RESOURCES") ── */
.stat-card {
    display: flex;
    align-items: center;
    background: rgba(3,3,6,0.95);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 14px;
}
.stat-half {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}
.stat-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: -0.5px;
    line-height: 1.1;
}
.stat-label {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #94A3B8;
    margin-top: 4px;
}
.stat-divider {
    width: 1px;
    align-self: stretch;
    background: rgba(255,255,255,0.10);
    margin: 0 20px;
}

.complexity-box {
    background: rgba(3,3,6,0.95);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 8px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.5);
}
.complexity-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    font-weight: 900;
    margin: 4px 0;
    letter-spacing: -0.5px;
}
.eyebrow {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: #71717A;
    margin-bottom: 4px;
    font-family: 'Space Grotesk', sans-serif;
}

/* ── STEP-BY-STEP SCROLLABLE PROOF ── */
.step-scroll-box {
    max-height: 260px;
    overflow-y: auto;
    padding: 4px 10px 4px 2px;
    margin-top: 8px;
    scrollbar-width: thin;
    scrollbar-color: rgba(139,92,246,0.5) rgba(16,15,19,0.6);
}
.step-scroll-box::-webkit-scrollbar { width: 5px; }
.step-scroll-box::-webkit-scrollbar-track { background: rgba(16,15,19,0.6); border-radius: 8px; }
.step-scroll-box::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #A855F7, #F472B6); border-radius: 8px; }
.step-row {
    display: flex;
    gap: 10px;
    background: rgba(3,3,6,0.9);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 9px 12px;
    margin-bottom: 7px;
    font-size: 12.5px;
    color: #E2E8F0;
    line-height: 1.5;
    transition: border-color 0.2s ease;
}
.step-row:hover { border-color: rgba(192,132,252,0.4); }
.step-num {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 800;
    background: rgba(139,92,246,0.22);
    color: #C084FC;
}

/* ── CLEAN SEGMENT PILL (no emoji, vivid solid accent) ── */
.segment-pill {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 12px;
    padding: 13px 18px;
    margin-bottom: 12px;
    border-left-width: 4px;
    border-left-style: solid;
    border-top: 1px solid rgba(255,255,255,0.06);
    border-right: 1px solid rgba(255,255,255,0.06);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(3,3,6,0.96);
    box-shadow: 0 2px 10px rgba(0,0,0,0.35);
    transition: box-shadow 0.2s ease;
}
.segment-pill:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
}
.segment-pill-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 14.5px;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.segment-pill-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px;
    font-weight: 700;
    color: #94A3B8;
    background: rgba(255,255,255,0.05);
    padding: 3px 10px;
    border-radius: 20px;
    flex-shrink: 0;
    margin-left: 10px;
}

/* ── CODE SUMMARY & KEY FEATURES ── */
.summary-box {
    background: rgba(4,4,7,0.95);
    border: 1px solid rgba(251,191,36,0.3);
    border-radius: 14px;
    padding: 16px 18px;
    margin-top: 10px;
    margin-bottom: 14px;
    box-shadow: 0 6px 22px rgba(0,0,0,0.5);
}
.summary-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px;
    font-weight: 800;
    color: #FBBF24;
    letter-spacing: 0.3px;
    margin: 0 0 8px 0;
}
.summary-heading.alt { color: #C084FC; margin-top: 16px; }
.summary-text {
    font-size: 13.5px;
    color: #E2E8F0;
    line-height: 1.6;
    margin: 0 0 4px 0;
}
.how-it-works-row {
    display: flex;
    gap: 10px;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 13px;
    color: #E2E8F0;
    line-height: 1.5;
}
.how-it-works-num {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    font-weight: 800;
    background: rgba(251,191,36,0.18);
    color: #FBBF24;
}
.key-feature-row {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 13px;
    color: #E2E8F0;
    line-height: 1.55;
}
.key-feature-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #FCD34D;
    background: rgba(252,211,77,0.12);
    padding: 2px 8px;
    border-radius: 6px;
    margin-right: 6px;
}

/* ── CLEAN DETAIL PANEL (no emoji) ── */
.detail-banner {
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    margin: 8px 0 10px 0;
    font-size: 13.5px;
    font-weight: 500;
    line-height: 1.55;
    color: #E2E8F0;
    border-left: 4px solid;
}
.detail-label {
    display: block;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 3px;
    opacity: 0.9;
}

.use-banner {
    background: linear-gradient(90deg, rgba(251,191,36,0.12), rgba(124,58,237,0.08));
    border-left: 4px solid #FBBF24;
    padding: 10px 14px;
    border-radius: 0 10px 10px 0;
    color: #E2E8F0;
    font-size: 13.5px;
    font-weight: 500;
    margin: 8px 0 10px 0;
    line-height: 1.5;
}
.logic-banner {
    background: linear-gradient(90deg, rgba(192,132,252,0.12), rgba(124,58,237,0.08));
    border-left: 4px solid #C084FC;
    padding: 10px 14px;
    border-radius: 0 10px 10px 0;
    color: #E2E8F0;
    font-size: 13.5px;
    font-weight: 500;
    margin: 8px 0 10px 0;
    line-height: 1.5;
}

.badge-match {
    padding: 12px 16px;
    border-radius: 10px;
    background: rgba(3,3,6,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #10B981;
    color: #6EE7B7;
    font-weight: 600;
    font-size: 13.5px;
    margin-bottom: 12px;
}
.badge-partial {
    padding: 12px 16px;
    border-radius: 10px;
    background: rgba(3,3,6,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #F59E0B;
    color: #FCD34D;
    font-weight: 600;
    font-size: 13.5px;
    margin-bottom: 12px;
}
.badge-mismatch {
    padding: 12px 16px;
    border-radius: 10px;
    background: rgba(3,3,6,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #EF4444;
    color: #FCA5A5;
    font-weight: 600;
    font-size: 13.5px;
    margin-bottom: 12px;
}

.complexity-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(28,25,29,0.85);
    border: 1px solid rgba(255,255,255,0.12);
    color: #FBBF24;
    margin-right: 6px;
}

.code-header {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-bottom: none;
    border-radius: 10px 10px 0 0;
    padding: 8px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #94A3B8;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.code-header .code-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}
div[data-testid="element-container"]:has(.code-header) + div[data-testid="element-container"] pre {
    margin-top: 0 !important;
    border-top-left-radius: 0 !important;
    border-top-right-radius: 0 !important;
}

.line-card {
    background: rgba(3,3,6,0.9);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.line-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #FCD34D;
    background: rgba(0,0,0,0.5);
    padding: 5px 8px;
    border-radius: 6px;
    margin-bottom: 6px;
    display: block;
    word-break: break-all;
}

.showcase-box {
    background: rgba(4,4,7,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s ease;
}
.showcase-box:hover {
    border-color: rgba(168,85,247,0.35);
}
.showcase-icon { font-size: 22px; margin-bottom: 6px; }
.showcase-title { font-size: 14.5px; font-weight: 700; color: #F1F5F9; font-family: 'Space Grotesk', sans-serif; }
.showcase-desc { font-size: 12.5px; color: #94A3B8; margin-top: 4px; line-height: 1.4; }

.stTextArea textarea {
    background-color: rgba(3,3,6,0.92) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13.5px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextArea textarea:focus {
    border-color: rgba(59,130,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
.stTextInput input {
    background-color: rgba(3,3,6,0.92) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput input:focus {
    border-color: rgba(59,130,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.03);
    padding: 5px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.07);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    padding: 8px 18px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    color: #94A3B8;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: rgba(59,130,246,0.16) !important;
    color: #BFDBFE !important;
}
.stTabs [data-baseweb="tab-highlight"] { background: transparent !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── WORKFLOW STEPPER ── */
.stepper {
    display: flex;
    align-items: flex-start;
    margin-bottom: 10px;
}
.step-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    position: relative;
}
.step-circle {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 10.5px;
    font-weight: 800;
    border: 2px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.03);
    color: #71717A;
    z-index: 1;
}
.step-circle.done {
    border-color: #3B82F6;
    background: rgba(59,130,246,0.18);
    color: #93C5FD;
}
.step-circle.active {
    border-color: #3B82F6;
    background: #3B82F6;
    color: #fff;
}
.step-label {
    font-size: 10px;
    font-weight: 700;
    color: #71717A;
    margin-top: 4px;
    text-align: center;
    letter-spacing: 0.3px;
}
.step-label.on { color: #BFDBFE; }
.step-line {
    position: absolute;
    top: 11px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: rgba(255,255,255,0.10);
    z-index: 0;
}
.step-line.done { background: #3B82F6; }
.step-item:last-child .step-line { display: none; }

/* ── SIDEBAR POLISH ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(6,6,9,0.99) 0%, rgba(4,4,6,0.99) 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.03) !important;
    border-color: rgba(255,255,255,0.10) !important;
}
.sidebar-eyebrow {
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: #71717A;
    margin-bottom: 2px;
    font-family: 'Space Grotesk', sans-serif;
}
.sidebar-title {
    font-size: 17px;
    font-weight: 800;
    color: #F1F5F9;
    font-family: 'Space Grotesk', sans-serif;
    margin-bottom: 14px;
}
.status-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 11.5px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    margin-bottom: 14px;
    margin-right: 6px;
}
.status-chip.online {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.4);
    color: #6EE7B7;
}
.status-chip.offline {
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.4);
    color: #FCA5A5;
}
.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: currentColor;
}
.sidebar-feature-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 9px;
    font-size: 12.5px;
    color: #CBD5E1;
    margin-bottom: 4px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
}
.sidebar-feature-icon { font-size: 14px; flex-shrink: 0; }
</style>""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────
defaults = {
    "code_input": "", "goal_input": "", "language": "Python",
    "analysis_data": None, "improved_data": None,
    "chat_history": {}, "active_inspect_tab": None,
    "show_time_steps": False, "show_space_steps": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── EXACT ATTACHED IMAGE THEMES (Vibrant & Neon) ───────────
SEGMENT_THEMES = [
    {
        "icon": "✨", "color": "#C084FC", "st_color": "violet",
        "bg": "linear-gradient(90deg, rgba(88,28,135,0.45) 0%, rgba(30,15,60,0.7) 100%)",
        "border": "1px solid rgba(192,132,252,0.65)"
    },
    {
        "icon": "📥", "color": "#60A5FA", "st_color": "blue",
        "bg": "linear-gradient(90deg, rgba(30,64,175,0.4) 0%, rgba(12,20,40,0.7) 100%)",
        "border": "1px solid rgba(96,165,250,0.55)"
    },
    {
        "icon": "⚙️", "color": "#FB923C", "st_color": "orange",
        "bg": "linear-gradient(90deg, rgba(194,65,12,0.45) 0%, rgba(45,20,15,0.7) 100%)",
        "border": "1px solid rgba(251,146,60,0.65)"
    },
    {
        "icon": "🧮", "color": "#34D399", "st_color": "green",
        "bg": "linear-gradient(90deg, rgba(4,120,87,0.45) 0%, rgba(10,35,25,0.7) 100%)",
        "border": "1px solid rgba(52,211,153,0.65)"
    },
    {
        "icon": "🔀", "color": "#F472B6", "st_color": "red",
        "bg": "linear-gradient(90deg, rgba(190,24,93,0.45) 0%, rgba(40,15,30,0.7) 100%)",
        "border": "1px solid rgba(244,114,182,0.65)"
    },
    {
        "icon": "🔄", "color": "#FBBF24", "st_color": "orange",
        "bg": "linear-gradient(90deg, rgba(180,83,9,0.45) 0%, rgba(40,25,10,0.7) 100%)",
        "border": "1px solid rgba(251,191,36,0.65)"
    },
    {
        "icon": "📤", "color": "#2DD4BF", "st_color": "green",
        "bg": "linear-gradient(90deg, rgba(15,118,110,0.45) 0%, rgba(10,30,30,0.7) 100%)",
        "border": "1px solid rgba(45,212,191,0.65)"
    },
    {
        "icon": "🚀", "color": "#818CF8", "st_color": "violet",
        "bg": "linear-gradient(90deg, rgba(67,56,202,0.45) 0%, rgba(20,15,50,0.7) 100%)",
        "border": "1px solid rgba(129,140,248,0.65)"
    }
]

def get_segment_theme(idx, name):
    n = name.lower()
    if "init" in n: return SEGMENT_THEMES[0]
    if "input" in n or "read" in n or "prompt" in n or "add" in n: return SEGMENT_THEMES[1]
    if "calc" in n or "total" in n or "sum" in n or "math" in n: return SEGMENT_THEMES[3]
    if "decision" in n or "check" in n or "if" in n or "branch" in n or "find" in n: return SEGMENT_THEMES[4]
    if "loop" in n or "iterat" in n or "for" in n or "while" in n: return SEGMENT_THEMES[5]
    if "output" in n or "print" in n or "display" in n or "show" in n: return SEGMENT_THEMES[6]
    if "main" in n or "exec" in n or "entry" in n: return SEGMENT_THEMES[7]
    return SEGMENT_THEMES[(idx - 1) % len(SEGMENT_THEMES)]

# ── TEMPLATES ──────────────────────────────────────────────
CODE_TEMPLATES = {
    "Expense Tracker (Python)": {
        "lang": "Python",
        "aim": "Track, store, total, and display personal expenses. Find the highest expense.",
        "code": (
            "class ExpenseTracker:\n"
            "    def __init__(self):\n"
            "        self.expenses = []\n\n"
            "    def add_expense(self, name, amount):\n"
            "        self.expenses.append({'name': name, 'amount': amount})\n\n"
            "    def calculate_total(self):\n"
            "        total = 0\n"
            "        for expense in self.expenses:\n"
            "            total += expense['amount']\n"
            "        return total\n\n"
            "    def find_highest_expense(self):\n"
            "        if not self.expenses:\n"
            "            return None\n"
            "        highest = self.expenses[0]\n"
            "        for expense in self.expenses:\n"
            "            if expense['amount'] > highest['amount']:\n"
            "                highest = expense\n"
            "        return highest\n\n"
            "    def display_expenses(self):\n"
            "        for expense in self.expenses:\n"
            "            print(f\"{expense['name']}: {expense['amount']}\")\n\n"
            "def main():\n"
            "    tracker = ExpenseTracker()\n"
            "    tracker.add_expense('Rent', 1200)\n"
            "    tracker.add_expense('Groceries', 300)\n"
            "    tracker.add_expense('Electricity', 150)\n"
            "    tracker.display_expenses()\n"
            "    print('Total:', tracker.calculate_total())\n"
            "    print('Highest:', tracker.find_highest_expense())\n\n"
            "if __name__ == '__main__':\n"
            "    main()"
        )
    },
    "Two Sum (JavaScript)": {
        "lang": "JavaScript",
        "aim": "Find indices of two numbers that add up to target.",
        "code": (
            "function twoSum(nums, target) {\n"
            "    const seen = new Map();\n"
            "    for (let i = 0; i < nums.length; i++) {\n"
            "        const complement = target - nums[i];\n"
            "        if (seen.has(complement)) {\n"
            "            return [seen.get(complement), i];\n"
            "        }\n"
            "        seen.set(nums[i], i);\n"
            "    }\n"
            "    return [];\n"
            "}"
        )
    },
    "Binary Search (C++)": {
        "lang": "C++",
        "aim": "Search for a target value in a sorted vector efficiently.",
        "code": (
            "int binarySearch(const std::vector<int>& arr, int target) {\n"
            "    int low = 0, high = arr.size() - 1;\n"
            "    while (low <= high) {\n"
            "        int mid = low + (high - low) / 2;\n"
            "        if (arr[mid] == target) return mid;\n"
            "        else if (arr[mid] < target) low = mid + 1;\n"
            "        else high = mid - 1;\n"
            "    }\n"
            "    return -1;\n"
            "}"
        )
    },
    "Code with Bug / Error (Test Fixer)": {
        "lang": "Python",
        "aim": "Calculate average of a numbers list.",
        "code": (
            "def calculate_average(numbers):\n"
            "    total = 0\n"
            "    for num in numbers\n"
            "        total = total + num\n"
            "    return total / len(numbers)\n\n"
            "print(calculate_average([10, 20, 30]))"
        )
    }
}

def load_template(name):
    t = CODE_TEMPLATES[name]
    st.session_state["language"] = t["lang"]
    st.session_state["goal_input"] = t["aim"]
    st.session_state["code_input"] = t["code"]
    st.session_state["analysis_data"] = None
    st.session_state["improved_data"] = None
    st.session_state["active_inspect_tab"] = None

def clean_fences(text):
    text = text.strip()
    text = re.sub(r"^`{3}[a-zA-Z0-9+_-]*\n?", "", text)
    text = re.sub(r"\n?`{3}$", "", text)
    return text.strip()

# ── LLM: GENERATE TEXT WRAPPER ─────────────────────────────
def generate_llm_response(prompt_text, json_mode=True):
    if USE_NEW_SDK and client:
        cfg = types.GenerateContentConfig(response_mime_type="application/json") if json_mode else None
        res = client.models.generate_content(
            model=selected_model,
            contents=prompt_text,
            config=cfg
        )
        return res.text
    elif legacy_model:
        res = legacy_model.generate_content(prompt_text)
        return res.text
    else:
        raise Exception("No active Gemini API configuration found.")

# ── LLM: ANALYSIS WITH SIMPLE EXPLANATIONS ─────────────────
def analyze_and_segregate(code, language, aim):
    prompt = f"""
You are DECODE — a super-friendly code explainer. Your goal is to explain code so that ANYONE (even complete beginners) can understand it immediately.

USER AIM:
{aim}

USER CODE ({language}):
{code}

CRITICAL RULES:
1. EXPLAIN SIMPLY: Use short sentences (max ~15-18 words), everyday words, and a real-world analogy where it helps. Avoid dense academic or jargon-heavy words entirely. Write like you're explaining to a smart 12-year-old who has never coded before.
2. CHECK FOR ERRORS: If there is a syntax or logical crash, set "has_error": true, describe the error, and provide the working "corrected_code".
3. TIME & SPACE COMPLEXITY WITH PROOF:
   - Provide standard Big-O notation for both time and space.
   - For time_complexity_reasoning and space_complexity_reasoning, write 1-2 simple sentences explaining exactly why that is the case.
   - Additionally provide "time_complexity_steps" and "space_complexity_steps": ordered arrays of short strings walking through the FULL step-by-step derivation (e.g. "Step 1: The outer loop runs N times because it visits every item once.", "Step 2: ...") so a beginner can follow the entire proof from start to finish.
4. CODE SUMMARY (high level, before segments):
   - "what_it_does": 1-3 simple sentences describing the overall goal of the program in plain English, no jargon.
   - "how_it_works": an ordered array of short, simple sentences (like a numbered story) walking through what the program does from start to finish, in the order it happens.
5. KEY FEATURES:
   - "key_features": an array of the most important lines, parameters, or function calls in the code that a beginner should notice (e.g. a timeout parameter, a specific method call, a safety check). For each: "code" is the exact short snippet (like `timeout=5` or `raise_for_status()`), and "description" is one simple sentence on why it matters.
6. CODE SEGREGATION:
   - Divide into natural, contiguous logical segments.
   - "name": Uppercase label format like 'INITIALIZATION — CLASS INITIALIZATION' or 'INPUT — READ USER VALUES' or 'CALCULATION — COMPUTE TOTAL'.
   - "use": Exactly ONE short, super-simple sentence.
   - "purpose": 1-2 short, simple sentences (max ~15 words each) explaining what this part does and why it's needed. Use an everyday comparison if it helps beginners.
   - "logic": 1-2 short, simple sentences explaining the step-by-step thinking in plain English, as if narrating out loud.
   - "line_by_line": Step-by-step breakdown of every line in plain, beginner-friendly English.

Respond ONLY with a VALID JSON object adhering strictly to this schema:
{{
  "has_error": true | false,
  "error_details": {{
    "error_type": "SyntaxError",
    "error_location": "Line 3",
    "error_description": "Missing colon at the end of the loop line",
    "suggested_fix": "Add a colon (:) at the end of the line",
    "corrected_code": "full working corrected code"
  }},
  "aim_verification": {{
    "status": "MATCH" | "PARTIAL" | "MISMATCH",
    "headline": "Short status headline",
    "explanation": "2 simple sentences on whether the code matches the user's aim."
  }},
  "code_summary": {{
    "what_it_does": "1-3 simple sentences on the overall goal of the program.",
    "how_it_works": ["It loads the requests library so Python can talk to websites.", "It defines a function that takes a user id.", "..."]
  }},
  "key_features": [
    {{"code": "timeout=5", "description": "Prevents the script from hanging forever if the server does not respond."}}
  ],
  "overall_analysis": {{
    "time_complexity": "O(N)",
    "time_complexity_reasoning": "We loop through the list once from start to finish, so if there are N items, it takes N steps.",
    "time_complexity_steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
    "space_complexity": "O(1)",
    "space_complexity_reasoning": "We only use a single variable to store the total sum, requiring no extra memory.",
    "space_complexity_steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],
    "functions": [
      {{"name": "function_name", "type": "User-defined" | "Built-in", "use": "Stores a new expense name and amount"}}
    ],
    "variables": [
      {{"name": "variable_name", "datatype": "list / int etc.", "use": "Stores all expense records"}}
    ],
    "keywords": [
      {{"keyword": "keyword_name", "use": "Used to create a new class or function"}}
    ]
  }},
  "segments": [
    {{
      "segment_number": 1,
      "name": "INITIALIZATION — CLASS INITIALIZATION",
      "use": "Creates the expense tracker and sets up an empty list.",
      "purpose": "This sets up the initial storage so the rest of the program can add and read expenses.",
      "logic": "When a new tracker is created, it starts with an empty list ready to store items.",
      "code": "Exact code slice",
      "line_by_line": [
        {{"line": "exact line", "explanation": "Simple explanation in plain English."}}
      ]
    }}
  ]
}}
"""
    try:
        raw_text = generate_llm_response(prompt, json_mode=True)
        return json.loads(clean_fences(raw_text))
    except Exception as e:
        st.error(f"Analysis Generation Error: {e}")
        return {
            "has_error": False,
            "aim_verification": {"status": "PARTIAL", "headline": "Analysis Error", "explanation": str(e)},
            "code_summary": {"what_it_does": "", "how_it_works": []},
            "key_features": [],
            "overall_analysis": {
                "time_complexity": "O(N)", "time_complexity_reasoning": "Runs through the main instructions sequentially.",
                "time_complexity_steps": [],
                "space_complexity": "O(1)", "space_complexity_reasoning": "Uses a fixed amount of memory.",
                "space_complexity_steps": [],
                "functions": [], "variables": [], "keywords": []
            },
            "segments": [{
                "segment_number": 1, "name": "MAIN PROGRAM — CODE EXECUTION",
                "use": "Executes the main instructions of the code.",
                "purpose": "Runs the algorithm to accomplish the goal.",
                "logic": "Executes each statement step-by-step.",
                "code": code,
                "line_by_line": []
            }]
        }

# ── LLM: IMPROVE CODE ──────────────────────────────────────
def generate_improved_code(code, language, aim):
    prompt = f"""
You are DECODE's polyglot performance optimizer. Improve and optimize this {language} code.

USER AIM: {aim}

ORIGINAL CODE:
{code}

Respond ONLY with VALID JSON:
{{
  "improved_title": "Short optimization title",
  "why_better": "Simple explanation in plain English of why this new code is better and faster.",
  "comparison_points": ["Point 1", "Point 2", "Point 3"],
  "user_code_complexity": {{ "time": "O(N^2)", "space": "O(1)" }},
  "improved_code_complexity": {{ "time": "O(N)", "space": "O(N)" }},
  "improved_code": "Complete code without backticks."
}}
"""
    try:
        raw_text = generate_llm_response(prompt, json_mode=True)
        return json.loads(clean_fences(raw_text))
    except Exception as e:
        st.error(f"Improvement Generation Error: {e}")
        return {
            "improved_title": "Optimization Error",
            "why_better": str(e),
            "comparison_points": [],
            "user_code_complexity": {"time": "N/A", "space": "N/A"},
            "improved_code_complexity": {"time": "N/A", "space": "N/A"},
            "improved_code": code
        }

# ── HERO BANNER ────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-left">
        <div class="hero-brand-row">
            <span class="hero-brand-dash"></span>
            <span class="hero-brand">Decode</span>
            <span class="hero-brand-dash"></span>
        </div>
        <div class="hero-tagline">Know what you <span class="tagline-code">CODE</span></div>
    </div>
    <div class="hero-right">
        <span class="hero-badge">✨ Powered by Gemini</span>
        <div class="hero-chip-row">
            <span class="hero-chip">🚨 Bug Fixer</span>
            <span class="hero-chip">📊 Complexity Proofs</span>
            <span class="hero-chip">🧩 Segments</span>
            <span class="hero-chip">⚡ Optimizer</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if not ACTIVE_API_KEY:
    st.warning("Gemini API Key Required — enter in sidebar or set GEMINI_API_KEY in .env")

# ── MAIN 50/50 LAYOUT ──────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

# ──────────────────────────────────────────────────────────
# LEFT COLUMN: INPUT & CONTROLS
# ──────────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="eyebrow">Step 1 · Setup</div><div class="panel-heading">💻 Code Input & Configuration</div>', unsafe_allow_html=True)

    sel = st.selectbox("⚡ Quick Load Sample:", ["-- Select Template (Optional) --"] + list(CODE_TEMPLATES.keys()))
    if sel != "-- Select Template (Optional) --":
        if st.button("📥 Load Template into Editor", use_container_width=True):
            load_template(sel)
            st.rerun()

    lang_list = ["Python", "JavaScript", "TypeScript", "C++", "Java", "C#", "Go", "Rust", "C", "PHP", "Ruby", "Kotlin", "Swift"]
    cur_idx = lang_list.index(st.session_state["language"]) if st.session_state["language"] in lang_list else 0
    st.session_state["language"] = st.selectbox("Programming Language", lang_list, index=cur_idx)

    st.session_state["goal_input"] = st.text_input(
        "🎯 Aim / Expected Behavior of Code:",
        value=st.session_state["goal_input"],
        placeholder="e.g. Track expenses, find highest, compute total..."
    )

    st.session_state["code_input"] = st.text_area(
        f"📝 Paste your {st.session_state['language']} code here:",
        value=st.session_state["code_input"],
        height=300,
        placeholder="// Paste your code here..."
    )

    b1, b2, b3 = st.columns([1.3, 1.3, 1])
    with b1:
        analyze_clicked = st.button("🚀 Decode Code", type="primary", use_container_width=True)
    with b2:
        improve_clicked = st.button("⚡ Improve Code", use_container_width=True)
    with b3:
        if st.button("🧹 Clear", use_container_width=True):
            st.session_state["code_input"] = ""
            st.session_state["goal_input"] = ""
            st.session_state["analysis_data"] = None
            st.session_state["improved_data"] = None
            st.session_state["active_inspect_tab"] = None
            st.rerun()

    if analyze_clicked:
        if not ACTIVE_API_KEY:
            st.error("Please enter a valid Gemini API Key in the sidebar or .env.")
        elif not st.session_state["code_input"].strip():
            st.error("Please paste code before analyzing.")
        else:
            goal = st.session_state["goal_input"].strip() or "General algorithm execution"
            st.session_state["goal_input"] = goal
            with st.spinner("🧠 Decoding code, finding errors & explaining every line..."):
                st.session_state["analysis_data"] = analyze_and_segregate(
                    st.session_state["code_input"], st.session_state["language"], goal
                )
            st.rerun()

    if improve_clicked:
        if not ACTIVE_API_KEY:
            st.error("Please enter a valid Gemini API Key in the sidebar or .env.")
        elif not st.session_state["code_input"].strip():
            st.error("Please paste code before improving.")
        else:
            goal = st.session_state["goal_input"].strip() or "General algorithm execution"
            st.session_state["goal_input"] = goal
            with st.spinner("⚡ Generating optimized code & comparison..."):
                st.session_state["improved_data"] = generate_improved_code(
                    st.session_state["code_input"], st.session_state["language"], goal
                )
            st.rerun()

# ──────────────────────────────────────────────────────────
# RIGHT COLUMN: DECODE RESULTS
# ──────────────────────────────────────────────────────────
with col_right:
    _has_code = bool(st.session_state["code_input"].strip())
    _has_analysis = st.session_state["analysis_data"] is not None
    _has_error_state = _has_analysis and st.session_state["analysis_data"].get("has_error", False)
    _explored = _has_analysis and not _has_error_state

    _s1 = "done" if _has_code else "active"
    _s2 = "done" if _has_analysis else ("active" if _has_code else "")
    _s3 = "done" if _explored else ("active" if _has_analysis else "")
    _l1 = "on" if _has_code else ""
    _l2 = "on" if _has_analysis else ""
    _l3 = "on" if _explored else ""

    st.markdown(f"""
    <div class="stepper">
        <div class="step-item">
            <div class="step-line {'done' if _has_analysis else ''}"></div>
            <div class="step-circle {_s1}">{'✓' if _has_code else '1'}</div>
            <div class="step-label {_l1}">SETUP</div>
        </div>
        <div class="step-item">
            <div class="step-line {'done' if _explored else ''}"></div>
            <div class="step-circle {_s2}">{'✓' if _has_analysis else '2'}</div>
            <div class="step-label {_l2}">ANALYZE</div>
        </div>
        <div class="step-item">
            <div class="step-circle {_s3}">{'✓' if _explored else '3'}</div>
            <div class="step-label {_l3}">EXPLORE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state["analysis_data"] is None and st.session_state["improved_data"] is None:
        st.markdown('<div class="eyebrow">Getting Started</div><div class="panel-heading">✨ Studio Capabilities</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="border-color:rgba(124,58,237,0.35);">
            <h4 style="margin:0 0 8px 0;color:#F8FAFC;font-family:'Space Grotesk',sans-serif;">👋 Welcome to Decode</h4>
            <p style="color:#94A3B8;font-size:13.5px;line-height:1.5;margin:0;">
                Paste code on the left, declare your aim, and click <strong>Decode Code</strong>. Decode automatically detects syntax bugs with solutions, provides interactive Time & Space complexity proofs, and segregates code into colorful meaningful logical segments with simple line-by-line breakdowns.
            </p>
        </div>
        """, unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("""
            <div class="showcase-box">
                <div class="showcase-icon">🚨</div>
                <div class="showcase-title">Bug & Syntax Fixer</div>
                <div class="showcase-desc">Instantly catches code errors and gives exact line numbers, explanations, and corrected code.</div>
            </div>
            <div class="showcase-box">
                <div class="showcase-icon">📊</div>
                <div class="showcase-title">Complexity Proofs</div>
                <div class="showcase-desc">Click Time & Space complexity cards to see the exact step-by-step proof in simple English.</div>
            </div>
            """, unsafe_allow_html=True)
        with r2:
            st.markdown("""
            <div class="showcase-box">
                <div class="showcase-icon">🧩</div>
                <div class="showcase-title">Bold Code Segments</div>
                <div class="showcase-desc">Colorful functional badges with purpose, simple logic, and line-by-line explanations.</div>
            </div>
            <div class="showcase-box">
                <div class="showcase-icon">⚡</div>
                <div class="showcase-title">Code Improver</div>
                <div class="showcase-desc">Side-by-side Big-O comparison and clear rationales on why the improved version is superior.</div>
            </div>
            """, unsafe_allow_html=True)
        st.info("💡 **Quick Start:** Pick any algorithm from the template dropdown on the left to test instantly!")

    else:
        # Aim Verification Status Badge
        if st.session_state["analysis_data"]:
            av = st.session_state["analysis_data"].get("aim_verification", {})
            status = av.get("status", "MATCH").upper()
            icon = "🟢" if status == "MATCH" else ("🟡" if status == "PARTIAL" else "🔴")
            cls = "badge-match" if status == "MATCH" else ("badge-partial" if status == "PARTIAL" else "badge-mismatch")
            st.markdown(f"""
            <div class="{cls}">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span>{icon} <strong>Aim Check:</strong> {av.get('headline','')}</span>
                    <span style="font-size:11.5px;opacity:0.85;text-transform:uppercase;font-family:'Space Grotesk',sans-serif;">{status}</span>
                </div>
                <div style="font-size:13px;font-weight:400;margin-top:6px;color:#E2E8F0;">{av.get('explanation','')}</div>
            </div>
            """, unsafe_allow_html=True)

        tab_analysis, tab_imp, tab_qa = st.tabs(["📊 Code Analysis & Segments", "⚡ Improved Code", "💬 Ask Doubts"])

        # ── TAB 1: OVERALL ANALYSIS & SEGMENTS ──
        with tab_analysis:
            if st.session_state["analysis_data"]:
                data = st.session_state["analysis_data"]
                has_err = data.get("has_error", False)
                err_info = data.get("error_details", {})
                overall = data.get("overall_analysis", {})
                segments = data.get("segments", [])

                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

                # ============================================================
                # ERROR HANDLING / CODE BUG DETECTION POPUP
                # ============================================================
                if has_err and err_info:
                    st.markdown(f"""
                    <div class="error-box">
                        <div class="error-title">🚨 Error Detected: {err_info.get('error_type', 'Code Error')} ({err_info.get('error_location', 'In Code')})</div>
                        <p style="color:#FCA5A5;font-size:13.5px;margin:0 0 10px 0;line-height:1.5;">
                            {err_info.get('error_description', 'A syntax or logical error prevents this code from executing correctly.')}
                        </p>
                        <div style="background:rgba(0,0,0,0.3);padding:10px 14px;border-radius:10px;border-left:3px solid #F87171;">
                            <strong style="color:#FEF08A;font-size:13px;">💡 Suggested Fix:</strong>
                            <span style="color:#F3F4F6;font-size:13px;"> {err_info.get('suggested_fix', '')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if err_info.get("corrected_code"):
                        st.markdown(
                            f'<div class="code-header"><span class="code-dot" style="background:#10B981;"></span>Fixed · {st.session_state["language"]}</div>',
                            unsafe_allow_html=True
                        )
                        st.code(err_info.get("corrected_code"), language=st.session_state["language"].lower())
                        if st.button("🛠️ Apply Corrected Code", key="apply_fix_btn", type="primary", use_container_width=True):
                            st.session_state["code_input"] = err_info.get("corrected_code")
                            st.session_state["analysis_data"] = None
                            st.session_state["improved_data"] = None
                            st.session_state["active_inspect_tab"] = None
                            st.session_state["show_time_steps"] = False
                            st.session_state["show_space_steps"] = False
                            st.success("Corrected code applied to the editor. Click Decode Code again to re-analyze.")
                            st.rerun()

                    st.markdown("---")

                # ============================================================
                # SECTION 1 — OVERALL CODE ANALYSIS & COMPLEXITY PROOFS
                # ============================================================
                st.markdown('<div class="eyebrow">Step 2 · Insights</div><div class="panel-heading">📊 Overall Code Analysis</div>', unsafe_allow_html=True)
                
                t_val = overall.get("time_complexity") or "O(N)"
                t_proof = overall.get("time_complexity_reasoning") or "Derived by analyzing loop iterations and recursive paths relative to input size N."
                t_steps = overall.get("time_complexity_steps") or []

                s_val = overall.get("space_complexity") or "O(1)"
                s_proof = overall.get("space_complexity_reasoning") or "Derived by tracking additional memory structures, arrays, and variables relative to input size N."
                s_steps = overall.get("space_complexity_steps") or []

                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-half">
                        <div class="stat-value" style="color:#60A5FA;">{t_val}</div>
                        <div class="stat-label">Time Complexity</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat-half">
                        <div class="stat-value" style="color:#C084FC;">{s_val}</div>
                        <div class="stat-label">Space Complexity</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_t, col_s = st.columns(2)
                with col_t:
                    with st.expander("🔍 How Time Complexity was calculated", expanded=False):
                        st.markdown(f"""
                        <div style="background:rgba(15,13,17,0.7);padding:12px 14px;border-radius:10px;border-left:3px solid #60A5FA;font-size:13px;color:#E2E8F0;line-height:1.6;">
                            <strong>Explanation:</strong><br>{t_proof}
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("📐 Step-by-Step Solution", key="btn_time_steps", use_container_width=True):
                            st.session_state["show_time_steps"] = not st.session_state["show_time_steps"]
                        if st.session_state["show_time_steps"]:
                            if t_steps:
                                rows = "".join(
                                    f'<div class="step-row"><span class="step-num">{i}</span><span>{step}</span></div>'
                                    for i, step in enumerate(t_steps, 1)
                                )
                                st.markdown(f'<div class="step-scroll-box">{rows}</div>', unsafe_allow_html=True)
                            else:
                                st.caption("No detailed step-by-step breakdown available.")

                with col_s:
                    with st.expander("🔍 How Space Complexity was calculated", expanded=False):
                        st.markdown(f"""
                        <div style="background:rgba(15,13,17,0.7);padding:12px 14px;border-radius:10px;border-left:3px solid #C084FC;font-size:13px;color:#E2E8F0;line-height:1.6;">
                            <strong>Explanation:</strong><br>{s_proof}
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("📐 Step-by-Step Solution", key="btn_space_steps", use_container_width=True):
                            st.session_state["show_space_steps"] = not st.session_state["show_space_steps"]
                        if st.session_state["show_space_steps"]:
                            if s_steps:
                                rows = "".join(
                                    f'<div class="step-row"><span class="step-num">{i}</span><span>{step}</span></div>'
                                    for i, step in enumerate(s_steps, 1)
                                )
                                st.markdown(f'<div class="step-scroll-box">{rows}</div>', unsafe_allow_html=True)
                            else:
                                st.caption("No detailed step-by-step breakdown available.")

                # ============================================================
                # ON-DEMAND TOGGLE: FUNCTIONS, VARIABLES, KEYWORDS
                # (Collapsed by default, opens only when user clicks)
                # ============================================================
                funcs = overall.get("functions", [])
                vars_list = overall.get("variables", [])
                kws = overall.get("keywords", [])

                col_btn_f, col_btn_v, col_btn_k = st.columns(3)
                
                with col_btn_f:
                    f_btn_type = "primary" if st.session_state["active_inspect_tab"] == "funcs" else "secondary"
                    if st.button(f"⚙️ Functions ({len(funcs)})", key="btn_f", type=f_btn_type, use_container_width=True):
                        st.session_state["active_inspect_tab"] = None if st.session_state["active_inspect_tab"] == "funcs" else "funcs"
                        st.rerun()

                with col_btn_v:
                    v_btn_type = "primary" if st.session_state["active_inspect_tab"] == "vars" else "secondary"
                    if st.button(f"📦 Variables ({len(vars_list)})", key="btn_v", type=v_btn_type, use_container_width=True):
                        st.session_state["active_inspect_tab"] = None if st.session_state["active_inspect_tab"] == "vars" else "vars"
                        st.rerun()

                with col_btn_k:
                    k_btn_type = "primary" if st.session_state["active_inspect_tab"] == "kws" else "secondary"
                    if st.button(f"🔑 Keywords ({len(kws)})", key="btn_k", type=k_btn_type, use_container_width=True):
                        st.session_state["active_inspect_tab"] = None if st.session_state["active_inspect_tab"] == "kws" else "kws"
                        st.rerun()

                # Render content ONLY if a button is currently active
                if st.session_state["active_inspect_tab"] == "funcs":
                    st.markdown('<div class="inspect-box"><div class="inspect-scroll">', unsafe_allow_html=True)
                    if funcs:
                        for f in funcs:
                            ftype = f.get("type", "Function")
                            fcolor = "#34D399" if "user" in ftype.lower() else "#60A5FA"
                            st.markdown(f"""
                            <div style="background:rgba(16,15,19,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;margin-bottom:8px;">
                                <span style="font-family:JetBrains Mono,monospace;color:#FCD34D;font-weight:700;font-size:13.5px;">{f.get('name', '')}</span><br>
                                <span style="background:{fcolor}22;color:{fcolor};font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">{ftype}</span><br>
                                <span style="color:#CBD5E1;font-size:12.5px;margin-top:4px;display:block;">{f.get('use', '')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("No functions detected in this code.")
                    st.markdown('</div></div>', unsafe_allow_html=True)

                elif st.session_state["active_inspect_tab"] == "vars":
                    st.markdown('<div class="inspect-box"><div class="inspect-scroll">', unsafe_allow_html=True)
                    if vars_list:
                        for v in vars_list:
                            st.markdown(f"""
                            <div style="background:rgba(16,15,19,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;margin-bottom:8px;">
                                <span style="font-family:JetBrains Mono,monospace;color:#C084FC;font-weight:700;font-size:13.5px;">{v.get('name', '')}</span><br>
                                <span style="background:rgba(192,132,252,0.15);color:#C084FC;font-size:10.5px;font-weight:800;padding:2px 6px;border-radius:4px;">{v.get('datatype', 'variable')}</span><br>
                                <span style="color:#CBD5E1;font-size:12.5px;margin-top:4px;display:block;">{v.get('use', '')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("No variables detected in this code.")
                    st.markdown('</div></div>', unsafe_allow_html=True)

                elif st.session_state["active_inspect_tab"] == "kws":
                    st.markdown('<div class="inspect-box"><div class="inspect-scroll">', unsafe_allow_html=True)
                    if kws:
                        for kw in kws:
                            st.markdown(f"""
                            <div style="background:rgba(16,15,19,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;margin-bottom:8px;">
                                <span style="font-family:JetBrains Mono,monospace;color:#FCD34D;font-weight:700;font-size:13.5px;">{kw.get('keyword', '')}</span><br>
                                <span style="color:#CBD5E1;font-size:12.5px;margin-top:4px;display:block;">{kw.get('use', '')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("No keywords detected in this code.")
                    st.markdown('</div></div>', unsafe_allow_html=True)

                st.markdown("---")

                # ============================================================
                # SECTION 1.5 — CODE SUMMARY & KEY FEATURES (above segments)
                # ============================================================
                if not has_err:
                    code_summary = data.get("code_summary", {}) or {}
                    key_features = data.get("key_features", []) or []
                    what_it_does = code_summary.get("what_it_does", "")
                    how_it_works = code_summary.get("how_it_works", []) or []

                    col_sum, col_feat = st.columns(2)
                    with col_sum:
                        sum_btn_type = "primary" if st.session_state["active_inspect_tab"] == "summary" else "secondary"
                        if st.button("Code Summary", key="btn_summary", type=sum_btn_type, use_container_width=True):
                            st.session_state["active_inspect_tab"] = None if st.session_state["active_inspect_tab"] == "summary" else "summary"
                            st.rerun()
                    with col_feat:
                        feat_btn_type = "primary" if st.session_state["active_inspect_tab"] == "keyfeatures" else "secondary"
                        if st.button(f"Key Features ({len(key_features)})", key="btn_keyfeatures", type=feat_btn_type, use_container_width=True):
                            st.session_state["active_inspect_tab"] = None if st.session_state["active_inspect_tab"] == "keyfeatures" else "keyfeatures"
                            st.rerun()

                    if st.session_state["active_inspect_tab"] == "summary":
                        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
                        st.markdown('<div class="summary-heading">What It Does</div>', unsafe_allow_html=True)
                        st.markdown(f'<p class="summary-text">{what_it_does or "No summary available."}</p>', unsafe_allow_html=True)
                        st.markdown('<div class="summary-heading alt">How It Works</div>', unsafe_allow_html=True)
                        if how_it_works:
                            rows = "".join(
                                f'<div class="how-it-works-row"><span class="how-it-works-num">{i}</span><span>{step}</span></div>'
                                for i, step in enumerate(how_it_works, 1)
                            )
                            st.markdown(f'<div class="step-scroll-box">{rows}</div>', unsafe_allow_html=True)
                        else:
                            st.caption("No step-by-step walkthrough available.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    elif st.session_state["active_inspect_tab"] == "keyfeatures":
                        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
                        st.markdown('<div class="summary-heading">Key Features</div>', unsafe_allow_html=True)
                        if key_features:
                            rows = "".join(
                                f'<div class="key-feature-row"><span class="key-feature-code">{kf.get("code","")}</span>{kf.get("description","")}</div>'
                                for kf in key_features
                            )
                            st.markdown(f'<div class="step-scroll-box">{rows}</div>', unsafe_allow_html=True)
                        else:
                            st.caption("No key features detected for this code.")
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown("---")

                # ============================================================
                # SECTION 2 — EXACT ATTACHED IMAGE SEGMENT PILLS
                # ============================================================
                st.markdown('<div class="eyebrow">Step 3 · Walkthrough</div><div class="panel-heading">Segments — Click to Explore</div>', unsafe_allow_html=True)

                if not has_err:
                    for idx, seg in enumerate(segments, 1):
                        seg_name = seg.get("name", f"SEGMENT {idx}").upper()
                        seg_use = seg.get("use", "")
                        seg_purpose = seg.get("purpose", "")
                        seg_logic = seg.get("logic", "")
                        seg_code = seg.get("code", "")
                        line_explanations = seg.get("line_by_line", [])

                        theme = get_segment_theme(idx, seg_name)

                        # No emojis in the segments section — colorful, bold heading text
                        expander_label = f"**:{theme['st_color']}[{seg_name}]**  —  {seg_use}"

                        with st.expander(expander_label, expanded=False):
                            # CLEAN, VIVID SEGMENT PILL — no emojis
                            st.markdown(f"""
                            <div class="segment-pill" style="border-left-color:{theme['color']};">
                                <span class="segment-pill-title" style="color:{theme['color']};">{seg_name}</span>
                                <span class="segment-pill-badge">Segment #{idx}</span>
                            </div>
                            """, unsafe_allow_html=True)

                            if seg_purpose:
                                st.markdown(f"""
                                <div class="detail-banner" style="background:linear-gradient(90deg, {theme['color']}1F, transparent); border-left-color:{theme['color']};">
                                    <span class="detail-label" style="color:{theme['color']};">Purpose</span>{seg_purpose}
                                </div>
                                """, unsafe_allow_html=True)

                            if seg_logic:
                                st.markdown(f"""
                                <div class="detail-banner" style="background:linear-gradient(90deg, rgba(148,163,184,0.12), transparent); border-left-color:#94A3B8;">
                                    <span class="detail-label" style="color:#CBD5E1;">Logic &amp; Thinking</span>{seg_logic}
                                </div>
                                """, unsafe_allow_html=True)

                            # Exact Code Slice
                            st.markdown(
                                f'<div class="code-header"><span class="code-dot" style="background:#71717A;"></span>Snippet · {st.session_state["language"]}</div>',
                                unsafe_allow_html=True
                            )
                            st.code(seg_code, language=st.session_state["language"].lower())

                            # Line-by-Line Breakdown
                            with st.expander("View Line-by-Line Explanation", expanded=False):
                                if line_explanations:
                                    for l_item in line_explanations:
                                        st.markdown(f"""
                                        <div class="line-card">
                                            <span class="line-code">{l_item.get('line', '').strip()}</span>
                                            <p style="color:#CBD5E1;font-size:12.5px;margin:4px 0 0 4px;line-height:1.4;">{l_item.get('explanation', '')}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.caption("No line-by-line breakdown available for this segment.")
                else:
                    st.info("💡 Segments are hidden because errors were detected above. Fix the errors to view full segmentation.")

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Click **🚀 Decode Code** on the left to view the analysis.")

        # ── TAB 2: IMPROVED CODE ──
        with tab_imp:
            if st.session_state["improved_data"]:
                imp = st.session_state["improved_data"]
                st.markdown('<div class="eyebrow">Optimizer</div>', unsafe_allow_html=True)
                st.markdown(f"### 💡 {imp.get('improved_title', 'Improved Code')}")
                st.markdown(f"""
                <div class="glass-card" style="border-left:4px solid #10B981;margin-bottom:14px;">
                    <h5 style="margin:0 0 6px 0;color:#34D399;font-family:'Space Grotesk',sans-serif;">🌟 Why this is better:</h5>
                    <p style="color:#E2E8F0;font-size:13px;margin:0;line-height:1.5;">{imp.get('why_better','')}</p>
                </div>
                """, unsafe_allow_html=True)

                uc = imp.get("user_code_complexity", {"time": "O(N)", "space": "O(1)"})
                ic = imp.get("improved_code_complexity", {"time": "O(N)", "space": "O(1)"})
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown(f"""
                    <div class="glass-card" style="padding:12px;text-align:center;">
                        <span style="color:#94A3B8;font-size:12px;">Your Code Complexity</span>
                        <div style="margin-top:6px;">
                            <span class="complexity-pill">⏳ {uc.get('time','N/A')}</span>
                            <span class="complexity-pill">💾 {uc.get('space','N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cc2:
                    st.markdown(f"""
                    <div class="glass-card" style="padding:12px;text-align:center;border-color:rgba(52,211,153,0.3);">
                        <span style="color:#34D399;font-size:12px;font-weight:600;">Improved Complexity</span>
                        <div style="margin-top:6px;">
                            <span class="complexity-pill" style="color:#34D399;">⏳ {ic.get('time','N/A')}</span>
                            <span class="complexity-pill" style="color:#34D399;">💾 {ic.get('space','N/A')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                pts = imp.get("comparison_points", [])
                if pts:
                    st.markdown("#### 📊 Key Comparison Points:")
                    for pt in pts:
                        st.markdown(f"- ✅ {pt}")
                st.markdown("#### ⚡ Improved Code:")
                st.markdown(
                    f'<div class="code-header"><span class="code-dot" style="background:#3B82F6;"></span>Optimized · {st.session_state["language"]}</div>',
                    unsafe_allow_html=True
                )
                st.code(imp.get("improved_code",""), language=st.session_state["language"].lower())
            else:
                st.info("Click **⚡ Improve Code** on the left to generate an optimized version.")

        # ── TAB 3: Q&A ──
        with tab_qa:
            st.markdown('<div class="eyebrow">Tutor</div>', unsafe_allow_html=True)
            st.markdown("### 💬 Ask Doubts About Your Code")
            st.caption("Code-specific questions only. Off-topic questions will be politely refused.")

            if not st.session_state["chat_history"].get("general"):
                st.markdown("""
                <div class="glass-card" style="border-color:rgba(59,130,246,0.3);">
                    <p style="color:#94A3B8;font-size:13px;margin:0;line-height:1.5;">
                        No questions yet — try asking something like <em>"why is this loop condition used?"</em> or <em>"what happens if the list is empty?"</em>
                    </p>
                </div>
                """, unsafe_allow_html=True)

            for msg in st.session_state["chat_history"].get("general", []):
                st.chat_message(msg["role"]).write(msg["content"])

            user_q = st.text_input("Your question:", placeholder="e.g. Why is this loop condition used?")
            if st.button("Ask Tutor 🚀"):
                if user_q.strip():
                    if "general" not in st.session_state["chat_history"]:
                        st.session_state["chat_history"]["general"] = []
                    st.session_state["chat_history"]["general"].append({"role": "user", "content": user_q})
                    guard = f"""
You are DECODE's AI Code Tutor. Answer ONLY questions about this {st.session_state.get('language','')} code.
Aim: {st.session_state.get('goal_input','')}
Language: {st.session_state.get('language','')}
Code:
{st.session_state.get('code_input','')}

User Question: "{user_q}"

RULES:
1. Explain in super simple, beginner-friendly English with everyday examples.
2. If IRRELEVANT, respond: "⚠️ I am designed specifically to clarify doubts about your code. Please ask a question related to this code or algorithm."
"""
                    with st.spinner("Answering..."):
                        try:
                            ans = generate_llm_response(guard, json_mode=False)
                        except Exception as e:
                            ans = f"Could not answer: {str(e)}"
                    st.session_state["chat_history"]["general"].append({"role": "assistant", "content": ans})
                    st.rerun()

# ── FOOTER ────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#475569;font-size:12px;margin-top:35px;padding-top:15px;border-top:1px solid rgba(255,255,255,0.06);font-family:'Space Grotesk',sans-serif;">
    ⚡ DECODE — "Know What You Code." • Powered by Streamlit & Gemini
</div>
""", unsafe_allow_html=True)