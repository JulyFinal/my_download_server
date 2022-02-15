import os
import re
import ssl
from datetime import datetime
from urllib import request
from typing import Optional

import pymongo
import uvicorn
from fastapi import FastAPI, Body
from bs4 import BeautifulSoup

ssl._create_default_https_context = ssl._create_unverified_context

mongodb_client_url = os.getenv("mongodb_url")
client = pymongo.MongoClient(mongodb_client_url)
collection = client['download_db']['bt']

app = FastAPI()


@app.get("/")
def root():
    return {"status": "successful"}


@app.post("/")
def download_api(download_info: str = Body(..., embed=True)):
    return info_parse(download_info)


# 传入类型判断
def info_parse(download_info: str):
    download_info = re.sub(r'\s', '', download_info)
    id_list = []
    if re.match("http", download_info):
        hash_code_list = http_parse(download_info)
        if hash_code_list:
            for hash_code in hash_code_list:
                insert_id = insert_info(download_info, hash_code)
                id_list.append(insert_id)
            return {"status": "successful", "ids": str(id_list)}
        else:
            return {"status": "Not Found Hash Code"}
    elif re.match(r'(magnet:?xt=urn:btih:[0-9a-fA-F]{32,40}|[0-9a-fA-F]{32,40})', download_info):
        insert_id = insert_info(download_info, download_info)
        id_list.append(insert_id)
        return {"status": "successful", "ids": str(id_list)}
    else:
        return {"status": "unknown info"}


# http parse
def http_parse(http_url: str):
    # if re.search(r"hacg|liuli", http_url):
    hash_code_list = get_hash_code(get_context(http_url))
    return hash_code_list


# 解析网站
def get_context(url):
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
    }
    req = request.Request(url=url, headers=headers)
    context = request.urlopen(req).read().decode('utf-8')
    return context


# 网页内搜索磁力
def get_hash_code(info):
    info = info.replace('<br>', '')
    soup = BeautifulSoup(info, "lxml")  # 设置解析器为“lxml”
    html_text = soup.div.get_text(r'|', strip=True)
    hash_list = re.findall(r'(?:|)(magnet:?xt=urn:btih:[0-9a-fA-F]{32,40}|[0-9a-fA-F]{32,40})(?:|$)', html_text)
    return hash_list


def insert_info(download_info, hash_code, tool='qb'):
    status = collection.insert_one({
        "origin_info": download_info,
        "hash_code": hash_code,
        "tool": tool,
        "datetime": datetime.utcnow()
    })
    return status.inserted_id


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=80, log_level="info", reload=True)
