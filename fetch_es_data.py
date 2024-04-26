# fetch_es_data.py
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from search_service import parse_search_results
from datetime import datetime

# 加載環境變數
load_dotenv()

ES_URL = os.getenv('ELASTICSEARCH_URL')
API_KEY = os.getenv('USER_API_KEY')
index_name = "mygo_subtitles"

def fetch_data():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"ApiKey {API_KEY}"
    }
    response = requests.get(f"{ES_URL}/{index_name}/_search/?size=10000", headers=headers, json={"query": {"match_all": {}}})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

def save_to_csv(search_results):
    # 獲取當前日期和時間
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_results_{current_time}.csv"

    # 將 SearchResult 對象列表轉換為 DataFrame
    df = pd.DataFrame([result.dict() for result in search_results])
    # 儲存 DataFrame 至 CSV
    df.to_csv(filename, index=False)
    print(f"Data saved to '{filename}'.")

def main():
    data = fetch_data()
    search_results = parse_search_results(data)
    save_to_csv(search_results)

if __name__ == '__main__':
    main()
