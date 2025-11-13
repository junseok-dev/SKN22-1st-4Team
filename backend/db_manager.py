# 파일 이름: backend/db_manager.py
import mysql.connector
from mysql.connector import Error
import streamlit as st # [신규] st.secrets를 읽기 위해 임포트

# [수정] 하드코딩된 DB_CONFIG 딕셔너리 삭제
# DB_CONFIG = { ... } <-- 이 부분을 삭제합니다.

def create_connection():
    """
    st.secrets에서 DB 정보를 읽어와 연결합니다.
    """
    conn = None
    try:
        # [수정] st.secrets에서 직접 DB 정보 가져오기
        conn = mysql.connector.connect(
            host=st.secrets['db_credentials']['host'],
            user=st.secrets['db_credentials']['user'],
            password=st.secrets['db_credentials']['password'],
            database=st.secrets['db_credentials']['database']
        )
        return conn
    except Error as e:
        print(f"데이터베이스 연결 오류: {e}")
    except KeyError:
        st.error("DB 접속 정보 오류: .streamlit/secrets.toml 파일에 [db_credentials] 섹션을 확인하세요.")
        return None
    except Exception as e:
        st.error(f"알 수 없는 DB 연결 오류: {e}")
        return None