import pandas as pd
import numpy as np
import time
from sklearn.externals import joblib

biz_df = pd.read_csv('biz-data.csv', encoding="ISO-8859-1")

clf = joblib.load('sent.pkl')

X = np.array(biz_df['comment'].values)

predictions = clf.predict(X)

labels = {'0':'neg',
          '1':'pos'}

biz_df_with_sentiment = pd.DataFrame(columns=['comment','sentiment'])   

for i, prediction in enumerate(predictions):
    biz_df_with_sentiment = biz_df_with_sentiment.append({'comment':str(X[i]), 'sentiment':labels[str(prediction)]}, ignore_index=True)

biz_df_with_sentiment = pd.merge(biz_df, biz_df_with_sentiment, on='comment')
print(biz_df_with_sentiment.head())
print(biz_df_with_sentiment.describe())

filename = 'biz-data-with-sentiment.csv'
biz_df_with_sentiment.to_csv(filename)
print ("Saved file {}".format(filename))

def sentiment(text):
    return clf.predict(text)
