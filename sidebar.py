import streamlit as st

def show_sidebar():
    if not st.session_state.get("logged_in", True): #Trả về Fale nếu muốn người dùng phải đăng nhập
        # 👉 Chỉ khi chưa đăng nhập mới tạo biến `hide` và áp dụng
        hide = """
            <style>
                [data-testid="stSidebar"] {display: none;}
                [data-testid="collapsedControl"] {display: none;}
            </style>
        """
        st.markdown(hide, unsafe_allow_html=True)
        st.warning("🔒 Bạn cần đăng nhập để xem nội dung.")
        st.stop()  # ⛔ Dừng tại đây

    # ✅ Phần này chỉ chạy khi đã đăng nhập — KHÔNG dùng biến `hide` ở đây!
    # st.sidebar.subheader("Thông tin")
    # st.sidebar.page_link("pages/thông tin 1.py", label="Bảng nhiệm vụ")
    # st.sidebar.page_link("pages/thông tin 2.py", label="Tổng hợp tài liệu")

    # st.sidebar.markdown("---")


    st.sidebar.subheader("Báo cáo")
    st.sidebar.page_link("pages/dashboard-1.py", label="Báo cáo tổng hợp Fresh")
    st.sidebar.page_link("pages/dashboard-2.py", label="Báo cáo nhóm đạm")
    st.sidebar.page_link("pages/dashboard-3.py", label="Báo cáo thử nghiệm")

    st.sidebar.markdown("---")

    st.sidebar.subheader("Công cụ")
    st.sidebar.page_link("pages/tool-1.py", label="Kiểm tra nhu cầu siêu thị khai trương")
    st.sidebar.page_link("pages/tool-rai-so.py", label="Rải số mua đều")
    st.sidebar.page_link("pages/tool-xu-li-so-mua.py", label="Xử lí số mua Thuỷ sản")


    st.sidebar.markdown("---")