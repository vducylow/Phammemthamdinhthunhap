import streamlit as st
import math

# 1. CẤU HÌNH TRANG RỘNG RÃI & GỌN GÀNG
st.set_page_config(page_title="Thẩm định vay vốn - DTI", page_icon="🏦", layout="wide")

st.title("🏦 Bảng Thẩm Định Hệ Số Nợ Trên Thu Nhập (DTI)")
st.caption("Điều chỉnh các thông số ở thanh bên trái (Sidebar) để xem kết quả phân tích và gợi ý cấu trúc lại khoản vay.")

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
    nguong_dti = st.slider("Trần DTI cho phép (%)", min_value=30, max_value=90, value=60, step=5)

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

# --- 4. MÀN HÌNH CHÍNH: HIỂN THỊ KẾT QUẢ ---

if so_du_cuoi_cung < 0:
    st.error(f"### ❌ TỪ CHỐI CHO VAY\n**Lý do:** Khách hàng bị âm dòng tiền (**{so_du_cuoi_cung:,.2f} triệu/tháng**). Thu nhập sau sinh hoạt không đủ trả nợ.")
elif dti_tong <= nguong_dti:
    st.success(f"### ✅ ĐỦ ĐIỀU KIỆN CHO VAY\n**Đánh giá:** Hệ số DTI đạt **{dti_tong:.1f}%** (nằm trong ngưỡng an toàn $\le$ {nguong_dti}%). Khách hàng vẫn dư **{so_du_cuoi_cung:,.2f} triệu/tháng** sau khi trả mọi chi phí.")
else:
    st.warning(f"### ⚠️ CẦN XEM XÉT LẠI (VƯỢT TRẦN DTI)\n**Đánh giá:** Khách hàng vẫn dư **{so_du_cuoi_cung:,.2f} triệu/tháng**, nhưng DTI hiện tại là **{dti_tong:.1f}%** (vượt quy định {nguong_dti}% của ngân hàng).")

st.write("")

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

left_col, right_col = st.columns([1.2, 1])

with left_col:
    with st.container(border=True):
        st.markdown("#### 🎯 Đo lường Hệ số DTI")
        st.write(f"**DTI trên Tổng thu nhập:** `{dti_tong:.2f}%` *(Ngưỡng cho phép: {nguong_dti}%)*")
        st.progress(min(int(dti_tong), 100))
        st.write("")
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

# --- 5. PHẦN MỚI: ĐỀ XUẤT GIẢI PHÁP TỐI ƯU DTI ---
st.divider()
st.subheader("💡 Đề xuất giải pháp đưa DTI về mức phù hợp")

# Mức tổng nợ tối đa cho phép mỗi tháng (đảm bảo thỏa mãn cả trần DTI và không bị âm tiền sinh hoạt)
tong_no_toi_da_dti = thu_nhap * (nguong_dti / 100)
tong_no_muc_tieu = min(tong_no_toi_da_dti, thu_nhap_con_lai)
tra_vay_moi_toi_da = tong_no_muc_tieu - no_cu

if so_du_cuoi_cung >= 0 and dti_tong <= nguong_dti:
    st.info(f"🎉 Hồ sơ hiện tại đã đạt chuẩn (DTI = **{dti_tong:.1f}%** $\le$ **{nguong_dti}%**). Không cần điều chỉnh thêm!")
