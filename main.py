from fastapi import FastAPI, HTTPException
from search_service import parse_search_results, SearchResult
from typing import List
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from frame_extractor import extract_frame, extract_random_frame
import pandas as pd
import random
from fastapi.responses import Response, JSONResponse
import base64
from fastapi.middleware.cors import CORSMiddleware


df = pd.read_csv('search_results_20240426_181613.csv')
load_dotenv()


ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
API_KEY = os.getenv("USER_API_KEY")
index_name = "mygo_subtitles"

es_client = Elasticsearch(
    ELASTICSEARCH_URL,
    headers={"Authorization": f"ApiKey {API_KEY}"}
)

app = FastAPI()

origins = [
    # local
    "http://localhost:5173",
    # hosting
    "https://red-forest-0b9298900.5.azurestaticapps.net",
    "https://somygo.xuno8.com",
    "https://somygo.com",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# for testing
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],  
#     allow_headers=["*"],
# )

class SearchRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/search", response_model=List[SearchResult])
def search(request: SearchRequest):
    try:
        response = es_client.search(
            index=index_name,
            body={"query": {"bool": {"must": [{"match": {"text": {"query": request.query}}}]}}}
        )
        # print("Elasticsearch response:", response)
        search_results = parse_search_results(response)
        return search_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/id/{item_id}")
def get_image(item_id: str):
    # print(item_id)
    record = df[df['id'] == item_id].iloc[0]
    if record.empty:
        raise HTTPException(status_code=404, detail="Item not found")

    # Cloud
    video_filename = f"/vids/{record['episode']}.mp4"
    # Local
    # video_filename = f"vids/{record['episode']}.mp4"
    frame_number = random.randint(record['start_frame'], record['end_frame'])
    image_data = extract_frame(video_filename, frame_number, save_to_file=False)
    if image_data:
        print(record['episode'], record['start_time'])
        # return Response(content=image_data, media_type='image/jpeg')
        
        # return JSONResponse(content={
        #     "image_data": "data:image/jpeg;base64," + base64.b64encode(image_data).decode(),
        #     "episode": record['episode'],
        #     "time_info": record['start_time']
        # }, media_type='application/json')
        response_data = {
        "text": record['text'],
        "episode": int(record['episode']),
        "time_info": record['start_time'],
        "image_data": "data:image/jpeg;base64," + base64.b64encode(image_data).decode(),
        }
        return JSONResponse(content=response_data)
    else:
        raise HTTPException(status_code=500, detail="Failed to extract frame")

@app.get("/random-image")
def get_random_image():
    #Cloud
    video_directory = '/vids'
    #Local
    # video_directory = 'vids'
    image_data, episode, time_info = extract_random_frame(video_directory)
    if image_data:
        return JSONResponse(content={
            "episode": episode,
            "time_info": time_info,
            "image_data": "data:image/jpeg;base64," + base64.b64encode(image_data).decode(),
        }, media_type='application/json')
    else:
        return {"error": "Failed to extract frame"}