import streamlit as st
import gspread
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

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes=scope
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key("14JzikRFubHFg7atCi3JYOqBbQOTQc7LC_jYKZ_sAxTU")
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
    "준우": [
        {"이름": "조한주", "직책": "사장"},
        {"이름": "허경아", "직책": "사원"},
        {"이름": "김은미", "직책": "사원"},
        {"이름": "이진수", "직책": "사원"},
        {"이름": "전창규", "직책": "사원"},
    ],
    "삼보": [
        {"이름": "박소영", "직책": "사장"},
        {"이름": "채수복", "직책": "사원"},
        {"이름": "박병직", "직책": "반장"},
        {"이름": "이원일", "직책": "사원"},
        {"이름": "허정란", "직책": "대리"},
        {"이름": "김민정", "직책": "사원"},
    ],
    "더원": [
        {"이름": "이상헌", "직책": "사장"},
        {"이름": "양현성", "직책": "반장"},
        {"이름": "황성근", "직책": "기사"},
        {"이름": "김병규", "직책": "기사"},
    ],
    "TOP": [
        {"이름": "허재열", "직책": "사장"},
        {"이름": "허문성", "직책": "차장"},
    ],
    "ATS": [
        {"이름": "강종대", "직책": "팀장"},
        {"이름": "김종권", "직책": "이사"},
        {"이름": "박태용", "직책": "사원"},
        {"이름": "최학진", "직책": "사원"},
        {"이름": "이승원", "직책": "사원"},
        {"이름": "이승민", "직책": "사원"},
    ],
}

groups = list(employee_data.keys())

# =========================
# 화면
# =========================
st.markdown("# 🍽️ HAAC 현장 식수 신청 시스템")

col_date, col_group = st.columns(2)

with col_date:
    meal_date = st.date_input("식사 일자 선택", value=date.today())

with col_group:
    selected_group = st.selectbox("소속팀 선택", groups)

st.markdown(f"## 👥 {selected_group} 명단")

people = employee_data[selected_group]

col_all1, col_all2, col_blank = st.columns([1, 1, 4])

with col_all1:
    all_lunch = st.checkbox("중식 전체 선택", key=f"{selected_group}_all_lunch")

with col_all2:
    all_dinner = st.checkbox("석식 전체 선택", key=f"{selected_group}_all_dinner")

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

result_rows = []

for idx, person in enumerate(people):
    c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1, 1])

    with c1:
        st.markdown(f'<div class="data-row">{selected_group}</div>', unsafe_allow_html=True)

    with c2:
        st.markdown(f'<div class="data-row">{person["직책"]}</div>', unsafe_allow_html=True)

    with c3:
        st.markdown(f'<div class="data-row">{person["이름"]}</div>', unsafe_allow_html=True)

    with c4:
        lunch = st.checkbox("", value=all_lunch, key=f"{selected_group}_{idx}_lunch")

    with c5:
        dinner = st.checkbox("", value=all_dinner, key=f"{selected_group}_{idx}_dinner")

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

st.divider()

# =========================
# 제출 → 구글시트 저장
# =========================
if st.button("제출"):
    if not result_rows:
        st.error("체크된 인원이 없어.")
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