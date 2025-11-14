import streamlit as st
import pandas as pd
import os
from backend.stats_queries import get_summary_stats
from Home import display_custom_header 

# --- [0] 페이지 기본 설정 ---
st.set_page_config(
    page_title="레몬 스캐너 - 부품 사전",
    page_icon="🚗", 
    layout="wide"
)

display_custom_header()

st.markdown("""
<style>
    .part-description {
        font-size: 17px !important;
        line-height: 1.6 !important;
    }
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------------

# --- [1] 부품 정보 딕셔너리 ---
PARTS_INFO = {
    "--- 부품 선택 ---": {
        "part_image": "", # (이미지 경로 키 이름 통일)
        "description": "궁금한 부품을 선택하세요. 해당 부품의 실제 사진과 상세 설명을 보여줍니다."
    },
    "엔진 (Engine)": {
        "part_image": "assets/suv_parts/suv_engine.jpg", 
        "description": """
        **엔진은 자동차의 심장입니다.** 연료(가솔린, 디젤 등)를 연소시켜 동력을 발생시키는 장치입니다.
        
        - **주요 결함 (리콜 사유):**
            - **엔진 오일 누유:** 엔진 내부 윤활유가 새어 나와 화재의 원인이 될 수 있습니다.
            - **시동 꺼짐:** 연료 공급 불량, 점화 장치(코일, 플러그) 결함 등으로 주행 중 시동이 꺼질 수 있습니다.
            - **냉각 불량:** 냉각수 누수, 워터펌프 고장 등으로 엔진이 과열(오버히트)될 수 있습니다.
        """
    },
    "브레이크 (Brake System)": {
        "part_image": "assets/suv_parts/suv_brake.jpg", 
        "description": """
        **브레이크는 자동차를 멈추는 제동 장치입니다.** 디스크, 캘리퍼, 브레이크 패드, 브레이크 오일 등으로 구성됩니다.
        
        - **주요 결함 (리콜 사유):**
            - **제동 밀림:** 브레이크 오일 누유, 브레이크 호스 파열 등으로 제동력이 급격히 저하될 수 있습니다.
            - **ABS 모듈 결함:** ABS(잠김 방지 브레이크 시스템) 모듈 내부에 이물질이 유입되거나 전자 결함이 발생하여 브레이크가 제대로 작동하지 않을 수 있습니다.
        """
    },
    "ECU (Electronic Control Unit)": {
        "part_image": "assets/suv_parts/suv_ecu.jpg", 
        "description": """
        **ECU는 자동차의 '두뇌' 역할을 하는 전자 제어 유닛입니다.** 엔진, 변속기, 브레이크 등 차량의 거의 모든 부분을 전자적으로 제어합니다.
        
        - **주요 결함 (리콜 사유):**
            - **소프트웨어 오류:** ECU 소프트웨어 로직 오류로 인해 주행 중 시동이 꺼지거나, 변속이 비정상적으로 작동하거나, 경고등이 잘못 점등될 수 있습니다. (가장 흔한 리콜 사유 중 하나)
            - **ECU 내부 결함:** ECU 기판의 납땜 불량, 방수 처리 미흡으로 인한 부식 등으로 ECU가 고장 날 수 있습니다.
        """
    },
    "조향 장치 (Steering System)": {
        "part_image": "assets/suv_parts/suv_steering_system.jpg",
        "description": """
        **조향 장치는 자동차의 방향을 바꾸는 장치입니다.** 운전대(스티어링 휠)와 바퀴를 연결해줍니다. (예: MDPS)
        
        - **주요 결함 (리콜 사유):**
            - **MDPS 결함:** 전동식 파워 스티어링(MDPS) 모터 또는 센서의 결함으로 운전대가 갑자기 무거워지거나(핸들 잠김) 특정 방향으로 쏠릴 수 있습니다.
            - **조향 기어 불량:** 핸들 조작을 바퀴로 전달하는 기어(기어박스)의 부품 불량으로 유격이 발생할 수 있습니다.
        """
    },
    "배터리 (Battery / BMS)": {
        "part_image": "assets/suv_parts/suv_battery.jpg",
        "description": """
        **배터리는 전력을 저장하고 공급하는 장치입니다.** (일반 12V 배터리, 전기차/하이브리드의 고전압 배터리)
        
        - **주요 결함 (리콜 사유):**
            - **BMS 오류:** 배터리 관리 시스템(BMS)의 소프트웨어 오류로 인해 배터리가 과충전되거나, 주행 가능 거리가 잘못 표시될 수 있습니다.
            - **배터리 셀 결함:** (주로 전기차) 배터리 셀 자체의 제조 불량으로 인해 내부 합선(쇼트)이 발생하여 화재의 위험이 있습니다.
        """
    },
     "연료 장치 (Fuel System)": {
        "part_image": "assets/suv_parts/suv_fuel_system.png",
        "description": """
        **연료 장치는 엔진에 연료를 공급하는 시스템입니다.** 연료 탱크, 연료 펌프, 연료 라인(호스) 등으로 구성됩니다.
        
        - **주요 결함 (리콜 사유):**
            - **연료 누유:** 연료 라인의 균열이나 연결부 불량으로 연료가 새어 나와 화재의 원인이 될 수 있습니다.
            - **연료 펌프 결함:** 연료 펌프 내부 부품의 결함으로, 주행 중 시동이 꺼질 수 있습니다.
        """
    },
    "변속기 (Transmission)": {
        "part_image": "assets/suv_parts/suv_Transmission.jpg",
        "description": """
        **변속기는 엔진의 동력을 바퀴로 전달하는 속도를 조절하는 장치입니다.** (자동, 수동, 듀얼 클러치 등)
        
        - **주요 결함 (리콜 사유):**
            - **TCU 오류:** 변속기 제어 유닛(TCU)의 소프트웨어 오류로 변속이 충격이 발생하거나, 특정 단수로 변속이 안 될 수 있습니다.
            - **내부 부품 결함:** 오일 펌프, 클러치 팩 등 내부 부품의 내구성 부족으로 파손될 수 있습니다.
        """
    },
    "에어백 (Airbag)": {
        "part_image": "assets/suv_parts/suv_airbag.jpg",
        "description": """
        **에어백은 충돌 시 탑승자를 보호하는 안전 장치입니다.** 제어 유닛(ACU), 센서, 인플레이터(가스 발생 장치)로 구성됩니다.
        
        - **주요 결함 (리콜 사유):**
            - **인플레이터 결함:** (다카타 에어백 이슈) 에어백이 터질 때 인플레이터가 파손되면서 금속 파편이 튀어 탑승자에게 2차 상해를 입힐 수 있습니다.
            - **센서 오류:** 충돌 감지 센서의 오류로 에어백이 필요할 때 전개되지 않거나, 불필요하게 전개될 수 있습니다.
        """
    },
    "센서 (Sensors)": {
        "part_image": "assets/suv_parts/suv_senseors.png", 
        "description": """
        **센서는 차량의 상태를 감지하는 다양한 전자 부품입니다.** (ABS 휠 속도 센서, 크랭크각 센서, 카메라 센서 등)
        
        - **주요 결함 (리콜 사유):**
            - **센서 신호 오류:** 특정 센서가 잘못된 신호를 ECU로 보내, ABS나 ESC(차체 자세 제어) 기능이 오작동하거나 엔진 출력이 저하될 수 있습니다.
            - **센서 내부 결함:** 센서 자체의 방수 불량이나 내부 단선으로 인해 고장 날 수 있습니다.
        """
    },
}
PART_LIST = list(PARTS_INFO.keys()) # Selectbox의 목록

# --- [2] 제목 ---
st.title("🚗 자동차 부품 사전")
st.info("리콜 사유에 자주 등장하는 자동차 부품이 어떤 역할을 하는지 알아보세요.")
st.markdown("---")

# --- [3] (수정) 부품 선택 (도면 삭제) ---
selected_part = st.selectbox(
    "궁금한 부품을 선택하세요:",
    PART_LIST
)
st.markdown("---") # 선택 상자와 정보란 구분

# --- [4] (신규) 2단 레이아웃 (사진 + 설명) ---
part = PARTS_INFO[selected_part]

if selected_part == "--- 부품 선택 ---":
    # 기본 안내 메시지 (이것도 CSS를 적용합니다)
    st.markdown(f'<div class="part-description">{part["description"]}</div>', unsafe_allow_html=True)
else:
    # 선택 시, 2단으로 분리
    col_img, col_desc = st.columns([0.5, 0.5]) # 50:50 비율

    with col_img:
        # 왼쪽: 실제 부품 사진
        st.subheader(f"📷 {selected_part} 이미지")
        if os.path.exists(part["part_image"]):
            st.image(part["part_image"], caption=f"실제 {selected_part} 이미지")
        else:
            st.warning(f"`{part['part_image']}` 이미지를 찾을 수 없습니다. ('assets/suv_parts/' 폴더 확인 필요)")
    
    with col_desc:
        # 오른쪽: 부품 설명
        st.subheader("⚙️ 부품 설명 및 주요 결함")
        
        # (CSS 클래스를 적용하기 위해 div로 감싸줍니다)
        st.markdown(f"""
        <div class="part-description">
        {part["description"]}
        </div>
        """, unsafe_allow_html=True)

# --- [5] 데이터 기준 기간 표시 ---
try:
    summary_stats = get_summary_stats()
    min_date, max_date = summary_stats['data_period']
    st.markdown("---")
    if min_date != 'N/A':
        st.caption(f"ℹ️ (데이터 기준 기간: {min_date} ~ {max_date})")
except Exception:
    pass
