# pages/_8_✍️_회원가입.py
import streamlit as st
import re
import time
from backend.db_manager import create_connection

# 페이지 설정
st.set_page_config(page_title="회원가입", page_icon="✍️")
st.title("✍️ Lemon Scanner 회원가입")

# --- 유효성 검사 함수 ---
def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)

def is_valid_password(password):
    if len(password) < 8:
        return False, "비밀번호는 8자 이상이어야 합니다."
    if not re.search(r"[a-zA-Z]", password):
        return False, "비밀번호는 영문자를 포함해야 합니다."
    if not re.search(r"\d", password):
        return False, "비밀번호는 숫자를 포함해야 합니다."
    if not re.search(r"[!@#$%^&*()_+=\-{}\[\]:\"';<>,./?]", password):
        return False, "비밀번호는 특수문자를 포함해야 합니다."
    return True, ""

# --- DB 함수 ---
def check_user_exists(email):
    conn = create_connection()
    if conn is None: return True 
    cursor = None
    try:
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM User WHERE user_email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result and result[0] > 0
    except Exception as e:
        st.error(f"DB 오류 (중복 확인): {e}")
        return True 
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

def create_user(email, hashed_password, username, phone):
    conn = create_connection()
    if conn is None: return False
    cursor = None
    try:
        cursor = conn.cursor()
        query = "INSERT INTO User (user_email, user_password, user_name, phone_number, join_date) VALUES (%s, %s, %s, %s, CURDATE())"
        cursor.execute(query, (email, hashed_password, username, phone))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"DB 오류 (사용자 생성): {e}")
        conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# --- 회원가입 폼 ---
with st.form(key="signup_form"):
    st.markdown("**필수 정보를 입력해주세요.**")
    email = st.text_input("이메일 (ID)", placeholder="example@email.com")
    username = st.text_input("이름 (닉네임)", placeholder="레몬스캐너")
    password = st.text_input("비밀번호", type="password", placeholder="8자 이상, 영문/숫자/특수문자 포함")
    confirm_password = st.text_input("비밀번호 확인", type="password")
    phone = st.text_input("전화번호 (선택)", placeholder="010-1234-5678 (선택)")
    submit_button = st.form_submit_button(label="가입하기")

if submit_button:
    if not email or not username or not password or not confirm_password:
        st.error("필수 항목(이메일, 이름, 비밀번호)을 모두 입력해주세요.")
    elif not is_valid_email(email):
        st.error("유효한 이메일 주소를 입력해주세요.")
    elif password != confirm_password:
        st.error("비밀번호가 일치하지 않습니다.")
    else:
        is_strong, message = is_valid_password(password)
        if not is_strong:
            st.error(message)
        else:
            if check_user_exists(email):
                st.error("이미 사용 중인 이메일입니다.")
            else:
                hashed_password = password # [!] 임시 조치.
                if create_user(email, hashed_password, username, phone):
                    st.success(f"{username}님, 회원가입을 축하합니다!")
                    st.info("3초 후 자동으로 로그인 페이지(홈)로 이동합니다.")
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email
                    st.session_state['user_name'] = username
                    time.sleep(3)
                    
                    # [★ 오류 수정] "0_🏠_메인.py" -> "Home.py"
                    st.switch_page("Home.py") 
                    
                else:
                    st.error("회원가입 중 오류가 발생했습니다. 다시 시도해주세요.")