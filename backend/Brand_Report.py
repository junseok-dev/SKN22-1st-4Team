# 브랜드 리포트 페이지

import streamlit as st
import altair as alt
from data_queries import get_brand_rankings

st.set_page_config(page_title="브랜드 리포트", page_icon="📈")
st.title("📈 브랜드 리콜 현황 분석")

# --- 1. 데이터 로드 ---
df_recall_count, df_correction_rate = get_brand_rankings()

if df_recall_count.empty:
    st.error("데이터베이스에서 브랜드 순위 정보를 가져오는 데 실패했습니다.")
else:
    # --- 2. 리콜 건수 순위 ---
    st.header("🏆 리콜 건수 순위")
    st.markdown("전체 기간 동안 브랜드별 리콜 건수를 기준으로 순위를 매겼습니다.")
    
    col_rank, col_chart = st.columns([1, 2])
    
    with col_rank:
        st.subheader("순위표")
        st.dataframe(df_recall_count.head(10), use_container_width=True)
        
    with col_chart:
        st.subheader("상위 10개 브랜드 시각화")
        chart_count = alt.Chart(df_recall_count.head(10).reset_index()).mark_bar().encode(
            x=alt.X('총 리콜 건수:Q', title='총 리콜 건수'),
            y=alt.Y('브랜드:N', sort='-x', title='브랜드'),
            tooltip=['브랜드', '총 리콜 건수']
        ).properties(height=350)
        st.altair_chart(chart_count, use_container_width=True)

    st.divider()

    # --- 3. 평균 시정률 순위 ---
    st.header("🛠️ 평균 시정률 순위")
    st.markdown("리콜 건수 5회 이상인 브랜드들을 대상으로 평균 시정률(%)을 기준으로 순위를 매겼습니다. **시정률이 높을수록 리콜 조치가 적극적**이라고 볼 수 있습니다.")

    if not df_correction_rate.empty:
        col_rate_rank, col_rate_chart = st.columns([1, 2])

        with col_rate_rank:
            st.subheader("순위표")
            # 시정률이 100%에 가까울수록 (즉, 순위가 높을수록) 신뢰도가 높다고 가정
            st.dataframe(df_correction_rate.head(10), use_container_width=True)
        
        with col_rate_chart:
            st.subheader("상위 10개 브랜드 시각화")
            chart_rate = alt.Chart(df_correction_rate.head(10).reset_index()).mark_bar().encode(
                x=alt.X('평균 시정률 (%):Q', title='평균 시정률 (%)'),
                y=alt.Y('브랜드:N', sort='-x', title='브랜드'),
                color=alt.Color('평균 시정률 (%):Q', scale=alt.Scale(range='heatmap')),
                tooltip=['브랜드', '평균 시정률 (%)', '리콜 건수']
            ).properties(height=350)
            st.altair_chart(chart_rate, use_container_width=True)
    else:
        st.info("리콜 건수 5회 이상인 브랜드의 시정률 데이터가 없습니다.")