import couchdb
import pandas as pd
import numpy as np
from time import time
import re
import json
from couchdb.mapping import Document, TextField, IntegerField, DateTimeField

def initServer(url='http://localhost:5985'):
    server = couchdb.Server(url)
    return server

def getDb(server):
    return server['biz-data']

def getThreadsId(db):
    return [docid['id'] for docid in db.view('_all_docs')]

def getPostsData(db):
    posts = []
    for post in db.view('derivatives/posts'):
        posts.append(post)
    return posts
        
          
def buildDataFrame(posts):
    df = pd.DataFrame(columns=['id',
                               'comment'])
    for i, post in enumerate(posts):
        if not(i==0) and i % 1000==0:
            print (i, 'iterations completed')
        id = post.id
        comment = re.sub('','',str(post.value))
        if len(comment) > 0:
            df = df.append({'id':id, 'comment':comment}, ignore_index=True)
    return df

t0=time()
server = initServer()
db = getDb(server)
posts = getPostsData(db)
df = buildDataFrame(posts)
print("done in %fs" % (time() - t0))
print(df.describe())

filename='biz-data.csv'
df.to_csv(filename)
print ('Saved new {}.csv file'.format(filename))
