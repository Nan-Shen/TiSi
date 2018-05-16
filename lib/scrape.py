#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 01:11:31 2018

@author: Nan
"""

import re
import tweepy
import click
import os


class TweetsCollect(object):
    """
    Generic Class for twitter collection.
    """
    def __init__(self):
        """
        Authentication
        """
        # keys and tokens from the Twitter Dev Console
        CONSUMER_KEY = ‘XXXXXX’
        CONSUMER_SECRET = 'XXXXXX'
        ACCESS_TOKEN = 'XXXXXX'
        ACCESS_TOKEN_SECRET = 'XXXXXX'
 
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            # set access token and secret
            self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        except:
            print("Error: Authentication Failed")

    def preprocess(self, tweet):
        """1. Convert the tweets to lower case.
           2. Replace all URLs with _URL.
           3. Replace "@username" with AT_USER.
           4. Remove hashtags, punctuations and additional white spaces.
        """
        tweet = tweet.lower()
        #Convert www.* or https?://* to URL
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '_URL', tweet)
        #Convert @username to AT_USER
        tweet = re.sub('@[^\s]+','AT_USER',tweet)
        #Remove special characters
        tweet = re.sub('[\W \t]', ' ', tweet)
        #Remove additional white spaces
        tweet = re.sub(' +', ' ', tweet)
        #trim
        tweet = tweet.strip('\'"')
        return tweet
    
    def collect(self, query, start, end, outfp, count=100):
        """Search for tweets contain query words, from a start date to an 
        end date.
        """
        i = 0
        try:
            tweets = tweepy.Cursor(self.api.search, q=query, lang='en', 
                               since=start, unitl=end)
            OutputFileExist = Exception('Output file already exists')
            try:
                if os.path.isfile(outfp):
                     raise  OutputFileExist
            except OutputFileExist:
                exit
            f = open(outfp, 'w')
            f.write('Time\tID\tName\tLocation\tRetweet_time\tTweet\n')
            f.close()
            texts = []
            for tweet in tweets.items():
                tweet_txt = self.preprocess(tweet.text)
                if tweet.retweet_count > 0:
                    if tweet_txt in texts:
                        continue
                texts.append(tweet_txt)
                print i, tweet.created_at
                i += 1
                f = open(outfp, 'a')
                f.write('%s\t%s\t%s\t%s\t%s\t%s\n' % (tweet.created_at, 
                                                      tweet.user.id,
                                                      tweet.user.name.encode('utf-8'),
                                                      tweet.user.location.encode('utf-8'),
                                                      tweet.retweet_count, 
                                                      tweet_txt.encode('utf-8')))
                f.close()
        except tweepy.TweepError as e:
            print("Error : " + str(e))  
        return
    

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=0.1)

@click.option('-o', '--outfp', required=True,
              type=click.Path(exists=False),
              help='Output file path')
@click.option('-s', '--start', required=True,
              help='Start date')
@click.option('-e', '--end', required=True,
              help='End date')
@click.option('-q', '--query', required=True,
              help='Query word')

def scrape(outfp, query, start, end):
    """
    """
    # creating object of TweetsCollect Class
    api = TweetsCollect()
    api.collect(query=query, start=start, end=end, outfp=outfp)
    
if __name__ == "__main__":
    scrape()    
    
            