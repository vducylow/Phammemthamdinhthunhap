import streamlit as st

# 1. CẤU HÌNH TRANG RỘNG RÃI & GỌN GÀNG
st.set_page_config(page_title="Thẩm định vay vốn - DTI", page_icon="🏦", layout="wide")

st.title("🏦 Bảng Thẩm Định Hệ Số Nợ Trên Thu Nhập (DTI)")
st.caption("Điều chỉnh các thông số ở thanh bên trái (Sidebar) để xem kết quả phân tích tự động.")

# --- 2. THANH BÊN TRÁI (SIDEBAR): NHẬP THÔNG SỐ ---
with st.sidebar:
    st.header("⚙️ Thông số đầu vào")
    
    st.subheader("1. Khoản vay mới")
    vay_moi = st.number_input("Số tiền vay (triệu đ)", min_value=0.0, value=800.0, step=50.0)
    thoi_han_nam = st.slider("Thời hạn vay (năm)", min_value=1, max_value=30, value=5)
    lai_suat_nam = st.number_input("Lãi suất (%/năm)", min_value=0.0, value=12.0, step=0.5)
    phuong_thuc = st.radio(
        "Cách tính trả nợ:",
        ["Dư nợ giảm dần (Tháng đầu)", "Trả góp đều (PMT)"]
    )
    
    st.divider()
    st.subheader("2. Khách hàng & Gia đình")
    thu_nhap = st.number_input("Tổng thu nhập/tháng (triệu đ)", min_value=1.0, value=45.0, step=1.0)
    no_cu = st.number_input("Trả nợ cũ/tháng (triệu đ)", min_value=0.0, value=10.0, step=1.0)
    so_nguoi = st.number_input("Số người trong gia đình", min_value=1, value=3, step=1)
    phi_1_nguoi = st.number_input("Sinh hoạt phí/người (triệu đ)", min_value=0.0, value=4.0, step=0.5)

    st.divider()
    st.subheader("3. Tiêu chuẩn Ngân hàng")
    nguong_dti = st.slider("Trần DTI cho phép (%)", min_value=30, max_value=90, value=70, step=5)

# --- 3. XỬ LÝ TÍNH TOÁN ---
thang = thoi_han_nam * 12
lai_thang = (lai_suat_nam / 100) / 12

if phuong_thuc == "Dư nợ giảm dần (Tháng đầu)":
    goc = vay_moi / thang
    lai = vay_moi * lai_thang
    tra_vay_moi = goc + lai
else:
    goc = 0
    lai = 0
    tra_vay_moi = vay_moi * (lai_thang * (1 + lai_thang)**thang) / ((1 + lai_thang)**thang - 1) if lai_thang > 0 else vay_moi / thang

sinh_hoat_phi = so_nguoi * phi_1_nguoi
tong_no = no_cu + tra_vay_moi
thu_nhap_con_lai = thu_nhap - sinh_hoat_phi
so_du_cuoi_cung = thu_nhap_con_lai - tong_no

dti_tong = (tong_no / thu_nhap) * 100
dti_rong = (tong_no / thu_nhap_con_lai) * 100 if thu_nhap_con_lai > 0 else 100.0

# --- 4. MÀN HÌNH CHÍNH: HIỂN THỊ KẾT QUẢ DỄ NHÌN ---

# 4.1. Khối Kết luận nổi bật ngay đầu trang
if so_du_cuoi_cung < 0:
    st.error(f"### ❌ TỪ CHỐI CHO VAY\n**Lý do:** Khách hàng bị âm dòng tiền (**{so_du_cuoi_cung:,.2f} triệu/tháng**). Thu nhập sau sinh hoạt không đủ trả nợ.")
elif dti_tong <= nguong_dti:
    st.success(f"### ✅ ĐỦ ĐIỀU KIỆN CHO VAY\n**Đánh giá:** Hệ số DTI đạt **{dti_tong:.1f}%** (nằm trong ngưỡng an toàn $\le$ {nguong_dti}%). Khách hàng vẫn dư **{so_du_cuoi_cung:,.2f} triệu/tháng** sau khi trả mọi chi phí.")
else:
    st.warning(f"### ⚠️ CẦN XEM XÉT LẠI (VƯỢT TRẦN DTI)\n**Đánh giá:** Khách hàng vẫn dư **{so_du_cuoi_cung:,.2f} triệu/tháng**, nhưng DTI hiện tại là **{dti_tong:.1f}%** (vượt quy định {nguong_dti}% của ngân hàng).")

st.write("") # Tạo khoảng trống

# 4.2. Các thẻ chỉ số quan trọng (Đặt trong khung viền)
st.subheader("📊 Tóm tắt dòng tiền hàng tháng")
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.metric("1. Tổng thu nhập", f"{thu_nhap:,.1f} trđ")
with col2:
    with st.container(border=True):
        st.metric("2. Sinh hoạt phí", f"{sinh_hoat_phi:,.1f} trđ", f"{so_nguoi} người", delta_color="off")
with col3:
    with st.container(border=True):
        st.metric("3. Tổng nợ phải trả", f"{tong_no:,.2f} trđ", f"Vay mới: {tra_vay_moi:,.2f} trđ", delta_color="off")
with col4:
    with st.container(border=True):
        st.metric("4. Tiền dư cuối tháng", f"{so_du_cuoi_cung:,.2f} trđ", "An toàn" if so_du_cuoi_cung >= 0 else "Thiếu hụt", delta_color="normal" if so_du_cuoi_cung >= 0 else "inverse")

st.write("")

# 4.3. Thanh đo lường DTI & Bảng chi tiết (Chia 2 cột)
left_col, right_col = st.columns([1.2, 1])

with left_col:
    with st.container(border=True):
        st.markdown("#### 🎯 Đo lường Hệ số DTI")
        
        # Thanh tiến trình DTI trên tổng thu nhập
        st.write(f"**DTI trên Tổng thu nhập:** `{dti_tong:.2f}%` *(Ngưỡng cho phép: {nguong_dti}%)*")
        st.progress(min(int(dti_tong), 100))
        
        st.write("")
        
        # Thanh tiến trình DTI trên thu nhập sau sinh hoạt
        st.write(f"**DTI trên Thu nhập sau sinh hoạt:** `{dti_rong:.2f}%` *(Tỷ lệ nợ / Tiền còn lại)*")
        st.progress(min(int(dti_rong), 100))

with right_col:
    with st.container(border=True):
        st.markdown("#### 🧾 Chi tiết nghĩa vụ nợ/tháng")
        st.table({
            "Khoản mục": [
                "Trả nợ vay cũ",
                "Gốc vay mới",
                "Lãi vay mới (tháng đầu)",
                "Tổng trả vay mới",
                "TỔNG NGHĨA VỤ NỢ"
            ],
            "Số tiền (Triệu đồng)": [
                f"{no_cu:,.2f}",
                f"{goc:,.2f}" if phuong_thuc == "Dư nợ giảm dần (Tháng đầu)" else "Tính gộp (PMT)",
                f"{lai:,.2f}" if phuong_thuc == "Dư nợ giảm dần (Tháng đầu)" else "Tính gộp (PMT)",
                f"{tra_vay_moi:,.2f}",
                f"{tong_no:,.2f}"
            ]
        })
