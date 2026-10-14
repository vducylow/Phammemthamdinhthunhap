import streamlit as st
import pandas as pd
import math
from datetime import date
import calendar

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Thẩm định Tín dụng & Kế hoạch trả nợ", page_icon="🏦", layout="wide")

st.title("🏦 Hệ Thống Thẩm Định DTI & Lập Kế Hoạch Trả Nợ")
st.caption("Tích hợp tính toán chỉ số DTI, lập lịch trả nợ đa giai đoạn và mô phỏng tái cấu trúc khoản vay.")

# --- HÀM HỖ TRỢ CỘNG THÁNG ---
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

# --- HÀM TÍNH BẢNG KẾ HOẠCH TRẢ NỢ ---
def lap_bang_tra_no(so_tien_vay, thoi_han_nam, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do, 
                    ngay_gn, ngay_tinh_lai, ngay_thu_no, so_ky_hien_thi, cach_tinh_lai, thu_nhap, no_cu):
    tong_so_ky = thoi_han_nam * 12
    goc_hang_ky = so_tien_vay / tong_so_ky
    ls_tha_noi = ls_huy_dong + bien_do
    
    du_no = so_tien_vay
    danh_sach_ky = []
    
    # Xác định ngày tính lãi kỳ đầu tiên
    if ngay_gn.day < ngay_tinh_lai:
        moc_tinh_lai_1 = date(ngay_gn.year, ngay_gn.month, ngay_tinh_lai)
    else:
        thang_sau = add_months(ngay_gn, 1)
        moc_tinh_lai_1 = date(thang_sau.year, thang_sau.month, ngay_tinh_lai)
        
    moc_tinh_lai_truoc = ngay_gn

    for ky in range(1, min(so_ky_hien_thi, tong_so_ky) + 1):
        # 1. Xác định ngày tính lãi và ngày thu nợ của kỳ hiện tại
        moc_tinh_lai_hien_tai = add_months(moc_tinh_lai_1, ky - 1)
        if ngay_thu_no >= ngay_tinh_lai:
            moc_thu_no = date(moc_tinh_lai_hien_tai.year, moc_tinh_lai_hien_tai.month, ngay_thu_no)
        else:
            thang_thu = add_months(moc_tinh_lai_hien_tai, 1)
            moc_thu_no = date(thang_thu.year, thang_thu.month, ngay_thu_no)
            
        so_ngay = (moc_tinh_lai_hien_tai - moc_tinh_lai_truoc).days
        
        # 2. Xác định lãi suất áp dụng (Ưu đãi hay Thả nổi)
        ls_nam = ls_uu_dai if ky <= so_thang_ud else ls_tha_noi
        
        # 3. Tính tiền lãi theo quy chuẩn giáo trình
        if cach_tinh_lai == "Tính tròn tháng (Lãi năm / 12)":
            tien_lai = du_no * (ls_nam / 100) / 12
            dien_giai_ngay = "1 tháng"
        elif cach_tinh_lai == "Theo số ngày thực tế (Cơ sở 365 ngày)":
            tien_lai = du_no * (ls_nam / 100) * (so_ngay / 365)
            dien_giai_ngay = f"{so_ngay} ngày"
        else: # Cơ sở 360 ngày
            tien_lai = du_no * (ls_nam / 100) * (so_ngay / 360)
            dien_giai_ngay = f"{so_ngay} ngày"
            
        tong_tra_ky = goc_hang_ky + tien_lai
        du_no_cuoi = max(0.0, du_no - goc_hang_ky)
        dti_ky = ((tong_tra_ky + no_cu) / thu_nhap) * 100 if thu_nhap > 0 else 0
        
        danh_sach_ky.append({
            "Kỳ": f"Kỳ {ky}",
            "Ngày chốt lãi": moc_tinh_lai_hien_tai.strftime("%d/%m/%Y"),
            "Ngày thu nợ": moc_thu_no.strftime("%d/%m/%Y"),
            "Thời gian tính lãi": dien_giai_ngay,
            "Lãi suất (%/năm)": f"{ls_nam:.1f}%",
            "Dư nợ đầu kỳ (trđ)": round(du_no, 2),
            "Trả gốc (trđ)": round(goc_hang_ky, 2),
            "Trả lãi (trđ)": round(tien_lai, 2),
            "Tổng trả vay mới (trđ)": round(tong_tra_ky, 2),
            "DTI kỳ này (%)": round(dti_ky, 2),
            "Dư nợ cuối kỳ (trđ)": round(du_no_cuoi, 2)
        })
        
        du_no = du_no_cuoi
        moc_tinh_lai_truoc = moc_tinh_lai_hien_tai
        
    return pd.DataFrame(danh_sach_ky)


