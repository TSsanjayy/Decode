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
    page_title="Decode — EVERY LINE makes sense.",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── API SETUP ──────────────────────────────────────────────
env_api_key = os.getenv("GEMINI_API_KEY", "")

with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    user_api_key = st.text_input("Gemini API Key", value=env_api_key, type="password")
    selected_model = st.selectbox(
        "Model Version",
        ["gemini-3.6-flash", "gemini-3.7-flash", "gemini-3.5-flash"],
        index=0
    )
    st.markdown("---")
    st.markdown("""
    **Decode Features:**
    - 🚨 Instant Bug / Error Detection & Fix
    - 📊 Deep Time & Space Complexity Breakdown
    - 🧩 Smart Functional Segments
    - 🧠 Simple Purpose & Logic Explanations
    - 📖 Line-by-Line Logic Breakdown
    - ⚡ Code Optimizer & Comparison
    - 💬 Contextual Code Tutor
    """)

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
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700;800;900&display=swap');

html, body, [class*="css"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
}
code, pre { 
    font-family: 'JetBrains Mono', monospace !important; 
}

.stApp {
    background:
        radial-gradient(circle at 10% 15%, rgba(124,58,237,0.22), transparent 40%),
        radial-gradient(circle at 90% 15%, rgba(6,182,212,0.18), transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(236,72,153,0.12), transparent 45%),
        #060913;
    color: #F1F5F9;
}
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 100%; }

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
    scrollbar-color: rgba(139,92,246,0.5) rgba(15,23,42,0.6);
}
.scroll-container::-webkit-scrollbar { width: 6px; }
.scroll-container::-webkit-scrollbar-track { background: rgba(15,23,42,0.6); border-radius: 10px; }
.scroll-container::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #A855F7, #38BDF8); border-radius: 10px; }

.inspect-box {
    background: rgba(12,18,35,0.85);
    border: 1px solid rgba(139,92,246,0.35);
    border-radius: 14px;
    padding: 14px;
    margin-top: 10px;
    margin-bottom: 14px;
}
.inspect-scroll {
    max-height: 240px;
    overflow-y: auto;
    padding-right: 6px;
    scrollbar-width: thin;
    scrollbar-color: rgba(139,92,246,0.5) rgba(15,23,42,0.6);
}
.inspect-scroll::-webkit-scrollbar { width: 5px; }
.inspect-scroll::-webkit-scrollbar-track { background: rgba(15,23,42,0.6); border-radius: 8px; }
.inspect-scroll::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #A855F7, #38BDF8); border-radius: 8px; }

