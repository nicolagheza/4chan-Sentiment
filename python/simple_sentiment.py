from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import pandas as pd
from time import time
import numpy as np

def getDataFrame(url='biz_1.csv', FEATURES = ['comment']):
    data_df = pd.DataFrame.from_csv(url, encoding="ISO-8859-1") # Interesting encoding ;)
    return data_df

if __name__ == "__main__":
    df = getDataFrame()
    df_with_sentiment = pd.DataFrame(columns=['comment','sentiment'])
    comments = np.array(df['comment'])
    naivebayes = NaiveBayesAnalyzer()
    print('Number of comments: ' , len(comments))
    print('Starting sentiment analysis...')
    t0 = time()
    for idx, comment in enumerate(comments):
        if idx <> 0 and idx % 100 == 0 :
            print (idx, 'iterations completed')
        try: 
            analysis = TextBlob(str(comment), analyzer=naivebayes)
            df_with_sentiment = df_with_sentiment.append({'comment':comment, 'sentiment':str(analysis.sentiment.classification)}, ignore_index=True)
        except Exception as e:
            print (str(e))
    
    print("done in %fs" % (time() - t0))
    df_with_sentiment = pd.merge(df, df_with_sentiment, on='comment')

    print(df_with_sentiment.head())

    filename='biz_with_sentiment.csv'
    df_with_sentiment.to_csv(filename)
    print ('Saved new {}.csv file'.format(filename))