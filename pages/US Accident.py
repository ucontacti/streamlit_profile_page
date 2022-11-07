
import pandas as pd
import pydeck as pdk
import streamlit as st

data = pd.read_csv('~/Downloads/US_Accidents_Dec21_updated.csv')
df = data.head(1000)
df.dropna(inplace=True)

view = pdk.data_utils.compute_view(df[["Start_Lng", "Start_Lat"]])
view.pitch = 75
view.bearing = 60

column_layer = pdk.Layer(
    "ColumnLayer",
    data=df,
    get_position=["Start_Lng", "Start_Lat"],
    get_elevation="Severity",
    elevation_scale=100,
    radius=50,
    get_fill_color=[200, 200, 200],
    pickable=True,
    auto_highlight=True,
)

tooltip = {
    "html": "hmmmmmmmmmmmmmmmmm",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}

r = pdk.Deck(
    column_layer,
    initial_view_state=view,
    tooltip=tooltip,
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE,
)

st.pydeck_chart(r)