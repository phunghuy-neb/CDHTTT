import streamlit as st
from PIL import Image
from search import search

st.set_page_config(
    page_title="VisualSearch AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ───────────────────────── SESSION STATE ──────────────────────────
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = 'resnet50'

# ───────────────────────── MODEL METADATA ─────────────────────────
MODEL_INFO = {
    'resnet50': {
        'icon': '🏗️',
        'name': 'ResNet50',
        'dim': '2048 chiều',
        'speed': 'Nhanh',
        'speed_icon': '⚡',
        'desc': 'Mạng 50 lớp với skip connections. Cân bằng tốt giữa độ chính xác và tốc độ.',
        'color': '#63b3ed',
        'glow': 'rgba(99,179,237,0.25)',
    },
    'mobilenetv2': {
        'icon': '📱',
        'name': 'MobileNetV2',
        'dim': '1280 chiều',
        'speed': 'Rất nhanh',
        'speed_icon': '🚀',
        'desc': 'Tối ưu cho thiết bị di động với depthwise separable conv. Nhẹ nhất trong 3 model.',
        'color': '#34d399',
        'glow': 'rgba(52,211,153,0.25)',
    },
    'vit': {
        'icon': '🔭',
        'name': 'ViT-Base/16',
        'dim': '768 chiều',
        'speed': 'Chậm hơn',
        'speed_icon': '🌐',
        'desc': 'Vision Transformer chia ảnh thành 196 patches. Nắm bắt ngữ cảnh toàn cục tốt nhất.',
        'color': '#a78bfa',
        'glow': 'rgba(167,139,250,0.25)',
    },
}

# ───────────────────────── CUSTOM CSS ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

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

[data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }

.block-container {
    padding: 3rem 4rem !important;
    max-width: 1400px !important;
}

/* ── Hero ── */
.hero-section {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--border);
}
.hero-icon {
    width: 52px; height: 52px;
    border-radius: 14px;
    background: var(--accent-grad);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; flex-shrink: 0;
    box-shadow: 0 8px 24px rgba(99,179,237,0.3);
}
.hero-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.2rem !important; font-weight: 800 !important;
    letter-spacing: -0.03em;
    background: var(--accent-grad);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    line-height: 1.1; margin: 0 !important;
}
.hero-sub {
    font-size: 0.95rem; color: var(--text-muted);
    margin-top: 0.25rem; font-weight: 300; letter-spacing: 0.01em;
}

/* ── Section label ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--text-muted); margin-bottom: 0.75rem;
}

/* ── Model selector buttons ── */
[data-testid="stButton"] > button {
    background: var(--bg-card) !important;
    color: var(--text-subtle) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    letter-spacing: 0.03em !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: 0.75rem 1.5rem !important;
    box-shadow: var(--shadow-card) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
[data-testid="stButton"] > button:hover {
    border-color: rgba(255,255,255,0.18) !important;
    color: var(--text-primary) !important;
    transform: translateY(-2px) !important;
}

/* ── Active model button (via .model-active helper) ── */
.model-active [data-testid="stButton"] > button {
    background: var(--accent-grad) !important;
    color: #050810 !important;
    border-color: transparent !important;
    box-shadow: 0 4px 24px rgba(99,179,237,0.4) !important;
}
.model-active-green [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
    color: #050810 !important;
    border-color: transparent !important;
    box-shadow: 0 4px 24px rgba(52,211,153,0.4) !important;
}
.model-active-purple [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%) !important;
    color: #fff !important;
    border-color: transparent !important;
    box-shadow: 0 4px 24px rgba(167,139,250,0.4) !important;
}
.model-active-compare [data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%) !important;
    color: #fff !important;
    border-color: transparent !important;
    box-shadow: 0 4px 24px rgba(245,158,11,0.4) !important;
}

/* ── Model info cards ── */
.model-card {
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-card);
    margin-top: 0.5rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.model-card-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem; font-weight: 700;
    color: var(--text-primary); margin-bottom: 0.4rem;
}
.model-card-meta {
    display: flex; gap: 0.5rem; flex-wrap: wrap;
    margin-bottom: 0.6rem;
}
.model-pill {
    padding: 0.15rem 0.6rem;
    border-radius: 99px;
    font-size: 0.72rem; font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    border: 1px solid;
}
.model-card-desc {
    font-size: 0.82rem; color: var(--text-muted);
    font-weight: 300; line-height: 1.55;
}

/* ── Search button ── */
.search-btn [data-testid="stButton"] > button {
    background: var(--accent-grad) !important;
    color: #050810 !important;
    border: none !important;
    box-shadow: 0 4px 24px rgba(99,179,237,0.35) !important;
    padding: 0.85rem 2.5rem !important;
}
.search-btn [data-testid="stButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(99,179,237,0.5) !important;
    filter: brightness(1.08) !important;
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
[data-testid="stFileUploadDropzone"] { background: transparent !important; border: none !important; }
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] small { color: var(--text-subtle) !important; }
[data-testid="stFileUploadDropzone"] svg { fill: var(--accent) !important; opacity: 0.6; }

/* ── Image cards ── */
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

