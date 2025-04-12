import streamlit as st
from PIL import Image
import time
from sidebar import show_sidebar
from utils import hide_default_sidebar

st.set_page_config(page_title="Team mua chia Bách hóa XANH", layout="centered", initial_sidebar_state="auto")
hide_default_sidebar()

show_sidebar()
st.title("Trang chủ")
st.success("Chào mừng bạn đã đăng nhập thành công!")