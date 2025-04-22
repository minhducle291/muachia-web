# region Thư viện
import streamlit as st
from sidebar import show_sidebar
from utils import hide_default_sidebar, apply_custom_styles
import os
import pandas as pd
import numpy as np
import duckdb
from tqdm import tqdm
from datetime import datetime, timedelta
import gc
import psutil
import sys
import io
# endregion

# Cấu hình trang Streamlit
st.set_page_config(page_title="Team mua chia Bách hóa XANH", layout="wide", initial_sidebar_state="auto", page_icon="assets/logo.png")
apply_custom_styles()
hide_default_sidebar()

# Hiển thị sidebar khi đã đăng nhập
show_sidebar()

# Tiêu đề trang
st.title("Rải số mua đều")

st.header("📥 Chuẩn bị dữ liệu")


danh_muc = [
    {"ten": "Dữ liệu vòng đời", "key": "vongdoi"},
    {"ten": "Dữ liệu mua đều", "key": "muadeu"},
    {"ten": "Dữ liệu giá", "key": "gia"},
    {"ten": "Dữ liệu tồn kho", "key": "tonkho"},
]

# Header
col1, col2, col3 = st.columns([3, 5, 2])
col1.markdown("**Tên dữ liệu cần upload**")
col2.markdown("**Chọn file Excel**")
col3.markdown("**Trạng thái**")

# Tạo biến lưu trữ riêng biệt
df_vongdoi = df_muadeu = df_gia = df_tonkho = None

uploaded_data = {}

for item in danh_muc:
    with st.container():
        col1, col2, col3 = st.columns([3, 5, 2])

        with col1:
            st.markdown(f"📄 **{item['ten']}**")

        with col2:
            file = st.file_uploader(
                label="",
                type=["xlsx"],
                key=item["key"],
                label_visibility="collapsed"
            )

        with col3:
            if file:
                try:
                    df = pd.read_excel(file)
                    uploaded_data[item["key"]] = df

                    # Gán vào biến riêng theo key
                    if item["key"] == "vongdoi":
                        df_vongdoi = df
                    elif item["key"] == "muadeu":
                        df_muadeu = df
                    elif item["key"] == "gia":
                        df_gia = df
                    elif item["key"] == "tonkho":
                        df_tonkho = df

                    st.success("✅ Đã upload", icon="📤")
                except Exception as e:
                    st.error("❌ Lỗi đọc file")
            else:
                st.warning("🕗 Chờ upload", icon="⏳")
