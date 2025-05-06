# region Thư viện
import streamlit as st
from sidebar import show_sidebar
from utils import hide_default_sidebar, apply_custom_styles
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gc
import psutil
import sys
import io
import json
import openpyxl
from io import BytesIO
# endregion

# region Khai báo hàm và tham số
def mround(n, quycach, rate=0.5):
    phan_nguyen = n // quycach
    phan_du = n % quycach
    if (phan_du >= quycach * rate):
        number = phan_nguyen * quycach  + quycach
    else:
        number = phan_nguyen * quycach
    return number

# Tham số
rate_nhap = 0.8
rate_da_dang = 0.5
rate_chu_luc = 0.5
# endregion

# region Cấu hình Streamlit
# Cấu hình trang Streamlit
st.set_page_config(page_title="Team mua chia Bách hóa XANH", layout="wide", initial_sidebar_state="auto", page_icon="assets/logo.png")
apply_custom_styles()
hide_default_sidebar()

# Hiển thị sidebar khi đã đăng nhập
show_sidebar()
# endregion

# Tiêu đề trang
st.title("Cook số thuỷ sản 🐟")

st.header("Input")

# region Tải template
with open("tools/Xử lí số mua thuỷ sản/local data/khai báo tăng giảm.xlsx", "rb") as f:
    file_bytes = f.read()
st.download_button("Tải template", data=file_bytes, file_name="Template khai báo tăng giảm.xlsx")
# endregion

