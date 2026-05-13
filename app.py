import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime, date

st.set_page_config(page_title="HAAC 현장 식수 신청 시스템", layout="wide")

# =========================
# 구글시트 연결
# =========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = json.loads(
    st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"]
)

creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=scope
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(
    "14JzikRFubHFg7atCi3JYOqBbQOTQc7LC_jYKZ_sAxTU"
)

sheet = spreadsheet.worksheet("식수결과")

# =========================
# 디자인
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}

h1, h2, h3 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.header-row {
    background-color: #1f222b;
    padding: 10px 8px;
    border-radius: 6px 6px 0 0;
    border-bottom: 1px solid #343946;
    font-weight: 700;
    color: #cbd5e1;
}

.data-row {
    padding: 8px 8px;
    border-bottom: 1px solid #2b303b;
    font-weight: 600;
}

.mobile-card {
    background-color: #1f222b;
    padding: 14px;
    border-radius: 12px;
    margin-top: 14px;
    margin-bottom: 8px;
    border: 1px solid #343946;
}

.mobile-name {
    font-size: 18px;
    font-weight: 800;
    color: white;
}

.mobile-info {
    font-size: 14px;
    color: #cbd5e1;
    margin-top: 4px;
}

.vendor-box {
    background-color: #1f222b;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #343946;
    margin-top: 20px;
    margin-bottom: 20px;
}

