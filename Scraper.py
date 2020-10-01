import tweepy;
import pandas as pd
import re
from textblob import TextBlob
import GetOldTweets3 as got
import sys;
import jsonpickle;
import os;

auth = tweepy.AppAuthHandler("7O7X2Gs8XtsmZc3pESOp0UAij", "xhgtSw8ovaCKhR3gi7AlYTuvRGq7heAbzUpUJJvcrpeM3WY2gt")

consumer_key= '7O7X2Gs8XtsmZc3pESOp0UAij'
consumer_secret= 'xhgtSw8ovaCKhR3gi7AlYTuvRGq7heAbzUpUJJvcrpeM3WY2gt'
access_token= '1230058983253331968-9UIqplP5aUWP51hrc4WSO3Pa0nTqhu'
access_token_secret= 'h0YXsYbqrn5Unt6M6gTl8I07ZmBtWycaqITcofxORoqyj'

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)



def clean_tweet(tweet): 
    ''' 
    Utility function to clean tweet text by removing links, special characters 
    using simple regex statements. 
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split()) 

def get_tweet_sentiment(tweet): 
    ''' 
    Utility function to classify sentiment of passed tweet 
    using textblob's sentiment method 
    '''
    # create TextBlob object of passed tweet text 
    analysis = TextBlob(clean_tweet(tweet)) 
    # set sentiment 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'

#searchQuery = 'chess lang:en'
searchQuery = '#tesla OR #elonmusk OR "Elon Musk" OR "elon musk" OR "Tesla" OR "tesla" -filter:retweets since:2020-9-1 lang:en'  # this is what we're searching for
maxTweets = 100000000 # Some arbitrary large number
tweetsPerQry = 100  # this is the max the API permits
fName = 'teslaTweets.json' # We'll store the tweets in a text file.

sinceId = None

max_id = -1
tweet_list = []    
tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))
with open(fName, 'w') as f:
    while tweetCount < maxTweets:
        try:
            if (max_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, tweet_mode='extended')
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, since_id=sinceId, tweet_mode='extended')
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), tweet_mode='extended')
                else: new_tweets = api.search(q=searchQuery, count=tweetsPerQry, max_id=str(max_id - 1), since_id=sinceId, tweet_mode='extended')
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                tweet.sentiment = get_tweet_sentiment(tweet.full_text)
                #if (not tweet.sentiment):
                #    tweet.sentiment = None
                tweet_list.append([tweet.full_text, tweet.user.screen_name, tweet.user.location, tweet.created_at, tweet.sentiment])
            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets".format(tweetCount))
            max_id = new_tweets[-1].id
        except tweepy.TweepError as e:
               # # Just exit if any error
            print("some error : " + str(e))
            break
    
print ("Downloaded {0} tweets.".format(tweetCount))
tweet_text = pd.DataFrame(data=tweet_list, columns=['text', 'user', 'location', 'date', 'sentiment'])
tweet_text.to_csv('9-28-tweets.csv', index=False)
