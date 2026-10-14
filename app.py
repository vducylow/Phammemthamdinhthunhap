import streamlit as st
import pandas as pd
import math
from datetime import date
import calendar

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Thẩm định Tín dụng & Lịch trả nợ", page_icon="🏦", layout="wide")

st.title("🏦 Hệ Thống Thẩm Định DTI & Kế Hoạch Trả Nợ")

# --- HÀM HỖ TRỢ CỘNG THÁNG & LẬP BẢNG TRẢ NỢ ---
def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

def lap_bang_tra_no(so_tien_vay, thoi_han_nam, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do, 
                    ngay_gn, ngay_tinh_lai, ngay_thu_no, so_ky_hien_thi, cach_tinh_lai, thu_nhap, no_cu):
    tong_so_ky = thoi_han_nam * 12
    goc_hang_ky = so_tien_vay / tong_so_ky
    ls_tha_noi = ls_huy_dong + bien_do
    du_no = so_tien_vay
    danh_sach_ky = []
    
    if ngay_gn.day < ngay_tinh_lai:
        moc_tinh_lai_1 = date(ngay_gn.year, ngay_gn.month, ngay_tinh_lai)
    else:
        thang_sau = add_months(ngay_gn, 1)
        moc_tinh_lai_1 = date(thang_sau.year, thang_sau.month, ngay_tinh_lai)
        
    moc_tinh_lai_truoc = ngay_gn

    for ky in range(1, min(so_ky_hien_thi, tong_so_ky) + 1):
        moc_tinh_lai_hien_tai = add_months(moc_tinh_lai_1, ky - 1)
        if ngay_thu_no >= ngay_tinh_lai:
            moc_thu_no = date(moc_tinh_lai_hien_tai.year, moc_tinh_lai_hien_tai.month, ngay_thu_no)
        else:
            thang_thu = add_months(moc_tinh_lai_hien_tai, 1)
            moc_thu_no = date(thang_thu.year, thang_thu.month, ngay_thu_no)
            
        so_ngay = (moc_tinh_lai_hien_tai - moc_tinh_lai_truoc).days
        ls_nam = ls_uu_dai if ky <= so_thang_ud else ls_tha_noi
        
        if cach_tinh_lai == "Tính tròn tháng (Lãi năm / 12)":
            tien_lai = du_no * (ls_nam / 100) / 12
            dien_giai_ngay = "1 tháng"
        elif cach_tinh_lai == "Theo số ngày thực tế (Cơ sở 365 ngày)":
            tien_lai = du_no * (ls_nam / 100) * (so_ngay / 365)
            dien_giai_ngay = f"{so_ngay} ngày"
        else:
            tien_lai = du_no * (ls_nam / 100) * (so_ngay / 360)
            dien_giai_ngay = f"{so_ngay} ngày"
            
        tong_tra_ky = goc_hang_ky + tien_lai
        du_no_cuoi = max(0.0, du_no - goc_hang_ky)
        dti_ky = ((tong_tra_ky + no_cu) / thu_nhap) * 100 if thu_nhap > 0 else 0
        
        danh_sach_ky.append({
            "Kỳ": f"Kỳ {ky}",
            "Ngày tính lãi": moc_tinh_lai_hien_tai.strftime("%d/%m/%Y"),
            "Ngày thu nợ": moc_thu_no.strftime("%d/%m/%Y"),
            "Số ngày": dien_giai_ngay,
            "Lãi suất": f"{ls_nam:.1f}%",
            "Dư nợ đầu kỳ": round(du_no, 2),
            "Trả gốc": round(goc_hang_ky, 2),
            "Trả lãi": round(tien_lai, 2),
            "Tổng trả vay mới": round(tong_tra_ky, 2),
            "DTI kỳ này (%)": round(dti_ky, 2),
            "Dư nợ cuối kỳ": round(du_no_cuoi, 2)
        })
        
        du_no = du_no_cuoi
        moc_tinh_lai_truoc = moc_tinh_lai_hien_tai
        
    return pd.DataFrame(danh_sach_ky)