/* ── Result layout ── */
.result-header {
    display: flex; align-items: center;
    gap: 0.75rem; margin: 2.5rem 0 1.5rem;
}
.result-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem; font-weight: 700; color: var(--text-primary);
}
.result-count {
    padding: 0.2rem 0.65rem; border-radius: 99px;
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.25);
    color: var(--success); font-size: 0.78rem; font-weight: 600;
}
.rank-badge {
    display: inline-block; padding: 0.15rem 0.55rem;
    border-radius: 99px; background: var(--accent-grad);
    color: #050810; font-size: 0.7rem; font-weight: 700;
    font-family: 'Syne', sans-serif; margin-bottom: 0.4rem;
}

/* Compare section header */
.compare-section-header {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.75rem 1.25rem;
    border-radius: var(--radius-lg);
    margin: 2rem 0 1rem;
    border-left: 3px solid;
}
.compare-section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem; font-weight: 700; color: var(--text-primary);
}
.compare-section-dim {
    font-size: 0.78rem; color: var(--text-muted);
}

/* ── Misc ── */
.query-label {
    font-family: 'Syne', sans-serif;
    font-size: 1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;
}
[data-testid="stSpinner"] p, [data-testid="stSpinner"] span {
    color: var(--accent) !important; font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stImage"] img { border-radius: 12px !important; }
[data-testid="stImage"] div {
    color: var(--text-muted) !important; font-size: 0.8rem !important;
    font-family: 'DM Sans', sans-serif !important; text-align: center !important;
}
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 2rem 0 !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# ───────────────────────── HEADER ─────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-icon">🔍</div>
    <div>
        <div class="hero-title">Tìm kiếm ảnh tương tự</div>
        <div class="hero-sub">So sánh kết quả giữa ResNet50 · MobileNetV2 · ViT-Base</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ───────────────────────── MODEL SELECTOR ─────────────────────────
st.markdown('<div class="section-label">🤖 Chọn model AI</div>', unsafe_allow_html=True)

sel = st.session_state.selected_model

btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4, gap="small")

with btn_col1:
    active_cls = "model-active" if sel == 'resnet50' else ""
    st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
    if st.button("🏗️  ResNet50", use_container_width=True, key="btn_resnet"):
        st.session_state.selected_model = 'resnet50'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with btn_col2:
    active_cls = "model-active-green" if sel == 'mobilenetv2' else ""
    st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
    if st.button("📱  MobileNetV2", use_container_width=True, key="btn_mobile"):
        st.session_state.selected_model = 'mobilenetv2'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with btn_col3:
    active_cls = "model-active-purple" if sel == 'vit' else ""
    st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
    if st.button("🔭  ViT-Base/16", use_container_width=True, key="btn_vit"):
        st.session_state.selected_model = 'vit'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with btn_col4:
    active_cls = "model-active-compare" if sel == 'compare' else ""
    st.markdown(f'<div class="{active_cls}">', unsafe_allow_html=True)
    if st.button("📊  So sánh tất cả", use_container_width=True, key="btn_compare"):
        st.session_state.selected_model = 'compare'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Model info cards ──
if sel != 'compare':
    info = MODEL_INFO[sel]
    st.markdown(f"""
    <div class="model-card" style="border-color:{info['color']}33; box-shadow: 0 0 40px {info['glow']};">
        <div class="model-card-title">{info['icon']} {info['name']}</div>
        <div class="model-card-meta">
            <span class="model-pill" style="color:{info['color']};border-color:{info['color']}44;background:{info['color']}11;">
                📐 {info['dim']}
            </span>
            <span class="model-pill" style="color:var(--text-subtle);border-color:var(--border);background:var(--bg-elevated);">
                {info['speed_icon']} {info['speed']}
            </span>
        </div>
        <div class="model-card-desc">{info['desc']}</div>
    </div>
    """, unsafe_allow_html=True)
