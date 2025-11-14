# 파일 이름: 5_🔍_모델_프로필.py
import streamlit as st
import pandas as pd
import altair as alt
from wordcloud import WordCloud 
import matplotlib.pyplot as plt 
import os 
from backend.search_queries import get_all_brands, get_models_by_brand, get_recall_comparison, get_model_profile_data
from backend.stats_queries import get_summary_stats
from Home import display_custom_header 


# --- [0] 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너 - 모델 프로필",
    page_icon="🔍", 
    layout="wide"
)

display_custom_header()


# --- [1] 제목 ---
st.title("🔍 모델 상세 프로필")
st.info("관심 있는 차량의 종합 리콜 리포트를 확인해 보세요.")
st.markdown("---")

# --- [2] 차량 선택 UI (사이드바) ---
st.sidebar.header("🚗 차량 선택")
try:
    brand_list = ["전체"] + get_all_brands()
except Exception as e:
    st.sidebar.error(f"브랜드 목록 로딩 실패: {e}")
    brand_list = ["전체"]
selected_brand = st.sidebar.selectbox(
    "1. 브랜드 선택", brand_list, key="profile_brand", index=0
)
if selected_brand != "전체":
    try:
        model_list = ["전체"] + get_models_by_brand(selected_brand)
    except Exception as e:
        st.sidebar.error(f"차종 목록 로딩 실패: {e}")
        model_list = ["전체"]
else:
    model_list = ["전체"] 
selected_model = st.sidebar.selectbox(
    "2. 차종 선택", model_list, key="profile_model", index=0
)

# --- [3] 리포트 생성 ---
if selected_brand != "전체" and selected_model != "전체":
    st.header(f"🚗 {selected_brand} {selected_model} 리포트")
    
    with st.spinner(f"'{selected_model}' 모델의 데이터를 분석 중입니다..."):
        stats, keywords_df = get_recall_comparison(selected_brand, selected_model)
        history_df, all_reasons_string = get_model_profile_data(selected_brand, selected_model)

    if stats is None or history_df.empty:
        st.warning("해당 모델의 리콜 데이터를 찾을 수 없습니다.")
    else:
        # --- [3-1] 종합 통계 ---
        st.subheader("📊 종합 통계")
        metric_cols = st.columns(2)
        metric_cols[0].metric("총 리콜 건수", f"{stats['total_recalls']} 건")
        metric_cols[1].metric("평균 시정률", f"{stats['avg_correction_rate']} %")
        st.markdown("---")

        # --- [3-2] 시각화 (워드 클라우드 + 키워드 차트) ---
        viz_col1, viz_col2 = st.columns(2)
        with viz_col1:
            st.subheader("☁️ 리콜 사유 워드 클라우드")
            if all_reasons_string:
                try:
                    font_path = None
                    if os.path.exists("c:/Windows/Fonts/malgun.ttf"):
                        font_path = "c:/Windows/Fonts/malgun.ttf"
                    
                    wordcloud = WordCloud(
                        font_path=font_path, width=800, height=400, 
                        background_color='white'
                    ).generate(all_reasons_string)
                    
                    fig, ax = plt.subplots()
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"워드 클라우드 생성 오류: {e}")
                    st.info("한글 폰트(malgun.ttf)를 찾을 수 없거나, wordcloud 라이브러리 문제입니다.")
            else:
                st.info("워드 클라우드를 생성할 리콜 사유 데이터가 없습니다.")

        with viz_col2:
            st.subheader("📉 핵심 결함 키워드 TOP 10")
            if not keywords_df.empty:
                chart = alt.Chart(keywords_df).mark_bar().encode(
                    x=alt.X('keyword_text', title='리콜 키워드', sort=None, axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('keyword_count', title='키워드 빈도'),
                    tooltip=[
                        alt.Tooltip('keyword_text', title='키워드'),
                        alt.Tooltip('keyword_count', title='빈도수'),
                        alt.Tooltip('keyword_desc', title='설명')
                    ]
                ).properties(height=380).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("분석된 키워드 데이터가 없습니다.")
        st.markdown("---")
        
        # --- [3-3] 전체 리콜 이력 ---
        st.subheader("📋 전체 리콜 이력")
        st.dataframe(history_df, use_container_width=True, height=400)
else:
    st.info("👈 사이드바에서 분석할 브랜드와 차종을 선택해 주세요.")

# --- [4] 데이터 기준 기간 표시 ---
try:
    summary_stats = get_summary_stats()
    min_date, max_date = summary_stats['data_period']
    st.markdown("---")
    if min_date != 'N/A':
        st.caption(f"ℹ️ (데이터 기준 기간: {min_date} ~ {max_date})")
except Exception:
    pass
