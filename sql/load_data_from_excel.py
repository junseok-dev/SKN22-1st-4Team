# 파일 이름: load_data_from_excel.py
# (경로: C:\Workspaces\SKN22-1st-4Team\sql\load_data_from_excel.py)

import pandas as pd
import numpy as np
import re
import os
import mysql.connector
from mysql.connector import Error

# --- [필수] 설정 ---

# 1. DB 접속 정보
DB_CONFIG = {
    'host': 'localhost',
    'user': 'skn22', 
    'password': 'skn22',
    'database': 'lemon_scanner_db'
}

# --- [수정된 부분] Excel 파일 경로 설정 ---
# 1. 이 스크립트 파일이 있는 디렉토리 (즉, 'sql' 폴더)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 원본 Excel 파일 이름
EXCEL_FILE_NAME = '4조 프로젝트 자동차 리콜현황 Datebase.xlsx'

# 3. 원본 Excel 파일의 전체 경로 (스크립트와 같은 'sql' 폴더)
EXCEL_FILE_PATH = os.path.join(SCRIPT_DIR, EXCEL_FILE_NAME)

# 4. 읽어올 시트 이름 (원본 CSV 파일 이름에서 유추)
SHEET_NAMES = [
    '리콜현황', 
    '그외 차량 리콜 현황'
]
# ----------------------------------------

# --- 키워드 목록 (설명 포함) ---
KEYWORDS_DATA = [
    ('엔진', '엔진 본체, 냉각장치, 오일펌프 등 동력 발생 관련 결함'),
    ('시동', '시동 모터, 배선, 소프트웨어 오류로 인한 시동 꺼짐 또는 불량'),
    ('화재', '전기 배선, 연료 누유, 배터리 과열 등으로 인한 화재 발생 가능성'),
    ('브레이크', '제동 장치(ABS, ESC), 브레이크 오일 누유, 페달 관련 결함'),
    ('연료', '연료 펌프, 연료 탱크, 연료 누유 등 연료 공급 장치 관련 결함'),
    ('누유', '엔진 오일, 변속기 오일, 연료, 브레이크 오일 등이 새는 결함'),
    ('누수', '냉각수, 워셔액 누수 또는 빗물 등의 차내 유입 결함'),
    ('에어백', '에어백 센서, 인플레이터, 제어 유닛 등 에어백 시스템 관련 결함'),
    ('소프트웨어', 'ECU, 변속기 제어, 인포테인먼트 등 차량 제어 S/W 오류'),
    ('ECU', '엔진, 변속기, 차체 제어 유닛(ECU)의 하드웨어 또는 소프트웨어 결함'),
    ('전기', '배선, 퓨즈, 스위치, 조명 등 전반적인 전기 장치 결함'),
    ('배터리', '고전압 배터리(전기차), 12V 배터리, 배터리 관리 시스템(BMS) 결함'),
    ('설계', '부품 또는 시스템의 근본적인 설계 오류로 인한 결함'),
    ('결함', '특정 부품의 제조상 불량 또는 기능적 결함'),
    ('부식', '차체, 배선, 연료 탱크 등의 부식으로 인한 안전 문제 발생 가능성'),
    ('변속기', '자동/수동 변속기, TCU, 기어 변속 관련 결함'),
    ('조향', '핸들, 파워 스티어링(MDPS), 조향 기어 박스 등 방향 전환 장치 결함'),
    ('와이퍼', '와이퍼 모터, 링크, 블레이드 작동 불량'),
    ('시트', '시트 프레임, 리클라이닝, 열선/통풍 기능 결함'),
    ('안전벨트', '시트벨트 리트랙터, 버클, 프리텐셔너 기능 결함'),
    ('잠금', '도어, 트렁크, 시동키 등의 잠금 장치(액추에이터, 스위치) 결함'),
    ('경고등', '계기판에 각종 시스템의 이상을 알리는 경고등 점등 결함'),
    ('ABS', '안티록 브레이크 시스템(ABS) 모듈, 센서, 유압 장치 결함'),
    ('ESC', '차체 자세 제어장치(ESC/VDC) 모듈, 센서, 유압 장치 결함'),
    ('센서', '크랭크각 센서, ABS 휠속도 센서, 에어백 센서 등 각종 센서 오류')
]