# ==============================================================================
# THANH BÊN TRÁI (SIDEBAR): NHẬP THÔNG SỐ GỐC
# ==============================================================================
with st.sidebar:
    st.header("⚙️ 1. Thông số Khoản Vay")
    vay_moi = st.number_input("Số tiền vay (triệu đ)", min_value=10.0, value=700.0, step=50.0)
    thoi_han_nam = st.slider("Thời hạn vay (năm)", min_value=1, max_value=30, value=5)
    
    st.markdown("**Cấu trúc lãi suất:**")
    col_s1, col_s2 = st.columns(2)
    ls_uu_dai = col_s1.number_input("Lãi ưu đãi (%/năm)", min_value=0.0, value=9.0, step=0.5)
    so_thang_ud = col_s2.number_input("Số kỳ ưu đãi (tháng)", min_value=0, value=3, step=1)
    
    col_s3, col_s4 = st.columns(2)
    ls_huy_dong = col_s3.number_input("Lãi huy động (%)", min_value=0.0, value=10.0, step=0.5)
    bien_do = col_s4.number_input("Biên độ cộng (%)", min_value=0.0, value=4.0, step=0.5)
    st.caption(f"👉 Lãi suất sau ưu đãi: **{ls_huy_dong + bien_do:.1f}%/năm**")

    st.divider()
    st.header("📅 2. Mốc Thời Gian & Kỳ Hạn")
    ngay_giai_ngan = st.date_input("Ngày giải ngân", value=date(2023, 10, 22))
    col_d1, col_d2 = st.columns(2)
    ngay_tinh_lai = col_d1.number_input("Ngày tính lãi", min_value=1, max_value=28, value=10)
    ngay_thu_lai = col_d2.number_input("Ngày thu nợ", min_value=1, max_value=28, value=15)
    so_ky_xem = st.slider("Số kỳ muốn lập bảng", min_value=1, max_value=60, value=5)
    cach_tinh = st.selectbox(
        "Quy chuẩn tính lãi trên lớp:",
        ["Tính tròn tháng (Lãi năm / 12)", "Theo số ngày thực tế (Cơ sở 365 ngày)", "Theo số ngày thực tế (Cơ sở 360 ngày)"]
    )

    st.divider()
    st.header("👨‍👩‍👦 3. Hồ Sơ Khách Hàng (DTI)")
    thu_nhap = st.number_input("Tổng thu nhập/tháng (triệu đ)", min_value=1.0, value=45.0, step=1.0)
    no_cu = st.number_input("Trả nợ cũ/tháng (triệu đ)", min_value=0.0, value=10.0, step=1.0)
    so_nguoi = st.number_input("Số người trong gia đình", min_value=1, value=3, step=1)
    phi_1_nguoi = st.number_input("Sinh hoạt phí/người (triệu đ)", min_value=0.0, value=4.0, step=0.5)
    nguong_dti = st.slider("Trần DTI Ngân hàng cho phép (%)", min_value=30, max_value=90, value=60, step=5)


# ==============================================================================
# XỬ LÝ DỮ LIỆU CHÍNH
# ==============================================================================
df_ke_hoach = lap_bang_tra_no(
    vay_moi, thoi_han_nam, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do,
    ngay_giai_ngan, ngay_tinh_lai, ngay_thu_lai, so_ky_xem, cach_tinh, thu_nhap, no_cu
)

