import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode # ★ 추가된 전문 도구

st.set_page_config(layout="wide")

# ==========================================

# 🎁 [팝업창 UI] 상세 매물 정보

# ==========================================

@st.dialog("📄 상세 매물 정보", width="large")

def show_detail_popup(row_data):

    # 데이터 형식 변환 (AgGrid 대응)

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

    

    # --- 수정된 매물특징 부분 (들여쓰기 주의!) ---

    st.write("**매물특징**")

    st.info(row_data.get("매물특징", "내용 없음"))

    

    st.divider() # 이 줄의 시작 위치가 바로 윗줄인 st.info와 똑같아야 합니다!

    

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
    # 📍 매물 검색 및 드롭다운
    # ------------------------------------------
    st.write("### 🔍 매물 검색")
    search_keyword = st.text_input("검색어를 입력하세요 (예: 문정역, 정상, 월세 등)")
    
    if search_keyword:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False, na=False)).any(axis=1)
        filtered_df = df[mask]
        
        if len(filtered_df) > 0:
            def format_selectbox(idx):
                if idx == "default": return "👇 클릭하여 확인할 매물을 선택하세요"
                row = filtered_df.loc[idx]
                date_val = str(row.get('작성일자', '')).split(' ')[0]
                area_val = str(row.get('건물평', ''))
                area_str = f"{area_val}평" if area_val.strip() else ""
                
                items = [
                    date_val, str(row.get('거래유형', '')), str(row.get('매물종류', '')),
                    area_str, str(row.get('보증금', '')), str(row.get('입주가능일자', '')),
                    str(row.get('소재지', '')), str(row.get('매물특징', '')), str(row.get('주소', ''))
                ]
                return " | ".join(items)

            options = ["default"] + filtered_df.index.tolist()
            selected_idx = st.selectbox("작업할 매물을 선택하세요:", options, format_func=format_selectbox)
            
            if selected_idx != "default":
                row_data = filtered_df.loc[selected_idx]
                show_detail_popup(row_data)
        else:
            st.warning("검색어와 일치하는 데이터가 없습니다.")

    st.write("---")
    
    # ------------------------------------------
    # 📍 전체 현황 표 (클릭 시 자동 팝업 기능 적용!)
    # ------------------------------------------
    st.write("### 📋 전체 매물 현황")
    
    display_df = df.copy()
    display_df["작성일자"] = display_df["작성일자"].astype(str).apply(lambda x: x.split(" ")[0])
    display_df["건물평"] = display_df["건물평"].astype(str).apply(lambda x: f"{x}평" if x.strip() != "" else x)

    # AgGrid 옵션 설정
    gb = GridOptionsBuilder.from_dataframe(display_df)
    
    # 아예 열을 삭제하지 않고 '숨기기'만 해서 원본 데이터를 안전하게 유지합니다.
    cols_to_hide = ["매물번호", "Y열", "Z열", "AA열", "AB열", "부동산"]
    for col in cols_to_hide:
        if col in display_df.columns:
            gb.configure_column(col, hide=True)

    # ★ 핵심: 체크박스 없이 아무 곳이나 눌러도 행이 선택되도록 설정
    gb.configure_selection('single', use_checkbox=False)
    gridOptions = gb.build()

    # 화면에 예쁜 표 그리기
    grid_response = AgGrid(
        display_df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.SELECTION_CHANGED, # 선택이 바뀔 때마다 파이썬에 알려줌
        height=750,
        fit_columns_on_grid_load=True,
        theme="streamlit"
    )

    # 사용자가 표에서 특정 행을 클릭했다면?
    selected = grid_response['selected_rows']
    if selected is not None:
        if isinstance(selected, pd.DataFrame) and len(selected) > 0:
            show_detail_popup(selected)
        elif isinstance(selected, list) and len(selected) > 0:
            show_detail_popup(selected[0])
