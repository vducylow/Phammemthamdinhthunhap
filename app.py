import streamlit as st
import pandas as pd
import math
from datetime import date
import calendar

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Thẩm định Tín dụng & Lịch trả nợ", page_icon="🏦", layout="wide")

# --- 2. CSS TÙY CHỈNH MÀU SẮC, CỠ CHỮ & HIỆU ỨNG BẮT MẮT ---
st.markdown("""
<style>
    /* Tiêu đề chính Gradient */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(29, 78, 216, 0.3);
    }
    .main-header h1 {
        color: #ffffff !important;
        font-size: 32px !important;
        font-weight: 800 !important;
        margin: 0 0 6px 0 !important;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #bfdbfe !important;
        font-size: 16px !important;
        margin: 0 !important;
    }

    /* Banner Kết luận thẩm định */
    .status-banner {
        padding: 20px 26px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .status-banner h3 {
        margin: 0 0 8px 0 !important;
        font-size: 23px !important;
        font-weight: 800 !important;
    }
    .status-banner p {
        margin: 0 !important;
        font-size: 16.5px !important;
        line-height: 1.5;
    }
    .banner-success { background: linear-gradient(to right, #ecfdf5, #d1fae5); border-left: 8px solid #10b981; color: #065f46; }
    .banner-warning { background: linear-gradient(to right, #fffbeb, #fef3c7); border-left: 8px solid #f59e0b; color: #92400e; }
    .banner-danger  { background: linear-gradient(to right, #fef2f2, #fee2e2); border-left: 8px solid #ef4444; color: #991b1b; }

    /* Thẻ KPI (Metric Cards) nhiều màu sắc */
    .kpi-card {
        padding: 20px;
        border-radius: 14px;
        background: #ffffff;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        height: 100%;
    }
    .kpi-title {
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748b;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 29px;
        font-weight: 800;
        margin-bottom: 6px;
    }
    .kpi-sub {
        font-size: 13.5px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
    }

    /* Thẻ Giải pháp (Solution Cards) */
    .sol-card {
        padding: 18px 20px;
        border-radius: 14px;
        height: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .sol-title {
        font-size: 17px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .sol-val {
        font-size: 25px;
        font-weight: 800;
        margin: 6px 0;
    }
    .sol-desc {
        font-size: 14px;
        opacity: 0.9;
    }

    /* Làm đẹp chữ của các Tab */
    button[data-baseweb="tab"] div p {
        font-size: 17px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Hiển thị Header
st.markdown("""
<div class="main-header">
    <h1>🏦 Hệ Thống Thẩm Định Tín Dụng & Lập Kế Hoạch Trả Nợ</h1>
    <p>Phân tích chỉ số DTI, lập lịch trả nợ đa giai đoạn và mô phỏng tái cấu trúc khoản vay trực quan</p>
</div>
""", unsafe_allow_html=True)

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
# 3. THANH BÊN TRÁI (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown("## ⚙️ BẢNG ĐIỀU KHIỂN")
    
    with st.expander("💰 1. Khoản vay & Lãi suất", expanded=True):
        vay_moi = st.number_input("Số tiền vay (triệu đ)", min_value=10.0, value=700.0, step=50.0)
        thoi_han_nam = st.slider("Thời hạn vay (năm)", min_value=1, max_value=30, value=5)
        
        c_s1, c_s2 = st.columns(2)
        ls_uu_dai = c_s1.number_input("Lãi ưu đãi (%)", min_value=0.0, value=9.0, step=0.5)
        so_thang_ud = c_s2.number_input("Số kỳ ưu đãi", min_value=0, value=3, step=1)
        
        c_s3, c_s4 = st.columns(2)
        ls_huy_dong = c_s3.number_input("Lãi huy động (%)", min_value=0.0, value=10.0, step=0.5)
        bien_do = c_s4.number_input("Biên độ (%)", min_value=0.0, value=4.0, step=0.5)
        st.markdown(f"<div style='background:#eff6ff; padding:8px 12px; border-radius:8px; color:#1e40af; font-weight:700; font-size:14px;'>📈 Lãi suất thả nổi: {ls_huy_dong + bien_do:.1f}%/năm</div>", unsafe_allow_html=True)

    with st.expander("👨‍👩‍👦 2. Tài chính & Trần DTI", expanded=True):
        thu_nhap = st.number_input("Tổng thu nhập/tháng (triệu đ)", min_value=1.0, value=45.0, step=1.0)
        no_cu = st.number_input("Trả nợ cũ/tháng (triệu đ)", min_value=0.0, value=10.0, step=1.0)
        c_kh1, c_kh2 = st.columns(2)
        so_nguoi = c_kh1.number_input("Số người", min_value=1, value=3, step=1)
        phi_1_nguoi = c_kh2.number_input("Phí SH/người", min_value=0.0, value=4.0, step=0.5)
        nguong_dti = st.slider("Trần DTI Ngân hàng (%)", min_value=30, max_value=90, value=60, step=5)

    with st.expander("📅 3. Mốc thời gian & Cách tính", expanded=False):
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
# 4. XỬ LÝ TÍNH TOÁN TRUNG TÂM
# ==============================================================================
df_ke_hoach = lap_bang_tra_no(
    vay_moi, thoi_han_nam, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do,
    ngay_giai_ngan, ngay_tinh_lai, ngay_thu_lai, so_ky_xem, cach_tinh, thu_nhap, no_cu
)

tra_ky_1 = df_ke_hoach.loc[0, "Tổng trả vay mới"]
tra_ky_max = df_ke_hoach["Tổng trả vay mới"].max()
ten_ky_max = df_ke_hoach.loc[df_ke_hoach["Tổng trả vay mới"].idxmax(), "Kỳ"]

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

# --- BANNER KẾT LUẬN VỚI MÀU SẮC & CỠ CHỮ LỚN ---
if so_du_cuoi < 0:
    st.markdown(f"""
    <div class="status-banner banner-danger">
        <h3>❌ TỪ CHỐI CHO VAY — Khách hàng bị âm dòng tiền ({so_du_cuoi:,.2f} triệu/tháng)</h3>
        <p>Thu nhập sau sinh hoạt (<b>{thu_nhap_con_lai:,.2f} triệu</b>) không đủ để thanh toán tổng nghĩa vụ nợ hàng tháng (<b>{tong_no_xet:,.2f} triệu</b>). Vui lòng mở <b>Tab 3</b> bên dưới để tái cấu trúc khoản vay!</p>
    </div>
    """, unsafe_allow_html=True)
elif dti_tong <= nguong_dti:
    st.markdown(f"""
    <div class="status-banner banner-success">
        <h3>✅ ĐỦ ĐIỀU KIỆN PHÊ DUYỆT — Hệ số DTI đạt {dti_tong:.2f}% (An toàn ≤ {nguong_dti}%)</h3>
        <p>Khách hàng đảm bảo tốt khả năng thanh toán nợ và vẫn còn dư <b>{so_du_cuoi:,.2f} triệu/tháng</b> sau khi đã trừ toàn bộ chi phí sinh hoạt gia đình.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="status-banner banner-warning">
        <h3>⚠️ CẢNH BÁO VƯỢT TRẦN DTI — DTI hiện tại: {dti_tong:.2f}% (Vượt ngưỡng {nguong_dti}%)</h3>
        <p>Khách hàng vẫn dư <b>{so_du_cuoi:,.2f} triệu/tháng</b> sau sinh hoạt phí, nhưng tỷ lệ nợ trên thu nhập vượt quy định của Ngân hàng. Hãy chuyển sang <b>Tab 3</b> để xem các giải pháp hạ DTI!</p>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 5. BA TAB CHỨC NĂNG VỚI GIAO DIỆN MÀU SẮC TRỰC QUAN
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
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid #2563eb;">
            <div class="kpi-title">💰 1. Tổng thu nhập</div>
            <div class="kpi-value" style="color: #1d4ed8;">{thu_nhap:,.1f} trđ</div>
            <span class="kpi-sub" style="background: #eff6ff; color: #1e40af;">Sinh hoạt phí: -{sinh_hoat_phi:,.1f} trđ</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid #8b5cf6;">
            <div class="kpi-title">🏠 2. Thu nhập sau SH</div>
            <div class="kpi-value" style="color: #6d28d9;">{thu_nhap_con_lai:,.1f} trđ</div>
            <span class="kpi-sub" style="background: #f5f3ff; color: #5b21b6;">Gia đình {so_nguoi} người ({phi_1_nguoi} tr/người)</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        mau_no = "#dc2626" if dti_tong > nguong_dti else "#d97706"
        bg_no = "#fef2f2" if dti_tong > nguong_dti else "#fffbeb"
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid {mau_no};">
            <div class="kpi-title">💳 3. Tổng nợ phải trả/tháng</div>
            <div class="kpi-value" style="color: {mau_no};">{tong_no_xet:,.2f} trđ</div>
            <span class="kpi-sub" style="background: {bg_no}; color: {mau_no};">Mới: {tra_vay_moi_xet:,.2f} | Cũ: {no_cu:,.1f} trđ</span>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        mau_du = "#059669" if so_du_cuoi >= 0 else "#dc2626"
        bg_du = "#ecfdf5" if so_du_cuoi >= 0 else "#fef2f2"
        trang_thai_du = "Дòng tiền dương an toàn" if so_du_cuoi >= 0 else "Thâm hụt dòng tiền"
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid {mau_du};">
            <div class="kpi-title">✨ 4. Tiền dư cuối tháng</div>
            <div class="kpi-value" style="color: {mau_du};">{so_du_cuoi:,.2f} trđ</div>
            <span class="kpi-sub" style="background: {bg_du}; color: {mau_du};">{trang_thai_du}</span>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    col_t1, col_t2 = st.columns([1.2, 1])
    
    with col_t1:
        with st.container(border=True):
            st.markdown("#### 🎯 Thước đo Hệ số Nợ trên Thu nhập (DTI)")
            
            mau_dti_1 = "#10b981" if dti_tong <= nguong_dti else "#ef4444"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:16px; font-weight:700; color:#334155;">1. DTI trên Tổng thu nhập (Trần cho phép: {nguong_dti}%)</span>
                <span style="font-size:24px; font-weight:800; color:{mau_dti_1};">{dti_tong:.2f}%</span>
            </div>
            <div style="width:100%; background:#e2e8f0; height:18px; border-radius:10px; overflow:hidden; margin-bottom:22px;">
                <div style="width:{min(dti_tong, 100)}%; background:{mau_dti_1}; height:100%; border-radius:10px;"></div>
            </div>
            """, unsafe_allow_html=True)

            mau_dti_2 = "#3b82f6" if dti_rong <= 80 else "#f59e0b"
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                <span style="font-size:16px; font-weight:700; color:#334155;">2. DTI trên Thu nhập sau sinh hoạt</span>
                <span style="font-size:24px; font-weight:800; color:{mau_dti_2};">{dti_rong:.2f}%</span>
            </div>
            <div style="width:100%; background:#e2e8f0; height:18px; border-radius:10px; overflow:hidden; margin-bottom:10px;">
                <div style="width:{min(dti_rong, 100)}%; background:{mau_dti_2}; height:100%; border-radius:10px;"></div>
            </div>
            """, unsafe_allow_html=True)
            
    with col_t2:
        with st.container(border=True):
            st.markdown("#### 🧾 Bóc tách cơ cấu dòng tiền tháng đang xét")
            goc_moi_thang = vay_moi / (thoi_han_nam * 12)
            lai_ky_xet = tra_vay_moi_xet - goc_moi_thang
            st.dataframe(pd.DataFrame({
                "Khoản mục chi tiêu": ["🔹 Trả gốc vay mới", "🔸 Trả lãi vay mới", "💳 Trả nợ khoản vay cũ", "🍱 Chi phí sinh hoạt", "🏦 Số dư tích lũy còn lại"],
                "Số tiền (trđ)": [f"{goc_moi_thang:,.2f}", f"{lai_ky_xet:,.2f}", f"{no_cu:,.2f}", f"{sinh_hoat_phi:,.2f}", f"{so_du_cuoi:,.2f}"],
                "Tỷ trọng / Thu nhập": [f"{(goc_moi_thang/thu_nhap)*100:.1f}%", f"{(lai_ky_xet/thu_nhap)*100:.1f}%", f"{(no_cu/thu_nhap)*100:.1f}%", f"{(sinh_hoat_phi/thu_nhap)*100:.1f}%", f"{(so_du_cuoi/thu_nhap)*100:.1f}%"]
            }), use_container_width=True, hide_index=True)


