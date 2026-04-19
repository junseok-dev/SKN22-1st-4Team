# 파일 이름: Home.py
import streamlit as st
import time 

from backend.stats_queries import get_summary_stats
from backend.news_api import get_naver_news

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너", 
    page_icon="🍋",       
    layout="wide"
)

# --- [★ 1. 헤더 함수 정의] ---
def display_custom_header():
    """
    페이지 상단에 '오른쪽 정렬'된 로그인/회원가입/마이페이지 버튼을 표시합니다.
    """

    # (파일 이름 대신, 사이드바의 '순서'를 기준으로 마지막 2개 항목을 숨깁니다.)
    # (pages/ 폴더에 7개 파일이 있으므로, 6번, 7번을 숨깁니다)
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] ul > li:nth-last-child(1), /* 7_⚙️_마이페이지.py */
    [data-testid="stSidebarNav"] ul > li:nth-last-child(2)  /* 6_✍️_회원가입.py */
    {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        # --- 로그인된 상태 ---
        user_name = st.session_state.get('user_name', '사용자')
        
        col1, col2, col3 = st.columns([0.7, 0.15, 0.15]) 
        
        with col1:
            st.empty() # 왼쪽을 비워둠
        with col2:
            # [오류 수정] key 추가
            if st.button("⚙️ 마이페이지", use_container_width=True, key="header_mypage"):
               st.switch_page("pages/7_⚙️_마이페이지.py")
        with col3:
            # [오류 수정] key 추가
            if st.button("🚪 로그아웃", use_container_width=True, key="header_logout"):
                st.session_state.logged_in = False
                if 'user_email' in st.session_state: del st.session_state.user_email
                if 'user_name' in st.session_state: del st.session_state.user_name
                st.toast("로그아웃되었습니다.")
                time.sleep(1) 
                st.rerun() 

    else:
        # --- 로그아웃된 상태 ---
        col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
        
        with col1:
            st.empty() # 왼쪽을 비워둠
        with col2:
            # [★ 2차 수정] st.rerun() -> st.switch_page("Home.py")
            if st.button("🔑 로그인", use_container_width=True, key="header_login"):
               st.switch_page("Home.py")
        with col3:
            # [오류 수정] key 추가
            if st.button("✍️ 회원가입", use_container_width=True, key="header_signup"):
               st.switch_page("pages/6_✍️_회원가입.py")
    
    st.divider() # 헤더와 본문 구분선

# --- [★ 2. 헤더 함수 호출] ---
if __name__ == "__main__":
    display_custom_header()


# --- [★ 3. 기존 메인 페이지 콘텐츠] ---
st.title("🍋 레몬 스캐너 (Lemon Scanner)")
st.subheader("자동차 리콜 현황 분석 및 비교 대시보드")
st.markdown("---")

# --- 로그인 상태에 따른 분기 ---
if 'logged_in' in st.session_state and st.session_state.logged_in:
    # --- [로그인 시] 대시보드 ---
    try:
        summary_stats = get_summary_stats()
        brand_name, brand_count = summary_stats['most_recall_brand']
        min_date, max_date = summary_stats['data_period']
        
        st.markdown("### 📊 리콜 현황 요약") 
        
        cols = st.columns(4)
        cols[0].metric("총 리콜 건수", f"{summary_stats['total_recalls']:,} 건")
        cols[1].metric("리콜 대상 브랜드 수", f"{summary_stats['total_brands']:,} 개")
        cols[2].metric("리콜 대상 총 차종 수", f"{summary_stats['total_models']:,} 종")
        cols[3].metric("최다 리콜 브랜드", brand_name, f"{brand_count:,} 건")
        if min_date != 'N/A':
            st.caption(f"ℹ️ (데이터 기준 기간: {min_date} ~ {max_date})")
    except Exception as e:
        st.error(f"요약 통계 로딩 실패: {e}")
    st.markdown("---")

    # --- [로그인 시] 최신 리콜 뉴스 ---
    st.header("📰 최신 리콜 뉴스")
    st.caption("Powered by [Naver Search API](https://developers.naver.com/products/service-api/search/search.md)")
    try:
        news_list = get_naver_news("자동차 리콜")
        for news in news_list:
            st.markdown(f"**[{news['title']}]({news['link']})**")
            st.caption(f"{news['description'][:100]}...")
            st.divider()
    except Exception as e:
        st.error(f"뉴스 로딩 실패: {e}")
    st.markdown("---")

else:
    # --- [로그아웃 시] 로그인 폼 ---
    st.subheader("로그인이 필요합니다")
    
    with st.form("login_form"):
        email = st.text_input("이메일 (테스트: test@test.com)")
        password = st.text_input("비밀번호 (테스트: 1234)", type="password")
        login_button = st.form_submit_button("로그인")
        
        if login_button:
            if email == "test@test.com" and password == "1234": # 임시 테스트 로그인
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.user_name = "테스트 유저"
                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("이메일 또는 비밀번호가 잘못되었습니다.")
    st.markdown("---")


# --- [이하 공통 표시] 리콜 정보 & 꿀팁 ---
st.header("💡 리콜 절차 & 꿀팁")
st.markdown(
    """
    **1. 리콜 대상 확인 방법**
    - [자동차리콜센터(car.go.kr)](https://www.car.go.kr/home/main.do) 공식 사이트 접속
    - 차량번호 또는 차대번호(VIN) 17자리 입력
    - 본인 차량의 리콜 대상 여부 즉시 확인
    
    **2. 리콜 절차**
    - **(통지)** 차량 제조사로부터 리콜 통지서(우편, 문자 등) 수신
    - **(예약)** 해당 차량 제조사의 공식 서비스센터에 정비 예약
    - **(조치)** 예약된 날짜에 방문하여 **무상**으로 점검 및 수리 진행
    
    **3. 리콜 vs 무상수리 차이점**
    - **리콜 (강제/자발적)**: 안전 운행에 **중대한 지장**을 주는 결함 (예: 화재, 시동 꺼짐, 브레이크). 법적 의무이며 시정 기간(1년 6개월)이 정해져 있음.
    - **무상수리**: 안전과 **직접 관련 없는** 결함 (예: 소음, 부품 내구성). 제조사가 고객 만족을 위해 자발적으로 제공.
    """
)
st.markdown("---")

st.header("🔗 관련 사이트 링크")
tip_col1, tip_col2, tip_col3, tip_col4 = st.columns(4)

with tip_col1:
    with st.container(border=True):
        st.subheader("1. 자동차리콜센터 (공식)")
        st.markdown("내 차의 리콜 대상 여부를 차량번호로 즉시 조회할 수 있는 **공식 사이트**입니다.")
        st.link_button(
            "리콜센터 바로가기", 
            "https://www.car.go.kr/home/main.do", 
            use_container_width=True
        )
with tip_col2:
    with st.container(border=True):
        st.subheader("2. 리콜 절차 가이드")
        st.markdown("리콜 대상 확인부터 신청, 수리 절차까지 전 과정을 알기 쉽게 설명한 가이드입니다.")
        st.link_button(
            "절차 가이드 보기 (pro.re.kr)", 
            "https://pro.re.kr/자동차-리콜-대상-확인-방법과-신청-절차-완벽-가이드/", 
            use_container_width=True
        )
with tip_col3:
    with st.container(border=True):
        st.subheader("3. 리콜정보어플")
        st.markdown("중고차 살 때 리콜정보(시정조치)를 어플로 확인하세요.")
        st.link_button(
            "차이점 알아보기 (Naver)", 
            "https://blog.naver.com/llllll0987/222384380892", 
            use_container_width=True
        )
with tip_col4:
    with st.container(border=True):
        st.subheader("4. 리콜 vs 무상수리 ")
        st.markdown("리콜과 무상수리의 차이점을 더 자세히 비교한 블로그 포스트들입니다.")
        st.link_button(
            "비교 (1) - Brunch", 
            "https://brunch.co.kr/@emforce/301", 
            use_container_width=True
        )
        st.link_button(
            "비교 (2) - Naver Blog", 
            "https://m.blog.naver.com/autolog/221481598128", 
            use_container_width=True
        )

# --- 사이드바 설정 ---
st.sidebar.title("환영합니다!")
st.sidebar.markdown(
    """
    **🍋레몬 스캐너**에 오신 것을 환영합니다.
    
    왼쪽 메뉴에서 원하는 페이지를 선택하세요.
    """
)