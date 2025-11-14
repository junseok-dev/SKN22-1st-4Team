# 파일 이름: backend/search_queries.py
import pandas as pd
import streamlit as st
import decimal
from . import db_manager # 같은 폴더의 db_manager를 임포트

@st.cache_data(ttl=3600)
def get_all_brands():
    query = "SELECT brand_name FROM Brand ORDER BY brand_name;"
    conn = db_manager.create_connection()
    if conn is None: return []
    try:
        df = pd.read_sql(query, conn)
        return df['brand_name'].tolist()
    except Exception as e:
        print(f"get_all_brands 오류: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

@st.cache_data(ttl=3600)
def get_models_by_brand(brand_name):
    query = """
    SELECT m.model_name FROM Model m
    JOIN Brand b ON m.brand_id = b.brand_id
    WHERE b.brand_name = %s ORDER BY m.model_name;
    """
    conn = db_manager.create_connection()
    if conn is None: return []
    try:
        df = pd.read_sql(query, conn, params=(brand_name,))
        return df['model_name'].tolist()
    except Exception as e:
        print(f"get_models_by_brand 오류: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            conn.close()

@st.cache_data(ttl=3600)
def get_all_keywords_with_desc():
    query = "SELECT keyword_text, keyword_desc FROM Keyword ORDER BY keyword_text;"
    conn = db_manager.create_connection()
    if conn is None: return {}
    
    keyword_dict = {}
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                if isinstance(row, dict): 
                    key = row.get('keyword_text')
                    desc = row.get('keyword_desc')
                    if key: 
                        keyword_dict[key] = desc
                        
        return keyword_dict
        
    except Exception as e:
        print(f"get_all_keywords_with_desc 오류: {e}")
        return {}
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected():
            conn.close()

# --- [수정된 함수] ---
def search_recalls(brand, model, year, keyword):
    conn = db_manager.create_connection()
    if conn is None: return pd.DataFrame() 
    cursor = None
    try:
        query = """
        SELECT 
            r.recall_id AS '리콜ID', -- [★ 수정] 클릭 이벤트를 위해 recall_id 추가
            b.brand_name AS '브랜드', 
            m.model_name AS '차종', 
            r.recall_date AS '리콜개시일',
            r.prod_from AS '생산시작', 
            r.prod_to AS '생산종료', 
            r.reason AS '리콜사유',
            r.recall_count AS '리콜대수', 
            r.correction_count AS '시정대수', 
            r.correction_rate AS '시정률(%)' 
        FROM Recall AS r
        JOIN Model AS m ON r.model_id = m.model_id
        JOIN Brand AS b ON m.brand_id = b.brand_id
        LEFT JOIN Recall_Keyword_Junction AS rkj ON r.recall_id = rkj.recall_id
        LEFT JOIN Keyword AS k ON rkj.keyword_id = k.keyword_id
        """
        where_clauses = []
        params = []
        if brand and brand != "전체":
            where_clauses.append("b.brand_name = %s")
            params.append(brand)
        if model and model != "전체":
            where_clauses.append("m.model_name = %s")
            params.append(model)
        if year and year != "전체":
            where_clauses.append("YEAR(r.recall_date) = %s")
            params.append(str(year))
        if keyword and keyword != "전체":
            where_clauses.append("k.keyword_text = %s")
            params.append(keyword)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += " GROUP BY r.recall_id ORDER BY r.recall_date DESC LIMIT 200;"
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        results_list = cursor.fetchall()

        if not results_list:
            return pd.DataFrame()
        return pd.DataFrame(results_list)
    except Exception as e:
        print(f"백엔드 쿼리 오류 (search_recalls): {e}")
        return pd.DataFrame()
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
# --- [수정 끝] ---


def get_recall_comparison(brand, model):
    if not brand or not model or brand == "전체" or model == "전체":
        return None, pd.DataFrame() 
    conn = db_manager.create_connection()
    if conn is None:
        return None, pd.DataFrame()
    
    stats = {'total_recalls': 0, 'avg_correction_rate': 0}
    keywords_df = pd.DataFrame()
    cursor = None
    
    try:
        cursor = conn.cursor(dictionary=True)
        stats_query = """
        SELECT COUNT(DISTINCT r.recall_id) as total_recalls, AVG(r.correction_rate) as avg_correction_rate
        FROM Recall r JOIN Model m ON r.model_id = m.model_id JOIN Brand b ON m.brand_id = b.brand_id
        WHERE b.brand_name = %s AND m.model_name = %s;
        """
        cursor.execute(stats_query, (brand, model))
        stats_result = cursor.fetchone()
        
        if isinstance(stats_result, dict):
            total_recalls_count = 0
            value = stats_result.get('total_recalls')
            if isinstance(value, (int, float, decimal.Decimal, str)):
                try:
                    total_recalls_count = int(float(value)) 
                except (ValueError, TypeError):
                    total_recalls_count = 0
            
            if total_recalls_count > 0:
                final_avg_rate = 0
                avg_rate = stats_result.get('avg_correction_rate') 
                if isinstance(avg_rate, (decimal.Decimal, float, int)):
                    final_avg_rate = round(float(avg_rate), 2)
                
                stats = {'total_recalls': total_recalls_count, 'avg_correction_rate': final_avg_rate}

        keywords_query = """
        SELECT k.keyword_text, k.keyword_desc, COUNT(k.keyword_text) as keyword_count
        FROM Recall r
        JOIN Model m ON r.model_id = m.model_id
        JOIN Brand b ON m.brand_id = b.brand_id
        JOIN Recall_Keyword_Junction rkj ON r.recall_id = rkj.recall_id
        JOIN Keyword k ON rkj.keyword_id = k.keyword_id
        WHERE b.brand_name = %s AND m.model_name = %s
        GROUP BY k.keyword_text, k.keyword_desc ORDER BY keyword_count DESC LIMIT 10;
        """
        cursor.execute(keywords_query, (brand, model))
        keywords_list = cursor.fetchall()
        if keywords_list:
            keywords_df = pd.DataFrame(keywords_list)
            
    except Exception as e:
        print(f"백엔드 쿼리 오류 (get_recall_comparison): {e}")
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

    return stats, keywords_df

@st.cache_data(ttl=3600)
def get_model_profile_data(brand, model):
    if not brand or not model or brand == "전체" or model == "전체":
        return pd.DataFrame(), "" 
    conn = db_manager.create_connection()
    if conn is None:
        return pd.DataFrame(), ""
    history_df = pd.DataFrame()
    all_reasons_string = ""
    cursor = None 
    try:
        query = """
        SELECT 
            r.recall_date AS '리콜개시일', r.reason AS '리콜사유',
            r.recall_count AS '리콜대수', r.correction_rate AS '시정률(%)'
        FROM Recall r
        JOIN Model m ON r.model_id = m.model_id
        JOIN Brand b ON m.brand_id = b.brand_id
        WHERE b.brand_name = %s AND m.model_name = %s
        ORDER BY r.recall_date DESC;
        """
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (brand, model))
        rows = cursor.fetchall()
        
        if rows:
            history_df = pd.DataFrame(rows)
            
            reason_list = []
            for row in rows:
                if isinstance(row, dict):
                    reason = row.get('리콜사유')
                    if isinstance(reason, str): 
                        reason_list.append(reason)
            
            all_reasons_string = " ".join(reason_list)
            
    except Exception as e:
        print(f"get_model_profile_data 오류: {e}")
    finally:
        if cursor: cursor.close() 
        if conn and conn.is_connected(): conn.close()
    return history_df, all_reasons_string

# --- [★ 신규 함수] ---
@st.cache_data(ttl=600) # 10분간 캐시
def get_keywords_for_recall(recall_id):
    """특정 recall_id에 연결된 모든 키워드를 조회합니다."""
    
    conn = db_manager.create_connection()
    if conn is None:
        return []

    keywords = []
    cursor = None
    try:
        query = """
        SELECT k.keyword_text 
        FROM Recall_Keyword_Junction j
        JOIN Keyword k ON j.keyword_id = k.keyword_id
        WHERE j.recall_id = %s;
        """
        cursor = conn.cursor()
        cursor.execute(query, (recall_id,))
        rows = cursor.fetchall()
        
        if rows:
            keywords = [row[0] for row in rows] # (('엔진',), ('화재',)) -> ['엔진', '화재']

    except Exception as e:
        print(f"get_keywords_for_recall 오류: {e}")
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()
    
    return keywords
# --- [신규 함수 끝] ---