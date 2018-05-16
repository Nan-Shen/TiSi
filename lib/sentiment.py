#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 00:11:20 2018

@author: Nan
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap as Basemap
from matplotlib.colors import rgb2hex
from matplotlib.patches import Polygon

from textblob import TextBlob

from datetime import datetime

class TweetsSentiment(object):
    """
    """
    def parse_scraped(self, fp, s, e, query):
        """read in scraped tweets, pick tweets between two dates
        """
        df = pd.read_table(fp)
        df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        df = df.dropna(subset=['Time'])
        df = df[(df['Time'] > s) & (df['Time'] < e)]
        df = df[df['Tweet'].str.contains(query, na=False)]
        df['Tweet'] = df['Tweet'].map(lambda x: ' '.join([w for w in x.split()
                                          if w not in ['_URL', 'AT_USER', 'rt']]))
        return df
        
    def get_tweet_sentiment(self, tweet):
        """Get sentiment score of tweet content
        """
        sentiScore = TextBlob(tweet).sentiment.polarity
        return sentiScore
    
    def sentiScore_category(self, sentiScore, thr=0):
        """categorize sentiScore
        """
        if sentiScore > thr:
            return 'positive'
        elif sentiScore == thr:
            return 'neutral'
        else:
            return 'negative'
    
    def ave_longi_sentiment(self, df, start_time, time_scale='h'):
        """longitudinal change of sentiment towards topic
        time_scale: calculate datetime difference by hours or days, options are
        m for minutes, h for hours, D for days, M for months, Y for years
        """
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        df['time'] = df['Time'] - start_time
        df['time'] = df['time'].astype('timedelta64[%s]' % (time_scale))
            
        plt.figure()
        sns.set();sns.set_context({"figure.figsize": (20,20)})
        sns.set_context('talk');sns.set_style('white')
        # Plot the average value by date
        ax = df.groupby('time')['Score'].mean().plot(color='#db3236', alpha=.7)
        ax.axhline(y=0, linestyle='--', color='#4885ed')
        # Get a reference to the x-points corresponding to the dates
        x = df.groupby('time')['Score'].mean().index
        # Min and max of the score on each time point 
        #and plot a translucent band between them
        zero = np.zeros(len(df['time'].unique()))
        low = df.groupby('time')['Score'].min()
        high = df.groupby('time')['Score'].max()
        ax.fill_between(x, low, zero, alpha=.5, color= '#3cba54')
        ax.fill_between(x, zero, high, alpha=.5, color='#f4c20d')
        plt.savefig('./ave_longi.png', dpi=300)
        
    def proportion_longi_sentiment(self, df, start_time, time_scale='h', thr=0):
        """longitudinal change of proportion of positive, neutral and negative 
        sentiment towards topic
        time_scale: calculate datetime difference by hours or days, options are
        m for minutes, h for hours, D for days, M for months, Y for years
        """
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        df['time'] = df['Time'] - start_time
        df['time'] = df['time'].astype('timedelta64[%s]' % (time_scale))
        
        df['sentiment'] = map(lambda x : self.sentiScore_category(x,thr=thr), 
                               df['Score'])
        #transform table to have time as index, score category as columns and
        #counts of different score as value
        df_count = df.pivot_table(index='time', 
                                  values='ID', 
                                  columns='sentiment', 
                                  aggfunc='count').fillna(0)
        #stacked area plot
        cmap = mpl.colors.ListedColormap(['#3cba54', '#4885ed', '#f4c20d'])
        df_count.plot.area(colormap=cmap, alpha=.7)
        plt.savefig('./stack_longi.png', dpi=300)
        
    def location_sentiment(self, df):
        """locational ditribution of sentiments towards topic (US mainland only)
        """
        df_state = df.groupby('State')['Score'].mean()
        # Lambert Conformal map of lower 48 states.
        m = Basemap(llcrnrlon=-119,llcrnrlat=22,urcrnrlon=-64,urcrnrlat=49,
                    projection='lcc',lat_1=33,lat_2=45,lon_0=-95)
        # draw state boundaries.
        # data from U.S Census Bureau
        # http://www.census.gov/geo/www/cob/st2000.html
        shp_info = m.readshapefile('st99_d00','states',drawbounds=True)
        # choose a color for each state based on scores.
        colors={}
        statenames=[]
        cmap = plt.cm.hot # use 'hot' colormap
        vmin, vmax = -1, 1 # set range.
        for shapedict in m.states_info:
            statename = shapedict['State']
            if statename not in ['District of Columbia','Puerto Rico']:
                score = df[statename]
                # calling colormap with value between 0 and 1 returns
                # rgba value.  Invert color range (hot colors are high
                # score), take sqrt root to spread out colors more.
                colors[statename] = cmap(1.-np.sqrt((score-vmin)/(vmax-vmin)))[:3]
            statenames.append(statename)
        # cycle through state names, color each one.
        ax = plt.gca() # get current axes instance
        for nshape, seg in enumerate(m.states):
            if statenames[nshape] not in ['District of Columbia','Puerto Rico']:
                color = rgb2hex(colors[statenames[nshape]]) 
                poly = Polygon(seg, facecolor=color, edgecolor=color)
                ax.add_patch(poly)
        plt.title('Mean sentiment score in each state')
        plt.savefig('./location.png', dpi=300)
        
    