import streamlit as st

from Home import display_custom_header 

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너 - 프로젝트 소개", 
    page_icon="🚀", 
    layout="wide"
)

# [★ 헤더 함수 호출]
display_custom_header()

# --- [1] 제목 ---
st.title("🚀 프로젝트 소개")
st.markdown("---")

# --- [2] 프로젝트 소개 ---
st.header("1. 🍋 레몬 스캐너 (Lemon Scanner)란?")
st.markdown("""
이 프로젝트는 SK Networks Family AI Camp 22기 4조의 1차 프로젝트입니다.

국내에 등록된 차량의 리콜 데이터를 수집, 분석하여 사용자에게 유용한 정보로 제공하는 것을 목표로 합니다.
'내 차'의 리콜 이력뿐만 아니라, 구매하고자 하는 중고차의 잠재적 결함을 확인하고, 브랜드별 리콜 통계를 비교 분석할 수 있는 기능을 제공합니다.
""")

# --- [3. 이름의 유래 ] ---
st.header("2. 🍋 'Lemon Scanner' 이름의 유래")
st.markdown("""
이 프로젝트의 이름인 'Lemon Scanner'는 경제학 용어인 **레몬 마켓(Lemon Market)** 에서 유래했습니다.

'레몬 마켓'은 판매자가 구매자보다 상품(특히 중고차)에 대해 훨씬 더 많은 정보를 가진 **정보의 비대칭성**이 심한 시장을 의미합니다.
이러한 시장에서는 구매자가 좋은 차(복숭아, Peaches)와 나쁜 차(레몬, Lemons)를 구별하기 어려워, 결국 나쁜 '레몬' 차량만 시장에 남게 되는 품질 저하 현상이 발생합니다.

저희 **Lemon Scanner** 프로젝트는 리콜 데이터와 같은 차량의 중요 정보를 투명하게 제공함으로써, 이러한 정보의 비대칭성을 해소하고 사용자가 '레몬'을 '스캔(Scan)'하여 피할 수 있도록 돕는다는 의미를 담고 있습니다.
""")
st.markdown("---")


# --- [4. 팀원 소개] ---
st.header("3. 👤 팀원 소개")
col1, col2, col3, col4,col5 = st.columns(5)
with col1:
    st.info("**장완식 (팀장)**")
    st.markdown("- DB 설계 및 구축\n- 백엔드 로직 개발\n- Streamlit 앱 개발")
with col2:
    st.info("**문승준 (팀원)**")
    st.markdown("- 데이터 가공\n- 데이터 시각화")
with col3:
    st.info("**최민호 (팀원)**")
    st.markdown("- 데이터 가공\n- 데이터 시각화")
with col4:
    st.info("**박준석 (팀원)**")
    st.markdown("- 백엔드 로직 개발\n- Streamlit 앱 개발")
with col5:
    st.info("**이도훈 (팀원)**")
    st.markdown("- 백엔드 로직 개발\n- Streamlit 앱 개발")
st.markdown("---")

# --- [5. 주요 기능 소개] ---
st.header("4. 🛠️ 주요 기능")
st.markdown("""
- **상세 검색**: 브랜드, 차종, 연도, 핵심 키워드를 조합하여 리콜 내역을 상세하게 검색합니다.
- **차량 비교**: 두 개의 특정 차종을 선택하여 총 리콜 건수, 평균 시정률, 주요 결함 키워드를 시각적으로 비교합니다.
- **브랜드 리포트**: 전체 브랜드의 리콜 건수 순위와 평균 시정률 순위를 확인하여 가장 신뢰할 수 있는 브랜드를 분석합니다.
- **모델 프로필**: 특정 차량 모델의 리콜 사유를 워드 클라우드로 시각화하고, 전체 리콜 이력을 제공합니다.
""")

# --- [6. 데이터 출처] ---
st.header("5. 💾 데이터 출처")
st.markdown("""
- 본 프로젝트의 데이터는 공공데이터포털의 **[한국교통안전공단_자동차 리콜대수 및 시정률](https://www.data.go.kr/data/15125831/fileData.do)** 데이터를 기반으로 합니다.
- 4조에서 가공한 **'4조 프로젝트 자동차 리콜현황 Datebase.xlsx'** 파일을 사용하였습니다.
- 데이터 로드 스크립트(`sql/load_data_from_excel.py`)를 통해 MySQL DB(`lemon_scanner_db`)에 적재되어 사용됩니다.
""")

# --- [7. 사용 방법] ---
st.header("6. 📖 사용 방법")
st.success("👈 왼쪽 사이드바에서 원하는 메뉴를 클릭하여 시작하세요!")

# --- [8. 사이드바 설정] ---
st.sidebar.title("환영합니다!")
st.sidebar.markdown(
    """
    **🍋레몬 스캐너**에 오신 것을 환영합니다.
    
    왼쪽 메뉴에서 원하는 페이지를 선택하세요.
    """
)