# 파일 이름: backend/news_api.py
import streamlit as st
import requests
import re
from urllib.parse import quote

@st.cache_data(ttl=3600)
def get_naver_news(query):
    """네이버 뉴스 API를 호출하여 뉴스 목록(list)을 반환합니다."""
    try:
        client_id = st.secrets['naver_api']['client_id']
        client_secret = st.secrets['naver_api']['client_secret']
    except KeyError:
        return [{'title': "API 키 오류", 'link': "#", 'description': "`.streamlit/secrets.toml` 파일을 확인하세요."}]
    except Exception as e:
        return [{'title': f"Secrets 로딩 오류: {e}", 'link': "#", 'description': "secrets.toml 파일 접근 권한을 확인하세요."}]

    # [수정] display=5 -> display=3 (뉴스 3개만 가져오기)
    enc_query = quote(query)
    url = f"https://openapi.naver.com/v1/search/news.json?query={enc_query}&display=3&sort=date"
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        news_data = response.json()
        clean_news_list = []
        
        for item in news_data.get('items', []):
            clean_title = re.sub(r'<[^>]+>|&quot;|&gt;|&lt;|&amp;', '', item['title'])
            clean_desc = re.sub(r'<[^>]+>|&quot;|&gt;|&lt;|&amp;', '', item['description'])
            clean_news_list.append({
                'title': clean_title, 'link': item['link'], 'description': clean_desc
            })
        
        if not clean_news_list:
            return [{'title': "검색 결과 없음", 'link': "#", 'description': f"'{query}'에 대한 뉴스가 없습니다."}]
        return clean_news_list
    except requests.exceptions.RequestException as e:
        return [{'title': f"API 호출 오류: {e}", 'link': "#", 'description': "네이버 서버에 연결할 수 없거나 API 키가 잘못되었습니다."}]