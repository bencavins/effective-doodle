import os
import tweepy
import spacy
from twitoff.models import DB, Tweet, User

# Get API keys from environment vars
key = os.getenv('TWITTER_API_KEY')
secret = os.getenv('TWITTER_API_KEY_SECRET')

# Connect to the Twitter API
twitter_auth = tweepy.OAuthHandler(key, secret)
twitter_api = tweepy.API(twitter_auth)

nlp = spacy.load('my_model')

def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector


def add_or_update_user(username):
    # Query Twitter API for given user
    twitter_user = twitter_api.get_user(screen_name=username)

    # Create User DB object
    db_user = User.query.get(twitter_user.id)
    if db_user is None:
        db_user = User(id=twitter_user.id, username=username)
    # Save User to DB
    DB.session.add(db_user)

    # Get the user's tweets
    tweets = twitter_user.timeline(
        count=200,
        exclude_replies=True,
        include_rts=False,
        tweet_mode='extended',
    )
    # Query DB for user's tweets
    existing_db_tweets = Tweet.query.filter(Tweet.user_id == twitter_user.id).all()
    # grab all tweet ids
    db_tweet_ids = [tweet.id for tweet in existing_db_tweets]

    # Add each tweet to the DB (if it doesn't already exist)
    for tweet in tweets:
        if tweet.id not in db_tweet_ids:
            db_tweet = Tweet(
                id=tweet.id, 
                text=tweet.full_text, 
                vector=vectorize_tweet(tweet.full_text),
            )
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)

    # Commit our changes
    DB.session.commit()