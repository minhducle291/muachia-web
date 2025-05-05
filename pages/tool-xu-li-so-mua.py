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
st.title("Xử lí số mua Thuỷ sản")

st.header("📥 Chuẩn bị dữ liệu")

