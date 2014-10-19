import os
import time

import tweepy
import json
import requests

class TwitterAPI(object):
    """
    Class for accessing the Twitter API.

    Requires API credentials to be available in environment
    variables. These will be set appropriately if the bot was created
    with init.sh included with the heroku-twitterbot-starter
    """
    def __init__(self):
        consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def tweet(self, message):
        """Send a tweet"""
        self.api.update_status(message)

if __name__ == "__main__":
    twitter = TwitterAPI()
    api = twitter.api
    competitor = "Comcast"
    company = "DirecTV"
    queryString = competitor + " -" + company
    latest_id = 0
    while True:
        #Send a tweet here!
        tweets = api.search(q=queryString, rpp=50, show_user=True, lang="en", since_id = latest_id)
        sentimentQueries = []
        for tweet in tweets:
            latest_id = max(latest_id, tweet.id)
            text = tweet.text
            sentimentQuery = {}
            sentimentQuery['text'] = text
            sentimentQuery['query'] = competitor
            sentimentQuery['user'] = tweet.user.name
            if not tweet.user.name.lower() == competitor.lower():
                sentimentQueries.append(sentimentQuery)
        sentimentQueries = {'data':sentimentQueries}
        sentimentQueries = json.dumps(sentimentQueries)
        r = requests.post(url="http://www.sentiment140.com/api/bulkClassifyJson?mschorow@college.harvard.edu",
                      data=sentimentQueries)
        responses = json.loads(r.text)
        responses = responses['data']
        responses = filter(lambda x:x['polarity']==0, responses)
        for response in responses:
            twitter.tweet(response['user']+": "+response['text'])
            twitter.tweet(response['user']+" I'm sorry you didn't enjoy "+competitor+". Have you considered switching to "+company+"?")
        time.sleep(60) #1 minute