# --- 1. 데이터 로드 및 전처리 ---
def load_and_clean_data(file_path, sheets):
    df_list = []
    print("Excel 파일 로드 시도...")
    
    if not os.path.exists(file_path):
        print(f"[오류] Excel 파일을 찾을 수 없습니다: {file_path}")
        print(f"  > (팁: {EXCEL_FILE_NAME} 파일이 'sql' 폴더 안에 있는지 확인하세요.)")
        return None
        
    print(f" - {EXCEL_FILE_NAME} 파일 로드 중...")
    
    for sheet in sheets:
        try:
            # [수정] pd.read_csv -> pd.read_excel
            df = pd.read_excel(file_path, sheet_name=sheet)
            df_list.append(df)
            print(f"   - '{sheet}' 시트 로드 성공 ({len(df)}건)")
        except Exception as e:
            print(f"[경고] '{sheet}' 시트를 읽는 중 오류 발생: {e}. 건너뜁니다.")
            continue
    
    if not df_list:
        print("[치명적 오류] Excel 파일에서 읽을 수 있는 시트가 없습니다. 스크립트를 종료합니다.")
        return None

    df_raw = pd.concat(df_list, ignore_index=True)
    
    # [전처리] (이하 동일)
    df_raw.columns = df_raw.columns.str.strip()
    date_cols = ['생산기간(부터)', '생산기간(까지)', '리콜개시일']
    for col in date_cols:
        df_raw[col] = pd.to_datetime(df_raw[col].astype(str).str.replace(r'[^\d]', '', regex=True),
                                   format='%Y%m%d', errors='coerce')
    
    if '시정율(퍼센트)' in df_raw.columns:
        df_raw.rename(columns={'시정율(퍼센트)': '시정률(퍼센트)'}, inplace=True)
    
    # '시정률(퍼센트)' 컬럼이 없는 경우를 대비 (원본 파일에 '시정율'만 있을 수 있음)
    elif '시정율' in df_raw.columns:
         df_raw.rename(columns={'시정율': '시정률(퍼센트)'}, inplace=True)
         
    # 두 컬럼 다 없으면 새로 생성
    if '시정률(퍼센트)' not in df_raw.columns:
        print("[정보] '시정률(퍼센트)' 컬럼이 없어 새로 생성합니다.")
        df_raw['시정률(퍼센트)'] = 0.0 # 기본값 0

    df_raw['리콜대수'] = pd.to_numeric(df_raw['리콜대수'], errors='coerce').fillna(0).astype(int)
    df_raw['시정대수'] = pd.to_numeric(df_raw['시정대수'], errors='coerce').fillna(0).astype(int)
    df_raw['시정률(퍼센트)'] = pd.to_numeric(df_raw['시정률(퍼센트)'], errors='coerce').fillna(0).astype(float)

    df_cleaned = df_raw.where(pd.notnull(df_raw), None)
    df_cleaned = df_cleaned.dropna(subset=['리콜사유'])
    df_cleaned['제작자'] = df_cleaned['제작자'].str.replace(r"\(.*?\)", "", regex=True).str.strip()
    
    print(f"총 {len(df_cleaned)}건의 리콜 데이터를 전처리했습니다.")
    return df_cleaned


