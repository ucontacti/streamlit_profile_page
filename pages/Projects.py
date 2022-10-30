import streamlit as st
import tweepy
import json
import pandas as pd
import requests
import matplotlib.pyplot as plt

from config import tweepy_token
from sentiment_analyzer import text_cleaner, lemmatize_text, \
								getPolarity, getPolAnalysis, \
								getSubjectivity, getSubAnalysis

st.title("Tweeter hot topic Sentimental Analysis")


auth = tweepy.OAuthHandler(tweepy_token.API_KEY, tweepy_token.API_SECRET)
auth.set_access_token(tweepy_token.ACCESS_TOKEN, tweepy_token.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token=tweepy_token.BEARER_TOKEN, return_type=requests.Response)


locations = json.loads(json.dumps(api.available_trends(), indent=1))

loc_woeid_dict = {}
for loc in locations:
	if loc['placeType']['name'] == 'Country':
		loc_woeid_dict[f"{loc['name']} ({loc['placeType']['name']})"] = loc['woeid']

if 'country' not in st.session_state or \
	'topics' not in st.session_state or \
	'trends_json' not in st.session_state:
	st.session_state['country'] = ""
	st.session_state['topics'] = []
	st.session_state['trends_json'] = {}

def get_trending_topic(loc_woeid_dict):
	st.session_state['trends_json'] = json.loads(json.dumps(api.get_place_trends(loc_woeid_dict[st.session_state['country']]), indent=1))

st.session_state['country_new'] = st.session_state['country']
st.session_state['country'] = st.selectbox(
	'Available countries for hot topics in Twitter:',
	loc_woeid_dict.keys()
	)
	
if st.session_state['country'] != st.session_state['country_new']:
	get_trending_topic(loc_woeid_dict)

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
	st.session_state.tweet_df = pd.json_normalize(tweets_data) 
	st.dataframe(st.session_state.tweet_df)
	# st.session_state.tweet_df.to_csv('tweets.csv')

if st.button('Press to apply sentiment analysis'):
	st.session_state.tweet_df['clean_text'] = st.session_state.tweet_df['text'].apply(lemmatize_text)
	st.session_state.tweet_df["polarity"] = st.session_state.tweet_df["clean_text"].apply(getPolarity)
	st.session_state.tweet_df["sentiment"] = st.session_state.tweet_df["polarity"].apply(getPolAnalysis)
	st.session_state.tweet_df["subjectivity"] = st.session_state.tweet_df["clean_text"].apply(getSubjectivity)
	st.session_state.tweet_df["sub_obj"] = st.session_state.tweet_df["subjectivity"].apply(getSubAnalysis)
	st.dataframe(st.session_state.tweet_df)

if st.button('plot piechart'):
	fig1, ax1 = plt.subplots()
	sent_percentage = st.session_state.tweet_df['sentiment'].value_counts()/sum(st.session_state.tweet_df['sentiment'].value_counts())
	labels = sent_percentage.keys()
	sizes = sent_percentage.values
	ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

	st.pyplot(fig1)

# TODO: add code comment
# TODO: add second plot
# TODO: make second for pure text
# TODO: add better readme