# ==============================================================================
# 2. THANH BÊN TRÁI (SIDEBAR): GOM GỌN THEO NHÓM THU GỌN (EXPANDER)
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Bảng Điều Khiển")
    
    with st.expander("💰 1. Thông tin Khoản vay & Lãi suất", expanded=True):
        vay_moi = st.number_input("Số tiền vay (triệu đ)", min_value=10.0, value=700.0, step=50.0)
        thoi_han_nam = st.slider("Thời hạn vay (năm)", min_value=1, max_value=30, value=5)
        
        c_s1, c_s2 = st.columns(2)
        ls_uu_dai = c_s1.number_input("Lãi ưu đãi (%)", min_value=0.0, value=9.0, step=0.5)
        so_thang_ud = c_s2.number_input("Số tháng ưu đãi", min_value=0, value=3, step=1)
        
        c_s3, c_s4 = st.columns(2)
        ls_huy_dong = c_s3.number_input("Lãi huy động (%)", min_value=0.0, value=10.0, step=0.5)
        bien_do = c_s4.number_input("Biên độ (%)", min_value=0.0, value=4.0, step=0.5)
        st.caption(f"📈 Lãi suất thả nổi: **{ls_huy_dong + bien_do:.1f}%/năm**")

    with st.expander("👨‍👩‍👦 2. Tài chính Khách hàng & Trần DTI", expanded=True):
        thu_nhap = st.number_input("Tổng thu nhập/tháng (triệu đ)", min_value=1.0, value=45.0, step=1.0)
        no_cu = st.number_input("Trả nợ cũ/tháng (triệu đ)", min_value=0.0, value=10.0, step=1.0)
        c_kh1, c_kh2 = st.columns(2)
        so_nguoi = c_kh1.number_input("Số người", min_value=1, value=3, step=1)
        phi_1_nguoi = c_kh2.number_input("Phí SH/người", min_value=0.0, value=4.0, step=0.5)
        nguong_dti = st.slider("Trần DTI Ngân hàng (%)", min_value=30, max_value=90, value=60, step=5)

    with st.expander("📅 3. Mốc thời gian & Cách tính lãi", expanded=False):
        ngay_giai_ngan = st.date_input("Ngày giải ngân", value=date(2023, 10, 22))
        c_d1, c_d2 = st.columns(2)
        ngay_tinh_lai = c_d1.number_input("Ngày chốt lãi", min_value=1, max_value=28, value=10)
        ngay_thu_lai = c_d2.number_input("Ngày thu nợ", min_value=1, max_value=28, value=15)
        so_ky_xem = st.slider("Số kỳ hiển thị bảng", min_value=1, max_value=60, value=5)
        cach_tinh = st.selectbox(
            "Cơ sở tính lãi:",
            ["Tính tròn tháng (Lãi năm / 12)", "Theo số ngày thực tế (Cơ sở 365 ngày)", "Theo số ngày thực tế (Cơ sở 360 ngày)"]
        )


# ==============================================================================
# 3. XỬ LÝ TÍNH TOÁN TRUNG TÂM
# ==============================================================================
df_ke_hoach = lap_bang_tra_no(
    vay_moi, thoi_han_nam, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do,
    ngay_giai_ngan, ngay_tinh_lai, ngay_thu_lai, so_ky_xem, cach_tinh, thu_nhap, no_cu
)

# Chọn kỳ xét DTI ngay trên đầu trang
tra_ky_1 = df_ke_hoach.loc[0, "Tổng trả vay mới"]
tra_ky_max = df_ke_hoach["Tổng trả vay mới"].max()
ten_ky_max = df_ke_hoach.loc[df_ke_hoach["Tổng trả vay mới"].idxmax(), "Kỳ"]

col_opt1, col_opt2 = st.columns([2, 1])
with col_opt1:
    loai_xet_dti = st.radio(
        "🔍 **Chọn kỳ cơ sở để thẩm định DTI:**",
        [f"Kỳ áp lực cao nhất khi thả nổi ({ten_ky_max}: {tra_ky_max:,.2f} trđ)", 
         f"Kỳ đầu tiên (Kỳ 1: {tra_ky_1:,.2f} trđ)"],
        horizontal=True
    )

