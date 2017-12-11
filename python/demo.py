import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as md
from matplotlib import style
import datetime as dt
import ast
import time

style.use("ggplot")

df = pd.read_csv('biz-data-with-sentiment.csv', encoding='ISO-8859-1')

dates = np.array(df['unix_time'].values)
dateconv = np.vectorize(dt.datetime.fromtimestamp)

dates = dateconv(dates.tolist())

sentiment = np.array(df['sentiment'].values)
sentiment[sentiment=='pos'] = 1
sentiment[sentiment=='neg'] = -1

cur_date = dates[0]
sentiment_counter = 0
days = []
sent_ = []
for idx, date in enumerate(dates):
    if cur_date.hour == date.hour:
        if sentiment[idx] == 1:
            sentiment_counter += sentiment[idx]
    else:
        days.append(cur_date)
        sent_.append(sentiment_counter)
        cur_date = date
        sentiment_counter = 0

fig = plt.figure()
ax1 = plt.subplot2grid((1,1), (0,0))
ax1.plot_date(days,sent_, '-', label='Positive')
for label in ax1.xaxis.get_ticklabels():
    label.set_rotation(45)
ax1.grid(True)
plt.xlabel('Date')
plt.ylabel('Sentiment')
plt.title('BigMoneyEnterprise: Sentiment Analysis')
plt.legend()
plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
plt.show()