# --- TAB 2: BẢNG KẾ HOẠCH TRẢ NỢ ĐƯỢC TÔ MÀU BẮT MẮT ---
with tab2:
    st.write("")
    with st.container(border=True):
        st.markdown(f"#### 📋 Bảng Kế hoạch trả nợ {so_ky_xem} kỳ đầu tiên (Giải ngân: {ngay_giai_ngan.strftime('%d/%m/%Y')})")
        st.markdown(f"""
        <div style="background:#f8fafc; padding:12px 18px; border-radius:10px; border:1px solid #cbd5e1; margin-bottom:15px; font-size:15.5px;">
            📌 <b>Gốc trả đều mỗi kỳ:</b> <span style="color:#1d4ed8; font-weight:800;">{vay_moi/(thoi_han_nam*12):,.2f} triệu</span> &nbsp;|&nbsp; 
            🟢 <b>Lãi suất {so_thang_ud} kỳ đầu:</b> <span style="color:#059669; font-weight:800;">{ls_uu_dai}%/năm</span> &nbsp;|&nbsp; 
            🟠 <b>Lãi suất từ kỳ {so_thang_ud+1}:</b> <span style="color:#d97706; font-weight:800;">{ls_huy_dong + bien_do}%/năm</span> ({cach_tinh})
        </div>
        """, unsafe_allow_html=True)
        
        # Hàm tô màu cho bảng Pandas
        def style_dti(val):
            if val > nguong_dti:
                return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
            return 'background-color: #dcfce7; color: #166534; font-weight: bold;'

        def style_laisuat(val):
            if val == f"{ls_uu_dai:.1f}%":
                return 'color: #059669; font-weight: bold;'
            return 'color: #d97706; font-weight: bold;'

        styled_df = df_ke_hoach.style.format({
            "Dư nợ đầu kỳ": "{:,.2f}",
            "Trả gốc": "{:,.2f}",
            "Trả lãi": "{:,.2f}",
            "Tổng trả vay mới": "{:,.2f}",
            "DTI kỳ này (%)": "{:.2f}%",
            "Dư nợ cuối kỳ": "{:,.2f}",
        }).map(style_dti, subset=["DTI kỳ này (%)"])\
          .map(style_laisuat, subset=["Lãi suất"])\
          .set_properties(subset=["Tổng trả vay mới"], **{'background-color': '#eff6ff', 'color': '#1e40af', 'font-weight': 'bold'})

        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        tong_goc = df_ke_hoach["Trả gốc"].sum()
        tong_lai = df_ke_hoach["Trả lãi"].sum()
        st.markdown(f"""
        <div style="background: linear-gradient(to right, #eff6ff, #dbeafe); padding: 16px 22px; border-radius: 12px; border-left: 6px solid #2563eb; margin-top: 10px; font-size: 16px; color: #1e3a8a;">
            💡 <b>Tổng kết sau {so_ky_xem} kỳ đầu tiên:</b> Khách hàng đã thanh toán <b>{tong_goc:,.2f} triệu</b> nợ gốc + <b>{tong_lai:,.2f} triệu</b> tiền lãi = <b style="font-size:19px; color:#1d4ed8;">{tong_goc + tong_lai:,.2f} triệu đồng</b>.
        </div>
        """, unsafe_allow_html=True)


