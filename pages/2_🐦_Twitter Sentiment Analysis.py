import streamlit as st
import tweepy
import json
import pandas as pd
import requests
import matplotlib.pyplot as plt

from config import tweepy_token
from utils.sentiment_analyzer import text_cleaner, lemmatize_text, \
								getPolarity, getPolAnalysis, \
								getSubjectivity, getSubAnalysis

st.set_page_config(
    layout="wide",
    page_icon='assets/favicon.png'
)
with open('styles/main.css') as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.markdown('### Twitter hot topic Sentimental Analysis')
st.markdown(
    """ An interactive Sentiment Analysis dashboard using twitter's latest trends. 
		The code uses several open-source libraries such as [tweepy](https://www.tweepy.org/), 
		[nltk](https://www.nltk.org/) and [textblob](https://textblob.readthedocs.io/en/dev/).
"""
)

if 'country' not in st.session_state or \
	'topics' not in st.session_state or \
	'trends_json' not in st.session_state or\
	'df_not_exists' not in st.session_state:
	st.session_state['country'] = ""
	st.session_state['topics'] = []
	st.session_state['trends_json'] = {}
	st.session_state['df_not_exists'] = True


# Load tweepy tokens
auth = tweepy.OAuthHandler(tweepy_token.API_KEY, tweepy_token.API_SECRET)
auth.set_access_token(tweepy_token.ACCESS_TOKEN, tweepy_token.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)
client = tweepy.Client(bearer_token=tweepy_token.BEARER_TOKEN, return_type=requests.Response)

# Query available locations in twitter
locations = json.loads(json.dumps(api.available_trends(), indent=1))

# Create a dictionary of countries and WOEID
loc_woeid_dict = {}
for loc in locations:
	if loc['placeType']['name'] == 'Country':
		loc_woeid_dict[f"{loc['name']} ({loc['placeType']['name']})"] = loc['woeid']

# Gets called if country changes
def get_trending_topic(loc_woeid_dict):
	# Queries list of hot topics given a country
	st.session_state['trends_json'] = json.loads(json.dumps(api.get_place_trends(loc_woeid_dict[st.session_state['country']]), indent=1))
	st.session_state['df_not_exists'] = True

st.session_state['country_new'] = st.session_state['country']
# Country selectobx
st.session_state['country'] = st.selectbox(
	'Available countries for hot topics in Twitter:',
	loc_woeid_dict.keys()
	)
	
if st.session_state['country'] != st.session_state['country_new']:
	get_trending_topic(loc_woeid_dict)

# st.write('You selected country :', st.session_state['country'])


# List trending topic
trends_topic = []
if st.session_state['trends_json'] != {}:
	for trend in st.session_state['trends_json'][0]["trends"]:	
		trends_topic.append(trend["name"].strip("#"))

# Selecting topic
st.session_state['topics'] = st.multiselect(
	'Choose one or more topics (additional topics will restrict your query not extend):',
	trends_topic
	)

# st.write('You selected:', st.session_state['topics'])

# Twitter query with given topics, only english, no retweets
query = f"{' '.join(st.session_state['topics'])} lang:en -is:retweet"

# Run query and store in a Dataframe
if st.button('Press to Query'):
	response = client.search_recent_tweets(query=query, max_results=50, tweet_fields=['text', 'lang', 'geo'])
	tweets_data = response.json()['data']
	st.session_state.tweet_df = pd.json_normalize(tweets_data) 
	with st.expander("DataFrame ⤵️"):
		st.dataframe(st.session_state.tweet_df)
	st.session_state['df_not_exists'] = False
	# st.session_state.tweet_df.to_csv('tweets.csv')

# Apply sentimental analysis on the text and plot
if st.button('Press to apply sentiment analysis', disabled=st.session_state['df_not_exists']):
	st.session_state.tweet_df['clean_text'] = st.session_state.tweet_df['text'].apply(lemmatize_text)
	st.session_state.tweet_df["polarity"] = st.session_state.tweet_df["clean_text"].apply(getPolarity)
	st.session_state.tweet_df["sentiment"] = st.session_state.tweet_df["polarity"].apply(getPolAnalysis)
	st.session_state.tweet_df["subjectivity"] = st.session_state.tweet_df["clean_text"].apply(getSubjectivity)
	st.session_state.tweet_df["sub_obj"] = st.session_state.tweet_df["subjectivity"].apply(getSubAnalysis)
	# st.dataframe(st.session_state.tweet_df)

	col1, col2 = st.columns(2)
	with col1:
		fig1, ax1 = plt.subplots()
		sent_percentage = st.session_state.tweet_df['sentiment'].value_counts()/sum(st.session_state.tweet_df['sentiment'].value_counts())
		labels = sent_percentage.keys()
		sizes = sent_percentage.values
		ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
		ax1.axis('equal') 
		plt.title('Sentiment Pie Chart')
		
		st.pyplot(fig1)

	with col2:
		fig1, ax1 = plt.subplots()
		sent_percentage = st.session_state.tweet_df['sub_obj'].value_counts()/sum(st.session_state.tweet_df['sub_obj'].value_counts())
		labels = sent_percentage.keys()
		sizes = sent_percentage.values
		ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
		ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
		plt.title('Subjectivity Pie Chart')
		
		st.pyplot(fig1)


# TODO: make second for pure text