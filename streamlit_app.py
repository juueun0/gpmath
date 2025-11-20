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

# ---------------------------
# ★ 추가된 부분: 값이 1이면 연두색으로 칠해주는 스타일 함수
# ---------------------------
def _is_one(val):
    try:
        if pd.isna(val):
            return False
        num = float(val)
        return num == 1.0
    except:
        return str(val).strip() == "1"

def highlight_one(cell):
    return "background-color: #ccffcc" if _is_one(cell) else ""

# ---------------------------
# 정수이면 1, 아니면 그대로 표시하는 포맷터
# ---------------------------
def _fmt(x):
    try:
        if pd.isna(x):
            return "—"
        xf = float(x)
        return str(int(xf)) if xf.is_integer() else str(xf)
    except:
        return str(x) if x is not None else "—"

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
                table_part3 = filtered_df.iloc[:, 27:33]   # 28열 ~ 33열
                table_part4 = filtered_df.iloc[:, 33:47]   # 34열 ~ 47열

                st.write("#### 1️⃣ 1단원 제출 현황(9/1(월) 마감)")
                st.dataframe(table_part1.style.format(_fmt).applymap(highlight_one))

                if not table_part2.empty:
                    st.write("#### 2️⃣-1 2단원(중간범위) 제출 현황(9/22(월) 마감)")
                    st.dataframe(table_part2.style.format(_fmt).applymap(highlight_one))

                if not table_part3.empty:
                    st.write("#### 2️⃣-2 2단원(기말범위) 제출 현황(10/31(금) 마감)")
                    st.dataframe(table_part3.style.format(_fmt).applymap(highlight_one))

                if not table_part4.empty:
                    st.write("#### 3️⃣ 3단원 제출 현황(11/28(금) 마감 예정)")
                    st.dataframe(table_part4.style.format(_fmt).applymap(highlight_one))

                # 안내 사항
                st.markdown(
                    """
                    <span style="color:red; font-weight:bold;">
                    ⭐ 3단원 포트폴리오 검사 마감: 11/28(금) 16:00
                    </span><br>  
                    - 표시 구분: 1(제출 및 통과), 0.5(제출은 했으나 미흡), 0(미제출 또는 빈종이)<br>  
                    - 도장을 받았는데 점수가 다를 경우, 성찰일지가 없을 경우 등은 선생님께 문의할 것  
                    """,
                    unsafe_allow_html=True
                )

                
                st.write("---")  # ★ 추가
                st.markdown("### 📌 수행평가 점수 확인")  # ★ 추가

                # 숫자/결측 안전 포맷터  # ★ 추가
                def _fmt(x):  # ★ 추가
                    try:  # ★ 추가
                        if pd.isna(x):  # ★ 추가
                            return "—"  # ★ 추가
                        xf = float(x)  # ★ 추가
                        return str(int(xf)) if xf.is_integer() else str(xf)  # ★ 추가
                    except Exception:  # ★ 추가
                        return str(x) if x is not None else "—"  # ★ 추가

                # ==== 1) 포트폴리오 ====  # ★ 추가
                st.markdown("#### 1. 포트폴리오")  # ★ 추가
                try:  # ★ 추가
                    col_AY, col_AZ, col_BA, col_BB = df.columns[50], df.columns[51], df.columns[52], df.columns[53]  # ★ 추가

                    # AY, AZ, BA: 1행 표(헤더 포함)  # ★ 추가
                    pf_table = filtered_df[[col_AY, col_AZ, col_BA]].reset_index(drop=True)  # ★ 추가
                    st.dataframe(pf_table, use_container_width=True)  # ★ 추가

                    # BB: 내용만 별도 강조  # ★ 추가
                    bb_val_raw = filtered_df.iloc[0, 53]  # ★ 추가
                    bb_val = _fmt(bb_val_raw)  # ★ 추가

                    st.markdown(
                    """
                    <span style="color:red; font-weight:bold;">
                    ⭐ 마감일 전까지 점수는 변동되니 마지막 성찰일지까지 최선을 다해주세요 :)
                    </span><br>    
                    """,
                    unsafe_allow_html=True
                )
                    st.write("\n")

                    # "최종 점수: {BB}/20점"  # ★ 추가
                    st.markdown(f"**최종 점수: {bb_val}/20점**")  # ★ 추가
                except Exception as e:  # ★ 추가
                    st.warning(f"포트폴리오(AY~BB) 표시 중 오류가 발생했습니다: {e}")  # ★ 추가

                st.write("\n")
                
                # ==== 2) 매쓰티콘 ====  # ★ 추가
                st.markdown("#### 2. 매쓰티콘(추후 안내)")  # ★ 추가
                try:  # ★ 추가
                    av = _fmt(filtered_df.iloc[0, 47])  # AV  # ★ 추가
                    st.markdown(f"**최종 점수: {av}/10점**")  # ★ 추가
                except Exception as e:  # ★ 추가
                    st.warning(f"매쓰티콘(AV) 표시 중 오류가 발생했습니다: {e}")  # ★ 추가

                st.write("\n")
                
                # ==== 3) 수학 프로젝트 ====  # ★ 추가
                st.markdown("#### 3. 수학 프로젝트(추후 안내)")  # ★ 추가
                try:  # ★ 추가
                    aw_raw = filtered_df.iloc[0, 48]  # AW  # ★ 추가
                    ax_raw = filtered_df.iloc[0, 49]  # AX  # ★ 추가
                    aw = _fmt(aw_raw)  # ★ 추가
                    ax = _fmt(ax_raw)  # ★ 추가

                    # 합계(결측/문자 안전 합산)  # ★ 추가
                    try:  # ★ 추가
                        aw_num = float(aw_raw) if pd.notna(aw_raw) else 0.0  # ★ 추가
                    except Exception:  # ★ 추가
                        aw_num = 0.0  # ★ 추가
                    try:  # ★ 추가
                        ax_num = float(ax_raw) if pd.notna(ax_raw) else 0.0  # ★ 추가
                    except Exception:  # ★ 추가
                        ax_num = 0.0  # ★ 추가
                    total = aw_num + ax_num  # ★ 추가
                    total_str = _fmt(total)  # ★ 추가

                    st.markdown(f"(1) 개요: {aw}/4점")  # ★ 추가
                    st.markdown(f"(2) 보고서: {ax}/16점")  # ★ 추가
                    st.markdown(f"(3) **최종 점수: {total_str}/20점**")  # ★ 추가
                except Exception as e:  # ★ 추가
                    st.warning(f"수학 프로젝트(AW, AX) 표시 중 오류가 발생했습니다: {e}")  # ★ 추가
            else:
                st.error("학번과 이름이 올바르지 않습니다. 다시 확인해주세요.")
        except KeyError as ke:
            st.error(f"컬럼을 찾을 수 없습니다: {ke}. Google Sheet의 컬럼명을 다시 확인해주세요.")
