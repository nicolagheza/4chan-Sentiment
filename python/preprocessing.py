import pandas as pd
import numpy as np
from time import time
import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import matplotlib as mpl

stopwords = nltk.corpus.stopwords.words('english')

def tokenize(text):
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens

def getCorpus(url='biz_1.csv', FEATURES = ['comment']):
    data_df = pd.DataFrame.from_csv(url, encoding="ISO-8859-1")
    data_df = data_df[FEATURES].dropna()
    corpus = np.array(data_df[FEATURES].values)
    return corpus

if __name__ == "__main__":
    corpus = getCorpus()
    vocab_tokenized = []
    for i in corpus:
        allwords_tokenized = tokenize(str(i))
        vocab_tokenized.extend(allwords_tokenized)

    vocab_frame = pd.DataFrame({'words': vocab_tokenized}, index=None)
    print ('there are ' + str(vocab_frame.shape[0]) + ' items in vocab_frame')
    
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', tokenizer=tokenize)
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus[:,0])
    print(tfidf_matrix.shape)
    terms = tfidf_vectorizer.get_feature_names()

    num_clusters = 8

    km = KMeans(n_clusters=num_clusters)
    t0 = time()
    km.fit(tfidf_matrix)
    print("done in %fs" % (time() - t0))

    clusters = km.labels_.tolist()

    print("Top terms per cluster:")
    
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    terms = tfidf_vectorizer.get_feature_names()

    dist = 1 - cosine_similarity(tfidf_matrix)  

    for i in range(num_clusters):
        print("Cluster %d:" % i, end='')
        for ind in order_centroids[i, :10]:
            print(' %s' % terms[ind], end='')
        print()