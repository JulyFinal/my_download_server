# -*- coding: utf-8 -*-
import os
import time

import aria2p
import pymongo
import qbittorrentapi
import dns.resolver
from apscheduler.schedulers.blocking import BlockingScheduler

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

scheduler = BlockingScheduler()

# qb option
qb_host = os.getenv("qb_host")
qb_port = os.getenv("qb_port")
qb_username = os.getenv("qb_account")
qb_password = os.getenv("qb_password")

# aria2 option
aria2_url = os.getenv('aria2_url')
aria2_rpc_port = os.getenv('aria2_rpc_port')


# download runner
# def aria2_download(uri=None, bt_file=None):
#     aria2 = aria2p.API(aria2p.Client(host=aria2_url, port=aria2_rpc_port))
#     if uri:
#         if re.search(r"^http", uri):
#             aria2.add(uri=uri)
#         aria2.add_magnet(uri)
#         return {"status": "successful"}
#     if bt_file:
#         aria2.add_torrent(bt_file)
#         return {"status": "successful"}
#     return {"status": "What Fuck"}


# qbittorrent 调用
def qb_download(uri):
    qbt_client = qbittorrentapi.Client(
        host=qb_host,
        port=qb_port,
        username=qb_username,
        password=qb_password,
    )
    try:
        qbt_client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e)
        return {'status': 'qBitt Login Failed!'}
    status = qbt_client.torrents_add(uri)
    if status == 'Ok.':
        return {'status': "successful"}
    else:
        return {'status': "maybe successful ?"}


def mongodb_check():
    mongodb_url = os.getenv('mongodb_url')
    try:
        with pymongo.MongoClient(mongodb_url) as client:
            print("MongoDB Client Successful!")
            collection = client['download_db']['bt']
            data_list = collection.find({"download_status": {"$exists": False}})
            for i in data_list:
                hash_code = i.get('hash_code')
                if i.get('tool') == 'qb':
                    download_status = qb_download(hash_code)
                    collection.update_one({"_id": i.get("_id")},
                                          {"$set": {"download_status": download_status.get("status")}})
    except Exception as e:
        print(e)


@scheduler.scheduled_job('interval', hours=1, timezone="UTC")
def job():
    mongodb_check()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


if __name__ == '__main__':
    print("Auto Check Server Start! ")
    scheduler.start()
