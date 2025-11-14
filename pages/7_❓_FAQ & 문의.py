import streamlit as st
from backend.stats_queries import get_summary_stats
from Home import display_custom_header 

# --- [0] 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너 - FAQ",
    page_icon="❓", 
    layout="wide"
)

display_custom_header()

# --- [1] 제목 ---
st.title("❓ 자주 묻는 질문 (FAQ)")
st.info("레몬 스캐너 프로젝트와 자동차 리콜에 대해 자주 묻는 질문들을 모았습니다.")
st.markdown("---")

# --- [2] FAQ / 개인 문의 탭 생성 ---
tab_faq, tab_contact = st.tabs(["❓ 자주 묻는 질문 (FAQ)", "✉️ 개인 문의하기"])


# --- [탭 1: FAQ (볼드체/들여쓰기/텍스트 수정 완료)] ---
with tab_faq:

    # --- 카테고리 1: 프로젝트 관련 ---
    st.subheader("프로젝트 (레몬 스캐너) 관련")
    
    with st.expander("Q. 🍋 '레몬 스캐너' 프로젝트는 무엇인가요?"):
       st.markdown("""
이 프로젝트는 SK Networks Family AI Camp 22기 4조의 1차 프로젝트입니다.

국내에 등록된 차량의 리콜 데이터를 수집, 분석하여 사용자에게 유용한 정보로 제공하는 것을 목표로 합니다.

자세한 내용은 **🚀 프로젝트 소개** 페이지를 참고해주세요!
""")

    with st.expander("Q. 💾 이 앱의 데이터는 얼마나 최신인가요?"):
        st.markdown("""
이 앱의 데이터는 `sql/load_data_from_excel.py` 스크립트를 수동으로 실행할 때만 업데이트됩니다.

따라서 **실시간 데이터가 아닙니다.**

현재 DB에 저장된 데이터의 기준 기간은 아래와 같습니다.
""")
        try:
            summary_stats = get_summary_stats()
            min_date, max_date = summary_stats['data_period']
            if min_date != 'N/A':
                st.success(f"**현재 데이터 기준 기간: {min_date} ~ {max_date}**")
        except Exception as e:
            st.error(f"데이터 기간을 불러오는 데 실패했습니다: {e}")

    st.markdown("---")
    
    # --- 카테고리 2: 리콜 기본 정보 ---
    st.subheader("리콜 정보 관련")
    
    with st.expander("Q. 🚗 제 차가 리콜 대상인지 어떻게 확인하나요?"):
        st.markdown("""
가장 정확하고 빠른 방법은 **자동차리콜센터** 공식 사이트를 이용하는 것입니다.

1. **[자동차리콜센터(car.go.kr)](https://www.car.go.kr/home/main.do)** 사이트에 접속합니다.
2. '리콜알리미' 섹션에서 **차량번호** 또는 **차대번호(VIN) 17자리**를 입력합니다.
3. 본인 차량의 리콜 대상 여부와 조치 현황을 즉시 확인할 수 있습니다.

리콜 대상이라면, 제조사의 공식 서비스센터에 예약 후 방문하여 **무상으로 조치**를 받으실 수 있습니다.
""")
        st.link_button(
            "자동차리콜센터 바로가기", 
            "https://www.car.go.kr/home/main.do", 
            use_container_width=True
        )


    with st.expander("Q. 💡 리콜(Recall)과 무상수리는 어떻게 다른가요?"):
        # [수정] 볼드체가 적용되도록 내부 들여쓰기 제거
        st.markdown("""
**가장 큰 차이는 '안전'과 '강제성'입니다.**

- **리콜 (법적 의무)**: 
    - **이유:** 안전 운행에 **중대한 지장**을 주는 결함 (예: 화재, 시동 꺼짐, 브레이크 결함)
    - **특징:** 법적 의무이며, 제조사는 차량 소유주에게 이 사실을 **공개적으로 통지**해야 합니다. 시정 기간(보통 1년 6개월)이 정해져 있습니다.

- **무상수리 (자발적 서비스)**:
    - **이유:** 안전과 **직접 관련 없는** 결함 (예: 소음, 부품 내구성 불만, 편의장치 작동 불량)
    - **특징:** 제조사가 고객 만족 차원에서 자발적으로 제공하는 '서비스'입니다. 통지 의무가 없어 소유주가 모르면 받지 못하는 경우도 많습니다.

더 궁금한 점이 있다면 아래 링크를 참고하세요.
""")
        st.link_button(
            "리콜 vs 무상수리 차이점", 
            "https://brunch.co.kr/@emforce/301", 
            use_container_width=True
        )
        
    with st.expander("Q. 📖 리콜 절차 가이드가 필요해요."):
        st.markdown("""
리콜 대상 확인부터 신청, 수리 절차까지 전 과정을 알기 쉽게 설명한 가이드입니다.

또한, 중고차 구매 시 리콜 정보를 어플로 확인하는 팁도 얻을 수 있습니다.
""")
        st.link_button(
            "절차 가이드 보기 (pro.re.kr)", 
            "https://pro.re.kr/자동차-리콜-대상-확인-방법과-신청-절차-완벽-가이드/", 
            use_container_width=True
        )

    with st.expander("Q. ⚙️ 'ECU', 'BMS', 'MDPS'가 무슨 뜻인가요?"):
        # [수정] 볼드체가 적용되도록 내부 들여쓰기 제거
        st.markdown("""
리콜 사유에 자주 등장하는 약어들입니다.

- **ECU (Electronic Control Unit):** 자동차의 '두뇌' 역할을 하는 전자 제어 유닛입니다.
- **BMS (Battery Management System):** (주로 전기차/하이브리드) 배터리를 관리하는 시스템입니다.
- **MDPS (Motor-Driven Power Steering):** 전동식 파워 스티어링(핸들)입니다.

더 자세한 내용은 **🚗 부품 사전** 페이지를 참고해주세요!
""") 
    st.markdown("---")

    # --- 카테고리 3: 앱 활용 팁 ---
    st.subheader("앱 활용 팁")

    with st.expander("Q. 🔍 구매하려는 차량의 리콜 이력을 어떻게 확인하나요?"):
        st.markdown("""
**🍋 상세 검색** 페이지를 활용하세요.

궁금한 차량의 **브랜드**와 **차종**을 선택하고, **연도**까지 지정하여 검색하면 해당 차량의 모든 리콜 이력을 한눈에 볼 수 있습니다. 구매 전 잠재적 결함을 파악하는 데 큰 도움이 됩니다.
""")

    with st.expander("Q. ⚖️ 두 차량 중 어떤 걸 사야 할지 모르겠어요. 비교할 수 있나요?"):
        st.markdown("""
**📊 차량 비교** 페이지를 활용하세요.

비교하고 싶은 **차량 1**과 **차량 2**를 각각 선택하고 '비교하기' 버튼을 누르면, 두 차량의 **총 리콜 건수, 평균 시정률, 주요 결함 키워드(TOP 10)**를 그래프로 한눈에 비교할 수 있습니다.
""")

    with st.expander("Q. 🏆 어떤 브랜드가 가장 신뢰할 만한가요?"):
        # [수정] 볼드체가 적용되도록 내부 들여쓰기 제거
        st.markdown("""
**🏆 브랜드 리포트** 페이지를 확인해 보세요.

- **리콜 건수 순위**에서는 어떤 브랜드가 리콜을 많이 했는지 볼 수 있습니다.
- **평균 시정률 순위**에서는 리콜 발생 시 얼마나 책임감 있게 조치를 완료했는지 볼 수 있습니다.

시정률이 높은 브랜드는 사후 관리가 잘 되는 브랜드라고 판단할 수 있습니다.
""")
        
    with st.expander("Q. 📈 리콜 이력이 많은 차는 무조건 나쁜 차인가요?"):
        # [수정] 볼드체가 적용되도록 내부 들여쓰기 제거
        st.markdown("""
**그렇지 않습니다. 리콜이 많다는 것은 2가지 의미가 있습니다.**

1. 해당 차량에 결함이 많다. (부정적)
2. 제조사가 사소한 결함도 숨기지 않고 **적극적으로 리콜하여 고객에게 알린다.** (긍정적)

단순히 리콜 건수만 보지 마시고, **"시정률"이 높은지** (조치를 잘 해주는지)를 함께 확인하는 것이 중요합니다.
""")
        
    with st.expander("Q. 📝 제가 찾는 모델이나 리콜 데이터가 없으면 어떻게 해야 하나요?"):
        # [수정] 볼드체가 적용되도록 내부 들여쓰기 제거
        st.markdown("""
이 앱의 데이터는 `sql/load_data_from_excel.py`로 적재된 데이터를 기반으로 합니다. 

만약 데이터에 오류가 있거나, 누락된 모델이 있다고 생각되시면, **[✉️ 개인 문의하기]** 탭을 통해 팀장에게 직접 문의하시거나 GitHub 이슈로 제보해주시면 감사하겠습니다.
""")


# --- [탭 2: 개인 문의하기] ---
with tab_contact:
    st.subheader("프로젝트 팀에게 문의하기")
    st.markdown("""
        이 프로젝트의 기능, 코드, 데이터 등에 대해 궁금한 점이 있으신가요?
        
        가장 좋은 방법은 **GitHub 리포지토리의 'Issues' 탭**에 질문을 남겨주시는 것입니다. 
        팀원들이 확인하고 답변을 드릴 수 있으며, 다른 사용자들과도 논의를 공유할 수 있습니다.
    """)
    
    st.link_button(
        "GitHub Issues 바로가기", 
        "https://github.com/skn-ai22-251029/SKN22-1st-4Team/issues", # (수정된 주소)
        use_container_width=True
    )
    
    st.markdown("---")
    st.subheader("팀장(장완식)에게 직접 연락하기")
    st.info("이메일: skn22@skn22") # (수정된 이메일)