dang_xet_ky_1 = "Kỳ 1" in loai_xet_dti
tra_vay_moi_xet = tra_ky_1 if dang_xet_ky_1 else tra_ky_max
ls_xet_nam = ls_uu_dai if dang_xet_ky_1 else (ls_huy_dong + bien_do)
du_no_xet = vay_moi if dang_xet_ky_1 else vay_moi - (vay_moi / (thoi_han_nam * 12)) * min(so_thang_ud, thoi_han_nam * 12 - 1)

sinh_hoat_phi = so_nguoi * phi_1_nguoi
thu_nhap_con_lai = thu_nhap - sinh_hoat_phi
tong_no_xet = no_cu + tra_vay_moi_xet
so_du_cuoi = thu_nhap_con_lai - tong_no_xet
dti_tong = (tong_no_xet / thu_nhap) * 100
dti_rong = (tong_no_xet / thu_nhap_con_lai) * 100 if thu_nhap_con_lai > 0 else 100.0

# --- BANNER KẾT LUẬN LUÔN HIỂN THỊ TRÊN CÙNG ---
if so_du_cuoi < 0:
    st.error(f"### ❌ TỪ CHỐI CHO VAY — Khách hàng bị âm dòng tiền ({so_du_cuoi:,.2f} triệu/tháng)\nThu nhập sau sinh hoạt (**{thu_nhap_con_lai:,.2f} trđ**) không đủ thanh toán tổng nghĩa vụ nợ (**{tong_no_xet:,.2f} trđ**). Xem ngay **Tab 3** để cơ cấu lại khoản vay!")
elif dti_tong <= nguong_dti:
    st.success(f"### ✅ ĐỦ ĐIỀU KIỆN PHÊ DUYỆT — Hệ số DTI đạt {dti_tong:.2f}% (Trần cho phép ≤ {nguong_dti}%)\nKhách hàng hoàn toàn đủ khả năng trả nợ và vẫn dư **{so_du_cuoi:,.2f} triệu/tháng** sau khi trừ toàn bộ sinh hoạt phí.")
else:
    st.warning(f"### ⚠️ CẢNH BÁO VƯỢT TRẦN DTI — DTI hiện tại: {dti_tong:.2f}% (Vượt trần {nguong_dti}%)\nDù khách hàng vẫn dư **{so_du_cuoi:,.2f} triệu/tháng**, hồ sơ đang vượt ngưỡng DTI quy định. Chuyển sang **Tab 3** bên dưới để xem giải pháp giảm DTI!")


# ==============================================================================
# 4. CHIA GIAO DIỆN THÀNH 3 TAB RÕ RÀNG, DỄ NHÌN
# ==============================================================================
tab1, tab2, tab3 = st.tabs([
    "📊 1. Tổng quan Thẩm định DTI", 
    f"📅 2. Bảng Kế hoạch trả nợ ({so_ky_xem} kỳ đầu)", 
    "🛠️ 3. Giải pháp & Tùy chỉnh giảm DTI"
])

