import streamlit as st
from PIL import Image
from sidebar import show_sidebar
from utils import hide_default_sidebar, hide_sidebar_when_not_logged_in

st.set_page_config(page_title="Team mua chia Bách hóa XANH", layout="centered", page_icon="assets/logo.png")
hide_sidebar_when_not_logged_in()
hide_default_sidebar()

# Khởi tạo session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# 👉 Nếu đã đăng nhập, hiển thị sidebar custom
if st.session_state.logged_in:
    show_sidebar()

# Hàm xác thực tài khoản
def check_login(username, password):
    return username == "admin" and password == "bhx"

# Trang đăng nhập
def login_page():
    st.title("Đăng nhập")
    username = st.text_input("Tài khoản")
    password = st.text_input("Mật khẩu", type='password')
    submitted = st.button("Đăng nhập")

    if submitted:
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.page = "home"
            st.success("✅ Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("❌ Sai tài khoản hoặc mật khẩu!")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/cat.gif", use_container_width=True)

# Trang chủ
def home_page():
    st.title("Trang chủ")
    st.success("Chào mừng bạn đã đăng nhập thành công!")

#region Điều hướng login và home
if st.session_state.page == "login":
    login_page()
elif st.session_state.page == "home":
    if not st.session_state.logged_in:
        st.warning("Bạn chưa đăng nhập.")
        st.session_state.page = "login"
        st.rerun()
    else:
        home_page()
#endregion
