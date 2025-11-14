# pages/_9_⚙️_마이페이지.py
import streamlit as st
import time 

st.set_page_config(page_title="마이페이지", page_icon="⚙️", layout="wide")
st.title("⚙️ 마이페이지")

# --- 1. 로그인 확인 ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("로그인이 필요한 페이지입니다. 홈 화면에서 로그인해주세요.")
    
    if st.button("홈으로 이동"):
        st.switch_page("Home.py") 
            
else:
    # --- 2. 로그인된 사용자 정보 표시 ---
    st.subheader(f"👋 {st.session_state.get('user_name', '사용자')}님, 환영합니다.")
    st.write(f"**이메일:** {st.session_state.get('user_email', '정보 없음')}")
    
    # --- 3. 회원 정보 수정 (가상) ---
    with st.expander("회원 정보 수정 (가상)", expanded=False):
        st.info("이 기능은 현재 개발 중입니다.")
        new_name = st.text_input("이름 (닉네임) 변경", value=st.session_state.get('user_name', ''))
        new_phone = st.text_input("전화번호 변경", value=st.session_state.get('phone_number', ''))
        
        if st.button("정보 저장"):
            st.success("정보가 (가상으로) 저장되었습니다.")
            st.session_state['user_name'] = new_name 
            st.session_state['phone_number'] = new_phone
            st.rerun() 

    # --- 4. 로그아웃 ---
    st.divider()
    if st.button("로그아웃"):
        for key in st.session_state.keys():
            if key in ['logged_in', 'user_email', 'user_name', 'phone_number']:
                del st.session_state[key]
        
        st.success("로그아웃되었습니다. 3초 후 홈으로 이동합니다.")
        time.sleep(3)
        
        # [★ 오류 수정 2] "0_🏠_메인.py" -> "Home.py"
        st.switch_page("Home.py")