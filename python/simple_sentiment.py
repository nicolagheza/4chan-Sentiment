from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import pandas as pd
from time import time
import numpy as np
from nltk.corpus import stopwords
# Download the punkt tokenizer for sentence splitting
import nltk.data
#nltk.download()
# Load the punkt tokenizer
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
from gensim.models import word2vec 
# Import the built-in logging module and configure it so that Word2Vec 
# creates nice output messages
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
    level=logging.INFO)

SAVE = False
ADDSENTIMENT     = False
LOAD = True

def getDataFrame(url='biz-data.csv', FEATURES = ['comment']):
    data_df = pd.DataFrame.from_csv(url, encoding="ISO-8859-1") # Interesting encoding ;)
    return data_df

def comment_to_wordlist(comment, remove_stopwords=True):
    words = comment.lower().split()
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        words = [w for w in words if not w in w in stops]
    
    return words

def comment_to_sentences(comment, tokenizer, remove_stopwords=True):
    raw_sentences = tokenizer.tokenize(str(comment).strip())
    sentences = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(comment_to_wordlist(raw_sentence, remove_stopwords))
    return sentences

def addSentiment(df):
    df_with_sentiment = pd.DataFrame(columns=['comment','sentiment'])
    comments = np.array(df['comment'])
    naivebayes = NaiveBayesAnalyzer()
    print('Number of comments: ' , len(comments))
    print('Starting sentiment analysis...')
    for idx, comment in enumerate(comments):
        if not(idx == 0) and idx % 100 == 0 :
            print (idx, 'iterations completed')
        try: 
            analysis = TextBlob(str(comment), analyzer=naivebayes)
            df_with_sentiment = df_with_sentiment.append({'comment':comment, 'sentiment':str(analysis.sentiment.classification)}, ignore_index=True)
        except Exception as e:
            print (str(e))
    
    return df_with_sentiment

if __name__ == "__main__":

    if ADDSENTIMENT == True:
        df = getDataFrame()
        t0 = time()
        df_with_sentiment = addSentiment(df)
        print("done in %fs" % (time() - t0))
        print('Dataframe.head():\n', df_with_sentiment.head())
    
    if LOAD == True:
        filename='biz_with_sentiment.csv'
        df_with_sentiment = getDataFrame(filename)
        ## Do something with the data
        comments = [] # Init an empty list of sentences
        print ("Parsing sentences from dataset")
        for comment in df_with_sentiment["comment"]:
            comments += comment_to_sentences(comment, tokenizer)

        # Set values for various parameters
        num_features = 300    # Word vector dimensionality                      
        min_word_count = 40   # Minimum word count                        
        num_workers = 4       # Number of threads to run in parallel
        context = 10          # Context window size                                                                                    
        downsampling = 1e-3   # Downsample setting for frequent words

        # Initialize and train the model (this will take some time)
        print ("Training model...")
        model = word2vec.Word2Vec(comments, workers=num_workers, \
                    size=num_features, min_count = min_word_count, \
                    window = context, sample = downsampling)

        print ("Most similar test..")
        print (model.most_similar(("moon")))

        # It can be helpful to create a meaningful model name and 
        # save the model for later use. You can load it later using Word2Vec.load()
        model_name = "300features_40minwords_10context"
        model.save(model_name)

    if SAVE == True:
        filename='biz_with_sentiment.csv'
        df_with_sentiment.to_csv(filename)
        print ('Saved new {}.csv file'.format(filename))