# region upload file khai báo
uploaded_file = st.file_uploader("Chọn file Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_khaibao = pd.read_excel(uploaded_file)
        #st.success("✅ Đã đọc file thành công!")

    except Exception as e:
        st.error(f"❌ Lỗi khi đọc file: {e}")
# endregion

# region Ngày bắt đầu và kết thúc
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Ngày bắt đầu", value=datetime.today())
with col2:
    end_date = st.date_input("Ngày kết thúc", value=datetime.today())

# Chuyển định dạng sang yyMMdd
from_date = start_date.strftime('%Y%m%d')
to_date = end_date.strftime('%Y%m%d')
# endregion

def xu_ly_du_lieu(df_khaibao):
    # region Đọc file đã xử lí từ local
    st.info(f"Đang xử lý...chờ chút nhé!")
    df_final = pd.read_parquet('tools/Xử lí số mua thuỷ sản/local data/data-detail-735-827-951.parquet')
    df_final['Ngày'] = pd.to_datetime(df_final['Ngày'], format='%Y%m%d')

    df_final = df_final[(df_final['Ngày'] >= from_date) & (df_final['Ngày'] <= to_date)]
    df_808 = pd.read_parquet('tools/Xử lí số mua thuỷ sản/local data/data-quycachmua-tonmin.parquet')
    df_lichvehang = pd.read_parquet('tools/Xử lí số mua thuỷ sản/local data/data-lichvehang.parquet')
    df_muadeu = pd.read_parquet('tools/Xử lí số mua thuỷ sản/local data/data-muadeu.parquet')
    # endregion

    # region Tính tỉ lệ NG/Nhập
    df_nhap = df_final.copy()
    df_nhap = pd.pivot_table(df_nhap, index=['Mã siêu thị','Mã sản phẩm gộp'],
                            values=['SL PO','SL nhập','SL bán','Nhập (KG)','Nguyên giá (KG)'], aggfunc='sum').reset_index()
    df_nhap['Tỉ lệ NG/Nhập'] = df_nhap['Nguyên giá (KG)'] / df_nhap['Nhập (KG)']
    # Chặn giá trị cột 'Tỉ lệ NG/Nhập' từ 0 đến 1
    df_nhap['Tỉ lệ NG/Nhập'] = df_nhap['Tỉ lệ NG/Nhập'].clip(lower=0, upper=1)
    df_nhap.rename(columns={'Nguyên giá (KG)':'Tổng NG (KG)', 'Nhập (KG)': 'Tổng nhập (KG)', 'Mã sản phẩm gộp': 'Mã sản phẩm'}, inplace=True)
    # endregion

    # region Tính sức bán, Tỉ lệ bán NG/Nhập
    df_detail = df_final.copy()
    df_detail = df_detail[df_detail['là ngày tính sức bán'] == 'yes']
    df_detail['Nguyên giá (KG)'] = df_detail['Nguyên giá (KG)'].fillna(0, inplace=True)

    # Sum số bán lại theo tổng ngày trước
    df_detail_2 = pd.pivot_table(df_detail, index=['Ngày','Mã siêu thị','Gom code','Mã sản phẩm gộp','Tên sản phẩm gộp'],
                                        values='Nguyên giá (KG)', aggfunc='sum').reset_index()

    # Định nghĩa hàm count distinct
    def count_distinct(x):
        return len(x.unique())

    df_pivot = pd.pivot_table(df_detail_2, index=['Mã siêu thị','Gom code','Mã sản phẩm gộp','Tên sản phẩm gộp'],
                            values=['Nguyên giá (KG)', 'Ngày'],
                            aggfunc={
                                'Nguyên giá (KG)': 'mean',
                                'Ngày': count_distinct
                            }).reset_index()
    df_pivot.rename(columns={'Mã sản phẩm gộp':'Mã sản phẩm','Tên sản phẩm gộp':'Tên sản phẩm','Ngày':'Số ngày tính SB'}, inplace=True)
    df_quydoikg = pd.read_excel('external data/Danh sách sản phẩm.xlsx', usecols=['Mã sản phẩm','Trọng lượng (kg)'])
    df_quydoikg['Trọng lượng (kg)'] = df_quydoikg['Trọng lượng (kg)'].replace(0, 1)
    df_pivot = pd.merge(df_pivot, df_quydoikg, on='Mã sản phẩm', how='left')
    df_pivot['Sức bán chuẩn'] = df_pivot['Nguyên giá (KG)'] / df_pivot['Trọng lượng (kg)']
    df_pivot.rename(columns={'Nguyên giá (KG)': 'Sức bán (KG)'}, inplace=True)
    df_pivot = pd.merge(df_pivot, df_nhap, on=['Mã siêu thị','Mã sản phẩm'], how='left')
    # endregion

    # region Thêm thông tin số ngày có lịch về trong tuần
    df_lichvehang = df_lichvehang[['Mã siêu thị','Mã sản phẩm','Lịch về hàng']]
    df_lichvehang['Số ngày có lịch'] = df_lichvehang['Lịch về hàng'].apply(lambda x: len(str(x).split(',')))
    df_pivot = pd.merge(df_pivot, df_lichvehang[['Mã siêu thị','Mã sản phẩm','Số ngày có lịch']], on=['Mã siêu thị','Mã sản phẩm'], how='left')
    # endregion

    # region Map dữ liệu quy cách, phân loại chủ lực, tính tồn kho qua đêm vào bảng tính số mua
    df_pivot = pd.merge(df_pivot, df_808[['Mã siêu thị','Mã sản phẩm','Quy cách mua']], on=['Mã siêu thị','Mã sản phẩm'], how='left')
    df_chuluc = pd.read_excel('external data/Danh sách sản phẩm chủ lực.xlsx', sheet_name='Final', usecols=['Nhóm sản phẩm','Phân loại tổng'])
    
    df_pivot = pd.merge(df_pivot, df_chuluc, left_on='Gom code', right_on='Nhóm sản phẩm', how='left')
    df_pivot.drop(columns='Nhóm sản phẩm', inplace=True)
    df_tinhtonquadem = pd.read_excel('external data/Danh sách sản phẩm.xlsx', usecols=['Mã sản phẩm','Tính tồn kho qua đêm'])
    df_pivot = pd.merge(df_pivot, df_tinhtonquadem, on='Mã sản phẩm', how='left')
    # endregion

    # region Tiền xử lí trước khi tính số mua
    df_pivot['Phân loại tổng'].fillna('Đa dạng', inplace=True)
    df_pivot.dropna(subset='Quy cách mua', inplace=True)
    df_pivot = df_pivot[df_pivot['Quy cách mua'] != 0]
    # endregion


    def Tinh_so_luong_tuan_thuysan(row):
        # Khởi tạo từ điển để lưu các bước và hệ số
        steps = {
            "input": {},
            "intermediate": {},
            "output": {}
        }
        
        # Lưu giá trị đầu vào
        steps["input"]["sum_nhap"] = row['SL nhập']
        steps["input"]["sum_ban"] = row['SL bán']
        steps["input"]["rate_NG_nhap"] = row['Tỉ lệ NG/Nhập']
        steps["input"]["suc_ban"] = row['Sức bán chuẩn']
        steps["input"]["quy_cach_mua"] = row['Quy cách mua']
        steps["input"]["tinh_ton_qua_dem"] = row['Tính tồn kho qua đêm']
        steps["input"]["so_ngay_co_lich"] = row['Số ngày có lịch']
        steps["input"]["phan_loai_tong"] = row['Phân loại tổng']
        
        # Logic gốc của hàm
        sum_nhap = row['SL nhập']
        sum_ban = row['SL bán']
        rate_NG_nhap = row['Tỉ lệ NG/Nhập']
        suc_ban = row['Sức bán chuẩn']
        quy_cach_mua = row['Quy cách mua']
        tinh_ton_qua_dem = row['Tính tồn kho qua đêm']
        so_ngay_co_lich = row['Số ngày có lịch']
        try:
            ti_le_ban = min(sum_ban / sum_nhap, 1)
        except ZeroDivisionError:
            ti_le_ban = 0
        steps["intermediate"]["ti_le_ban"] = ti_le_ban

        # region CT anh Nguyên
        if rate_NG_nhap < rate_da_dang or rate_NG_nhap >= 0.75:
            rate_mua_hang = rate_da_dang
        if rate_NG_nhap >= rate_da_dang and rate_NG_nhap < 0.75:
            rate_mua_hang = rate_NG_nhap
        # endregion
        steps["intermediate"]["rate_mua_hang"] = rate_mua_hang

        if row['Phân loại tổng'] == 'Đa dạng':
            if tinh_ton_qua_dem == 1:
                so_ngay_co_lich = 7
                steps["intermediate"]["so_ngay_co_lich_adjusted"] = so_ngay_co_lich
                steps["intermediate"]["tinh_ton_qua_dem_note"] = "Đặt so_ngay_co_lich thành 7 vì tinh_ton_qua_dem = 1"
            so_luong_tuan = mround(suc_ban / rate_mua_hang, quy_cach_mua, 0.4) * so_ngay_co_lich
            steps["intermediate"]["mround_result"] = mround(suc_ban / rate_mua_hang, quy_cach_mua, 0.4)
            steps["intermediate"]["condition"] = "Phân loại tổng = Đa dạng"
        else:
            if tinh_ton_qua_dem == 0:
                mround_result = mround(suc_ban / rate_mua_hang, quy_cach_mua, 0.4)
                so_luong_tuan = max(mround_result, quy_cach_mua) * so_ngay_co_lich
                steps["intermediate"]["mround_result"] = mround_result
                steps["intermediate"]["max_result"] = max(mround_result, quy_cach_mua)
                steps["intermediate"]["tinh_ton_qua_dem_note"] = "Không có tồn kho qua đêm"
            else: # Sản phẩm có tồn qua đêm
                mround_result = mround(suc_ban / rate_mua_hang * so_ngay_co_lich, quy_cach_mua, 0.4)
                so_luong_tuan = max(mround_result, so_ngay_co_lich * quy_cach_mua)
                steps["intermediate"]["mround_result"] = mround_result
                steps["intermediate"]["max_result"] = max(mround_result, so_ngay_co_lich * quy_cach_mua)
                steps["intermediate"]["tinh_ton_qua_dem_note"] = "Có tồn kho qua đêm"
            steps["intermediate"]["condition"] = "Phân loại tổng != Đa dạng"
        
        steps["output"]["so_luong_tuan"] = so_luong_tuan
        
        # Chuyển steps thành chuỗi JSON
        json_data = json.dumps(steps, ensure_ascii=False)
        
        return so_luong_tuan, json_data
    # Áp dụng hàm lên DataFrame
    results = df_pivot.apply(Tinh_so_luong_tuan_thuysan, axis=1, result_type='expand')
    df_pivot['Số lượng tuần'] = results[0]
    df_pivot['jsondata'] = results[1]

    # region Thêm thông tin mua đều hiện tại
    df_muadeu['Tổng tuần hiện tại'] = df_muadeu[['T2','T3','T4','T5','T6','T7','CN']].sum(axis=1)
    df_muadeu = df_muadeu[['Mã siêu thị','Mã sản phẩm','Tổng tuần hiện tại']]
    df_pivot = pd.merge(df_pivot, df_muadeu, on=['Mã siêu thị','Mã sản phẩm'], how='left')
    df_pivot['Tổng tuần hiện tại'].fillna(df_pivot['Số lượng tuần'], inplace=True)
    # endregion

    # region Xử lí thông tin người dùng khai báo
    df_khaibao['Mã sản phẩm'] = df_khaibao['Mã sản phẩm'].fillna(-1).astype('int64')
    df_khaibao_single = df_khaibao[df_khaibao['Tên sản phẩm'] != 'all']

    # region xử lí cho khai báo dạng multi
    df_danhmuc_real = df_pivot[['Mã siêu thị','Mã sản phẩm','Tên sản phẩm']]
    df_khaibao_multi = df_khaibao[df_khaibao['Tên sản phẩm'] == 'all'].drop(columns=['Mã sản phẩm','Tên sản phẩm'])
    df_khaibao_multi = pd.merge(df_khaibao_multi,
                                df_danhmuc_real[df_danhmuc_real['Mã siêu thị'].isin(df_khaibao_multi['Mã siêu thị'].unique())],
                                on='Mã siêu thị', how='outer')
    # endregion

    df_khaibao = pd.concat([df_khaibao_single, df_khaibao_multi], ignore_index=True)
    df_khaibao = pd.merge(df_khaibao,
                        df_pivot[['Mã siêu thị','Mã sản phẩm','Quy cách mua','Số ngày tính SB','Số lượng tuần','jsondata','Số ngày có lịch','Tổng tuần hiện tại']],
                        on=['Mã siêu thị','Mã sản phẩm'], how='left')

    def Xu_li_so_mua(row):
        if row['Phân loại'] == 'Sức bán':
            return row['Số lượng tuần']
        if row['Phân loại'] == 'Mua min':
            return row['Quy cách mua'] * row['Số ngày có lịch']
        if row['Phân loại'] == 'Tăng/Giảm số':
            return max(
                mround(row['Tổng tuần hiện tại'] * row['Hệ số điều chỉnh'], row['Quy cách mua']),
                row['Quy cách mua']
            )
        
    df_khaibao['Result'] = df_khaibao.apply(Xu_li_so_mua, axis=1)
    df_khaibao.loc[df_khaibao['Phân loại'] != 'Sức bán', ['Số ngày tính SB', 'Số lượng tuần', 'jsondata']] = np.nan
    return df_khaibao
    # endregion


# Chỉ hiển thị nút nếu đã có file
if uploaded_file is not None:
    if st.button("Cook now!"):
        df = xu_ly_du_lieu(df_khaibao)
        st.dataframe(df, use_container_width=True, height=400)

        # region Button tải xuống
        # Thêm nút tải xuống
        @st.cache_data
        def convert_df_to_excel(df_pivot):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_pivot.to_excel(writer, index=False, sheet_name='Data')
            output.seek(0)  # Đưa con trỏ về đầu file
            return output.getvalue()

        # Gọi hàm để tạo file Excel
        excel_file = convert_df_to_excel(df)

        # Tải xuống file Excel
        st.download_button(
            label="⬇️ Tải xuống dữ liệu",
            data=excel_file,
            file_name="Lẩu hải sản.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # endregion