# --- TAB 1: TỔNG QUAN THẨM ĐỊNH DTI ---
with tab1:
    st.write("")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.metric("1. Tổng thu nhập", f"{thu_nhap:,.1f} trđ", f"Sinh hoạt phí: -{sinh_hoat_phi:,.1f} trđ", delta_color="off")
    with m2:
        with st.container(border=True):
            st.metric("2. Thu nhập sau sinh hoạt", f"{thu_nhap_con_lai:,.1f} trđ", f"Gia đình {so_nguoi} người", delta_color="off")
    with m3:
        with st.container(border=True):
            st.metric("3. Tổng nợ phải trả/tháng", f"{tong_no_xet:,.2f} trđ", f"Vay mới: {tra_vay_moi_xet:,.2f} | Cũ: {no_cu:,.1f}", delta_color="off")
    with m4:
        with st.container(border=True):
            st.metric("4. Tiền dư cuối tháng", f"{so_du_cuoi:,.2f} trđ", "An toàn" if so_du_cuoi >= 0 else "Thiếu hụt", delta_color="normal" if so_du_cuoi >= 0 else "inverse")

    col_t1, col_t2 = st.columns([1.2, 1])
    with col_t1:
        with st.container(border=True):
            st.markdown("#### 🎯 Thước đo Hệ số DTI")
            st.write(f"**DTI trên Tổng thu nhập:** `{dti_tong:.2f}%` *(Ngưỡng ngân hàng: ≤ {nguong_dti}%)*")
            st.progress(min(int(dti_tong), 100))
            st.write("")
            st.write(f"**DTI trên Thu nhập ròng (sau sinh hoạt):** `{dti_rong:.2f}%`")
            st.progress(min(int(dti_rong), 100))
            
    with col_t2:
        with st.container(border=True):
            st.markdown("#### 🧾 Bóc tách dòng tiền tháng đang xét")
            goc_moi_thang = vay_moi / (thoi_han_nam * 12)
            lai_ky_xet = tra_vay_moi_xet - goc_moi_thang
            st.dataframe(pd.DataFrame({
                "Hạng mục": ["Gốc vay mới hàng tháng", "Lãi vay mới (kỳ đang xét)", "Trả nợ khoản vay cũ", "Chi phí sinh hoạt gia đình", "Số dư tích lũy còn lại"],
                "Số tiền (trđ)": [f"{goc_moi_thang:,.2f}", f"{lai_ky_xet:,.2f}", f"{no_cu:,.2f}", f"{sinh_hoat_phi:,.2f}", f"{so_du_cuoi:,.2f}"],
                "Tỷ trọng / Thu nhập": [f"{(goc_moi_thang/thu_nhap)*100:.1f}%", f"{(lai_ky_xet/thu_nhap)*100:.1f}%", f"{(no_cu/thu_nhap)*100:.1f}%", f"{(sinh_hoat_phi/thu_nhap)*100:.1f}%", f"{(so_du_cuoi/thu_nhap)*100:.1f}%"]
            }), use_container_width=True, hide_index=True)


# --- TAB 2: BẢNG KẾ HOẠCH TRẢ NỢ ---
with tab2:
    st.write("")
    with st.container(border=True):
        st.markdown(f"#### 📋 Lịch trả nợ {so_ky_xem} kỳ đầu tiên (Giải ngân ngày {ngay_giai_ngan.strftime('%d/%m/%Y')})")
        st.caption(f"Gốc trả đều: **{vay_moi/(thoi_han_nam*12):,.2f} triệu/tháng** | Lãi suất {so_thang_ud} kỳ đầu: **{ls_uu_dai}%/năm** | Lãi suất từ kỳ {so_thang_ud+1}: **{ls_huy_dong + bien_do}%/năm** ({cach_tinh})")
        
        st.dataframe(
            df_ke_hoach.style.format({
                "Dư nợ đầu kỳ": "{:,.2f}",
                "Trả gốc": "{:,.2f}",
                "Trả lãi": "{:,.2f}",
                "Tổng trả vay mới": "{:,.2f}",
                "DTI kỳ này (%)": "{:.2f}%",
                "Dư nợ cuối kỳ": "{:,.2f}",
            }),
            use_container_width=True,
            hide_index=True
        )
        
        tong_goc = df_ke_hoach["Trả gốc"].sum()
        tong_lai = df_ke_hoach["Trả lãi"].sum()
        st.info(f"📌 **Tổng kết sau {so_ky_xem} kỳ:** Đã trả **{tong_goc:,.2f} triệu** nợ gốc + **{tong_lai:,.2f} triệu** tiền lãi = **{tong_goc + tong_lai:,.2f} triệu đồng**.")


