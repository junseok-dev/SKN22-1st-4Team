import streamlit as st
import pandas as pd
import altair as alt
from backend.search_queries import get_all_brands, get_models_by_brand, get_recall_comparison
from backend.stats_queries import get_summary_stats
from Home import display_custom_header 


# --- [0] 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너 - 차량 비교",
    page_icon="📊", 
    layout="wide"
)

display_custom_header()

# --- [1] 제목 ---
st.title("📊 차량 비교") 
st.info("비교하고 싶은 두 차량을 선택하고 '비교하기' 버튼을 눌러주세요.")
st.markdown("---")

# --- [2] 차량 선택 UI ---
try:
    brand_list_for_compare = ["전체"] + get_all_brands()
except Exception as e:
    st.error(f"브랜드 목록 로딩 실패: {e}")
    brand_list_for_compare = ["전체"]
col1, col2 = st.columns(2)
with col1:
    st.subheader("차량 1 (비교 대상)")
    brand1 = st.selectbox("브랜드 선택", brand_list_for_compare, key="brand1", index=0)
    if brand1 != "전체":
        model_list1 = ["전체"] + get_models_by_brand(brand1)
    else:
        model_list1 = ["전체"]
    model1 = st.selectbox("차종 선택", model_list1, key="model1", index=0)
with col2:
    st.subheader("차량 2 (비교 대상)")
    brand2 = st.selectbox("브랜드 선택", brand_list_for_compare, key="brand2", index=0)
    if brand2 != "전체":
        model_list2 = ["전체"] + get_models_by_brand(brand2)
    else:
        model_list2 = ["전체"]
    model2 = st.selectbox("차종 선택", model_list2, key="model2", index=0)
st.markdown("---")

# --- [3] 비교 결과 표시 ---
if st.button("비교하기", use_container_width=True):
    if (brand1 == "전체" or model1 == "전체") or (brand2 == "전체" or model2 == "전체"):
        st.error("오류: 2대의 차량(브랜드와 차종)을 모두 정확히 선택해야 합니다.")
    else:
        st.subheader(f"📊 {brand1} {model1}  vs  {brand2} {model2}  비교 결과")
        with st.spinner("두 차량의 리콜 데이터를 분석 중입니다..."):
            stats1, keywords_df1 = get_recall_comparison(brand1, model1)
            stats2, keywords_df2 = get_recall_comparison(brand2, model2)
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"#### 🚗 **{brand1} {model1}**")
            if stats1 and stats1['total_recalls'] > 0:
                metric_cols1 = st.columns(2)
                metric_cols1[0].metric("총 리콜 건수", f"{stats1['total_recalls']} 건")
                metric_cols1[1].metric("평균 시정률", f"{stats1['avg_correction_rate']} %")
                st.markdown("**주요 리콜 키워드 (Top 10)**")
                if not keywords_df1.empty:
                    chart1 = alt.Chart(keywords_df1).mark_bar().encode(
                        x=alt.X('keyword_text', title='리콜 키워드', sort=None, axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('keyword_count', title='키워드 빈도'),
                        tooltip=[
                            alt.Tooltip('keyword_text', title='키워드'),
                            alt.Tooltip('keyword_count', title='빈도수'),
                            alt.Tooltip('keyword_desc', title='설명')
                        ]
                    ).properties(height=350).interactive()
                    st.altair_chart(chart1, use_container_width=True)
                else:
                    st.info("분석된 키워드 데이터가 없습니다.")
            else:
                st.warning("해당 차종의 리콜 데이터가 없습니다.")
        with res_col2:
            st.markdown(f"#### 🚙 **{brand2} {model2}**")
            if stats2 and stats2['total_recalls'] > 0:
                metric_cols2 = st.columns(2)
                metric_cols2[0].metric("총 리콜 건수", f"{stats2['total_recalls']} 건")
                metric_cols2[1].metric("평균 시정률", f"{stats2['avg_correction_rate']} %")
                st.markdown("**주요 리콜 키워드 (Top 10)**")
                if not keywords_df2.empty:
                    chart2 = alt.Chart(keywords_df2).mark_bar().encode(
                        x=alt.X('keyword_text', title='리콜 키워드', sort=None, axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('keyword_count', title='키워드 빈도'),
                        tooltip=[
                            alt.Tooltip('keyword_text', title='키워드'),
                            alt.Tooltip('keyword_count', title='빈도수'),
                            alt.Tooltip('keyword_desc', title='설명')
                        ]
                    ).properties(height=350).interactive()
                    st.altair_chart(chart2, use_container_width=True)
                else:
                    st.info("분석된 키워드 데이터가 없습니다.")
            else:
                st.warning("해당 차종의 리콜 데이터가 없습니다.")

# --- [4] 데이터 기준 기간 표시 ---
try:
    summary_stats = get_summary_stats()
    min_date, max_date = summary_stats['data_period']
    st.markdown("---")
    if min_date != 'N/A':
        st.caption(f"ℹ️ (데이터 기준 기간: {min_date} ~ {max_date})")
except Exception:
    pass
