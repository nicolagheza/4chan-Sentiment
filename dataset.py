import couchdb
import pandas as pd
import numpy as np
import json
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField

def initServer(url='http://192.168.10.111:5984'):
    server = couchdb.Server(url)
    #secure_remote_server = Server('https://username:password@example.com:5984/')
    return server

def getDb(server):
    return server['bigmoney']

def getThreadsId(db):
    return [docid['id'] for docid in db.view('_all_docs')]

def getThreadData(db):
    posts = []
    threadsId = getThreadsId(db)
    for thread in threadsId:
        thread_doc = db.get(thread)
        for post in thread_doc['posts']:
            posts.append(post)
    return posts
            
            
def buildDataFrame(posts):
    df = pd.DataFrame(columns=['id',
                               'unix_time',
                               'comment',
                               'sentiment'])
    for post in posts:
        id = post['no']
        time = post['time']
        comment = post['com']
        df = df.append({'id':id, 'unix_time':time, 'comment':comment}, ignore_index=True)
    return df

server = initServer()
db = getDb(server)
posts = getThreadData(db)
df = buildDataFrame(posts)
print(df.describe())

df.to_csv('biz_1.csv')