# --- TAB 3: GIẢI PHÁP ĐỀ XUẤT & BẢNG TÙY CHỈNH KHI VƯỢT DTI ---
with tab3:
    st.write("")
    
    # PHẦN 3A: BẢNG ĐỀ XUẤT 4 GIẢI PHÁP TỰ ĐỘNG (GIỮ LẠI THEO YÊU CẦU)
    st.markdown("#### 💡 1. Đề xuất các giải pháp độc lập để đưa DTI về mức chuẩn")
    
    tong_no_muc_tieu = min(thu_nhap * (nguong_dti / 100), thu_nhap_con_lai)
    tra_vay_moi_toi_da = tong_no_muc_tieu - no_cu
    thang_hien_tai = thoi_han_nam * 12
    ls_thang_xet = (ls_xet_nam / 100) / 12
    ty_le_du_no = du_no_xet / vay_moi if vay_moi > 0 else 1.0

    if so_du_cuoi >= 0 and dti_tong <= nguong_dti:
        st.success(f"🎉 Hồ sơ hiện tại đã đạt chuẩn (DTI = **{dti_tong:.2f}%** ≤ **{nguong_dti}%**). Bạn vẫn có thể dùng bảng mô phỏng bên dưới nếu muốn thử các phương án khác.")
        vay_toi_da = vay_moi
    else:
        st.caption(f"Để đạt chuẩn phê duyệt, tổng nợ phải trả hàng tháng cần giảm từ **{tong_no_xet:,.2f} trđ** xuống tối đa **{tong_no_muc_tieu:,.2f} trđ/tháng**.")
        
        g1, g2, g3, g4 = st.columns(4)
        
        # Giải pháp 1: Giảm tiền vay
        with g1:
            with st.container(border=True):
                st.markdown("##### 📉 GP 1: Giảm tiền vay")
                if tra_vay_moi_toi_da <= 0:
                    vay_toi_da = 0.0
                    st.error("Nợ cũ đã vượt trần DTI. Cần tất toán nợ cũ trước.")
                else:
                    vay_toi_da = tra_vay_moi_toi_da / ((1 / thang_hien_tai) + ls_thang_xet * ty_le_du_no)
                    st.metric("Mức vay tối đa", f"{vay_toi_da:,.1f} trđ", f"Giảm {vay_moi - vay_toi_da:,.1f} trđ", delta_color="inverse")
                    st.caption("Giữ nguyên thời hạn & thu nhập.")

        # Giải pháp 2: Kéo dài thời gian vay
        with g2:
            with st.container(border=True):
                st.markdown("##### ⏳ GP 2: Kéo dài kỳ hạn")
                lai_xet_hien_tai = du_no_xet * ls_thang_xet
                if tra_vay_moi_toi_da <= lai_xet_hien_tai:
                    st.warning(f"Tiền lãi ({lai_xet_hien_tai:,.2f} trđ) đã vượt mức trả tối đa. Kéo dài kỳ hạn không khả thi.")
                else:
                    thang_can = vay_moi / (tra_vay_moi_toi_da - lai_xet_hien_tai)
                    nam_can = math.ceil(thang_can / 12)
                    if nam_can <= 30:
                        st.metric("Thời hạn cần thiết", f"{nam_can} năm", f"Tăng thêm {nam_can - thoi_han_nam} năm", delta_color="off")
                        st.caption(f"Tương đương khoảng {math.ceil(thang_can)} tháng.")
                    else:
                        st.warning(f"Cần tới **{nam_can} năm** (> 30 năm). Nên kết hợp giảm tiền vay.")

        # Giải pháp 3: Tăng thu nhập
        with g3:
            with st.container(border=True):
                st.markdown("##### 💰 GP 3: Thêm thu nhập")
                tn_can = max(tong_no_xet / (nguong_dti / 100), tong_no_xet + sinh_hoat_phi)
                can_them = tn_can - thu_nhap
                st.metric("Thu nhập cần đạt", f"{tn_can:,.1f} trđ", f"Cần thêm +{can_them:,.1f} trđ")
                st.caption("Bổ sung nguồn thu hoặc người đồng trả nợ.")

        # Giải pháp 4: Giảm nợ cũ
        with g4:
            with st.container(border=True):
                st.markdown("##### 💳 GP 4: Cơ cấu nợ cũ")
                no_can_giam = tong_no_xet - tong_no_muc_tieu
                if no_cu == 0:
                    st.info("Khách hàng không có nợ cũ.")
                elif no_cu >= no_can_giam:
                    st.metric("Nợ cũ tối đa", f"{no_cu - no_can_giam:,.1f} trđ/tháng", f"Tất toán bớt {no_can_giam:,.2f} trđ", delta_color="inverse")
                    st.caption("Trả bớt nợ cũ trước khi giải ngân.")
                else:
                    st.warning(f"Dù tất toán hết {no_cu:,.1f} trđ nợ cũ vẫn thiếu {no_can_giam - no_cu:,.2f} trđ/tháng.")

    st.divider()

    # PHẦN 3B: BẢNG TÙY CHỈNH KẾT HỢP (INTERACTIVE SIMULATOR)
    st.markdown("#### 🎛️ 2. Bảng Tùy Chỉnh & So Sánh Phương Án Trực Tiếp")
    st.caption("Bạn có thể kết hợp nhiều giải pháp cùng lúc bằng cách điều chỉnh các ô dưới đây để thiết kế phương án tối ưu nhất cho khách hàng:")

    with st.container(border=True):
        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            vay_dc = st.number_input("Số tiền vay mới (trđ)", min_value=10.0, max_value=float(vay_moi*2), value=float(round(min(vay_moi, vay_toi_da), 0)) if (dti_tong > nguong_dti and vay_toi_da >= 10) else float(vay_moi), step=10.0)
        with tc2:
            nam_dc = st.slider("Thời hạn vay mới (năm)", min_value=1, max_value=30, value=thoi_han_nam)
        with tc3:
            tn_them = st.number_input("Thu nhập bổ sung (trđ)", min_value=0.0, value=0.0, step=1.0)
        with tc4:
            no_cu_giam = st.number_input("Giảm trả nợ cũ/tháng (trđ)", min_value=0.0, max_value=float(no_cu), value=0.0, step=1.0)

        # Tính toán lại theo thông số tùy chỉnh
        tn_moi = thu_nhap + tn_them
        nc_moi = no_cu - no_cu_giam
        df_moi = lap_bang_tra_no(vay_dc, nam_dc, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do, ngay_giai_ngan, ngay_tinh_lai, ngay_thu_lai, so_ky_xem, cach_tinh, tn_moi, nc_moi)
        
        tra_moi_xet = df_moi.loc[0, "Tổng trả vay mới"] if dang_xet_ky_1 else df_moi["Tổng trả vay mới"].max()
        tong_no_moi = nc_moi + tra_moi_xet
        dti_moi = (tong_no_moi / tn_moi) * 100
        du_moi = (tn_moi - sinh_hoat_phi) - tong_no_moi

        # Bảng so sánh 2 bên
        st.dataframe(pd.DataFrame({
            "Chỉ tiêu so sánh": ["Số tiền vay", "Thời hạn vay", "Tổng thu nhập", "Trả nợ cũ/tháng", "Trả vay mới/tháng (kỳ xét)", "Tổng nghĩa vụ nợ/tháng", "Tiền dư sau sinh hoạt", "HỆ SỐ DTI (%)", "KẾT QUẢ DUYỆT"],
            "Phương Án Gốc (Hiện tại)": [
                f"{vay_moi:,.1f} trđ", f"{thoi_han_nam} năm", f"{thu_nhap:,.1f} trđ", f"{no_cu:,.1f} trđ",
                f"{tra_vay_moi_xet:,.2f} trđ", f"{tong_no_xet:,.2f} trđ", f"{so_du_cuoi:,.2f} trđ", f"{dti_tong:.2f}%",
                "✅ Đạt chuẩn" if (dti_tong <= nguong_dti and so_du_cuoi >= 0) else "❌ Vượt trần / Từ chối"
            ],
            "Phương Án Tùy Chỉnh (Mới)": [
                f"{vay_dc:,.1f} trđ", f"{nam_dc} năm", f"{tn_moi:,.1f} trđ", f"{nc_moi:,.1f} trđ",
                f"{tra_moi_xet:,.2f} trđ", f"{tong_no_moi:,.2f} trđ", f"{du_moi:,.2f} trđ", f"{dti_moi:.2f}%",
                "✅ ĐỦ ĐIỀU KIỆN DUYỆT" if (dti_moi <= nguong_dti and du_moi >= 0) else "⚠️ Cần điều chỉnh thêm"
            ]
        }), use_container_width=True, hide_index=True)

        with st.expander("📋 Xem Bảng kế hoạch trả nợ mới sau khi tùy chỉnh"):
            st.dataframe(
                df_moi.style.format({
                    "Dư nợ đầu kỳ": "{:,.2f}", "Trả gốc": "{:,.2f}", "Trả lãi": "{:,.2f}",
                    "Tổng trả vay mới": "{:,.2f}", "DTI kỳ này (%)": "{:.2f}%", "Dư nợ cuối kỳ": "{:,.2f}"
                }),
                use_container_width=True, hide_index=True
            )
