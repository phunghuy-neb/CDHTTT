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

# ───────────────────────── HEADER ─────────────────────────────────
st.title("Tìm kiếm ảnh tương tự")
st.caption("ResNet50 · MobileNetV2 · ViT-Base")

# ───────────────────────── MODEL SELECTOR ─────────────────────────
st.markdown("**Chọn model AI**")

sel = st.session_state.selected_model

btn_col1, btn_col2, btn_col3 = st.columns(3, gap="small")

with btn_col1:
    if st.button("🏗️  ResNet50", use_container_width=True, key="btn_resnet"):
        st.session_state.selected_model = 'resnet50'
        st.rerun()

with btn_col2:
    if st.button("📱  MobileNetV2", use_container_width=True, key="btn_mobile"):
        st.session_state.selected_model = 'mobilenetv2'
        st.rerun()

with btn_col3:
    if st.button("🔭  ViT-Base/16", use_container_width=True, key="btn_vit"):
        st.session_state.selected_model = 'vit'
        st.rerun()

# ── Model info card ──
info = MODEL_INFO[sel]
st.info(f"{info['icon']} **{info['name']}** — 📐 {info['dim']} · {info['speed_icon']} {info['speed']}\n\n{info['desc']}")

st.divider()

# ───────────────────────── UPLOAD ─────────────────────────────────
st.markdown("**Tải ảnh lên**")
uploaded_file = st.file_uploader(
    label="",
    type=["jpg", "png", "jpeg"],
    label_visibility="collapsed"
)

# ───────────────────────── SEARCH + RESULTS ───────────────────────
if uploaded_file:
    query_img = Image.open(uploaded_file)

    col1, col_gap, col2 = st.columns([1.2, 0.15, 1])

    with col1:
        st.markdown("**Ảnh của bạn**")
        st.image(query_img, use_container_width=True)

    with col2:
        st.markdown("**Tìm kiếm**")
        search_btn = st.button(
            f"🚀  Tìm với {MODEL_INFO[sel]['name']}",
            use_container_width=True,
            key="search_main"
        )

    st.divider()

    if search_btn:
        minfo = MODEL_INFO[sel]
        with st.spinner(f"⚡ Đang tìm kiếm với {minfo['name']} ..."):
            try:
                results = search(query_img, top_k=5, model_name=sel)
            except FileNotFoundError as e:
                st.error(f"⛔ {e}")
                st.stop()

        st.markdown(f"**Kết quả — {minfo['icon']} {minfo['name']}** · {len(results)} ảnh phù hợp")

        cols = st.columns(5, gap="small")
        for i, img_path in enumerate(results):
            try:
                img = Image.open(img_path)
                with cols[i]:
                    st.image(img, use_container_width=True, caption=f"#{i+1}")
            except Exception:
                pass

else:
    st.markdown("Tải lên một ảnh JPG hoặc PNG, chọn model AI, rồi nhấn tìm kiếm.")
