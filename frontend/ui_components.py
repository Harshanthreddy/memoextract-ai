import streamlit as st
from frontend.config import (
    APP_NAME,
    APP_SUBTITLE,
    APP_VERSION,
    COPYRIGHT_NAME,
    USER_DISPLAY_NAME,
)


def inject_custom_css():
    """
    Injects Apple Human Interface Design System (macOS Sequoia / iOS 18 Glassmorphism).
    Completely covers Streamlit's default Deploy button & header with an authentic Apple Menu Bar.
    Hides all ugly radio dots and styles sidebar items into macOS Finder/Settings list items.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ==========================================================================
       1. APPLE SF PRO TYPOGRAPHY & AMBIENT OBSIDIAN BACKGROUND
       ========================================================================== */
    html, body, [class*="css"], .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Plus Jakarta Sans", "Helvetica Neue", sans-serif !important;
        background-color: #000000 !important;
        background-image: 
            radial-gradient(at 50% 0%, rgba(10, 132, 255, 0.12) 0px, transparent 55%),
            radial-gradient(at 100% 100%, rgba(94, 92, 230, 0.08) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(48, 209, 88, 0.06) 0px, transparent 50%) !important;
        background-attachment: fixed !important;
        color: #F5F5F7 !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* ==========================================================================
       2. COVER / HIDE STREAMLIT DEPLOY BUTTON & STATUS BAR
       ========================================================================== */
    /* Completely hide Streamlit Deploy button, header decorations, toolbar, and status widget */
    .stAppDeployButton,
    [data-testid="stAppDeployButton"],
    .stDeployButton,
    [data-testid="stToolbarActions"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    button[title="View app in Streamlit Community Cloud"],
    header [data-testid="stToolbarActions"],
    header [data-testid="stAppDeployButton"],
    div[data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        pointer-events: none !important;
    }

    /* Style the top Streamlit header transparent so Apple Menu Bar takes over */
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        height: 38px !important;
        pointer-events: none !important;
    }

    /* Keep sidebar collapse/expand button clickable */
    div[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button {
        pointer-events: auto !important;
        z-index: 1000000001 !important;
    }

    .block-container {
        padding-top: 3.2rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1350px !important;
    }

    /* Selection Styling */
    ::selection {
        background: rgba(0, 113, 227, 0.35) !important;
        color: #FFFFFF !important;
    }

    /* ==========================================================================
       3. APPLE MACOS SIDEBAR (LIQUID FROSTED GLASS & SQUIRCLE LIST ITEMS)
       ========================================================================== */
    section[data-testid="stSidebar"] {
        background: rgba(18, 18, 20, 0.82) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5) !important;
        padding-top: 2.5rem !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1rem 0.9rem !important;
    }

    /* Remove weird widget label backgrounds */
    [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* COMPLETE ELIMINATION OF ALL RADIO DOTS & CIRCLES ACROSS ALL STREAMLIT VERSIONS */
    div[class*="e1dm8mpf4"],
    div[class*="e1dm8mpf5"],
    div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
    div[data-testid="stRadio"] div[role="radiogroup"] label div:first-of-type,
    div[data-testid="stRadio"] label > div > div:first-child,
    div[data-testid="stRadio"] input[type="radio"],
    div[role="radiogroup"] input[type="radio"],
    div[data-testid="stRadio"] span[aria-hidden="true"],
    div[data-testid="stRadio"] svg {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        visibility: hidden !important;
        position: absolute !important;
        pointer-events: none !important;
    }

    /* Apple macOS Sidebar List Item (Squircle frosted button) */
    div[data-testid="stRadio"] [data-baseweb="radio"],
    div[data-testid="stRadio"] div[role="radiogroup"] label,
    div[role="radiogroup"] label {
        display: flex !important;
        align-items: center !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 11px !important;
        padding: 0.65rem 0.95rem !important;
        margin-bottom: 0.4rem !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.22s cubic-bezier(0.25, 1, 0.5, 1) !important;
        cursor: pointer !important;
    }

    div[data-testid="stRadio"] [data-baseweb="radio"]:hover,
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover,
    div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.09) !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
        transform: translateX(3px) !important;
    }

    /* Active / Selected macOS List Item */
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-selected="true"],
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked),
    div[role="radiogroup"] label[data-selected="true"],
    div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(0, 113, 227, 0.32) 0%, rgba(0, 113, 227, 0.12) 100%) !important;
        border: 1px solid rgba(0, 113, 227, 0.75) !important;
        box-shadow: 0 4px 15px rgba(0, 113, 227, 0.3) !important;
        transform: translateX(3px) !important;
    }

    div[data-testid="stRadio"] label p,
    div[role="radiogroup"] label p {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #E5E5EA !important;
        margin: 0 !important;
        letter-spacing: -0.01em !important;
        background: transparent !important;
        user-select: none !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label[data-selected="true"] p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* ==========================================================================
       4. APPLE HIG HERO BANNER
       ========================================================================== */
    .apple-hero {
        padding: 0.5rem 0 1.2rem 0;
        margin-bottom: 0.5rem;
    }

    .apple-hero-greeting {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: #FFFFFF !important;
        margin: 0 0 0.35rem 0 !important;
    }

    .apple-hero-sub {
        font-size: 0.98rem !important;
        color: #A1A1A6 !important;
        margin: 0 !important;
        font-weight: 400 !important;
    }

    /* ==========================================================================
       5. APPLE WIDGET KPI CARDS (LIQUID GLASS SQUIRCLES)
       ========================================================================== */
    .apple-kpi-card {
        background: rgba(28, 28, 30, 0.65) !important;
        backdrop-filter: blur(35px) saturate(190%) !important;
        -webkit-backdrop-filter: blur(35px) saturate(190%) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 20px !important;
        padding: 1.3rem !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5) !important;
        transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        height: 100% !important;
    }

    .apple-kpi-card:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7) !important;
    }

    .apple-icon-squircle {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .squircle-blue { background: linear-gradient(135deg, #0A84FF 0%, #0071E3 100%); color: #FFFFFF; }
    .squircle-green { background: linear-gradient(135deg, #30D158 0%, #28CD41 100%); color: #FFFFFF; }
    .squircle-amber { background: linear-gradient(135deg, #FF9F0A 0%, #FF9500 100%); color: #FFFFFF; }
    .squircle-purple { background: linear-gradient(135deg, #BF5AF2 0%, #AF52DE 100%); color: #FFFFFF; }

    .apple-kpi-num {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
        color: #FFFFFF !important;
        margin: 0 0 0.2rem 0 !important;
        line-height: 1.1 !important;
    }

    .apple-kpi-label {
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: #F5F5F7 !important;
        margin: 0 !important;
    }

    .apple-kpi-sub {
        font-size: 0.8rem !important;
        color: #86868B !important;
        margin-top: 0.35rem !important;
    }

    /* ==========================================================================
       6. APPLE AIRDROP-STYLE UPLOAD ZONE
       ========================================================================== */
    .apple-upload-zone {
        background: rgba(28, 28, 30, 0.5) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 2px dashed rgba(255, 255, 255, 0.18) !important;
        border-radius: 22px !important;
        padding: 2.5rem 1.5rem !important;
        text-align: center !important;
        transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1) !important;
        margin-bottom: 1.5rem !important;
    }

    .apple-upload-zone:hover {
        border-color: #0A84FF !important;
        background: rgba(10, 132, 255, 0.08) !important;
        transform: scale(1.006) !important;
        box-shadow: 0 0 35px rgba(10, 132, 255, 0.2) !important;
    }

    .apple-cloud-icon {
        font-size: 3rem !important;
        color: #0A84FF !important;
        margin-bottom: 0.5rem !important;
        display: inline-block !important;
        animation: float-apple 3.5s ease-in-out infinite !important;
    }

    @keyframes float-apple {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    .apple-upload-title {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        margin-bottom: 0.25rem !important;
    }

    .apple-upload-desc {
        font-size: 0.82rem !important;
        color: #86868B !important;
    }

    /* ==========================================================================
       7. APPLE CONTROL CENTER WIDGETS
       ========================================================================== */
    .apple-widget {
        background: rgba(28, 28, 30, 0.6) !important;
        backdrop-filter: blur(30px) !important;
        -webkit-backdrop-filter: blur(30px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 20px !important;
        padding: 1.3rem !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5) !important;
        margin-bottom: 1.25rem !important;
    }

    .apple-widget-title {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        margin-bottom: 0.85rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }

    .apple-status-row {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 0.6rem 0 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        font-size: 0.85rem !important;
        color: #D1D1D6 !important;
    }

    .apple-status-row:last-child {
        border-bottom: none !important;
    }

    @keyframes apple-pulse {
        0% { box-shadow: 0 0 0 0 rgba(48, 209, 88, 0.7); }
        70% { box-shadow: 0 0 0 7px rgba(48, 209, 88, 0); }
        100% { box-shadow: 0 0 0 0 rgba(48, 209, 88, 0); }
    }

    .apple-green-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #30D158;
        display: inline-block;
        margin-right: 6px;
        animation: apple-pulse 2s infinite;
    }

    /* ==========================================================================
       8. APPLE ACCENT BUTTONS
       ========================================================================== */
    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: -0.01em !important;
        padding: 0.65rem 1.2rem !important;
        transition: all 0.25s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background: #0071E3 !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(0, 113, 227, 0.4) !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background: #0077ED !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 113, 227, 0.55) !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #F5F5F7 !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.14) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-1px) !important;
    }

    /* ==========================================================================
       9. APPLE MACOS MENU BAR AT TOP (COVERS DEPLOY & STATUS BAR)
       ========================================================================== */
    .apple-mac-menubar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 38px;
        background: rgba(18, 18, 20, 0.85);
        backdrop-filter: blur(30px) saturate(200%);
        -webkit-backdrop-filter: blur(30px) saturate(200%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 1.25rem;
        z-index: 9999999;
        font-size: 0.82rem;
        font-weight: 500;
        color: #D1D1D6;
    }

    .apple-mac-menubar a, .apple-mac-menubar span {
        color: #E5E5EA;
        text-decoration: none;
    }

    .apple-menu-left {
        display: flex;
        align-items: center;
        gap: 1.15rem;
    }

    .apple-menu-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .apple-avatar-chip {
        padding: 2px 9px;
        border-radius: 9999px;
        background: rgba(10, 132, 255, 0.2);
        border: 1px solid rgba(10, 132, 255, 0.4);
        color: #64D2FF;
        font-size: 0.72rem;
        font-weight: 700;
    }

    /* Dataframe Table */
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        background: rgba(28, 28, 30, 0.5) !important;
        backdrop-filter: blur(25px) !important;
        overflow: hidden !important;
    }

    /* ==========================================================================
       10. APPLE FOOTER (WITH ALL RIGHTS RESERVED BY DUVVURUHARSHANTHREDDY)
       ========================================================================== */
    .apple-footer {
        margin-top: 4.5rem;
        padding: 2.5rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        text-align: center;
    }

    .apple-footer-chip {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 9999px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #A1A1A6;
        font-size: 0.78rem;
        font-weight: 500;
        margin-bottom: 0.6rem;
    }

    .apple-footer-text {
        font-size: 0.85rem;
        color: #86868B;
        letter-spacing: -0.01em;
    }

    .apple-author {
        color: #0A84FF;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


def render_apple_menubar(active_engine: str = "Offline Local Extractor"):
    """
    Renders an Apple macOS Menu Bar that spans the top,
    covering the Streamlit deploy button and status bar completely.
    """
    engine_name = "Offline" if "Offline" in active_engine else ("Groq AI" if "Groq" in active_engine else "FastAPI")
    st.markdown(f"""
    <div class="apple-mac-menubar">
        <div class="apple-menu-left">
            <span style="font-size: 1.05rem; color: #FFFFFF; font-weight: 700; cursor: pointer;"></span>
            <span style="font-weight: 700; color: #FFFFFF; letter-spacing: -0.01em;">Marksheet AI</span>
            <span style="color: #A1A1A6; cursor: pointer;">File</span>
            <span style="color: #A1A1A6; cursor: pointer;">Edit</span>
            <span style="color: #A1A1A6; cursor: pointer;">Extraction</span>
            <span style="color: #A1A1A6; cursor: pointer;">Window</span>
            <span style="color: #A1A1A6; cursor: pointer;">Help</span>
        </div>
        <div class="apple-menu-right">
            <span style="font-size: 0.76rem; color: #30D158; font-weight: 600;"><span class="apple-green-dot"></span> System Online</span>
            <span style="color: #555558;">•</span>
            <span style="font-size: 0.74rem; background: rgba(255,255,255,0.08); padding: 2px 7px; border-radius: 6px; color: #E5E5EA;">⚡ {engine_name}</span>
            <span style="color: #555558;">•</span>
            <span style="color: #A1A1A6; font-size: 0.74rem;">v{APP_VERSION}</span>
            <span style="color: #555558;">•</span>
            <span class="apple-avatar-chip">{USER_DISPLAY_NAME}</span>
        </div>
    </div>
    <div style="height: 10px;"></div>
    """, unsafe_allow_html=True)


def render_hero_greeting(user_name: str = USER_DISPLAY_NAME):
    """Render Apple-styled hero section"""
    st.markdown(f"""
    <div class="apple-hero">
        <h1 class="apple-hero-greeting">Welcome back, {user_name}! 👋</h1>
        <p class="apple-hero-sub">Extract marksheet data quickly and accurately using AI-powered OCR.</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(
    total_docs: int = 12,
    successful_docs: int = 10,
    success_rate: float = 83.3,
    needs_review: int = 2,
    review_rate: float = 16.7,
    avg_time_sec: float = 28.0
):
    """Renders Apple-style widget squircle KPI cards"""
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="apple-kpi-card">
            <div class="apple-icon-squircle squircle-blue">📄</div>
            <div class="apple-kpi-num">{total_docs}</div>
            <div class="apple-kpi-label">Total Documents</div>
            <div class="apple-kpi-sub">Processed so far</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="apple-kpi-card">
            <div class="apple-icon-squircle squircle-green">✓</div>
            <div class="apple-kpi-num">{successful_docs}</div>
            <div class="apple-kpi-label">Successful Extractions</div>
            <div class="apple-kpi-sub"><span style="color: #30D158; font-weight: 700;">{int(success_rate)}%</span> success rate</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="apple-kpi-card">
            <div class="apple-icon-squircle squircle-amber">⚠️</div>
            <div class="apple-kpi-num">{needs_review}</div>
            <div class="apple-kpi-label">Needs Review</div>
            <div class="apple-kpi-sub"><span style="color: #FF9F0A; font-weight: 700;">{int(review_rate)}%</span> require attention</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="apple-kpi-card">
            <div class="apple-icon-squircle squircle-purple">⚡</div>
            <div class="apple-kpi-num">{int(avg_time_sec)}s</div>
            <div class="apple-kpi-label">Avg. Processing Time</div>
            <div class="apple-kpi-sub">Per document</div>
        </div>
        """, unsafe_allow_html=True)


def render_footer():
    """Render mandatory Apple-styled copyright footer with duvvuruharshanthreddy rights reserved"""
    st.markdown(f"""
    <div class="apple-footer">
        <div class="apple-footer-chip">Marksheet Extractor v{APP_VERSION} • Built with ❤️ using Streamlit</div>
        <div class="apple-footer-text">
            © 2026 <b>{APP_NAME}</b>. All rights reserved by <span class="apple-author">{COPYRIGHT_NAME}</span>.
        </div>
    </div>
    """, unsafe_allow_html=True)
