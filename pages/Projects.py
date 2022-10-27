import streamlit as st
import tweepy

st.title("Projects")
auth = tweepy.OAuth2AppHandler(
    "API / Consumer Key here", "API / Consumer Secret here"
)
api = tweepy.API(auth)