.stButton > button {
    width: 100%;
    height: 48px;
    font-size: 18px;
    font-weight: 800;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 명단 데이터
# =========================
employee_data = {
    "전장": [
        {"이름": "이재민", "직책": "팀장"},
        {"이름": "이경화", "직책": "조장"},
        {"이름": "이동건", "직책": "조장"},
        {"이름": "김보성", "직책": "사원"},
        {"이름": "나춘미", "직책": "사원"},
        {"이름": "곽도민", "직책": "사원"},
        {"이름": "정준식", "직책": "사원"},
        {"이름": "박진규", "직책": "사원"},
        {"이름": "김택성", "직책": "사원"},
        {"이름": "신종훈", "직책": "사원"},
        {"이름": "조명희", "직책": "사원"},
    ],
    "전장(자재)": [
        {"이름": "김경욱", "직책": "팀장"},
        {"이름": "배재석", "직책": "사원"},
        {"이름": "조문규", "직책": "사원"},
    ],
}

direct_groups = ["전장", "전장(자재)"]
vendor_groups = ["준우", "삼보", "더원", "TOP", "ATS"]
groups = direct_groups + vendor_groups

# =========================
# 상단 제목
# =========================
st.markdown("# 🍽️ HAAC 현장 식수 신청 시스템")

# =========================
# 관리자 모드
# =========================
admin_check = st.checkbox("관리자 모드")

if admin_check:
    admin_password = st.text_input(
        "관리자 비밀번호",
        type="password"
    )
    is_admin = admin_password == "0727"
else:
    is_admin = False

if is_admin:
    mode = st.radio(
        "메뉴 선택",
        ["식수 신청", "관리자"],
        horizontal=True
    )
else:
    mode = "식수 신청"

# =========================
# 식수 신청 화면
# =========================
if mode == "식수 신청":

    col_date, col_group = st.columns(2)

    with col_date:
        meal_date = st.date_input("식사 일자 선택", value=date.today())

    with col_group:
        selected_group = st.selectbox("구분 선택", groups)

    view_mode = st.radio(
        "화면 모드 선택",
        ["PC", "모바일"],
        horizontal=True
    )

    result_rows = []

    # =========================
    # 전장 / 전장(자재): 사람별 체크
    # =========================
    if selected_group in direct_groups:

        st.markdown(f"## 👥 {selected_group} 명단")

        people = employee_data[selected_group]

        col_all1, col_all2, col_blank = st.columns([1, 1, 4])

        with col_all1:
            all_lunch = st.checkbox(
                "중식 전체 선택",
                key=f"{view_mode}_{selected_group}_all_lunch"
            )

        with col_all2:
            all_dinner = st.checkbox(
                "석식 전체 선택",
                key=f"{view_mode}_{selected_group}_all_dinner"
            )

        # =========================
        # PC 화면
        # =========================
        if view_mode == "PC":

            h1, h2, h3, h4, h5 = st.columns([1.5, 1.5, 1.5, 1, 1])

            with h1:
                st.markdown('<div class="header-row">소속</div>', unsafe_allow_html=True)

            with h2:
                st.markdown('<div class="header-row">직책</div>', unsafe_allow_html=True)

            with h3:
                st.markdown('<div class="header-row">이름</div>', unsafe_allow_html=True)

            with h4:
                st.markdown('<div class="header-row">중식</div>', unsafe_allow_html=True)

            with h5:
                st.markdown('<div class="header-row">석식</div>', unsafe_allow_html=True)

            for idx, person in enumerate(people):
                c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1, 1])

                with c1:
                    st.markdown(
                        f'<div class="data-row">{selected_group}</div>',
                        unsafe_allow_html=True
                    )

                with c2:
                    st.markdown(
                        f'<div class="data-row">{person["직책"]}</div>',
                        unsafe_allow_html=True
                    )

                with c3:
                    st.markdown(
                        f'<div class="data-row">{person["이름"]}</div>',
                        unsafe_allow_html=True
                    )

                with c4:
                    lunch = st.checkbox(
                        "",
                        value=all_lunch,
                        key=f"pc_{selected_group}_{idx}_lunch"
                    )

                with c5:
                    dinner = st.checkbox(
                        "",
                        value=all_dinner,
                        key=f"pc_{selected_group}_{idx}_dinner"
                    )

                if lunch or dinner:
                    result_rows.append({
                        "입력시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "날짜": str(meal_date),
                        "구분": selected_group,
                        "이름": person["이름"],
                        "직책": person["직책"],
                        "중식": "Y" if lunch else "",
                        "석식": "Y" if dinner else "",
                    })

        # =========================
        # 모바일 화면
        # =========================
        else:
            for idx, person in enumerate(people):

                st.markdown(
                    f"""
                    <div class="mobile-card">
                        <div class="mobile-name">{person["이름"]}</div>
                        <div class="mobile-info">{selected_group} / {person["직책"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_m1, col_m2 = st.columns(2)

                with col_m1:
                    lunch = st.checkbox(
                        "중식",
                        value=all_lunch,
                        key=f"mobile_{selected_group}_{idx}_lunch"
                    )

                with col_m2:
                    dinner = st.checkbox(
                        "석식",
                        value=all_dinner,
                        key=f"mobile_{selected_group}_{idx}_dinner"
                    )

                if lunch or dinner:
                    result_rows.append({
                        "입력시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "날짜": str(meal_date),
                        "구분": selected_group,
                        "이름": person["이름"],
                        "직책": person["직책"],
                        "중식": "Y" if lunch else "",
                        "석식": "Y" if dinner else "",
                    })

    # =========================
    # 업체: 인원수 입력
    # =========================
    else:
        st.markdown(f"## 🏢 {selected_group} 식수 인원 입력")

        st.markdown(
            f"""
            <div class="vendor-box">
                <h3>{selected_group}</h3>
                <p style="color:#cbd5e1;">업체 인원은 이름 없이 중식/석식 인원수만 입력합니다.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_v1, col_v2 = st.columns(2)

        with col_v1:
            lunch_count = st.number_input(
                "중식 인원",
                min_value=0,
                step=1,
                key=f"{selected_group}_lunch_count"
            )

        with col_v2:
            dinner_count = st.number_input(
                "석식 인원",
                min_value=0,
                step=1,
                key=f"{selected_group}_dinner_count"
            )

        if lunch_count > 0 or dinner_count > 0:
            result_rows.append({
                "입력시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "날짜": str(meal_date),
                "구분": selected_group,
                "이름": "업체인원",
                "직책": "-",
                "중식": int(lunch_count),
                "석식": int(dinner_count),
            })

    st.divider()

    # =========================
    # 제출 → 구글시트 저장
    # =========================
    if st.button("제출"):
        if not result_rows:
            st.error("입력된 식수 인원이 없어.")
        else:
            for row in result_rows:
                sheet.append_row([
                    row["입력시간"],
                    row["날짜"],
                    row["구분"],
                    row["이름"],
                    row["직책"],
                    row["중식"],
                    row["석식"]
                ])

            st.success("제출완료!")

# =========================
# 관리자 화면
# =========================
elif mode == "관리자":

    st.markdown("## 🔒 관리자 모드")
    st.success("관리자 로그인 완료")

    st.info("여기에 주간 엑셀 다운로드 기능이 추가될 예정입니다.")
