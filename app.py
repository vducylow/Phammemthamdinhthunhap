import streamlit as st

# Cấu hình trang
st.set_page_config(page_title="Tính chỉ số DTI", page_icon="🏦", layout="centered")

st.title("🏦 Công cụ tính Hệ số Nợ trên Thu nhập (DTI)")
st.write("Nhập các thông số bên dưới để kiểm tra khả năng vay vốn của khách hàng.")

# --- PHẦN 1: NHẬP THÔNG SỐ ĐẦU VÀO ---
st.subheader("1. Thông số đầu vào")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Thông tin khoản vay mới**")
    vay_moi = st.number_input("Số tiền vay (triệu đồng)", min_value=0.0, value=800.0, step=10.0)
    thoi_han_nam = st.number_input("Thời hạn vay (năm)", min_value=1, value=5, step=1)
    lai_suat_nam = st.number_input("Lãi suất (%/năm)", min_value=0.0, value=12.0, step=0.5)
    phuong_thuc = st.selectbox(
        "Phương thức trả nợ",
        ["Dư nợ giảm dần (Xét tháng đầu cao nhất)", "Trả góp đều hàng tháng (Niên kim cố định - PMT)"]
    )

with col2:
    st.markdown("**Tài chính & Gia đình khách hàng**")
    thu_nhap = st.number_input("Thu nhập hàng tháng (triệu đồng)", min_value=1.0, value=45.0, step=1.0)
    no_cu_thang = st.number_input("Trả nợ khoản vay cũ/tháng (triệu đồng)", min_value=0.0, value=10.0, step=1.0)
    so_nguoi = st.number_input("Tổng số người trong gia đình", min_value=1, value=3, step=1, help="Bao gồm khách hàng và người phụ thuộc (VD: Khách hàng + 1 vợ + 1 con = 3)")
    chi_phi_1_nguoi = st.number_input("Chi phí sinh hoạt / người / tháng (triệu đồng)", min_value=0.0, value=4.0, step=0.5)

# Tùy chỉnh ngưỡng phê duyệt của ngân hàng
st.markdown("**Tiêu chuẩn xét duyệt của Ngân hàng**")
nguong_dti_cho_phep = st.slider("Ngưỡng DTI tối đa cho phép (%)", min_value=30, max_value=90, value=70, step=5)

# --- PHẦN 2: XỬ LÝ TÍNH TOÁN ---
thoi_han_thang = thoi_han_nam * 12
lai_suat_thang = (lai_suat_nam / 100) / 12

# Tính tiền trả khoản vay mới hàng tháng
if phuong_thuc == "Dư nợ giảm dần (Xét tháng đầu cao nhất)":
    goc_hang_thang = vay_moi / thoi_han_thang
    lai_thang_dau = vay_moi * lai_suat_thang
    tra_vay_moi_thang = goc_hang_thang + lai_thang_dau
else:
    # Công thức PMT
    if lai_suat_thang > 0:
        tra_vay_moi_thang = vay_moi * (lai_suat_thang * (1 + lai_suat_thang)**thoi_han_thang) / ((1 + lai_suat_thang)**thoi_han_thang - 1)
    else:
        tra_vay_moi_thang = vay_moi / thoi_han_thang

# Tính toán tổng hợp
chi_phi_sinh_hoat = so_nguoi * chi_phi_1_nguoi
tong_tra_no = no_cu_thang + tra_vay_moi_thang
thu_nhap_con_lai = thu_nhap - chi_phi_sinh_hoat

# Tính chỉ số DTI (%)
dti_tong_thu_nhap = (tong_tra_no / thu_nhap) * 100
dti_thu_nhap_rong = (tong_tra_no / thu_nhap_con_lai) * 100 if thu_nhap_con_lai > 0 else 999.99

# --- PHẦN 3: HIỂN THỊ KẾT QUẢ ---
st.divider()
st.subheader("2. Kết quả tính toán")

m1, m2, m3 = st.columns(3)
m1.metric("Trả vay mới/tháng", f"{tra_vay_moi_thang:,.2f} trđ")
m2.metric("Tổng nợ phải trả/tháng", f"{tong_tra_no:,.2f} trđ")
m3.metric("Thu nhập sau sinh hoạt", f"{thu_nhap_con_lai:,.2f} trđ", delta=f"-{chi_phi_sinh_hoat:,.1f} trđ sinh hoạt", delta_color="off")

c1, c2 = st.columns(2)
c1.info(f"📊 **DTI (Trên tổng thu nhập):** `{dti_tong_thu_nhap:.2f}%`\n\n*(Công thức: Tổng nợ / Tổng thu nhập)*")
c2.info(f"📉 **DTI (Trên thu nhập ròng):** `{dti_thu_nhap_rong:.2f}%`\n\n*(Công thức: Tổng nợ / Thu nhập sau sinh hoạt)*")

# --- PHẦN 4: ĐƯA RA KẾT LUẬN ---
st.subheader("3. Kết luận xét duyệt")

du_tien_sinh_hoat = tong_tra_no <= thu_nhap_con_lai
dat_chuan_dti = dti_tong_thu_nhap <= nguong_dti_cho_phep

if not du_tien_sinh_hoat:
    st.error(
        f"❌ **TỪ CHỐI CHO VAY**\n\n"
        f"**Lý do:** Tổng nghĩa vụ trả nợ hàng tháng (**{tong_tra_no:.2f} triệu**) vượt quá thu nhập còn lại sau khi trừ chi phí sinh hoạt (**{thu_nhap_con_lai:.2f} triệu**). Khách hàng mất khả năng thanh toán."
    )
elif dat_chuan_dti:
    st.success(
        f"✅ **ĐỒNG Ý CHO VAY**\n\n"
        f"**Lý do:**\n"
        f"- Thu nhập sau sinh hoạt (**{thu_nhap_con_lai:.2f} triệu**) đủ để chi trả tổng nợ hàng tháng (**{tong_tra_no:.2f} triệu**), số dư còn lại là **{(thu_nhap_con_lai - tong_tra_no):.2f} triệu/tháng**.\n"
        f"- Hệ số DTI (**{dti_tong_thu_nhap:.2f}%**) nằm trong ngưỡng an toàn cho phép của ngân hàng ($\le$ **{nguong_dti_cho_phep}%**)."
    )
else:
    st.warning(
        f"⚠️ **CÂN NHẮC / TỪ CHỐI THEO QUY ĐỊNH DTI**\n\n"
        f"**Chi tiết:**\n"
        f"- Về dòng tiền: Khách hàng vẫn đủ tiền trả nợ sau khi trừ sinh hoạt phí (dư **{(thu_nhap_con_lai - tong_tra_no):.2f} triệu/tháng**).\n"
        f"- Về quy định: Hệ số DTI hiện tại là **{dti_tong_thu_nhap:.2f}%**, vượt quá ngưỡng cài đặt là **{nguong_dti_cho_phep}%**. Cần kéo dài thời gian vay hoặc giảm số tiền vay."
    )
