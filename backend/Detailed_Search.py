# 상세 검색 페이지

import streamlit as st
import pandas as pd
from datetime import datetime
from data_queries import get_all_brands, get_models_by_brand, get_all_keywords_with_desc, search_recalls

# 페이지 설정
st.set_page_config(page_title="상세 검색", page_icon="🔍")
st.title("🔍 리콜 상세 검색")

# --- 1. 데이터 로드 및 전역 변수 설정 ---
# 데이터 쿼리 파일에서 브랜드, 키워드 리스트를 캐시된 값으로 가져옴
ALL_BRANDS = ["전체"] + get_all_brands()
KEYWORDS_DICT = get_all_keywords_with_desc()
ALL_KEYWORDS = ["전체"] + list(KEYWORDS_DICT.keys())

# 연도 범위 설정
current_year = datetime.now().year
ALL_YEARS = ["전체"] + list(range(current_year, 1999, -1))

# --- 2. 검색 필터 UI ---
with st.sidebar:
    st.header("필터 설정")
    
    # 1. 브랜드 선택
    selected_brand = st.selectbox("브랜드 선택", ALL_BRANDS, index=0)
    
    # 2. 모델 선택 (브랜드에 따라 동적 업데이트)
    if selected_brand != "전체":
        models = ["전체"] + get_models_by_brand(selected_brand)
    else:
        models = ["전체"]
    selected_model = st.selectbox("차종 선택", models, index=0)
    
    # 3. 연도 선택
    selected_year = st.selectbox("리콜 연도 선택", ALL_YEARS, index=0)
    
    # 4. 키워드 선택
    selected_keyword = st.selectbox("핵심 키워드 선택", ALL_KEYWORDS, index=0)

    # 5. 검색 버튼
    search_button = st.button("검색 실행", type="primary")

# --- 3. 검색 결과 표시 ---
if search_button:
    with st.spinner(f"'{selected_brand} {selected_model}' 리콜 정보를 검색 중..."):
        # data_queries.py의 함수 호출
        results_df = search_recalls(
            brand=selected_brand,
            model=selected_model,
            year=selected_year,
            keyword=selected_keyword
        )

    if not results_df.empty:
        st.subheader(f"✅ 검색 결과 (총 {len(results_df)} 건)")
        st.dataframe(results_df, use_container_width=True, height=500)
    else:
        st.warning("🔎 선택한 조건에 해당하는 리콜 내역이 없습니다.")

