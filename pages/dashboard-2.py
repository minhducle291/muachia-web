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
st.title("Dashboard ngành hàng thịt cá")

# Nhúng Power BI report thông qua iframe
iframe_code = """
<iframe title="Báo cáo nhóm đạm" width="100%" height="580" 
src="https://app.powerbi.com/view?r=eyJrIjoiOGQyOTlkMDctZTE5OC00ZmM1LWI1YTMtMWY4ZTZlMmQ4OGZlIiwidCI6ImZmMDM5ZTg5LTBjMDItNDNhYi05YmI1LTFlMDJlODdkZDM4YyIsImMiOjEwfQ%3D%3D" 
frameborder="0" allowFullScreen="true"></iframe>
"""

# Hiển thị iframe trong ứng dụng
st.markdown(iframe_code, unsafe_allow_html=True)
