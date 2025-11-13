# 파일 이름: backend/stats_queries.py
import pandas as pd
import streamlit as st
from datetime import date, datetime # [수정] datetime 객체도 import
from . import db_manager # 같은 폴더의 db_manager를 임포트
import decimal # 타입 검사를 위해 임포트

# --- [수정] Pylance 경고를 해결하기 위해 로직 재구성 ---
@st.cache_data(ttl=3600)
def get_summary_stats():
    """상단 요약 대시보드를 위한 통계 데이터를 가져옵니다."""
    stats = {
        'total_recalls': 0, 'total_brands': 0, 'total_models': 0,
        'most_recall_brand': ('N/A', 0), 'data_period': ('N/A', 'N/A')
    }
    conn = db_manager.create_connection()
    if conn is None: return stats
    
    cursor = None 
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Pylance를 위한 안전한 int 변환 헬퍼 함수
        def safe_int_from_value(value, default=0):
            if isinstance(value, (int, float, decimal.Decimal, str)):
                try:
                    return int(float(value)) 
                except (ValueError, TypeError):
                    return default 
            return default

        # 1. 총 리콜 건수
        cursor.execute("SELECT COUNT(recall_id) as count FROM Recall")
        result = cursor.fetchone()
        if isinstance(result, dict): 
             stats['total_recalls'] = safe_int_from_value(result.get('count'))

        # 2. 총 브랜드 수
        cursor.execute("SELECT COUNT(brand_id) as count FROM Brand")
        result = cursor.fetchone()
        if isinstance(result, dict): 
            stats['total_brands'] = safe_int_from_value(result.get('count'))

        # 3. 총 차종 수
        cursor.execute("SELECT COUNT(model_id) as count FROM Model")
        result = cursor.fetchone()
        if isinstance(result, dict): 
            stats['total_models'] = safe_int_from_value(result.get('count'))

        # 4. 최다 리콜 브랜드
        query = """
        SELECT b.brand_name, COUNT(r.recall_id) as count 
        FROM Recall r JOIN Model m ON r.model_id = m.model_id JOIN Brand b ON m.brand_id = b.brand_id
        GROUP BY b.brand_name ORDER BY count DESC LIMIT 1;
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if isinstance(result, dict): 
            brand_name = result.get('brand_name', 'N/A')
            brand_count = safe_int_from_value(result.get('count'))
            stats['most_recall_brand'] = (brand_name, brand_count)
            
        # 5. 데이터 기준 기간 (MIN/MAX 날짜)
        cursor.execute("SELECT MIN(recall_date) as min_date, MAX(recall_date) as max_date FROM Recall WHERE recall_date IS NOT NULL")
        result = cursor.fetchone()
        
        # --- [수정된 부분] Pylance 경고 해결 ---
        if isinstance(result, dict):
            min_date_val = result.get('min_date')
            max_date_val = result.get('max_date')
            
            # [안전 블록] strftime은 date 또는 datetime 객체에서만 호출
            if isinstance(min_date_val, (date, datetime)) and isinstance(max_date_val, (date, datetime)):
                min_date_str = min_date_val.strftime('%Y-%m-%d')
                max_date_str = max_date_val.strftime('%Y-%m-%d')
                stats['data_period'] = (min_date_str, max_date_str)
        # --- [수정 끝] ---
            
    except Exception as e:
        print(f"get_summary_stats 오류: {e}")
    finally:
        if cursor: cursor.close() 
        if conn and conn.is_connected():
            conn.close()
    return stats
# --- [수정된 함수 끝] ---


@st.cache_data(ttl=3600)
def get_brand_rankings():
    """브랜드 리포트 페이지를 위한 순위 데이터를 가져옵니다."""
    conn = db_manager.create_connection()
    if conn is None:
        return pd.DataFrame(), pd.DataFrame()
    df_recall_count = pd.DataFrame()
    df_correction_rate = pd.DataFrame()
    try:
        recall_count_query = """
        SELECT 
            b.brand_name AS '브랜드', COUNT(DISTINCT r.recall_id) AS '총 리콜 건수'
        FROM Recall r
        JOIN Model m ON r.model_id = m.model_id
        JOIN Brand b ON m.brand_id = b.brand_id
        GROUP BY b.brand_name ORDER BY `총 리콜 건수` DESC;
        """
        df_recall_count = pd.read_sql(recall_count_query, conn)
        df_recall_count.index = df_recall_count.index + 1

        correction_rate_query = """
        SELECT 
            b.brand_name AS '브랜드', AVG(r.correction_rate) AS '평균 시정률 (%)',
            COUNT(DISTINCT r.recall_id) AS '리콜 건수'
        FROM Recall r
        JOIN Model m ON r.model_id = m.model_id
        JOIN Brand b ON m.brand_id = b.brand_id
        GROUP BY b.brand_name HAVING `리콜 건수` >= 5 
        ORDER BY `평균 시정률 (%)` DESC;
        """
        df_correction_rate = pd.read_sql(correction_rate_query, conn)
        df_correction_rate.index = df_correction_rate.index + 1
        df_correction_rate['평균 시정률 (%)'] = df_correction_rate['평균 시정률 (%)'].round(2)
    except Exception as e:
        print(f"get_brand_rankings 오류: {e}")
        return pd.DataFrame(), pd.DataFrame() 
    finally:
        if conn and conn.is_connected():
            conn.close()
    return df_recall_count, df_correction_rate