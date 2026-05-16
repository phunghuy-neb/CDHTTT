import streamlit as st
from PIL import Image
from search import search

st.set_page_config(
    page_title="VisualSearch AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Root & Reset ── */
:root {
    --bg-deep:      #050810;
    --bg-card:      #0d1117;
    --bg-elevated:  #131924;
    --border:       rgba(255,255,255,0.07);
    --border-glow:  rgba(99,179,237,0.35);
    --accent:       #63b3ed;
    --accent-2:     #a78bfa;
    --accent-grad:  linear-gradient(135deg, #63b3ed 0%, #a78bfa 100%);
    --text-primary: #f0f4ff;
    --text-muted:   #64748b;
    --text-subtle:  #94a3b8;
    --success:      #34d399;
    --radius-lg:    18px;
    --radius-xl:    26px;
    --shadow-card:  0 4px 40px rgba(0,0,0,0.6), 0 1px 0 rgba(255,255,255,0.04) inset;
    --shadow-glow:  0 0 60px rgba(99,179,237,0.12);
}

html, body, [data-testid="stAppViewContainer"], .main {
    background: var(--bg-deep) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 10% 0%, rgba(99,179,237,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(167,139,250,0.07) 0%, transparent 60%),
        var(--bg-deep) !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
footer { display: none !important; }

.block-container {
    padding: 3rem 4rem !important;
    max-width: 1400px !important;
}

/* ── Header ── */
.hero-section {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
}

.hero-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: var(--accent-grad);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    flex-shrink: 0;
    box-shadow: 0 8px 24px rgba(99,179,237,0.3);
}

.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    background: var(--accent-grad);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin: 0 !important;
}

.hero-sub {
    font-size: 0.95rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
    font-weight: 300;
    letter-spacing: 0.01em;
}

.badge {
    margin-left: auto;
    padding: 0.35rem 1rem;
    border-radius: 99px;
    background: rgba(99,179,237,0.08);
    border: 1px solid rgba(99,179,237,0.2);
    color: var(--accent);
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-family: 'DM Sans', sans-serif;
    white-space: nowrap;
}

/* ── Upload Zone ── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1.5px dashed rgba(99,179,237,0.25) !important;
    border-radius: var(--radius-xl) !important;
    padding: 2.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: var(--shadow-card) !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(99,179,237,0.5) !important;
    box-shadow: var(--shadow-card), var(--shadow-glow) !important;
}

[data-testid="stFileUploadDropzone"] {
    background: transparent !important;
    border: none !important;
}

[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] small {
    color: var(--text-subtle) !important;
}

[data-testid="stFileUploadDropzone"] svg {
    fill: var(--accent) !important;
    opacity: 0.6;
}

/* ── Cards ── */
.img-card {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    overflow: hidden;
    box-shadow: var(--shadow-card);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.img-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-card), 0 16px 48px rgba(0,0,0,0.5);
    border-color: var(--border-glow);
}

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

.query-label {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

/* ── Button ── */
[data-testid="stButton"] > button {
    background: var(--accent-grad) !important;
    color: #050810 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.85rem 2.5rem !important;
    box-shadow: 0 4px 24px rgba(99,179,237,0.35) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

[data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(99,179,237,0.5) !important;
    filter: brightness(1.08) !important;
}

[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span {
    color: var(--accent) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Images ── */
[data-testid="stImage"] img {
    border-radius: 12px !important;
}

/* ── Captions / text ── */
[data-testid="stImage"] div {
    color: var(--text-muted) !important;
    font-size: 0.8rem !important;
    font-family: 'DM Sans', sans-serif !important;
    text-align: center !important;
}

/* ── Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2rem 0 !important;
}

/* ── Result grid labels ── */
.result-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2.5rem 0 1.5rem;
}

.result-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
}

.result-count {
    padding: 0.2rem 0.65rem;
    border-radius: 99px;
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.25);
    color: var(--success);
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
}

.rank-badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 99px;
    background: var(--accent-grad);
    color: #050810;
    font-size: 0.7rem;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
    text-align: center;
    margin-bottom: 0.4rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("""
<div class="hero-section">
    <div class="hero-icon">🔍</div>
    <div>
        <div class="hero-title">Tìm kiếm ảnh tương tự</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ===== UPLOAD =====
st.markdown('<div class="section-label">📤 Tải ảnh lên</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="",
    type=["jpg", "png", "jpeg"],
    label_visibility="collapsed"
)

if uploaded_file:
    query_img = Image.open(uploaded_file)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    col1, col_gap, col2 = st.columns([1.2, 0.15, 1])

    # ===== ẢNH QUERY =====
    with col1:
        st.markdown('<div class="query-label">Ảnh của bạn</div>', unsafe_allow_html=True)
        st.image(query_img, use_container_width=True)

    # ===== BUTTON + INFO =====
    with col2:
        st.markdown('<div class="query-label">Tìm kiếm</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # Thông tin ảnh
        w, h = query_img.size
        mode = query_img.mode

        search_btn = st.button("🚀  Tìm ảnh tương tự", use_container_width=True)

    st.markdown("<div style='margin-top:2.5rem; border-top:1px solid rgba(255,255,255,0.07)'></div>", unsafe_allow_html=True)

    # ===== SEARCH =====
    if search_btn:
        with st.spinner("⚡ Đang tìm kiếm ..."):
            results = search(query_img, top_k=5)

        # Header kết quả
        st.markdown(f"""
        <div class="result-header">
            <span class="result-title">Kết quả tìm kiếm</span>
            <span class="result-count">✓ {len(results)} ảnh phù hợp</span>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(5, gap="small")

        for i, img_path in enumerate(results):
            img = Image.open(img_path)
            with cols[i]:
                st.markdown(f'<div class="rank-badge"># {i+1}</div>', unsafe_allow_html=True)
                st.image(img, use_container_width=True, caption=f"Độ tương đồng #{i+1}")

else:
    # ===== EMPTY STATE =====
    st.markdown("""
    <div style="
        margin-top: 3rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        opacity: 0.45;
        user-select: none;
    ">
        <div style="font-size: 3.5rem;">🖼️</div>
        <div style="
            font-family: 'Syne', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: #f0f4ff;
            letter-spacing: -0.01em;
        ">Chưa có ảnh nào được chọn</div>
        <div style="
            font-family: 'DM Sans', sans-serif;
            font-size: 0.88rem;
            color: #64748b;
            text-align: center;
            max-width: 320px;
            line-height: 1.6;
        ">Tải lên một ảnh JPG hoặc PNG để bắt đầu tìm kiếm ảnh tương tự bằng AI</div>
    </div>
    """, unsafe_allow_html=True)