/* ── HERO BANNER ── */
.hero-header {
    padding: 24px 32px;
    border-radius: 22px;
    background: linear-gradient(135deg, rgba(26,16,65,0.95), rgba(9,14,32,0.98));
    border: 1px solid rgba(139,92,246,0.4);
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 14px 40px rgba(0,0,0,0.6);
}
.hero-brand {
    font-size: 42px;
    font-weight: 900;
    margin: 0;
    line-height: 1.1;
    letter-spacing: -1px;
    font-family: 'Space Grotesk', sans-serif;
    background: linear-gradient(90deg, #C084FC 0%, #38BDF8 50%, #F472B6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 10px rgba(192,132,252,0.3));
}
.hero-tagline {
    color: #38BDF8;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-top: 5px;
    font-family: 'Space Grotesk', sans-serif;
    text-shadow: 0 0 12px rgba(56,189,248,0.4);
}

.glass-card {
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 14px;
    backdrop-filter: blur(10px);
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
.complexity-box {
    background: rgba(15,23,42,0.88);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.complexity-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 800;
    margin: 4px 0;
}

/* ── STEP-BY-STEP SCROLLABLE PROOF ── */
.step-scroll-box {
    max-height: 260px;
    overflow-y: auto;
    padding: 4px 10px 4px 2px;
    margin-top: 8px;
    scrollbar-width: thin;
    scrollbar-color: rgba(139,92,246,0.5) rgba(15,23,42,0.6);
}
.step-scroll-box::-webkit-scrollbar { width: 5px; }
.step-scroll-box::-webkit-scrollbar-track { background: rgba(15,23,42,0.6); border-radius: 8px; }
.step-scroll-box::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #A855F7, #38BDF8); border-radius: 8px; }
.step-row {
    display: flex;
    gap: 10px;
    background: rgba(12,18,35,0.75);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 9px 12px;
    margin-bottom: 7px;
    font-size: 12.5px;
    color: #E2E8F0;
    line-height: 1.5;
}
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
    border-left-width: 5px;
    border-left-style: solid;
    background: rgba(15,23,42,0.9);
    box-shadow: 0 4px 16px rgba(0,0,0,0.3);
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

/* ── APPLY FIX BUTTON HIGHLIGHT ── */
.stButton button[kind="primary"] {
    box-shadow: 0 4px 14px rgba(139,92,246,0.35);
}

.use-banner {
    background: linear-gradient(90deg, rgba(56,189,248,0.12), rgba(124,58,237,0.08));
    border-left: 4px solid #38BDF8;
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
    border-radius: 12px;
    background: rgba(16,185,129,0.14);
    border: 1px solid rgba(16,185,129,0.4);
    color: #6EE7B7;
    font-weight: 600;
    font-size: 13.5px;
    margin-bottom: 12px;
}
.badge-partial {
    padding: 12px 16px;
    border-radius: 12px;
    background: rgba(245,158,11,0.14);
    border: 1px solid rgba(245,158,11,0.4);
    color: #FCD34D;
    font-weight: 600;
    font-size: 13.5px;
    margin-bottom: 12px;
}
.badge-mismatch {
    padding: 12px 16px;
    border-radius: 12px;
    background: rgba(239,68,68,0.14);
    border: 1px solid rgba(239,68,68,0.4);
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
    background: rgba(30,41,59,0.85);
    border: 1px solid rgba(255,255,255,0.12);
    color: #38BDF8;
    margin-right: 6px;
}

.line-card {
    background: rgba(15,23,42,0.75);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
}
.line-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #7DD3FC;
    background: rgba(12,18,35,0.7);
    padding: 5px 8px;
    border-radius: 6px;
    margin-bottom: 6px;
    display: block;
    word-break: break-all;
}

.showcase-box {
    background: rgba(17,24,39,0.7);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}
.showcase-icon { font-size: 22px; margin-bottom: 6px; }
.showcase-title { font-size: 14.5px; font-weight: 700; color: #F1F5F9; font-family: 'Space Grotesk', sans-serif; }
.showcase-desc { font-size: 12.5px; color: #94A3B8; margin-top: 4px; line-height: 1.4; }

.stTextArea textarea {
    background-color: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #F8FAFC !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13.5px !important;
}
.stTextInput input {
    background-color: rgba(15,23,42,0.9) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #F8FAFC !important;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px 10px 0 0;
    padding: 8px 16px;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
}
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
        "icon": "✨", "color": "#C084FC",
        "bg": "linear-gradient(90deg, rgba(88,28,135,0.45) 0%, rgba(30,15,60,0.7) 100%)",
        "border": "1px solid rgba(192,132,252,0.65)"
    },
    {
        "icon": "📥", "color": "#38BDF8",
        "bg": "linear-gradient(90deg, rgba(3,105,161,0.45) 0%, rgba(12,25,55,0.7) 100%)",
        "border": "1px solid rgba(56,189,248,0.65)"
    },
    {
        "icon": "⚙️", "color": "#FB923C",
        "bg": "linear-gradient(90deg, rgba(194,65,12,0.45) 0%, rgba(45,20,15,0.7) 100%)",
        "border": "1px solid rgba(251,146,60,0.65)"
    },
    {
        "icon": "🧮", "color": "#34D399",
        "bg": "linear-gradient(90deg, rgba(4,120,87,0.45) 0%, rgba(10,35,25,0.7) 100%)",
        "border": "1px solid rgba(52,211,153,0.65)"
    },
    {
        "icon": "🔀", "color": "#F472B6",
        "bg": "linear-gradient(90deg, rgba(190,24,93,0.45) 0%, rgba(40,15,30,0.7) 100%)",
        "border": "1px solid rgba(244,114,182,0.65)"
    },
    {
        "icon": "🔄", "color": "#FBBF24",
        "bg": "linear-gradient(90deg, rgba(180,83,9,0.45) 0%, rgba(40,25,10,0.7) 100%)",
        "border": "1px solid rgba(251,191,36,0.65)"
    },
    {
        "icon": "📤", "color": "#2DD4BF",
        "bg": "linear-gradient(90deg, rgba(15,118,110,0.45) 0%, rgba(10,30,30,0.7) 100%)",
        "border": "1px solid rgba(45,212,191,0.65)"
    },
    {
        "icon": "🚀", "color": "#818CF8",
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
1. EXPLAIN SIMPLY: Use clear, everyday English. Avoid dense academic words.
2. CHECK FOR ERRORS: If there is a syntax or logical crash, set "has_error": true, describe the error, and provide the working "corrected_code".
3. TIME & SPACE COMPLEXITY WITH PROOF:
   - Provide standard Big-O notation for both time and space.
   - For time_complexity_reasoning and space_complexity_reasoning, write 1-2 simple sentences explaining exactly why that is the case.
   - Additionally provide "time_complexity_steps" and "space_complexity_steps": ordered arrays of short strings that walk through the FULL step-by-step derivation from start to finish (e.g. "The outer loop runs N times because it visits every item once.", "Inside it we do constant-time work, so total work is N x 1."), so a beginner can follow the complete proof one step at a time.
   - Additionally provide "time_complexity_steps" and "space_complexity_steps": ordered arrays of short strings walking through the FULL step-by-step derivation (e.g. "Step 1: The outer loop runs N times because it visits every item once.", "Step 2: ...") so a beginner can follow the entire proof from start to finish.
4. CODE SEGREGATION:
   - Divide into natural, contiguous logical segments.
   - "name": Uppercase label format like 'INITIALIZATION — CLASS INITIALIZATION' or 'INPUT — READ USER VALUES' or 'CALCULATION — COMPUTE TOTAL'.
   - "use": Exactly ONE short, super-simple sentence.
   - "purpose": 1-2 simple sentences explaining what this part does and why we need it.
   - "logic": 1-2 simple sentences explaining the algorithm / step-by-step thinking in plain English.
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
    <div>
        <div class="hero-brand">Decode</div>
        <div class="hero-tagline">"EVERY LINE makes sense."</div>
    </div>
    <span style="background:rgba(124,58,237,0.25);border:1px solid rgba(124,58,237,0.5);padding:8px 16px;border-radius:12px;font-size:13px;font-weight:700;color:#C084FC;font-family:'Space Grotesk',sans-serif;">
        ✨ Powered by Gemini
    </span>
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
    st.markdown('<div class="panel-heading">💻 Code Input & Configuration</div>', unsafe_allow_html=True)

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
    if st.session_state["analysis_data"] is None and st.session_state["improved_data"] is None:
        st.markdown('<div class="panel-heading">✨ Studio Capabilities</div>', unsafe_allow_html=True)
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
                        st.markdown("**✅ Corrected Working Code:**")
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
                st.markdown('<div class="panel-heading">📊 Overall Code Analysis</div>', unsafe_allow_html=True)
                
                t_val = overall.get("time_complexity") or "O(N)"
                t_proof = overall.get("time_complexity_reasoning") or "Derived by analyzing loop iterations and recursive paths relative to input size N."
                t_steps = overall.get("time_complexity_steps") or []

                s_val = overall.get("space_complexity") or "O(1)"
                s_proof = overall.get("space_complexity_reasoning") or "Derived by tracking additional memory structures, arrays, and variables relative to input size N."
                s_steps = overall.get("space_complexity_steps") or []

                col_t, col_s = st.columns(2)
                with col_t:
                    st.markdown(f"""
                    <div class="complexity-box" style="border-color:rgba(56,189,248,0.35);">
                        <span style="color:#94A3B8;font-size:12px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;">⏳ Time Complexity</span>
                        <div class="complexity-value" style="color:#38BDF8;">{t_val}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("🔍 How Time Complexity was calculated", expanded=False):
                        st.markdown(f"""
                        <div style="background:rgba(12,18,35,0.7);padding:12px 14px;border-radius:10px;border-left:3px solid #38BDF8;font-size:13px;color:#E2E8F0;line-height:1.6;">
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
                    st.markdown(f"""
                    <div class="complexity-box" style="border-color:rgba(192,132,252,0.35);">
                        <span style="color:#94A3B8;font-size:12px;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;">💾 Space Complexity</span>
                        <div class="complexity-value" style="color:#C084FC;">{s_val}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("🔍 How Space Complexity was calculated", expanded=False):
                        st.markdown(f"""
                        <div style="background:rgba(12,18,35,0.7);padding:12px 14px;border-radius:10px;border-left:3px solid #C084FC;font-size:13px;color:#E2E8F0;line-height:1.6;">
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
                            fcolor = "#34D399" if "user" in ftype.lower() else "#38BDF8"
                            st.markdown(f"""
                            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;margin-bottom:8px;">
                                <span style="font-family:JetBrains Mono,monospace;color:#7DD3FC;font-weight:700;font-size:13.5px;">{f.get('name', '')}</span><br>
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
                            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;margin-bottom:8px;">
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
                            <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px;margin-bottom:8px;">
                                <span style="font-family:JetBrains Mono,monospace;color:#FCD34D;font-weight:700;font-size:13.5px;">{kw.get('keyword', '')}</span><br>
                                <span style="color:#CBD5E1;font-size:12.5px;margin-top:4px;display:block;">{kw.get('use', '')}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("No keywords detected in this code.")
                    st.markdown('</div></div>', unsafe_allow_html=True)

                st.markdown("---")

                # ============================================================
                # SECTION 2 — EXACT ATTACHED IMAGE SEGMENT PILLS
                # ============================================================
                st.markdown('<div class="panel-heading">Segments — Click to Explore</div>', unsafe_allow_html=True)

                if not has_err:
                    for idx, seg in enumerate(segments, 1):
                        seg_name = seg.get("name", f"SEGMENT {idx}").upper()
                        seg_use = seg.get("use", "")
                        seg_purpose = seg.get("purpose", "")
                        seg_logic = seg.get("logic", "")
                        seg_code = seg.get("code", "")
                        line_explanations = seg.get("line_by_line", [])

                        theme = get_segment_theme(idx, seg_name)

                        # No emojis in the segments section — clean, vivid text only
                        expander_label = f"{seg_name}  —  {seg_use}"

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
                st.code(imp.get("improved_code",""), language=st.session_state["language"].lower())
            else:
                st.info("Click **⚡ Improve Code** on the left to generate an optimized version.")

        # ── TAB 3: Q&A ──
        with tab_qa:
            st.markdown("### 💬 Ask Doubts About Your Code")
            st.caption("Code-specific questions only. Off-topic questions will be politely refused.")
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
    ⚡ DECODE — "EVERY LINE makes sense." • Powered by Streamlit & Gemini
</div>
""", unsafe_allow_html=True)