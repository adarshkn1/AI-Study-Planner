import streamlit as st
import matplotlib.pyplot as plt

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.02em;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Glassmorphic Metric Cards */
    .glass-card {
        background: linear-gradient(135deg, rgba(30, 34, 45, 0.8), rgba(22, 25, 34, 0.9));
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 15px;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(0, 191, 255, 0.3);
    }

    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    .hero-title {
        background: linear-gradient(90deg, #60A5FA 0%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* Status Badges */
    .badge-success {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .badge-warning {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .badge-info {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Agent Loop Callout */
    .agent-loop-card {
        background: linear-gradient(90deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.9) 100%);
        border-left: 4px solid #6366F1;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
    }

    /* Streamlit Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #4F46E5 0%, #6366F1 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #4338CA 0%, #4F46E5 100%);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.5);
        transform: translateY(-1px);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
"""

def apply_custom_theme():
    """Injects custom glassmorphism and gradient CSS styling."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_hero(title: str, subtitle: str, icon: str = "🧠"):
    """Renders a sleek, modern hero header banner."""
    st.markdown(f"""
    <div class="hero-container">
        <div style="font-size: 2rem; margin-bottom: 4px;">{icon}</div>
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

def style_matplotlib_dark():
    """Returns dark theme properties for matplotlib figures."""
    plt.rcParams.update({
        'figure.facecolor': '#0F172A',
        'axes.facecolor': '#1E293B',
        'axes.edgecolor': '#334155',
        'axes.labelcolor': '#94A3B8',
        'xtick.color': '#CBD5E1',
        'ytick.color': '#CBD5E1',
        'text.color': '#F8FAFC',
        'grid.color': '#334155',
        'grid.alpha': 0.4,
        'font.family': 'sans-serif'
    })
