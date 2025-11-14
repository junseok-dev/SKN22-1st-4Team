import streamlit as st
import pandas as pd
import altair as alt
from backend.stats_queries import get_summary_stats, get_brand_rankings
from Home import display_custom_header 


# --- [0] 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너 - 브랜드 리포트",
    page_icon="🏆", 
    layout="wide"
)

display_custom_header()

# --- [1] 제목 ---
st.title("🏆 브랜드 리포트") 
st.info("DB에 저장된 전체 브랜드를 대상으로 '리콜 건수'와 '평균 시정률' 순위를 분석합니다.")
st.markdown("---")

# --- [2] 데이터 로드 ---
try:
    with st.spinner("브랜드 랭킹 데이터를 분석 중입니다..."):
        df_recall_rank, df_rate_rank = get_brand_rankings()
except Exception as e:
    st.error(f"브랜드 리포트 데이터 로딩 중 오류 발생: {e}")
    df_recall_rank = pd.DataFrame()
    df_rate_rank = pd.DataFrame()

# --- [3] 리포트 표시 (2단 컬럼) ---
col1, col2 = st.columns(2)
with col1:
    st.header("🍋 리콜 건수 순위 (많은 순)")
    st.markdown("리콜이 **많이** 발생한 브랜드 순위입니다. (DB 내 전체 기간)")
    if not df_recall_rank.empty:
        chart_recall = alt.Chart(df_recall_rank.head(15)).mark_bar().encode(
            x=alt.X('총 리콜 건수', title='총 리콜 건수'),
            y=alt.Y('브랜드', title='브랜드', sort='-x'),
            tooltip=['브랜드', '총 리콜 건수']
        ).properties(title='리콜 건수 상위 15개 브랜드', height=500).interactive()
        st.altair_chart(chart_recall, use_container_width=True)
        with st.expander("전체 브랜드 리콜 건수 순위 보기 (표)"):
            st.dataframe(df_recall_rank, use_container_width=True)
    else:
        st.warning("리콜 건수 데이터를 찾을 수 없습니다.")
with col2:
    st.header("🛠️ 평균 시정률 순위 (높은 순)")
    st.markdown("리콜 발생 시 **시정 조치**가 잘 이루어진 브랜드 순위입니다. (리콜 5건 이상 대상)")
    if not df_rate_rank.empty:
        chart_rate = alt.Chart(df_rate_rank.head(15)).mark_bar(color="green").encode(
            x=alt.X('평균 시정률 (%)', title='평균 시정률 (%)', scale=alt.Scale(domain=[0, 100])),
            y=alt.Y('브랜드', title='브랜드', sort='-x'),
            tooltip=['브랜드', '평균 시정률 (%)', '리콜 건수']
        ).properties(title='평균 시정률 상위 15개 브랜드', height=500).interactive()
        st.altair_chart(chart_rate, use_container_width=True)
        with st.expander("전체 브랜드 시정률 순위 보기 (표)"):
            st.dataframe(df_rate_rank, use_container_width=True)
    else:
        st.warning("시정률 데이터를 찾을 수 없습니다.")

# --- [4] 데이터 기준 기간 표시 ---
try:
    summary_stats = get_summary_stats()
    min_date, max_date = summary_stats['data_period']
    st.markdown("---")
    if min_date != 'N/A':
        st.caption(f"ℹ️ (데이터 기준 기간: {min_date} ~ {max_date})")
except Exception:
    pass