# Lấy kỳ có số tiền phải trả cao nhất (thường là Kỳ 1 hoặc Kỳ đầu tiên thả nổi lãi suất - Kỳ 4) để xét DTI an toàn
tra_vay_moi_ky_1 = df_ke_hoach.loc[0, "Tổng trả vay mới (trđ)"]
tra_vay_moi_max = df_ke_hoach["Tổng trả vay mới (trđ)"].max()
ky_max = df_ke_hoach.loc[df_ke_hoach["Tổng trả vay mới (trđ)"].idxmax(), "Kỳ"]

sinh_hoat_phi = so_nguoi * phi_1_nguoi
thu_nhap_con_lai = thu_nhap - sinh_hoat_phi

# Cho phép chọn xét DTI theo Kỳ 1 hoặc Kỳ cao nhất (khi hết ưu đãi)
st.subheader("PHẦN 1: THẨM ĐỊNH HỆ SỐ NỢ TRÊN THU NHẬP (DTI)")
loai_xet_dti = st.radio(
    "Chọn cơ sở xét duyệt DTI:",
    [f"Xét theo Kỳ 1 ({tra_vay_moi_ky_1:,.2f} trđ/tháng)", 
     f"Xét theo Kỳ áp lực cao nhất khi thả nổi lãi suất - {ky_max} ({tra_vay_moi_max:,.2f} trđ/tháng)"],
    horizontal=True
)

tra_vay_moi_xet = tra_vay_moi_ky_1 if "Kỳ 1" in loai_xet_dti else tra_vay_moi_max
tong_no_xet = no_cu + tra_vay_moi_xet
so_du_cuoi = thu_nhap_con_lai - tong_no_xet
dti_tong = (tong_no_xet / thu_nhap) * 100

# Khối Kết luận
if so_du_cuoi < 0:
    st.error(f"### ❌ TỪ CHỐI CHO VAY (Âm dòng tiền: {so_du_cuoi:,.2f} triệu/tháng)\nThu nhập còn lại sau sinh hoạt (**{thu_nhap_con_lai:,.2f} trđ**) không đủ trả tổng nợ hàng tháng (**{tong_no_xet:,.2f} trđ**).")
elif dti_tong <= nguong_dti:
    st.success(f"### ✅ ĐỦ ĐIỀU KIỆN CHO VAY (DTI = {dti_tong:.2f}% ≤ {nguong_dti}%)\nKhách hàng đảm bảo khả năng thanh toán, số tiền dư sau khi trả nợ và sinh hoạt phí là **{so_du_cuoi:,.2f} triệu/tháng**.")
else:
    st.warning(f"### ⚠️ VƯỢT TRẦN DTI QUY ĐỊNH (DTI hiện tại: {dti_tong:.2f}% > Trần {nguong_dti}%)\nKhách hàng vẫn dư **{so_du_cuoi:,.2f} triệu/tháng** sau sinh hoạt, nhưng vượt tỷ lệ DTI của ngân hàng. Hãy sử dụng **Bảng Tùy Chỉnh** ở Phần 3 bên dưới để cơ cấu lại!")

# 4 Thẻ chỉ số nhanh
c1, c2, c3, c4 = st.columns(4)
c1.metric("1. Thu nhập sau sinh hoạt", f"{thu_nhap_con_lai:,.2f} trđ", f"-{sinh_hoat_phi:,.1f} trđ sinh hoạt ({so_nguoi} người)", delta_color="off")
c2.metric("2. Trả vay mới (kỳ đang xét)", f"{tra_vay_moi_xet:,.2f} trđ", f"Nợ cũ: {no_cu:,.1f} trđ", delta_color="off")
c3.metric("3. Tổng nghĩa vụ nợ/tháng", f"{tong_no_xet:,.2f} trđ", f"DTI: {dti_tong:.2f}%", delta_color="inverse" if dti_tong > nguong_dti else "normal")
c4.metric("4. Số dư ròng cuối tháng", f"{so_du_cuoi:,.2f} trđ", "Đạt" if so_du_cuoi >= 0 else "Thiếu hụt", delta_color="normal" if so_du_cuoi >= 0 else "inverse")


