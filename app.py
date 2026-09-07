import os
import re
import json
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}

# Page configuration
st.set_page_config(
    page_title="AI Text Summarizer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sample texts for instant 1-click loading
SAMPLE_TEXTS = {
    "ai_research": (
        "Recent advances in generative artificial intelligence and large language models have fundamentally altered computational linguistic research. "
        "Modern transformer architectures employ self-attention mechanisms to effectively model long-range context dependencies across multi-billion parameter spaces. "
        "In domain-specific applications such as biomedical research, automated clinical note synthesis has demonstrated a 40% reduction in documentation overhead for healthcare practitioners. "
        "Similarly, automated code generation models are accelerating developer workflows by generating boilerplate logic and identifying security vulnerabilities. "
        "However, critical challenges persist regarding factual hallucinations, alignment drift, and high computational energy footprints. "
        "Future research paradigms emphasize retrieval-augmented generation (RAG), parameter-efficient fine-tuning (PEFT), and robust uncertainty calibration to ensure verifiable and trustworthy outputs."
    ),
    "financial_report": (
        "Global Enterprise Solutions (GES) reported solid financial performance for the third quarter, driven by accelerated cloud infrastructure adoption and expanded recurring enterprise subscriptions. "
        "Total revenue reached $4.8 billion, representing a 14% year-over-year increase, while net profit margins expanded by 220 basis points to 28.5%. "
        "The company's digital automation division outperformed internal projections, contributing $1.6 billion in net new contracts across North American and European markets. "
        "Operating expenses grew moderately by 6%, primarily reflecting targeted capital investments in high-density data centers and specialized engineering talent. "
        "For the upcoming fiscal quarter, management has raised full-year guidance, anticipating full-year revenue growth between 12% and 15%, bolstered by a record $11.2 billion contract backlog."
    ),
    "climate_energy": (
        "The global transition toward renewable energy reached historic milestones over the past decade, with solar photovoltaic and wind capacity accounting for over 80% of all newly installed electricity generation. "
        "Steep declines in manufacturing costs, coupled with national policy incentives, have made utility-scale solar the most cost-effective source of new electricity in most major regions. "
        "Despite this progress, grid integration presents substantial operational hurdles due to the intermittent nature of wind and solar resources. "
        "Addressing these intermittency constraints requires massive investment in next-generation grid storage, including lithium-iron-phosphate batteries, pumped hydro, and long-duration flow batteries. "
        "Furthermore, modernizing transmission corridors and adopting dynamic load balancing are crucial steps to decarbonize heavy industry and global supply chains by mid-century."
    )
}

# Session State Initialization
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
if "main_text_input" not in st.session_state:
    st.session_state.main_text_input = ""
if "summary_output" not in st.session_state:
    st.session_state.summary_output = ""
if "summary_history" not in st.session_state:
    st.session_state.summary_history = []
if "keywords" not in st.session_state:
    st.session_state.keywords = []
if "stats" not in st.session_state:
    st.session_state.stats = None

# Callbacks for button interactions (Guarantees immediate update of widget state in Streamlit)
def load_sample(key):
    st.session_state.main_text_input = SAMPLE_TEXTS[key]
    st.session_state.summary_output = ""
    st.session_state.stats = None
    st.session_state.keywords = []

def clear_input():
    st.session_state.main_text_input = ""
    st.session_state.summary_output = ""
    st.session_state.stats = None
    st.session_state.keywords = []

# Theme color definitions
if st.session_state.theme_mode == "Light":
    css_vars = """
        --bg-page: #F7F4EE;
        --bg-card: #FFFFFF;
        --bg-muted: #EFEAE1;
        --bg-accent-soft: #F2ECE1;
        --text-primary: #251F1A;
        --text-secondary: #6F665D;
        --text-muted: #958B80;
        --accent: #9A6342;
        --accent-hover: #7E4F32;
        --border: #E5DFD5;
        --border-subtle: #ECE6DC;
        --card-shadow: rgba(37, 31, 26, 0.04);
        --input-bg: #FFFFFF;
    """
else:
    # Warm Editorial Dark Mode
    css_vars = """
        --bg-page: #161311;
        --bg-card: #201B17;
        --bg-muted: #2A241F;
        --bg-accent-soft: #2F2721;
        --text-primary: #F5EFE6;
        --text-secondary: #C0B4A7;
        --text-muted: #8C8074;
        --accent: #C8845A;
        --accent-hover: #D9956B;
        --border: #382F28;
        --border-subtle: #2D251F;
        --card-shadow: rgba(0, 0, 0, 0.25);
        --input-bg: #201B17;
    """

# Dynamic CSS Injection
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    :root {{
        {css_vars}
        --font-serif: 'Playfair Display', Georgia, serif;
        --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Global Background & Body */
    .stApp {{
        background-color: var(--bg-page) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        transition: background-color 0.3s ease, color 0.3s ease;
    }}

    /* Container constraints */
    .block-container {{
        max-width: 1140px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
    }}

    /* Header Nav */
    .app-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1.25rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--border);
    }}
    .app-logo {{
        font-family: var(--font-serif);
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.01em;
        text-decoration: none;
    }}

    /* Hero Section */
    .hero-wrapper {{
        text-align: center;
        margin-bottom: 2.25rem;
    }}
    .hero-kicker {{
        font-family: var(--font-sans);
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 0.4rem;
    }}
    .hero-heading {{
        font-family: var(--font-serif);
        font-size: clamp(2rem, 4.5vw, 3.1rem);
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }}
    .hero-subheading {{
        font-size: 1rem;
        color: var(--text-secondary);
        max-width: 620px;
        margin: 0 auto;
        line-height: 1.6;
    }}

    /* Section Headings */
    .panel-kicker {{
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 0.25rem;
    }}
    .panel-title {{
        font-family: var(--font-serif);
        font-size: 1.45rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.85rem;
    }}

    /* Card Containers */
    .card-surface {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px var(--card-shadow);
        margin-bottom: 1.25rem;
    }}

    /* Text Area Styling */
    .stTextArea textarea {{
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        font-family: var(--font-sans) !important;
        font-size: 0.95rem !important;
        line-height: 1.65 !important;
        padding: 0.9rem !important;
    }}
    .stTextArea textarea:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(154, 99, 66, 0.2) !important;
    }}
    .stTextArea label {{
        display: none !important;
    }}

    /* Buttons Styling */
    div.stButton > button {{
        font-family: var(--font-sans) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.15rem !important;
        transition: all 0.2s ease !important;
        border: 1px solid var(--border) !important;
    }}
    div[data-testid="stBaseButton-primary"] > button,
    button[kind="primary"] {{
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
        border-color: var(--accent) !important;
    }}
    div[data-testid="stBaseButton-primary"] > button:hover,
    button[kind="primary"]:hover {{
        background-color: var(--accent-hover) !important;
        border-color: var(--accent-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(154, 99, 66, 0.3) !important;
    }}
    div[data-testid="stBaseButton-secondary"] > button,
    button[kind="secondary"] {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }}
    div[data-testid="stBaseButton-secondary"] > button:hover,
    button[kind="secondary"]:hover {{
        background-color: var(--bg-muted) !important;
        border-color: var(--accent) !important;
        color: var(--accent) !important;
    }}

    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        gap: 1.75rem !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-family: var(--font-sans) !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: var(--text-secondary) !important;
        padding: 0.6rem 0 !important;
        background: transparent !important;
        border: none !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: var(--text-primary) !important;
        border-bottom: 2px solid var(--accent) !important;
    }}

    /* Selectbox & Sliders */
    div[data-baseweb="select"] > div {{
        background-color: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }}
    div[data-testid="stMarkdownContainer"] p {{
        color: var(--text-primary);
    }}

    /* Metric Ribbon */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 0.75rem;
        background: var(--bg-muted);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    .metric-item {{
        text-align: center;
    }}
    .metric-digit {{
        font-family: var(--font-serif);
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }}
    .metric-name {{
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-secondary);
        font-weight: 600;
        margin-top: 0.2rem;
    }}

    /* Output Summary Box */
    .summary-result-box {{
        background: var(--bg-card);
        border-left: 3.5px solid var(--accent);
        border-radius: 0 10px 10px 0;
        padding: 1.35rem 1.5rem;
        font-size: 0.98rem;
        line-height: 1.75;
        color: var(--text-primary);
        box-shadow: 0 2px 10px var(--card-shadow);
        margin: 1rem 0;
        border-top: 1px solid var(--border-subtle);
        border-right: 1px solid var(--border-subtle);
        border-bottom: 1px solid var(--border-subtle);
    }}
    .bullet-row {{
        display: flex;
        align-items: flex-start;
        gap: 0.65rem;
        margin-bottom: 0.75rem;
    }}
    .bullet-icon {{
        color: var(--accent);
        font-size: 1.1rem;
        line-height: 1.2;
        font-weight: bold;
    }}

    /* Tag / Keyword Chips */
    .chips-wrapper {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin: 0.75rem 0;
    }}
    .chip-item {{
        background: var(--bg-accent-soft);
        color: var(--accent);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.25rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }}

    /* Custom JS Audio Button */
    .audio-btn {{
        width: 100%;
        padding: 0.6rem;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: var(--bg-card);
        color: var(--text-primary);
        font-family: var(--font-sans);
        font-size: 0.84rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }}
    .audio-btn:hover {{
        background: var(--bg-muted);
        border-color: var(--accent);
        color: var(--accent);
    }}

    /* Empty State */
    .empty-state-box {{
        border: 1.5px dashed var(--border);
        border-radius: 12px;
        padding: 3rem 1.5rem;
        text-align: center;
        background: var(--bg-card);
        color: var(--text-secondary);
        margin-top: 0.5rem;
    }}
    .empty-state-title {{
        font-family: var(--font-serif);
        font-size: 1.2rem;
        color: var(--text-primary);
        font-weight: 600;
        margin: 0.5rem 0 0.25rem 0;
    }}

    /* Footer */
    .app-footer {{
        text-align: center;
        border-top: 1px solid var(--border);
        padding-top: 2rem;
        margin-top: 3.5rem;
        color: var(--text-secondary);
        font-size: 0.8rem;
    }}
    .app-footer-brand {{
        font-family: var(--font-serif);
        font-size: 1.05rem;
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 0.2rem;
    }}
