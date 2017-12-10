import couchdb
import pandas as pd
import numpy as np
import json
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField

def initServer(url='http://localhost:5985'):
    server = couchdb.Server(url)
    return server

def getDb(server):
    return server['biz-data']

def getThreadsId(db):
    return [docid['id'] for docid in db.view('_all_docs')]

def getThreadData(db):
    posts = []
    threadsId = getThreadsId(db)
    try:
        for thread in threadsId:
            thread_doc = db.get(thread)
            for post in thread_doc['posts']:
                posts.append(post)
    except Exception as e:
        print (str(e))    
    return posts
            
            
def buildDataFrame(posts):
    df = pd.DataFrame(columns=['id',
                               'unix_time',
                               'comment'])
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

filename='biz-data.csv'
df.to_csv(filename)
print ('Saved new {}.csv file'.format(filename))