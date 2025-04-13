import streamlit as st
import pandas as pd
from sidebar import show_sidebar
from utils import hide_default_sidebar, apply_custom_styles
from io import BytesIO
import openpyxl

# Cấu hình trang Streamlit
st.set_page_config(page_title="Team mua chia Bách hóa XANH", layout="wide", initial_sidebar_state="auto", page_icon="assets/logo.png")
apply_custom_styles()
hide_default_sidebar()

# Hiển thị sidebar khi đã đăng nhập
show_sidebar()

# Tiêu đề trang
st.title("Kiểm tra nhu cầu siêu thị khai trương")

# Upload file
uploaded_file = st.file_uploader("Chọn file Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_list_opening_store = pd.read_excel(uploaded_file)
        st.success("✅ Đã đọc file thành công!")
        st.dataframe(df_list_opening_store)

        #region Xử lí file theo danh sách người dùng upload
        #df = pd.read_parquet('/tools/Kiểm tra nhu cầu siêu thị khai trương/data.parquet')
        df = pd.read_parquet('tools/Kiểm tra nhu cầu siêu thị khai trương/data.parquet')
        df_list_opening_store = pd.read_excel('tools/Kiểm tra nhu cầu siêu thị khai trương/Khai báo/list_opening_store.xlsx')
        df = pd.merge(df, df_list_opening_store, how = 'left', on = 'Mã siêu thị')
        df = df[~df['Ngày khai trương'].isna()]
        df_pivot = df.pivot_table(index=['Ngày khai trương','Ngày nhận hàng','Mã siêu thị','Tên siêu thị','Ngành hàng','Nhóm hàng 2'],
                                    values=['Mã sản phẩm','Số lượng cần mua','Notify'],
                                    aggfunc={'Mã sản phẩm': 'count', 'Số lượng cần mua': 'sum', 'Notify':'sum'}).reset_index()
        df_pivot['Số lượng cần mua'] = round(df_pivot['Số lượng cần mua'], 1)
        df_pivot.sort_values(by=['Ngày khai trương','Mã siêu thị','Ngành hàng','Mã sản phẩm','Nhóm hàng 2','Ngày nhận hàng'],
                            ascending=[True,True,True,False,True,True], inplace=True)
        df_pivot.rename(columns={'Mã sản phẩm':'Số lượng SKU', 'Notify':'Số SKU Notify', 'Số lượng cần mua':'Tổng nhu cầu', 'Notify':'Tổng SKU Notify'}, inplace=True)

        df_pivot = df_pivot.sort_values(by=['Ngày khai trương','Mã siêu thị','Ngành hàng','Nhóm hàng 2','Ngày nhận hàng'],
                                        ascending=[True,True,True,True,True])
        df_dsst = pd.read_excel('tools/Kiểm tra nhu cầu siêu thị khai trương/Khai báo/Danh sách siêu thị.xlsx', usecols=['Mã siêu thị','Miền'])
        df_pivot = pd.merge(df_pivot, df_dsst[['Mã siêu thị','Miền']], how = 'left', on = 'Mã siêu thị')
        df_pivot['Miền'] = df_pivot['Miền'].fillna('Chưa cập nhật')
        df_pivot['Thứ (Khai trương)'] = pd.to_datetime(df_pivot['Ngày khai trương']).dt.day_name()
        df_pivot = df_pivot[['Ngày khai trương','Thứ (Khai trương)','Ngày nhận hàng','Mã siêu thị','Tên siêu thị','Miền','Ngành hàng','Nhóm hàng 2','Số lượng SKU','Tổng nhu cầu','Tổng SKU Notify']]
        df_pivot = df_pivot.reset_index(drop=True)
        #endregion

        # region Xử lý tiếp df_pivot một số chi tiết
        # Chuyển đổi định dạng cột
        df_pivot["Ngày khai trương"] = pd.to_datetime(df_pivot["Ngày khai trương"]).dt.date
        df_pivot["Ngày nhận hàng"] = df_pivot["Ngày nhận hàng"].dt.date
        df_pivot["Mã siêu thị"] = df_pivot["Mã siêu thị"].astype(str)
        df_pivot['Tổng nhu cầu'] = round(df_pivot['Tổng nhu cầu'], 1).astype(int)
        # Đổi tên cột nếu cần để đồng bộ với bộ lọc
        df_pivot.columns = ['Ngày khai trương', 'Thứ (Khai trương)','Ngày nhận hàng', 'Mã siêu thị', 'Tên siêu thị', 'Miền', 'Ngành hàng',
                    'Nhóm hàng 2', 'Số lượng SKU', 'Tổng nhu cầu','SL Notify']
        # endregion

        # Hiển thị bảng dữ liệu đã lọc với chiều dài tối đa
        st.header("Đây dzồi!")
        st.dataframe(df_pivot, use_container_width=True, height=530)

        # region Button tải xuống
        # Thêm nút tải xuống
        @st.cache_data
        def convert_df_to_excel(df_pivot):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            output.seek(0)  # Đưa con trỏ về đầu file
            return output.getvalue()

        # Gọi hàm để tạo file Excel
        excel_file = convert_df_to_excel(df_pivot)

        # Tải xuống file Excel
        st.download_button(
            label="⬇️ Tải xuống dữ liệu",
            data=excel_file,
            file_name="Dữ liệu nhu cầu siêu thị khai trương.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # endregion





    except Exception as e:
        st.error(f"❌ Lỗi khi đọc file: {e}")