# --- TAB 3: GIẢI PHÁP ĐỀ XUẤT & BẢNG TÙY CHỈNH ---
with tab3:
    st.write("")
    st.markdown("#### 💡 1. Bốn Giải Pháp Độc Lập Giúp Đưa DTI Về Ngưỡng An Toàn")
    
    tong_no_muc_tieu = min(thu_nhap * (nguong_dti / 100), thu_nhap_con_lai)
    tra_vay_moi_toi_da = tong_no_muc_tieu - no_cu
    thang_hien_tai = thoi_han_nam * 12
    ls_thang_xet = (ls_xet_nam / 100) / 12
    ty_le_du_no = du_no_xet / vay_moi if vay_moi > 0 else 1.0

    if so_du_cuoi >= 0 and dti_tong <= nguong_dti:
        st.success(f"🎉 Hồ sơ hiện tại đã đạt chuẩn phê duyệt (DTI = **{dti_tong:.2f}%** ≤ **{nguong_dti}%**). Bạn vẫn có thể thử nghiệm bảng mô phỏng phía dưới nếu muốn tối ưu thêm.")
        vay_toi_da = vay_moi
    else:
        st.markdown(f"<p style='font-size:15.5px; color:#475569;'>Để đạt chuẩn phê duyệt (DTI ≤ <b>{nguong_dti}%</b>), tổng nợ hàng tháng cần giảm từ <b style='color:#dc2626;'>{tong_no_xet:,.2f} trđ</b> xuống tối đa <b style='color:#059669;'>{tong_no_muc_tieu:,.2f} trđ/tháng</b>:</p>", unsafe_allow_html=True)
        
        g1, g2, g3, g4 = st.columns(4)
        
        # GP 1: Giảm tiền vay (Tone Xanh Dương)
        with g1:
            if tra_vay_moi_toi_da <= 0:
                vay_toi_da = 0.0
                noi_dung_gp1 = "<div class='sol-val' style='color:#dc2626;'>Không khả thi</div><div class='sol-desc'>Nợ cũ đã vượt trần DTI, cần tất toán nợ cũ trước.</div>"
            else:
                vay_toi_da = tra_vay_moi_toi_da / ((1 / thang_hien_tai) + ls_thang_xet * ty_le_du_no)
                noi_dung_gp1 = f"<div class='sol-val' style='color:#1d4ed8;'>{vay_toi_da:,.1f} triệu</div><div class='sol-desc'>Cần giảm bớt <b>{vay_moi - vay_toi_da:,.1f} triệu</b> tiền vay (tăng vốn tự có).</div>"
            
            st.markdown(f"""
            <div class="sol-card" style="background:#eff6ff; border: 1px solid #bfdbfe; border-top: 5px solid #2563eb; color:#1e3a8a;">
                <div class="sol-title">📉 GP 1: Giảm số tiền vay</div>
                {noi_dung_gp1}
            </div>
            """, unsafe_allow_html=True)

        # GP 2: Kéo dài kỳ hạn (Tone Tím)
        with g2:
            lai_xet_hien_tai = du_no_xet * ls_thang_xet
            if tra_vay_moi_toi_da <= lai_xet_hien_tai:
                noi_dung_gp2 = f"<div class='sol-val' style='color:#dc2626;'>Vượt quá lãi</div><div class='sol-desc'>Tiền lãi ({lai_xet_hien_tai:,.2f} trđ) đã vượt mức trả tối đa.</div>"
            else:
                thang_can = vay_moi / (tra_vay_moi_toi_da - lai_xet_hien_tai)
                nam_can = math.ceil(thang_can / 12)
                if nam_can <= 30:
                    noi_dung_gp2 = f"<div class='sol-val' style='color:#6d28d9;'>{nam_can} năm ({math.ceil(thang_can)} tháng)</div><div class='sol-desc'>Tăng thêm <b>{nam_can - thoi_han_nam} năm</b> so với phương án gốc ({thoi_han_nam} năm).</div>"
                else:
                    noi_dung_gp2 = f"<div class='sol-val' style='color:#d97706;'>{nam_can} năm (>30 năm)</div><div class='sol-desc'>Vượt kỳ hạn tối đa của NH, nên kết hợp giảm tiền vay.</div>"

            st.markdown(f"""
            <div class="sol-card" style="background:#f5f3ff; border: 1px solid #ddd6fe; border-top: 5px solid #7c3aed; color:#4c1d95;">
                <div class="sol-title">⏳ GP 2: Kéo dài kỳ hạn</div>
                {noi_dung_gp2}
            </div>
            """, unsafe_allow_html=True)

        # GP 3: Thêm thu nhập (Tone Xanh Lá)
        with g3:
            tn_can = max(tong_no_xet / (nguong_dti / 100), tong_no_xet + sinh_hoat_phi)
            can_them = tn_can - thu_nhap
            st.markdown(f"""
            <div class="sol-card" style="background:#ecfdf5; border: 1px solid #a7f3d0; border-top: 5px solid #10b981; color:#065f46;">
                <div class="sol-title">💰 GP 3: Bổ sung thu nhập</div>
                <div class="sol-val" style="color:#059669;">+{can_them:,.1f} triệu/tháng</div>
                <div class="sol-desc">Nâng tổng thu nhập chứng minh lên mức <b>{tn_can:,.1f} triệu/tháng</b>.</div>
            </div>
            """, unsafe_allow_html=True)

        # GP 4: Cơ cấu nợ cũ (Tone Cam)
        with g4:
            no_can_giam = tong_no_xet - tong_no_muc_tieu
            if no_cu == 0:
                noi_dung_gp4 = "<div class='sol-val' style='color:#9a3412;'>0 triệu</div><div class='sol-desc'>Khách hàng hiện không có khoản nợ cũ nào.</div>"
            elif no_cu >= no_can_giam:
                noi_dung_gp4 = f"<div class='sol-val' style='color:#d97706;'>-{no_can_giam:,.2f} triệu/tháng</div><div class='sol-desc'>Tất toán bớt nợ cũ để giảm nghĩa vụ xuống còn <b>{no_cu - no_can_giam:,.1f} trđ/tháng</b>.</div>"
            else:
                noi_dung_gp4 = f"<div class='sol-val' style='color:#dc2626;'>Thiếu {no_can_giam - no_cu:,.2f} trđ</div><div class='sol-desc'>Dù tất toán hết {no_cu:,.1f} trđ nợ cũ vẫn cần kết hợp GP 1 hoặc 2.</div>"

            st.markdown(f"""
            <div class="sol-card" style="background:#fffbeb; border: 1px solid #fde68a; border-top: 5px solid #f59e0b; color:#92400e;">
                <div class="sol-title">💳 GP 4: Tất toán nợ cũ</div>
                {noi_dung_gp4}
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.divider()

    # PHẦN 3B: BẢNG TÙY CHỈNH KẾT HỢP
    st.markdown("#### 🎛️ 2. Bảng Mô Phỏng Tùy Chỉnh & So Sánh Trực Tiếp")
    st.caption("Kéo chỉnh các thông số dưới đây để kết hợp nhiều giải pháp và xem ngay sự thay đổi giữa Phương án Gốc và Phương án Mới:")

    with st.container(border=True):
        tc1, tc2, tc3, tc4 = st.columns(4)
        with tc1:
            vay_dc = st.number_input("1. Số tiền vay mới (trđ)", min_value=10.0, max_value=float(vay_moi*2), value=float(round(min(vay_moi, vay_toi_da), 0)) if (dti_tong > nguong_dti and vay_toi_da >= 10) else float(vay_moi), step=10.0)
        with tc2:
            nam_dc = st.slider("2. Thời hạn vay mới (năm)", min_value=1, max_value=30, value=thoi_han_nam)
        with tc3:
            tn_them = st.number_input("3. Thu nhập bổ sung (trđ)", min_value=0.0, value=0.0, step=1.0)
        with tc4:
            no_cu_giam = st.number_input("4. Giảm trả nợ cũ/tháng (trđ)", min_value=0.0, max_value=float(no_cu), value=0.0, step=1.0)

        tn_moi = thu_nhap + tn_them
        nc_moi = no_cu - no_cu_giam
        df_moi = lap_bang_tra_no(vay_dc, nam_dc, ls_uu_dai, so_thang_ud, ls_huy_dong, bien_do, ngay_giai_ngan, ngay_tinh_lai, ngay_thu_lai, so_ky_xem, cach_tinh, tn_moi, nc_moi)
        
        tra_moi_xet = df_moi.loc[0, "Tổng trả vay mới"] if dang_xet_ky_1 else df_moi["Tổng trả vay mới"].max()
        tong_no_moi = nc_moi + tra_moi_xet
        dti_moi = (tong_no_moi / tn_moi) * 100
        du_moi = (tn_moi - sinh_hoat_phi) - tong_no_moi

        df_so_sanh = pd.DataFrame({
            "Chỉ tiêu đánh giá": ["Số tiền vay", "Thời hạn vay", "Tổng thu nhập", "Trả nợ cũ/tháng", "Trả vay mới/tháng (kỳ xét)", "Tổng nghĩa vụ nợ/tháng", "Tiền dư sau sinh hoạt", "HỆ SỐ DTI (%)", "KẾT QUẢ PHÊ DUYỆT"],
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
        })

        def style_comparison(col):
            if col.name == "Phương Án Tùy Chỉnh (Mới)":
                return ['background-color: #f0fdf4; color: #166534; font-weight: bold;' if (dti_moi <= nguong_dti and du_moi >= 0) else 'background-color: #fffbeb; color: #92400e; font-weight: bold;' for _ in col]
            return ['' for _ in col]

        st.dataframe(df_so_sanh.style.apply(style_comparison, axis=0), use_container_width=True, hide_index=True)

        with st.expander("📋 Xem Bảng kế hoạch trả nợ mới sau khi tùy chỉnh"):
            st.dataframe(
                df_moi.style.format({
                    "Dư nợ đầu kỳ": "{:,.2f}", "Trả gốc": "{:,.2f}", "Trả lãi": "{:,.2f}",
                    "Tổng trả vay mới": "{:,.2f}", "DTI kỳ này (%)": "{:.2f}%", "Dư nợ cuối kỳ": "{:,.2f}"
                }).map(style_dti, subset=["DTI kỳ này (%)"]),
                use_container_width=True, hide_index=True
            )