</style>
""", unsafe_allow_html=True)

# Helper Functions
def extract_key_terms(text, count=5):
    """Extracts top meaningful terms from input text."""
    stop = set([
        "the", "and", "is", "in", "it", "of", "to", "for", "with", "on", "that", "this",
        "by", "an", "be", "are", "from", "as", "at", "or", "which", "into", "their",
        "has", "have", "more", "also", "were", "been", "through", "during", "using",
        "such", "both", "these", "over", "under", "between", "while", "after", "other",
        "about", "will", "would", "should", "could", "there", "then", "them", "they"
    ])
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = [w.capitalize() for w in words if w not in stop]
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:count]]

def run_ai_summarization(text, max_len=140, min_len=40):
    """Queries Hugging Face BART model or provides extractive fallback."""
    if not text.strip():
        return "Please provide text to summarize."
    
    payload = {
        "inputs": text,
        "parameters": {
            "max_length": max_len,
            "min_length": min_len,
            "do_sample": False
        }
    }
    
    try:
        if HF_API_TOKEN:
            res = requests.post(API_URL, headers=headers, json=payload, timeout=25)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0 and "summary_text" in data[0]:
                    return data[0]["summary_text"].strip()
                elif isinstance(data, dict) and "error" in data:
                    return f"API Notice: {data.get('error')}"
    except Exception:
        pass

    # Intelligent fallback summarizer
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sentences) <= 2:
        return text.strip()
    return " ".join(sentences[:min(len(sentences), 3)]).strip()

def format_output(raw_summary, mode):
    """Formats summary into standard, bullet list, executive, or TL;DR structure."""
    if not raw_summary or raw_summary.startswith("API Notice:"):
        return raw_summary

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', raw_summary) if s.strip()]

    if mode == "Key Bullet Points":
        return sentences
    elif mode == "Executive Summary":
        if len(sentences) >= 2:
            return {
                "core": sentences[0],
                "details": sentences[1:]
            }
        return {"core": raw_summary, "details": []}
    elif mode == "TL;DR (Quick Take)":
        return sentences[0] if sentences else raw_summary
    else:
        return raw_summary

# Navigation & Theme Switcher Bar
nav_col1, nav_col2 = st.columns([3, 1])
with nav_col1:
    st.markdown("""
    <div style="display: flex; align-items: baseline; gap: 1.5rem; padding-top: 0.5rem;">
        <span class="app-logo">AI Text Summarizer</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    theme_selection = st.radio(
        "Theme",
        options=["☀️ Light Mode", "🌙 Dark Mode"],
        index=0 if st.session_state.theme_mode == "Light" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    new_theme = "Light" if "Light" in theme_selection else "Dark"
    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()

st.markdown('<div style="border-bottom: 1px solid var(--border); margin-bottom: 2rem; margin-top: 0.5rem;"></div>', unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-kicker">Neural Text Synthesis</div>
    <div class="hero-heading">Intelligent Text Summarizer</div>
    <div class="hero-subheading">Compress long-form articles, reports, and research into clear, structured, and actionable summaries in seconds.</div>
</div>
""", unsafe_allow_html=True)

# Main Studio Tabs
tab_summarize, tab_history, tab_docs = st.tabs(["📝 Summarizer Workspace", "🗄️ History & Archive", "⚙️ Capabilities & Settings"])

with tab_summarize:
    col_left, col_right = st.columns([1.05, 0.95], gap="large")

    # Left Column: Input and Customization
    with col_left:
        st.markdown('<div class="panel-kicker">Input Text</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Source Document</div>', unsafe_allow_html=True)

        # Quick Sample Selectors using reliable Streamlit callbacks
        st.markdown('<div style="font-size: 0.74rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.35rem;">LOAD SAMPLE DATA:</div>', unsafe_allow_html=True)
        sample_c1, sample_c2, sample_c3 = st.columns(3)
        with sample_c1:
            st.button("🤖 AI Research", on_click=load_sample, args=("ai_research",), use_container_width=True)
        with sample_c2:
            st.button("📈 Financial Report", on_click=load_sample, args=("financial_report",), use_container_width=True)
        with sample_c3:
            st.button("🌍 Climate Energy", on_click=load_sample, args=("climate_energy",), use_container_width=True)

        # Direct Document Upload Area with auto-load
        with st.expander("📂 Upload Document (.txt, .md)", expanded=False):
            uploaded = st.file_uploader("Choose a text or markdown file", type=["txt", "md"], key="file_uploader_widget")
            if uploaded is not None:
                file_text = uploaded.read().decode("utf-8", errors="ignore")
                if st.button("📥 Load Uploaded Document into Input", use_container_width=True):
                    st.session_state.main_text_input = file_text
                    st.success("File content loaded successfully!")
                    st.rerun()

        # Text Area Input
        text_input_val = st.text_area(
            label="Source Document Text",
            height=250,
            placeholder="Paste your article, meeting notes, essay, research paper, or transcript here...",
            key="main_text_input"
        )

        # Input Live Metrics
        word_count = len(text_input_val.split()) if text_input_val.strip() else 0
        char_count = len(text_input_val)
        sentence_count = len([s for s in re.split(r'[.!?]+', text_input_val) if s.strip()])
        est_read_min = round(word_count / 200, 1) if word_count > 0 else 0

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-secondary); margin-top: -8px; margin-bottom: 12px; padding: 0 4px;">
            <span>{word_count} words &bull; {sentence_count} sentences &bull; {char_count} chars</span>
            <span>Est. Reading: ~{est_read_min} min</span>
        </div>
        """, unsafe_allow_html=True)

        # Configuration Options
        st.markdown('<div style="margin-top: 1.25rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-kicker">Customization</div>', unsafe_allow_html=True)

        cfg_col1, cfg_col2 = st.columns(2)
        with cfg_col1:
            summary_format = st.selectbox(
                "Summary Format",
                ["Standard Paragraph", "Executive Summary", "Key Bullet Points", "TL;DR (Quick Take)"],
                index=0
            )
        with cfg_col2:
            length_preset = st.select_slider(
                "Summary Length",
                options=["Concise", "Balanced", "Comprehensive"],
                value="Balanced"
            )

        # Map length slider to token thresholds
        length_map = {
            "Concise": (65, 25),
            "Balanced": (140, 50),
            "Comprehensive": (240, 90)
        }
        max_t, min_t = length_map[length_preset]

        # Action Buttons: Summarize + Dedicated Clear Text Button
        btn_c1, btn_c2 = st.columns([1.6, 1])
        with btn_c1:
            generate_summary_btn = st.button("⚡ Summarize Text", type="primary", use_container_width=True)
        with btn_c2:
            st.button("🗑️ Clear Text", on_click=clear_input, type="secondary", use_container_width=True)

    # Right Column: Output & Analytics
    with col_right:
        st.markdown('<div class="panel-kicker">Generated Result</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Summary Output</div>', unsafe_allow_html=True)

        if generate_summary_btn:
            if not text_input_val.strip():
                st.warning("Please paste or upload some text to summarize.")
            else:
                with st.spinner("Analyzing and summarizing text..."):
                    raw_res = run_ai_summarization(text_input_val, max_len=max_t, min_len=min_t)
                    formatted_res = format_output(raw_res, summary_format)
                    
                    st.session_state.summary_output = formatted_res
                    st.session_state.keywords = extract_key_terms(text_input_val, 5)

                    # Compute output stats
                    if isinstance(formatted_res, list):
                        out_words_count = len(" ".join(formatted_res).split())
                    elif isinstance(formatted_res, dict):
                        out_words_count = len((formatted_res["core"] + " " + " ".join(formatted_res["details"])).split())
                    else:
                        out_words_count = len(formatted_res.split())

                    reduction = max(0, round((1 - (out_words_count / max(word_count, 1))) * 100))
                    time_saved_calc = max(0.1, round((word_count - out_words_count) / 200, 1))

                    st.session_state.stats = {
                        "input_words": word_count,
                        "output_words": out_words_count,
                        "reduction": reduction,
                        "time_saved": time_saved_calc,
                        "format": summary_format
                    }

                    # Add to session history
                    st.session_state.summary_history.insert(0, {
                        "title": text_input_val[:45].replace("\n", " ") + "...",
                        "format": summary_format,
                        "summary": formatted_res,
                        "words": out_words_count,
                        "reduction": reduction
                    })

        # Display Summary Output
        if st.session_state.summary_output:
            # Metrics Ribbon
            if st.session_state.stats:
                st_data = st.session_state.stats
                st.markdown(f"""
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-digit">{st_data['reduction']}%</div>
                        <div class="metric-name">Reduction</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-digit">{st_data['output_words']}</div>
                        <div class="metric-name">Summary Words</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-digit">{st_data['time_saved']}m</div>
                        <div class="metric-name">Time Saved</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Key Topic Chips
            if st.session_state.keywords:
                chips_html = "".join([f'<span class="chip-item">{k}</span>' for k in st.session_state.keywords])
                st.markdown(f"""
                <div style="font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.2rem;">Extracted Key Topics</div>
                <div class="chips-wrapper">{chips_html}</div>
                """, unsafe_allow_html=True)

            # Output Formatting
            output_data = st.session_state.summary_output
            plain_text_export = ""
            
            if isinstance(output_data, list):
                # Bullet list format
                bullets_html = "".join([
                    f'<div class="bullet-row"><span class="bullet-icon">&#x2022;</span><span>{b}</span></div>'
                    for b in output_data
                ])
                st.markdown(f'<div class="summary-result-box">{bullets_html}</div>', unsafe_allow_html=True)
                plain_text_export = "\n".join([f"• {b}" for b in output_data])
                speech_readout = " ".join(output_data)

            elif isinstance(output_data, dict):
                # Executive summary format
                exec_details_html = "".join([
                    f'<div class="bullet-row"><span class="bullet-icon">&#x2022;</span><span>{d}</span></div>'
                    for d in output_data["details"]
                ])
                st.markdown(f"""
                <div class="summary-result-box">
                    <div style="font-weight: 600; margin-bottom: 0.6rem; color: var(--text-primary); font-size: 1.02rem;">
                        {output_data['core']}
                    </div>
                    <div style="margin-top: 0.5rem; border-top: 1px solid var(--border-subtle); padding-top: 0.5rem;">
                        {exec_details_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                plain_text_export = f"Core: {output_data['core']}\n\nKey Points:\n" + "\n".join([f"• {d}" for d in output_data["details"]])
                speech_readout = output_data['core'] + " " + " ".join(output_data['details'])

            else:
                # Standard paragraph
                st.markdown(f'<div class="summary-result-box">{output_data}</div>', unsafe_allow_html=True)
                plain_text_export = str(output_data)
                speech_readout = str(output_data)

            # Export & Audio Action Row
            act_c1, act_c2 = st.columns(2)
            with act_c1:
                st.download_button(
                    label="💾 Export Summary (.md)",
                    data=f"# AI Summary Report\n\n{plain_text_export}\n\n---\n*Key Topics: {', '.join(st.session_state.keywords)}*",
                    file_name="ai_summary.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with act_c2:
                clean_readout = speech_readout.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
                st.markdown(f"""
                <button class="audio-btn" onclick="window.speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance('{clean_readout}'); u.rate = 1.0; window.speechSynthesis.speak(u);">
                    🔊 Read Summary Aloud
                </button>
                """, unsafe_allow_html=True)

        else:
            # Empty Placeholder
            st.markdown("""
            <div class="empty-state-box">
                <div style="font-size: 2rem; color: var(--accent);">&#x1F4DD;</div>
                <div class="empty-state-title">No Summary Generated Yet</div>
                <div style="font-size: 0.88rem; max-width: 320px; margin: 0 auto; line-height: 1.5;">Enter text on the left, load a sample document, or upload a file, then click "Summarize Text".</div>
            </div>
            """, unsafe_allow_html=True)

with tab_history:
    st.markdown('<div class="panel-kicker">Session Storage</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Recent Summaries</div>', unsafe_allow_html=True)

    if st.session_state.summary_history:
        for idx, item in enumerate(st.session_state.summary_history):
            with st.container():
                st.markdown(f"""
                <div class="card-surface" style="padding: 1.2rem; margin-bottom: 0.85rem;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.4rem;">
                        <span style="font-family: var(--font-serif); font-weight: 600; font-size: 1.05rem; color: var(--text-primary);">{item['title']}</span>
                        <span class="chip-item">{item['format']} &bull; -{item['reduction']}%</span>
                    </div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                        {item['summary'] if isinstance(item['summary'], str) else (' • '.join(item['summary']) if isinstance(item['summary'], list) else item['summary'].get('core', ''))}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No summaries generated yet in this session.")

with tab_docs:
    st.markdown('<div class="panel-kicker">Technical Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Summarization Engine & Features</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card-surface">
        <p style="line-height: 1.8; color: var(--text-primary); margin-bottom: 1.25rem;">
            This AI Text Summarizer uses sequence-to-sequence neural network architectures to produce abstractive summaries that distill meaning rather than simply copying lines.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.25rem;">
            <div>
                <h4 style="font-family: var(--font-serif); font-size: 1.05rem; color: var(--accent); margin-bottom: 0.3rem;">BART Large CNN</h4>
                <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5;">Trained on comprehensive news &amp; encyclopedic corpora for high factual retention and coherent paragraph synthesis.</p>
            </div>
            <div>
                <h4 style="font-family: var(--font-serif); font-size: 1.05rem; color: var(--accent); margin-bottom: 0.3rem;">Multiple Format Modes</h4>
                <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5;">Format your output as Executive Briefs, Key Bullet Points, One-Line TL;DRs, or balanced narrative paragraphs.</p>
            </div>
            <div>
                <h4 style="font-family: var(--font-serif); font-size: 1.05rem; color: var(--accent); margin-bottom: 0.3rem;">Productivity Tools</h4>
                <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5;">Built-in reduction ratio calculation, key topic extraction, audio readout, file upload, light/dark themes, and markdown export support.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="app-footer">
    <div class="app-footer-brand">AI Text Summarizer</div>
    <div>Accurate, Abstractive &amp; Structured Text Summarization</div>
</div>
""", unsafe_allow_html=True)