# ==============================================================================
# PHẦN 2: BẢNG KẾ HOẠCH TRẢ NỢ (THEO ĐỀ BÀI TRONG ẢNH)
# ==============================================================================
st.divider()
st.subheader(f"PHẦN 2: BẢNG KẾ HOẠCH TRẢ NỢ ({so_ky_xem} KỲ ĐẦU TIÊN)")
st.markdown(
    f"**Thông tin khoản vay:** Vay **{vay_moi:,.0f} triệu** trong **{thoi_han_nam} năm** ({thoi_han_nam*12} tháng) | "
    f"Gốc trả đều mỗi kỳ: **{vay_moi/(thoi_han_nam*12):,.2f} triệu** | "
    f"Lãi suất **{so_thang_ud} kỳ đầu**: `{ls_uu_dai}%/năm`, từ **kỳ {so_thang_ud+1}** trở đi: `{ls_huy_dong}% + {bien_do}% = {ls_huy_dong+bien_do}%/năm`."
)

# Hiển thị bảng dữ liệu đẹp mắt
st.dataframe(
    df_ke_hoach.style.format({
        "Dư nợ đầu kỳ (trđ)": "{:,.2f}",
        "Trả gốc (trđ)": "{:,.2f}",
        "Trả lãi (trđ)": "{:,.2f}",
        "Tổng trả vay mới (trđ)": "{:,.2f}",
        "DTI kỳ này (%)": "{:.2f}%",
        "Dư nợ cuối kỳ (trđ)": "{:,.2f}",
    }),
    use_container_width=True,
    hide_index=True
)

# Tổng kết 5 kỳ đầu
tong_goc_5_ky = df_ke_hoach["Trả gốc (trđ)"].sum()
tong_lai_5_ky = df_ke_hoach["Trả lãi (trđ)"].sum()
st.info(f"📌 **Tổng cộng sau {so_ky_xem} kỳ đầu tiên:** Khách hàng đã trả được **{tong_goc_5_ky:,.2f} triệu** tiền gốc và **{tong_lai_5_ky:,.2f} triệu** tiền lãi (Tổng số tiền đã thanh toán: **{(tong_goc_5_ky + tong_lai_5_ky):,.2f} triệu đồng**).")


# ==============================================================================
# PHẦN 3: BẢNG TÙY CHỈNH & TÁI CẤU TRÚC KHOẢN VAY KHI DTI CAO
# ==============================================================================
st.divider()
st.subheader("🛠️ PHẦN 3: BẢNG TÙY CHỈNH HỒ SƠ CHO KHÁCH HÀNG (KHI DTI QUÁ CAO)")

# Tính toán gợi ý tự động làm mốc tham khảo
tong_no_muc_tieu = min(thu_nhap * (nguong_dti / 100), thu_nhap_con_lai)
tra_vay_moi_toi_da = max(0.0, tong_no_muc_tieu - no_cu)
ls_xet_nam = ls_uu_dai if "Kỳ 1" in loai_xet_dti else (ls_huy_dong + bien_do)
ls_xet_thang = (ls_xet_nam / 100) / 12
vay_goi_y = tra_vay_moi_toi_da / ((1 / (thoi_han_nam * 12)) + ls_xet_thang) if tra_vay_moi_toi_da > 0 else 0

st.write("Kéo các thanh trượt dưới đây để thiết kế lại phương án vay cho khách hàng và so sánh trực tiếp với phương án gốc:")

