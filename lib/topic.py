#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 00:48:00 2018

@author: Nan
"""
import numpy as np
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image

n_top_words = 10


class TweetsTopic(object):
    """
    """
    def frqwords(self, df, mask_fp, query):
        """plot word cloud of positive or negative words
        """
        # join tweets to a single string
        words = ' '.join(df['Tweet'])
        # remove query words
        n_words = ' '.join([w for w in words.split()
                              if w not in query.split()])
        font_fp = './data/cabinsketch/CabinSketch-Bold.otf'
        mask = np.array(Image.open(mask_fp))
        image_colors = ImageColorGenerator(mask)
        wc = WordCloud(stopwords=set(STOPWORDS),
                              max_words=150,
                              background_color='white',
                              width=28000,
                              height=24000,
                              font_path=font_fp,
                              mask=mask).generate(n_words)
        plt.imshow(wc.recolor(color_func=image_colors), 
                              interpolation='bilinear')
        plt.axis('off')
        plt.savefig('./wordcloud.png', dpi=300)
    
    def LDA(self, tweets, num_topics, num_features=1000):
        """
        """
        lda_vectorizer = CountVectorizer(max_df=0.95, min_df=2, 
                                        max_features=num_features, 
                                        stop_words='english')
        lda_tf = lda_vectorizer.fit_transform(tweets)
        lda_feature_names = lda_vectorizer.get_feature_names()

        lda = LatentDirichletAllocation(n_topics=num_topics, 
                                        max_iter=5, learning_method='online', 
                                        learning_offset=50.,
                                        random_state=0).fit(lda_tf)
        return lda, lda_feature_names
    
    def NMF(self, tweets, num_topics, num_features=1000):
        """
        """
        nmf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, 
                                         max_features=num_features, 
                                         stop_words='english')
        nmf_tf = nmf_vectorizer.fit_transform(tweets)
        nmf_feature_names = nmf_vectorizer.get_feature_names()
        
        nmf = NMF(n_components=num_topics, random_state=1, alpha=.1, 
                  l1_ratio=.5, init='nndsvd').fit(nmf_tf)
        return nmf, nmf_feature_names

    def display_topics(self, model, feature_names, n_top_words):
        """
        """
        for topic_idx, topic in enumerate(model.components_):
            print 'Topic %d:' % (topic_idx)
            print ' '.join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]])


