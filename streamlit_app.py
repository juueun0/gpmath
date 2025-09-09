import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Google Sheets에서 데이터 불러오기
try:
    url = st.secrets["googlesheet"]["url"]
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url)

    if st.button("🔁데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"구글 시트 데이터를 불러오는 데 실패했습니다. secrets.toml 파일의 URL을 확인해주세요. 오류: {e}")
    st.stop()


# 2. 첫 화면 구성
st.title("2025학년도 개포고등학교 수학Ⅱ 성찰일지 확인표📚")

st.write("---")

# 학번과 이름 입력 창
student_id = st.text_input("학번을 입력하세요. (예: 20501)")
student_name = st.text_input("이름을 입력하세요. (예: 홍길동)")

# '결과 확인' 버튼
if st.button("🔥결과 확인"):
    if not student_id or not student_name:
        st.error("학번과 이름을 모두 입력해주세요.")
    else:
        # 입력된 학번과 이름으로 데이터프레임 필터링
        try:
            filtered_df = df[(df['학번'].astype(str) == student_id) & (df['이름'].str.strip() == student_name)]

            # 3. 두 번째 화면 구성 (필터링 결과에 따라)
            if not filtered_df.empty:
                st.success(f"{student_name} 학생, 환영합니다! 🎉")
                
                # 🔹 변경: 학번과 이름을 별도로 표시
                st.markdown(f"**학번:** {filtered_df.iloc[0, 0]}")
                st.markdown(f"**이름:** {filtered_df.iloc[0, 1]}")

                # 🔹 변경: 3열~15열 데이터 한 줄에 표시
                table_part1 = filtered_df.iloc[:, 2:15]  # 3열 ~ 15열
                table_part2 = filtered_df.iloc[:, 15:27]   # 16열 ~

                st.write("#### 1️⃣ 1단원 제출 현황(9/1(월) 마감)")
                st.dataframe(table_part1)

                if not table_part2.empty:
                    st.write("#### 2️⃣ 2단원 제출 현황(9/22(월) 마감예정)")
                    st.dataframe(table_part2)

                # 안내 사항
                st.markdown(
                    """
                    <span style="color:red; font-weight:bold;">
                    ⭐ 2단원 포트폴리오 검사 마감: 9/22(월) 16:00
                    </span><br>  
                    - 표시 구분: 1(제출 및 통과), 0.5(제출은 했으나 미흡), 0(미제출 또는 빈종이)<br>  
                    - 도장을 받았는데 점수가 다를 경우, 성찰일지가 없을 경우 등은 선생님께 문의할 것  
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.error("학번과 이름이 올바르지 않습니다. 다시 확인해주세요.")
        except KeyError as ke:
            st.error(f"컬럼을 찾을 수 없습니다: {ke}. Google Sheet의 컬럼명을 다시 확인해주세요.")