with st.container(border=True):
    tc1, tc2, tc3, tc4 = st.columns(4)
    
    with tc1:
        vay_dieu_chinh = st.number_input(
            "1. Điều chỉnh Số tiền vay (trđ)", 
            min_value=10.0, max_value=float(vay_moi * 2), 
            value=float(round(min(vay_moi, vay_goi_y), 0)) if dti_tong > nguong_dti and vay_goi_y >= 10 else float(vay_moi),
            step=10.0,
            help=f"Mức vay tối đa gợi ý để đạt DTI {nguong_dti}% là khoảng {vay_goi_y:,.1f} triệu"
        )
    with tc2:
        nam_dieu_chinh = st.slider(
            "2. Điều chỉnh Thời hạn vay (năm)", 
            min_value=1, max_value=30, 
            value=min(30, thoi_han_nam + 3) if dti_tong > nguong_dti else thoi_han_nam
        )
    with tc3:
        thu_nhap_bo_sung = st.number_input(
            "3. Cộng thêm thu nhập/đồng trả nợ (trđ)", 
            min_value=0.0, value=0.0, step=1.0
        )
    with tc4:
        giam_no_cu = st.number_input(
            "4. Tất toán bớt nợ cũ/tháng (trđ)", 
            min_value=0.0, max_value=float(no_cu), value=0.0, step=1.0
        )

    # Tính lại bảng kế hoạch và DTI theo thông số tùy chỉnh
    thu_nhap_moi = thu_nhap + thu_nhap_bo_sung
    no_cu_moi = no_cu - giam_no_cu
    
    df_moi = lap_bang_tra_no(
        vay_dieu_chinh, nam_dieu_chinh, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do,
        ngay_giai_ngan, ngay_tinh_lai, ngay_thu_lai, so_ky_xem, cach_tinh, thu_nhap_moi, no_cu_moi
    )
    
    tra_moi_xet = df_moi.loc[0, "Tổng trả vay mới (trđ)"] if "Kỳ 1" in loai_xet_dti else df_moi["Tổng trả vay mới (trđ)"].max()
    tong_no_moi = no_cu_moi + tra_moi_xet
    dti_moi = (tong_no_moi / thu_nhap_moi) * 100
    so_du_moi = (thu_nhap_moi - sinh_hoat_phi) - tong_no_moi

    st.markdown("#### 🔄 Bảng So Sánh Phương Án Gốc vs Phương Án Tùy Chỉnh")
    
    df_so_sanh = pd.DataFrame({
        "Chỉ tiêu đánh giá": [
            "Số tiền vay (triệu đồng)",
            "Thời hạn vay (năm)",
            "Tổng thu nhập xét duyệt (triệu/tháng)",
            "Nghĩa vụ nợ cũ (triệu/tháng)",
            "Trả gốc + lãi vay mới (triệu/tháng)",
            "Tổng nợ phải trả hàng tháng (triệu/tháng)",
            "Số dư sau sinh hoạt & trả nợ (triệu/tháng)",
            "HỆ SỐ DTI (%)",
            "TRẠNG THÁI PHÊ DUYỆT"
        ],
        "Phương án Gốc": [
            f"{vay_moi:,.1f} trđ",
            f"{thoi_han_nam} năm",
            f"{thu_nhap:,.1f} trđ",
            f"{no_cu:,.1f} trđ",
            f"{tra_vay_moi_xet:,.2f} trđ",
            f"{tong_no_xet:,.2f} trđ",
            f"{so_du_cuoi:,.2f} trđ",
            f"{dti_tong:.2f}%",
            "✅ Đạt chuẩn" if (dti_tong <= nguong_dti and so_du_cuoi >= 0) else "❌ Vượt ngưỡng / Từ chối"
        ],
        "Phương án Tùy Chỉnh Mới": [
            f"{vay_dieu_chinh:,.1f} trđ",
            f"{nam_dieu_chinh} năm",
            f"{thu_nhap_moi:,.1f} trđ",
            f"{no_cu_moi:,.1f} trđ",
            f"{tra_moi_xet:,.2f} trđ",
            f"{tong_no_moi:,.2f} trđ",
            f"{so_du_moi:,.2f} trđ",
            f"{dti_moi:.2f}%",
            "✅ ĐẠT CHUẨN DUYỆT VAY" if (dti_moi <= nguong_dti and so_du_moi >= 0) else "⚠️ Vẫn cần chỉnh thêm"
        ]
    })
    st.table(df_so_sanh)

    # Cho phép xem luôn bảng kế hoạch trả nợ mới sau khi tùy chỉnh
    with st.expander("📋 Xem Bảng kế hoạch trả nợ chi tiết của Phương án Tùy Chỉnh Mới"):
        st.dataframe(
            df_moi.style.format({
                "Dư nợ đầu kỳ (trđ)": "{:,.2f}",
                "Trả gốc (trđ)": "{:,.2f}",
                "Trả lãi (trđ)": "{:,.2f}",
                "Tổng trả vay mới (trđ)": "{:,.2f}",
                "DTI kỳ này (%)": "{:.2f}%",
                "Dư nợ cuối kỳ (trđ)": "{:,.2f}",
            }),
            use_container_width=True,
            hide_index=True
        )
