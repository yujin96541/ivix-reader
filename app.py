import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide")

# ==========================================
# 🎁 [팝업창 UI] 상세 매물 정보
# ==========================================
@st.dialog("📄 상세 매물 정보", width="large")
def show_detail_popup(row_data):
    # 데이터 형식 변환 (AgGrid 호환)
    if isinstance(row_data, pd.DataFrame):
        row_data = row_data.iloc[0].to_dict()
    elif isinstance(row_data, pd.Series):
        row_data = row_data.to_dict()

    st.subheader("1. 매물 기본 정보")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.text_input("작성일자", value=str(row_data.get("작성일자", "")).split(" ")[0])
    with col2: st.text_input("구분", value=row_data.get("구분", ""))
    with col3: st.text_input("거래유형", value=row_data.get("거래유형", ""))
    with col4: st.text_input("매물종류", value=row_data.get("매물종류", ""))
        
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        b_area = str(row_data.get('건물평', '')).replace("평", "")
        st.text_input("건물평(평)", value=f"{b_area}평" if b_area.strip() else "")
    with col6:
        r_area = str(row_data.get('실평', '')).replace("평", "")
        st.text_input("실평(평)", value=f"{r_area}평" if r_area.strip() else "")
    with col7: st.text_input("입주가능일자", value=row_data.get("입주가능일자", ""))
    with col8: st.text_input("담당자", value=row_data.get("담당자", ""))

    st.text_input("소재지", value=row_data.get("소재지", ""))
    st.write("**매물특징**")
    st.info(row_data.get("매물특징", "내용 없음"))
    
    st.divider() 
    
    st.subheader("2. 금액 정보 (단위: 만원)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1: st.text_input("매매금액", value=row_data.get("매매금액", ""))
    with col_p2: st.text_input("보증금", value=row_data.get("보증금", ""))
    with col_p3: st.text_input("월세", value=row_data.get("월세", ""))

    st.divider()

    st.subheader("3. 고객 기본 정보")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1: st.text_input("이름", value=row_data.get("이름", ""))
    with col_c2: st.text_input("핸드폰번호", value=row_data.get("핸드폰번호", ""))
    with col_c3: st.text_input("자택전화", value=row_data.get("자택전화", ""))
        
    st.text_input("주소", value=row_data.get("주소", ""))
    
    if st.button("닫기"): st.rerun()

# ==========================================
# 🖥️ [메인 화면] 아이빅스 데이터 리더
# ==========================================
st.title("📊 아이빅스 데이터 리더")
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=['xlsx', 'xls'])

if uploaded_file is not None:
    # 데이터 불러오기 및 헤더 설정
    df = pd.read_excel(uploaded_file, header=None)
    df = df.fillna("") 
    
    base_cols = [
        "매물번호", "작성일자", "거래유형", "매물종류", "건물평", "매매금액", "보증금", "월세", 
        "입주가능일자", "소재지", "담당자", "부동산", "매물특징", "구분", "O열", "P열", 
        "Q열", "R열", "S열", "실평", "U열", "V열", "W열", "X열", 
        "Y열", "Z열", "AA열", "AB열", "AC열", "AD열", "주소", "이름", 
        "자택전화", "핸드폰번호"
    ]
    
    new_cols = []
    for i in range(len(df.columns)):
        if i < len(base_cols): new_cols.append(base_cols[i])
        else: new_cols.append(f"이름미상_열{i+1}")
    df.columns = new_cols 

    st.write("---")
    
    # ------------------------------------------
    # 📍 실시간 검색 필터링
    # ------------------------------------------
    st.write("### 🔍 매물 필터링")
    search_keyword = st.text_input("검색어를 입력하면 아래 표가 실시간으로 필터링됩니다 (예: 문정역, 정상, 월세)")
    
    # 원본 데이터를 복사해서 필터링용 데이터프레임 생성
    display_df = df.copy()
    
    # 검색어가 있으면 필터링 적용
    if search_keyword:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    # 보기 좋게 날짜와 평수 정리
    display_df["작성일자"] = display_df["작성일자"].astype(str).apply(lambda x: x.split(" ")[0])
    display_df["건물평"] = display_df["건물평"].astype(str).apply(lambda x: f"{x}평" if x.strip() != "" and "평" not in str(x) else x)

    # ------------------------------------------
    # 📍 전체 현황 표 (AgGrid)
    # ------------------------------------------
    st.write(f"**총 {len(display_df)}건의 매물이 검색되었습니다.** (행을 클릭하면 상세 정보가 뜹니다)")
    
    gb = GridOptionsBuilder.from_dataframe(display_df)
    
    # 숨길 열 설정
    cols_to_hide = ["매물번호", "Y열", "Z열", "AA열", "AB열", "부동산"]
    for col in cols_to_hide:
        if col in display_df.columns:
            gb.configure_column(col, hide=True)

    # 클릭 시 행 선택 설정 (체크박스 없이 클릭만으로 작동)
    gb.configure_selection('single', use_checkbox=False)
    gridOptions = gb.build()

    # 표 출력
    grid_response = AgGrid(
        display_df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=700,
        fit_columns_on_grid_load=True,
        theme="streamlit",
        key="main_grid" # 고유 키 부여
    )

    # 행 클릭 시 팝업 띄우기
    selected = grid_response['selected_rows']
    if selected is not None and len(selected) > 0:
        if isinstance(selected, pd.DataFrame):
            row_data = selected.iloc[0].to_dict()
        else:
            row_data = selected[0]
        show_detail_popup(row_data)
