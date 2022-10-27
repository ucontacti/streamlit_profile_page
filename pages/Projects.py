import streamlit as st
import tweepy
from config import tweepy_token
import json

st.title("Projects")


auth = tweepy.OAuthHandler(tweepy_token.API_KEY, tweepy_token.API_SECRET)
auth.set_access_token(tweepy_token.ACCESS_TOKEN, tweepy_token.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)

WOE_ID = 1

woe_trends = api.get_place_trends(WOE_ID)

trends = json.loads(json.dumps(woe_trends, indent=1))

for trend in trends[0]["trends"]:
	st.write(trend["name"].strip("#"))

# client = tweepy.Client(bearer_token=tweepy_token.BEARER_TOKEN)

# query = "covid -is:retweet"

# response = client.search_recent_tweets(query=query, max_results=10, tweet_fields=['text', 'lang'])

# for tweet in response.data:
#     st.write(tweet.text)
#     st.write(tweet.lang)