from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import pandas as pd
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

    for idx, comment in enumerate(comments):
        if idx % 100 == 0 :
            print (idx, 'iterations completed')
        try: 
            analysis = TextBlob(str(comment), analyzer=naivebayes)
            df_with_sentiment = df_with_sentiment.append({'comment':comment, 'sentiment':str(analysis.sentiment.classification)}, ignore_index=True)
        except Exception as e:
            print (str(e))

    
    print (df_with_sentiment.head())