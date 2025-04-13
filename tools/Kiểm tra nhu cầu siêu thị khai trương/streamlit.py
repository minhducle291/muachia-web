# region Thư viện và Default setting
import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime, timedelta
import requests

def wide_space_default():
    st.set_page_config(layout='wide')
wide_space_default()
# endregion

# region Đọc dữ liệu cần đẩy lên Web
# Đọc dữ liệu từ file Excel
report_date = pd.to_datetime("today").strftime("%Y-%m-%d")
file_path = r'D:/TASK MUA CHIA/KIỂM TRA NHU CẦU SIÊU THỊ KHAI TRƯƠNG/data/data-'+ str(report_date) + '.xlsx'
df = pd.read_excel(file_path)

# Chuyển đổi định dạng cột\
df["Ngày khai trương"] = pd.to_datetime(df["Ngày khai trương"]).dt.date
df["Ngày nhận hàng"] = df["Ngày nhận hàng"].dt.date
df["Mã siêu thị"] = df["Mã siêu thị"].astype(str)
df['Tổng nhu cầu'] = round(df['Tổng nhu cầu'], 1).astype(int)
# Đổi tên cột nếu cần để đồng bộ với bộ lọc
df.columns = ['Ngày khai trương', 'Thứ (Khai trương)','Ngày nhận hàng', 'Mã siêu thị', 'Tên siêu thị', 'Miền', 'Ngành hàng',
              'Nhóm hàng 2', 'Số lượng SKU', 'Tổng nhu cầu','SL Notify']
# endregion

# Tiêu đề ứng dụng
st.title("🔎 Kiểm tra nhu cầu siêu thị khai trương")

# region Thông tin thời gian cập nhật GitHub
REPO_OWNER = "minhducle291"
REPO_NAME = "muachia-app"
FILE_PATH = "data-2025-04-06.xlsx"

def get_last_commit_time(owner, repo, file_path):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={file_path}&page=1&per_page=1"
    response = requests.get(url)
    if response.status_code == 200:
        commit_data = response.json()[0]
        commit_time = commit_data["commit"]["committer"]["date"]  # Dạng: 2025-04-04T09:13:53Z
        return commit_time
    else:
        return None

# Lấy ngày cập nhật gần nhất
last_modified_time = get_last_commit_time(REPO_OWNER, REPO_NAME, FILE_PATH)

if last_modified_time:
    # Parse string thời gian → datetime UTC
    utc_time = datetime.strptime(last_modified_time, "%Y-%m-%dT%H:%M:%SZ")
    
    # Chuyển sang giờ Việt Nam (UTC+7)
    vn_time = utc_time + timedelta(hours=7)

    # Hiển thị trên web
    st.markdown(
        f"<span style='font-size: 14px; font-style: italic;'>📅 Dữ liệu cập nhật lần cuối: {vn_time.strftime('%H:%M:%S %d/%m/%Y')} (giờ VN)</span>",
        unsafe_allow_html=True
    )
else:
    st.warning("Không thể lấy thời gian cập nhật file từ GitHub.")
# endregion

# region Sidebar - Bộ lọc

# Bộ lọc
st.sidebar.header("Bộ Lọc")

# Lọc theo Ngày khai trương
ngay_khai_truong = st.sidebar.date_input("Ngày khai trương", None)
if ngay_khai_truong:
    df = df[df['Ngày khai trương'] == pd.to_datetime(ngay_khai_truong).date()]

# Lọc theo Mã siêu thị (có tìm kiếm)
ma_sieu_options = df['Mã siêu thị'].unique().tolist()
ma_sieu = st.sidebar.selectbox("Mã Siêu Thị", ["Tất cả"] + sorted(ma_sieu_options), index=0)
if ma_sieu != "Tất cả":
    df = df[df['Mã siêu thị'] == ma_sieu]

# Lọc theo Mã siêu thị (có tìm kiếm)
mien_options = df['Miền'].unique().tolist()
mien = st.sidebar.selectbox("Miền", ["Tất cả"] + sorted(mien_options), index=0)
if mien != "Tất cả":
    df = df[df['Miền'] == mien]

# Lọc theo Ngành hàng (có tìm kiếm)
nganh_hang_options = df["Ngành hàng"].dropna().unique().tolist()
nganh_hang = st.sidebar.selectbox("Ngành Hàng", ["Tất cả"] + sorted(nganh_hang_options), index=0)
if nganh_hang != "Tất cả":
    df = df[df["Ngành hàng"] == nganh_hang]

# Lọc theo Nhóm hàng 2 (có tìm kiếm)
nhom_hang_options = df["Nhóm hàng 2"].dropna().unique().tolist()
nhom_hang = st.sidebar.selectbox("Nhóm Hàng 2", ["Tất cả"] + sorted(nhom_hang_options), index=0)
if nhom_hang != "Tất cả":
    df = df[df["Nhóm hàng 2"] == nhom_hang]
# endregion

# Hiển thị bảng dữ liệu đã lọc với chiều dài tối đa
st.dataframe(df, use_container_width=True, height=530)

# region Button tải xuống
# Thêm nút tải xuống
@st.cache_data
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)  # Đưa con trỏ về đầu file
    return output.getvalue()

# Gọi hàm để tạo file Excel
excel_file = convert_df_to_excel(df)

# Tải xuống file Excel
st.download_button(
    label="⬇️ Tải xuống dữ liệu",
    data=excel_file,
    file_name="danh_sach_sieu_thi_loc.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
# endregion
