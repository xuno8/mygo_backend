# search_service.py
from typing import List
from pydantic import BaseModel

# 定義數據
class SearchResult(BaseModel):
    id: str
    score: float
    text: str
    episode: int
    start_time: str
    end_time: str
    start_frame: int
    end_frame: int

# 解析 Elasticsearch 回應
def parse_search_results(data):
    # results = data.get("results", {}).get("hits", {}).get("hits", [])
    results = data["hits"]["hits"]
    # print(results)
    search_results = []
    for result in results:
        source = result["_source"]
        search_result = SearchResult(
            id=result["_id"],
            score=result["_score"],
            text=source["text"],
            episode=source["episode"],
            start_time=source["start"],
            end_time=source["end"],
            start_frame=source["start_frame"],
            end_frame=source["end_frame"]
        )
        search_results.append(search_result)
    return search_results
