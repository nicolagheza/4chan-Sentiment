import couchdb
import pandas as pd
from time import time

def initServer(url='http://localhost:5985'):
    server = couchdb.Server(url)
    return server

def getDb(server):
    return server['biz-data']

def getPostsData(db):
    posts = []
    for post in db.view('derivatives/posts'):
        posts.append(post)
    return posts

def getCurrencyMentionsData(db):
    mentions = []
    for mention in db.view('derivatives/currency-mentions', group=True, group_level=5, limit=100):
        mentions.append(mention.value)

    print ("mentions: {}".format(len(mentions)))
    return mentions

def getPostsWithCurrencyMentions(db):
    posts_with_mentions = []
    for post in db.view('derivatives/posts-currency'):
        posts_with_mentions.append(post)

    print ("post_with_mentions: {}".format(len(posts_with_mentions)))
    return posts_with_mentions

def buildDataFrame(posts):
    df = pd.DataFrame(columns=['unix_time', 'id', 'comment', 'mentions'])
    for i, post in enumerate(posts):
        if not(i==0) and i % 1000==0:
            print (i, 'iterations completed')
        id = post.id
        time = str(post.value["time"])
        comment = str(post.value["comment"])
        mentions = str(post.value["mentions"])
        if len(comment) > 0:
            df = df.append({'unix_time':time,'id':id, 'comment':comment, 'mentions':mentions}, ignore_index=True)

    return df

t0=time()
server = initServer()
db = getDb(server)
posts = getPostsWithCurrencyMentions(db)

posts_df = buildDataFrame(posts)
print("done in %fs" % (time() - t0))
print(posts_df.describe())

print(posts_df.head())

filename='biz-data.csv'
posts_df.to_csv(filename)
print ('Saved new {}.csv file'.format(filename))
