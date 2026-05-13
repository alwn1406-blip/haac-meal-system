import streamlit as st
import gspread
import json
import pandas as pd
from io import BytesIO
from google.oauth2.service_account import Credentials
from datetime import datetime, date, timedelta

st.set_page_config(page_title="HAAC 현장 식수 신청 시스템", layout="wide")

# =========================
# 구글시트 연결
# =========================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"])

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
        {"이름": "김경욱", "직책": "팀장"},
        {"이름": "배재석", "직책": "사원"},
        {"이름": "조문규", "직책": "사원"},
    ],
}

direct_groups = ["전장", "전장(자재)"]
vendor_groups = ["준우", "삼보", "더원", "TOP", "ATS"]
groups = direct_groups + vendor_groups

# =========================
# 공통 함수
# =========================
def meal_value(value):
    if value == "Y":
        return 1
    try:
        return int(value)
    except:
        return 0


def set_all_checks(group, view_mode, meal_type, value):
    people = employee_data[group]
    prefix = "pc" if view_mode == "PC" else "mobile"

    for idx in range(len(people)):
        key = f"{prefix}_{group}_{idx}_{meal_type}"
        st.session_state[key] = value


# =========================
# 상단
# =========================
st.markdown("# 🍽️ HAAC 현장 식수 신청 시스템")

admin_check = st.checkbox("관리자 모드")

if admin_check:
    admin_password = st.text_input("관리자 비밀번호", type="password")
    is_admin = admin_password == "0727"
else:
    is_admin = False

if is_admin:
    mode = st.radio("메뉴 선택", ["식수 신청", "관리자"], horizontal=True)
else:
    mode = "식수 신청"

# =========================
# 식수 신청 화면
# =========================
if mode == "식수 신청":

    date_mode = st.radio(
        "신청 방식",
        ["하루 신청", "기간 일괄 신청"],
        horizontal=True
    )

    if date_mode == "하루 신청":
        selected_date = st.date_input("식사 일자 선택", value=date.today())
        meal_dates = [selected_date]
    else:
        col_start, col_end = st.columns(2)

        with col_start:
            start_date = st.date_input("시작일", value=date.today())

        with col_end:
            end_date = st.date_input("종료일", value=date.today())

        if end_date < start_date:
            st.error("종료일은 시작일보다 빠를 수 없어.")
            st.stop()

        meal_dates = [
            start_date + timedelta(days=i)
            for i in range((end_date - start_date).days + 1)
        ]

        st.info(f"{start_date} ~ {end_date}, 총 {len(meal_dates)}일 신청")

    selected_group = st.selectbox("구분 선택", groups)

    view_mode = st.radio(
        "화면 모드 선택",
        ["PC", "모바일"],
        horizontal=True
    )

    result_rows = []

    # =========================
    # 전장 / 전장(자재)
    # =========================
    if selected_group in direct_groups:

        st.markdown(f"## 👥 {selected_group} 명단")

        people = employee_data[selected_group]

        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            if st.button("중식 전체 선택"):
                set_all_checks(selected_group, view_mode, "lunch", True)
                st.rerun()

        with col_btn2:
            if st.button("중식 전체 해제"):
                set_all_checks(selected_group, view_mode, "lunch", False)
                st.rerun()

        with col_btn3:
            if st.button("석식 전체 선택"):
                set_all_checks(selected_group, view_mode, "dinner", True)
                st.rerun()

        with col_btn4:
            if st.button("석식 전체 해제"):
                set_all_checks(selected_group, view_mode, "dinner", False)
                st.rerun()

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

                lunch_key = f"pc_{selected_group}_{idx}_lunch"
                dinner_key = f"pc_{selected_group}_{idx}_dinner"

                with c1:
                    st.markdown(f'<div class="data-row">{selected_group}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="data-row">{person["직책"]}</div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="data-row">{person["이름"]}</div>', unsafe_allow_html=True)
                with c4:
                    lunch = st.checkbox("", key=lunch_key)
                with c5:
                    dinner = st.checkbox("", key=dinner_key)

                if lunch or dinner:
                    result_rows.append({
                        "구분": selected_group,
                        "이름": person["이름"],
                        "직책": person["직책"],
                        "중식": "Y" if lunch else "",
                        "석식": "Y" if dinner else "",
                    })

        else:
            for idx, person in enumerate(people):

                lunch_key = f"mobile_{selected_group}_{idx}_lunch"
                dinner_key = f"mobile_{selected_group}_{idx}_dinner"

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
                    lunch = st.checkbox("중식", key=lunch_key)

                with col_m2:
                    dinner = st.checkbox("석식", key=dinner_key)

                if lunch or dinner:
                    result_rows.append({
                        "구분": selected_group,
                        "이름": person["이름"],
                        "직책": person["직책"],
                        "중식": "Y" if lunch else "",
                        "석식": "Y" if dinner else "",
                    })

    # =========================
    # 업체 인원수 입력
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
                "구분": selected_group,
                "이름": "업체인원",
                "직책": "-",
                "중식": int(lunch_count),
                "석식": int(dinner_count),
            })

    st.divider()

    if st.button("제출"):
        if not result_rows:
            st.error("입력된 식수 인원이 없어.")
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for meal_date in meal_dates:
                for row in result_rows:
                    sheet.append_row([
                        now,
                        str(meal_date),
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

    st.markdown("### 📊 식수 집계 엑셀 다운로드")

    start_date = st.date_input("시작일", value=date.today() - timedelta(days=7))
    end_date = st.date_input("종료일", value=date.today())

    if st.button("엑셀 생성"):

        records = sheet.get_all_records()
        df = pd.DataFrame(records)

        if df.empty:
            st.error("구글시트에 데이터가 없어.")
        else:
            df["날짜"] = pd.to_datetime(df["날짜"]).dt.date

            filtered_df = df[
                (df["날짜"] >= start_date) &
                (df["날짜"] <= end_date)
            ]

            if filtered_df.empty:
                st.error("선택한 기간에 데이터가 없어.")
            else:
                summary_df = filtered_df.copy()

                summary_df["중식수"] = summary_df["중식"].apply(meal_value)
                summary_df["석식수"] = summary_df["석식"].apply(meal_value)

                group_summary = summary_df.groupby("구분")[["중식수", "석식수"]].sum().reset_index()
                date_summary = summary_df.groupby("날짜")[["중식수", "석식수"]].sum().reset_index()

                output = BytesIO()

                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name="원본데이터")
                    group_summary.to_excel(writer, index=False, sheet_name="구분별집계")
                    date_summary.to_excel(writer, index=False, sheet_name="일자별집계")

                output.seek(0)

                file_name = f"식수집계_{start_date}_{end_date}.xlsx"

                st.download_button(
                    label="엑셀 다운로드",
                    data=output,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
