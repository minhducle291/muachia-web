import streamlit as st
from sidebar import show_sidebar
from utils import hide_default_sidebar, apply_custom_styles

# Cấu hình trang Streamlit
st.set_page_config(page_title="Team mua chia Bách hóa XANH", layout="wide", initial_sidebar_state="auto", page_icon="assets/logo.png")
apply_custom_styles()
hide_default_sidebar()

# Hiển thị sidebar khi đã đăng nhập
show_sidebar()

# Tiêu đề trang
st.title("Rải số mua đều")