else:
    c1, c2, c3 = st.columns(3, gap="small")
    for col, (key, info) in zip([c1, c2, c3], MODEL_INFO.items()):
        with col:
            st.markdown(f"""
            <div class="model-card" style="border-color:{info['color']}33;">
                <div class="model-card-title">{info['icon']} {info['name']}</div>
                <div class="model-card-meta">
                    <span class="model-pill" style="color:{info['color']};border-color:{info['color']}44;background:{info['color']}11;">
                        📐 {info['dim']}
                    </span>
                </div>
                <div class="model-card-desc">{info['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

# ───────────────────────── UPLOAD ─────────────────────────────────
st.markdown('<div class="section-label">📤 Tải ảnh lên</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="",
    type=["jpg", "png", "jpeg"],
    label_visibility="collapsed"
)

# ───────────────────────── SEARCH + RESULTS ───────────────────────
if uploaded_file:
    query_img = Image.open(uploaded_file)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    col1, col_gap, col2 = st.columns([1.2, 0.15, 1])

    with col1:
        st.markdown('<div class="query-label">Ảnh của bạn</div>', unsafe_allow_html=True)
        st.image(query_img, use_container_width=True)

    with col2:
        st.markdown('<div class="query-label">Tìm kiếm</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if sel == 'compare':
            btn_label = "📊  So sánh 3 model"
        else:
            btn_label = f"🚀  Tìm với {MODEL_INFO[sel]['name']}"

        st.markdown('<div class="search-btn">', unsafe_allow_html=True)
        search_btn = st.button(btn_label, use_container_width=True, key="search_main")
        st.markdown('</div>', unsafe_allow_html=True)

        if sel == 'compare':
            st.markdown("""
            <div style="margin-top:0.75rem;padding:0.65rem 0.9rem;border-radius:12px;
                        background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                        font-size:0.8rem;color:#f59e0b;line-height:1.5;">
                ⚠️ So sánh sẽ chạy cả 3 model — cần đủ index và mất nhiều thời gian hơn.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2rem; border-top:1px solid rgba(255,255,255,0.07)'></div>",
                unsafe_allow_html=True)

    # ── Run search ──
    if search_btn:
        if sel == 'compare':
            all_results = {}
            errors = {}
            progress_placeholder = st.empty()

            for model_key, minfo in MODEL_INFO.items():
                progress_placeholder.markdown(
                    f"<div style='text-align:center;color:var(--text-muted);font-family:Syne,sans-serif;"
                    f"font-size:0.9rem;padding:1rem;'>⚡ Đang chạy {minfo['name']} ...</div>",
                    unsafe_allow_html=True
                )
                try:
                    all_results[model_key] = search(query_img, top_k=5, model_name=model_key)
                except FileNotFoundError as e:
                    errors[model_key] = str(e)

            progress_placeholder.empty()

            # Show header
            found = len(all_results)
            st.markdown(f"""
            <div class="result-header">
                <span class="result-title">So sánh kết quả</span>
                <span class="result-count">✓ {found}/3 model</span>
            </div>
            """, unsafe_allow_html=True)

            # Show results per model
            for model_key, minfo in MODEL_INFO.items():
                if model_key in errors:
                    st.markdown(f"""
                    <div style="padding:1rem 1.25rem;border-radius:14px;
                                background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);
                                margin-bottom:1.5rem;color:#f87171;font-size:0.85rem;">
                        ⛔ <strong>{minfo['icon']} {minfo['name']}</strong> — {errors[model_key]}
                    </div>
                    """, unsafe_allow_html=True)
                    continue

                bg_hex = minfo['color'] + '11'
                border_hex = minfo['color'] + '44'
                st.markdown(f"""
                <div class="compare-section-header"
                     style="background:{bg_hex};border-left-color:{minfo['color']};">
                    <span style="font-size:1.4rem;">{minfo['icon']}</span>
                    <div>
                        <div class="compare-section-title">{minfo['name']}</div>
                        <div class="compare-section-dim">📐 {minfo['dim']} &nbsp;·&nbsp; {minfo['speed_icon']} {minfo['speed']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                cols = st.columns(5, gap="small")
                for i, img_path in enumerate(all_results[model_key]):
                    try:
                        img = Image.open(img_path)
                        with cols[i]:
                            st.markdown(
                                f'<div class="rank-badge" style="background:linear-gradient(135deg,{minfo["color"]},#050810 200%);">#{i+1}</div>',
                                unsafe_allow_html=True
                            )
                            st.image(img, use_container_width=True)
                    except Exception:
                        pass

                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        else:
            # Single model search
            minfo = MODEL_INFO[sel]
            with st.spinner(f"⚡ Đang tìm kiếm với {minfo['name']} ..."):
                try:
                    results = search(query_img, top_k=5, model_name=sel)
                except FileNotFoundError as e:
                    st.error(f"⛔ {e}")
                    st.stop()

            st.markdown(f"""
            <div class="result-header">
                <span class="result-title">Kết quả — {minfo['icon']} {minfo['name']}</span>
                <span class="result-count">✓ {len(results)} ảnh phù hợp</span>
            </div>
            """, unsafe_allow_html=True)

            cols = st.columns(5, gap="small")
            for i, img_path in enumerate(results):
                try:
                    img = Image.open(img_path)
                    with cols[i]:
                        st.markdown(f'<div class="rank-badge"># {i+1}</div>', unsafe_allow_html=True)
                        st.image(img, use_container_width=True, caption=f"Độ tương đồng #{i+1}")
                except Exception:
                    pass

else:
    # ── Empty state ──
    st.markdown("""
    <div style="
        margin-top: 3rem;
        display: flex; flex-direction: column; align-items: center;
        gap: 1rem; opacity: 0.45; user-select: none;
    ">
        <div style="font-size: 3.5rem;">🖼️</div>
        <div style="
            font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 600;
            color: #f0f4ff; letter-spacing: -0.01em;
        ">Chưa có ảnh nào được chọn</div>
        <div style="
            font-family: 'DM Sans', sans-serif; font-size: 0.88rem;
            color: #64748b; text-align: center; max-width: 340px; line-height: 1.6;
        ">Tải lên một ảnh JPG hoặc PNG, chọn model AI, rồi nhấn tìm kiếm để so sánh kết quả</div>
    </div>
    """, unsafe_allow_html=True)
