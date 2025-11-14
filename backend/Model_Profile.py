# 모델 프로필 페이지

import streamlit as st
import pandas as pd
from wordcloud import WordCloud # 워드 클라우드 생성을 위해 임포트
import matplotlib.pyplot as plt
import io
from data_queries import get_all_brands, get_models_by_brand, get_model_profile_data

st.set_page_config(page_title="모델 프로필", page_icon="👤")
st.title("👤 차종 리콜 프로필 (Word Cloud 분석)")

# --- 1. 데이터 로드 및 UI 설정 ---
ALL_BRANDS = ["전체"] + get_all_brands()
col_b, col_m = st.columns(2)

with col_b:
    selected_brand = st.selectbox("브랜드 선택", ALL_BRANDS, index=0)

models = ["전체"]
if selected_brand != "전체":
    models = ["전체"] + get_models_by_brand(selected_brand)

with col_m:
    selected_model = st.selectbox("차종 선택", models, index=0)

# --- 2. 워드 클라우드 생성 함수 ---
# 워드 클라우드는 캐싱하지 않고, 데이터 로드 함수만 캐싱
def create_wordcloud(text_data):
    if not text_data:
        return None
    
    # 폰트 설정 (한국어 지원을 위해 폰트 지정 필요)
    # 실제 환경에 맞게 폰트 경로를 수정해야 합니다.
    font_path = 'NanumGothic.ttf' # 예시: 나눔고딕
    try:
        # TfidfVectorizer 등을 사용하여 불용어 제거 및 가중치 부여 가능
        wordcloud = WordCloud(
            font_path=font_path,
            width=800, height=400,
            background_color='white',
            max_words=100
        ).generate(text_data)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        return fig
    except FileNotFoundError:
        st.error(f"워드 클라우드 폰트 파일('{font_path}')을 찾을 수 없습니다. 폰트 경로를 확인하거나 제거하세요.")
        return None
    except Exception as e:
        st.error(f"워드 클라우드 생성 오류: {e}")
        return None


# --- 3. 데이터 로드 및 결과 표시 ---
if selected_brand != "전체" and selected_model != "전체":
    history_df, all_reasons_string = get_model_profile_data(selected_brand, selected_model)
    
    if history_df.empty:
        st.info(f"선택하신 {selected_brand} {selected_model}에 대한 리콜 기록이 없습니다.")
    else:
        st.divider()

        # 3.1. 워드 클라우드 시각화 (리콜 사유 분석)
        st.header("📝 리콜 사유 핵심 키워드 분석 (Word Cloud)")
        if all_reasons_string:
            wc_fig = create_wordcloud(all_reasons_string)
            if wc_fig:
                st.pyplot(wc_fig)
        else:
            st.warning("분석 가능한 리콜 사유 텍스트 데이터가 없습니다.")

        st.divider()

        # 3.2. 전체 리콜 이력 제공
        st.header(f"📜 {selected_model} 리콜 이력 ({len(history_df)} 건)")
        st.dataframe(history_df, use_container_width=True)
else:
    st.info("브랜드와 차종을 선택하여 모델 프로필을 확인하세요.")
