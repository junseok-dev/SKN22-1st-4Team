# 차량비교 페이지

import streamlit as st
import pandas as pd
import altair as alt  # 시각화를 위해 altair 임포트
from data_queries import get_all_brands, get_models_by_brand, get_recall_comparison

st.set_page_config(page_title="차량 비교", page_icon="⚖️")
st.title("⚖️ 두 차종 리콜 현황 비교")

# --- 1. 데이터 로드 및 초기 설정 ---
ALL_BRANDS = ["전체"] + get_all_brands()
if "brand1" not in st.session_state:
    st.session_state.brand1 = "전체"
if "model1" not in st.session_state:
    st.session_state.model1 = "전체"
if "brand2" not in st.session_state:
    st.session_state.brand2 = "전체"
if "model2" not in st.session_state:
    st.session_state.model2 = "전체"

# --- 2. 비교 차량 선택 UI ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("첫 번째 차량 (A)")
    st.session_state.brand1 = st.selectbox("브랜드 A", ALL_BRANDS, key="sel_brand1")
    models1 = ["전체"]
    if st.session_state.brand1 != "전체":
        models1 = ["전체"] + get_models_by_brand(st.session_state.brand1)
    st.session_state.model1 = st.selectbox("차종 A", models1, key="sel_model1")

with col2:
    st.subheader("두 번째 차량 (B)")
    st.session_state.brand2 = st.selectbox("브랜드 B", ALL_BRANDS, key="sel_brand2")
    models2 = ["전체"]
    if st.session_state.brand2 != "전체":
        models2 = ["전체"] + get_models_by_brand(st.session_state.brand2)
    st.session_state.model2 = st.selectbox("차종 B", models2, key="sel_model2")

# 비교 실행 조건
is_ready = (
    st.session_state.brand1 != "전체"
    and st.session_state.model1 != "전체"
    and st.session_state.brand2 != "전체"
    and st.session_state.model2 != "전체"
)

if not is_ready:
    st.info("비교를 위해 두 차량의 브랜드와 차종을 모두 선택해주세요.")
else:
    # --- 3. 데이터 로드 및 비교 결과 ---
    @st.cache_data(ttl=3600)
    def load_comparison_data():
        stats1, keywords1_df = get_recall_comparison(
            st.session_state.brand1, st.session_state.model1
        )
        stats2, keywords2_df = get_recall_comparison(
            st.session_state.brand2, st.session_state.model2
        )
        return stats1, keywords1_df, stats2, keywords2_df

    stats1, keywords1_df, stats2, keywords2_df = load_comparison_data()

    if (
        stats1 is None
        or stats2 is None
        or (stats1["total_recalls"] == 0 and stats2["total_recalls"] == 0)
    ):
        st.warning("선택된 차종에 대한 리콜 기록이 충분하지 않아 비교할 수 없습니다.")
    else:
        st.subheader("📊 주요 리콜 통계 비교")

        # 3.1. 통계 요약 (총 리콜 건수, 평균 시정률)
        comp_data = pd.DataFrame(
            {
                "차종": [
                    f"A: {st.session_state.model1}",
                    f"B: {st.session_state.model2}",
                ],
                "총 리콜 건수": [stats1["total_recalls"], stats2["total_recalls"]],
                "평균 시정률 (%)": [
                    stats1["avg_correction_rate"],
                    stats2["avg_correction_rate"],
                ],
            }
        ).set_index("차종")
        st.dataframe(comp_data)

        # 3.2. 리콜 건수 시각화
        st.subheader("총 리콜 건수")
        chart_recall = (
            alt.Chart(comp_data.reset_index())
            .mark_bar()
            .encode(
                x=alt.X("총 리콜 건수:Q"),
                y=alt.Y("차종:N", sort="-x"),
                color=alt.Color("차종:N"),
                tooltip=["차종", "총 리콜 건수"],
            )
            .properties(height=200)
        )
        st.altair_chart(chart_recall, use_container_width=True)

        # 3.3. 키워드 분석 비교
        st.subheader("📌 주요 결함 키워드 비교 (상위 5개)")

        col_k1, col_k2 = st.columns(2)

        # 차량 A 키워드
        with col_k1:
            st.markdown(f"**{st.session_state.model1}**")
            if not keywords1_df.empty:
                st.dataframe(
                    keywords1_df[["keyword_text", "keyword_count"]]
                    .head(5)
                    .rename(
                        columns={
                            "keyword_text": "결함 키워드",
                            "keyword_count": "등장 횟수",
                        }
                    )
                    .set_index("결함 키워"),
                    use_container_width=True,
                )
            else:
                st.info("이 차량의 키워드 데이터가 없습니다.")

        # 차량 B 키워드
        with col_k2:
            st.markdown(f"**{st.session_state.model2}**")
            if not keywords2_df.empty:
                st.dataframe(
                    keywords2_df[["keyword_text", "keyword_count"]]
                    .head(5)
                    .rename(
                        columns={
                            "keyword_text": "결함 키워드",
                            "keyword_count": "등장 횟수",
                        }
                    )
                    .set_index("결함 키워"),
                    use_container_width=True,
                )
            else:
                st.info("이 차량의 키워드 데이터가 없습니다.")
