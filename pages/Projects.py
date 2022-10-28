from re import S
from nbformat import write
import streamlit as st
import tweepy
from config import tweepy_token
import json
import pandas as pd
import requests

st.title("Projects")


auth = tweepy.OAuthHandler(tweepy_token.API_KEY, tweepy_token.API_SECRET)
auth.set_access_token(tweepy_token.ACCESS_TOKEN, tweepy_token.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token=tweepy_token.BEARER_TOKEN, return_type=requests.Response)


locations = json.loads(json.dumps(api.available_trends(), indent=1))

loc_woeid_dict = {}
for loc in locations:
	if loc['placeType']['name'] == 'Country':
		loc_woeid_dict[f"{loc['name']} ({loc['placeType']['name']})"] = loc['woeid']

if 'country' not in st.session_state or not 'topics' in st.session_state or not 'trends_json' in st.session_state:
	st.session_state['country'] = ""
	st.session_state['topics'] = []
	st.session_state['trends_json'] = {}

def get_trending_topic(loc_woeid_dict):
	st.session_state['trends_json'] = json.loads(json.dumps(api.get_place_trends(loc_woeid_dict[st.session_state['country']]), indent=1))

st.session_state['country'] = st.selectbox(
	'Available countries for hot topics in Twitter:',
	loc_woeid_dict.keys(),
	on_change = get_trending_topic,
	args=[loc_woeid_dict]
	)

# st.write('You selected country :', st.session_state['country'])


trends_topic = []
if st.session_state['trends_json'] != {}:
	for trend in st.session_state['trends_json'][0]["trends"]:	
		trends_topic.append(trend["name"].strip("#"))

st.session_state['topics'] = st.multiselect(
	'Choose one of the topics:',
	trends_topic
	)

# st.write('You selected:', st.session_state['topics'])

query = f"{' '.join(st.session_state['topics'])} -is:retweet"


if st.button('Press to Query'):
	response = client.search_recent_tweets(query=query, max_results=50, tweet_fields=['text', 'lang', 'geo'])
	tweets_data = response.json()['data']
	tweet_df = pd.json_normalize(tweets_data) 
	st.dataframe(tweet_df)

# if st.button('Press to apply sentiment analysis'):

	