else:
    st.markdown(f"Để hồ sơ được duyệt (Tổng nợ/tháng không vượt quá **{tong_no_muc_tieu:,.2f} triệu đ**), khách hàng có thể chọn **1 trong 4 giải pháp** sau:")
    
    g1, g2 = st.columns(2)
    
    # GIẢI PHÁP 1: GIẢM SỐ TIỀN VAY
    with g1:
        with st.container(border=True):
            st.markdown("##### 📉 Giải pháp 1: Giảm số tiền vay")
            if tra_vay_moi_toi_da <= 0:
                st.error("Khoản nợ cũ đã vượt ngưỡng trả nợ cho phép. Không thể vay thêm nếu không tất toán nợ cũ.")
            else:
                if phuong_thuc == "Dư nợ giảm dần (Tháng đầu)":
                    vay_toi_da = tra_vay_moi_toi_da / ((1 / thang) + lai_thang)
                else:
                    he_so_pmt = (lai_thang * (1 + lai_thang)**thang) / ((1 + lai_thang)**thang - 1) if lai_thang > 0 else (1 / thang)
                    vay_toi_da = tra_vay_moi_toi_da / he_so_pmt
                
                can_giam = vay_moi - vay_toi_da
                st.write(f"- Số tiền vay tối đa nên duyệt: **{vay_toi_da:,.1f} triệu đ**")
                st.write(f"- Cần giảm bớt: **{can_giam:,.1f} triệu đ** *(tăng vốn tự có)*")

    # GIẢI PHÁP 2: KÉO DÀI THỜI GIAN VAY
    with g2:
        with st.container(border=True):
            st.markdown("##### ⏳ Giải pháp 2: Kéo dài thời gian vay")
            # Chỉ kéo dài được khi tiền trả tối đa lớn hơn tiền lãi tháng đầu
            if tra_vay_moi_toi_da <= lai_thang * vay_moi:
                st.warning("Mức trả nợ cho phép hàng tháng hiện thấp hơn cả tiền lãi phát sinh (**" + f"{lai_thang * vay_moi:,.2f} trđ" + "**), nên kéo dài thời gian vay một mình sẽ không giải quyết được.")
            else:
                if phuong_thuc == "Dư nợ giảm dần (Tháng đầu)":
                    thang_can_thiet = vay_moi / (tra_vay_moi_toi_da - vay_moi * lai_thang)
                else:
                    # Tính số kỳ hạn N từ công thức PMT bằng logarit
                    thang_can_thiet = -math.log(1 - (vay_moi * lai_thang) / tra_vay_moi_toi_da) / math.log(1 + lai_thang)
                
                nam_can_thiet = math.ceil(thang_can_thiet / 12)
                if nam_can_thiet <= 30:
                    st.write(f"- Nâng thời hạn vay từ **{thoi_han_nam} năm** lên ít nhất **{nam_can_thiet} năm** ({math.ceil(thang_can_thiet)} tháng).")
                    st.write(f"- Khi đó tiền trả hàng tháng sẽ giảm về mức an toàn.")
                else:
                    st.warning(f"Cần kéo dài tới **{nam_can_thiet} năm** (vượt quá giới hạn cho vay thông thường 25-30 năm của ngân hàng). Nên kết hợp giảm tiền vay.")

    g3, g4 = st.columns(2)

    # GIẢI PHÁP 3: CHỨNG MINH THÊM THU NHẬP / ĐỒNG TRẢ NỢ
    with g3:
        with st.container(border=True):
            st.markdown("##### 💰 Giải pháp 3: Bổ sung thu nhập / Đồng trả nợ")
            thu_nhap_can_dti = tong_no / (nguong_dti / 100)
            thu_nhap_can_sh = tong_no + sinh_hoat_phi
            thu_nhap_muc_tieu = max(thu_nhap_can_dti, thu_nhap_can_sh)
            can_tang_them = thu_nhap_muc_tieu - thu_nhap
            
            st.write(f"- Tổng thu nhập cần đạt: **{thu_nhap_muc_tieu:,.1f} triệu đ/tháng**")
            st.write(f"- Cần chứng minh thêm: **+{can_tang_them:,.1f} triệu đ/tháng** *(từ lương, cho thuê tài sản, hoặc thêm người đồng trả nợ)*.")

    # GIẢI PHÁP 4: TẤT TOÁN BỚT NỢ CŨ
    with g4:
        with st.container(border=True):
            st.markdown("##### 💳 Giải pháp 4: Tất toán/Cơ cấu khoản nợ cũ")
            no_cu_can_giam = tong_no - tong_no_muc_tieu
            if no_cu == 0:
                st.write("- Khách hàng hiện không có nợ cũ, bỏ qua giải pháp này.")
            elif no_cu >= no_cu_can_giam:
                st.write(f"- Tất toán một phần nợ cũ để giảm nghĩa vụ trả nợ cũ từ **{no_cu:,.1f} triệu** xuống còn **{(no_cu - no_cu_can_giam):,.1f} triệu/tháng** (giảm **{no_cu_can_giam:,.2f} triệu/tháng**).")
            else:
                st.write(f"- Kể cả khi tất toán hết **{no_cu:,.1f} triệu/tháng** nợ cũ, khách hàng vẫn thiếu hụt **{(no_cu_can_giam - no_cu):,.2f} triệu/tháng**. Cần kết hợp thêm giải pháp 1 hoặc 2.")
