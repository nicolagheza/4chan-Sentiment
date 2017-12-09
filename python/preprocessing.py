import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from time import time

def getCorpus(url='biz_0.csv', FEATURES = ['comment']):
    data_df = pd.DataFrame.from_csv(url, encoding="ISO-8859-1")
    corpus = data_df[FEATURES].values
    return corpus

if __name__ == "__main__":
    corpus = getCorpus()
    print(corpus.shape)
##    print (corpus.shape)
##    vectorizer = CountVectorizer()
##    X = vectorizer.fit_transform(corpus[:,0])
##    print (X)
    
    