# --- 2. DB에 데이터 저장 ---
def insert_data_to_db(df):
    conn = None
    cursor = None
    
    keywords_only = [k[0] for k in KEYWORDS_DATA]
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print(f"\n[연결 성공] MySQL DB '{DB_CONFIG['database']}'에 연결되었습니다.")

        # [Step 1] Brand 테이블 채우기
        all_brands = df['제작자'].unique()
        sql_brand = "INSERT INTO Brand (brand_name) VALUES (%s) ON DUPLICATE KEY UPDATE brand_name=brand_name"
        cursor.executemany(sql_brand, [(brand,) for brand in all_brands if brand])
        print(f" -> 'Brand' 테이블에 {cursor.rowcount}건 처리 완료.")

        cursor.execute("SELECT brand_id, brand_name FROM Brand")
        brand_map = {name: id for (id, name) in cursor.fetchall()}

        # [Step 2] Model 테이블 채우기
        models_data = df[['제작자', '차명']].drop_duplicates()
        model_tuples = []
        for _, row in models_data.iterrows():
            brand_id = brand_map.get(row['제작자'])
            if brand_id and row['차명']:
                model_tuples.append((brand_id, row['차명']))
        
        sql_model = "INSERT INTO Model (brand_id, model_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE brand_id=brand_id"
        cursor.executemany(sql_model, model_tuples)
        print(f" -> 'Model' 테이블에 {cursor.rowcount}건 처리 완료.")
        
        cursor.execute("SELECT model_id, brand_id, model_name FROM Model")
        model_map = {(b_id, name): m_id for (m_id, b_id, name) in cursor.fetchall()}

        # [Step 3] Keyword 테이블 채우기 (설명 포함)
        print(" -> 'Keyword' 테이블 업데이트 중...")
        sql_keyword = """
        INSERT INTO Keyword (keyword_text, keyword_desc) 
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE keyword_desc=VALUES(keyword_desc)
        """
        cursor.executemany(sql_keyword, KEYWORDS_DATA)
        print(f" -> 'Keyword' 테이블에 {cursor.rowcount}건 처리 완료.")

        cursor.execute("SELECT keyword_id, keyword_text FROM Keyword")
        keyword_map = {text: id for (id, text) in cursor.fetchall()}

        # [Step 4] Recall 및 Junction 테이블 채우기
        print(" -> 'Recall' 및 'Junction' 테이블 데이터 삽입 중 (가장 오래 걸림)...")
        recall_count = 0
        junction_count = 0

        for _, row in df.iterrows():
            try:
                brand_id = brand_map.get(row['제작자'])
                model_id = model_map.get((brand_id, row['차명']))
                
                if not model_id:
                    continue 

                sql_recall = """
                INSERT INTO Recall (model_id, reason, prod_from, prod_to, recall_date, recall_count, correction_count, correction_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE reason=VALUES(reason), recall_count=VALUES(recall_count)
                """
                recall_values = (
                    model_id,
                    row['리콜사유'],
                    row['생산기간(부터)'],
                    row['생산기간(까지)'],
                    row['리콜개시일'],
                    row['리콜대수'],
                    row['시정대수'],
                    row['시정률(퍼센트)']
                )
                cursor.execute(sql_recall, recall_values)
                
                new_recall_id = cursor.lastrowid
                if new_recall_id == 0: 
                    continue 

                recall_count += 1
                
                reason_text = row['리콜사유']
                found_keywords = []
                for keyword_text in keywords_only:
                    if keyword_text in reason_text:
                        found_keywords.append(keyword_text)
                
                if found_keywords:
                    for keyword_text in found_keywords:
                        keyword_id = keyword_map.get(keyword_text)
                        if keyword_id:
                            sql_junction = """
                            INSERT INTO Recall_Keyword_Junction (recall_id, keyword_id)
                            VALUES (%s, %s)
                            ON DUPLICATE KEY UPDATE recall_id=recall_id
                            """
                            cursor.execute(sql_junction, (new_recall_id, keyword_id))
                            junction_count += 1
                        
            except Exception as e:
                continue 

        print(f" -> 'Recall' 테이블에 {recall_count}건 신규 삽입 완료.")
        print(f" -> 'Recall_Keyword_Junction' 테이블에 {junction_count}건 연결 완료.")
        
        # [Step 5] 최종 커밋
        conn.commit()
        print("\n[완료] 모든 데이터가 성공적으로 DB에 저장되었습니다.")

    except Error as e:
        print(f"\n[치명적 오류] DB 작업 실패: {e}")
        if conn:
            print("작업을 롤백합니다.")
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL DB 연결이 종료되었습니다.")

# --- 3. 스크립트 실행 ---
if __name__ == "__main__":
    df_main = load_and_clean_data(EXCEL_FILE_PATH, SHEET_NAMES)
    if df_main is not None:
        insert_data_to_db(df_main)
        