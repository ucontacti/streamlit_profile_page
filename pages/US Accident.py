
import pandas as pd
import pydeck as pdk
import streamlit as st
import numpy as np
import geopandas as gpd
import pathlib
import requests
import zipfile
import os
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb

# @st.cache
def read_and_retrieve():
    data = pd.read_csv('../US_Accidents_Dec21_updated.csv',
            nrows=10000,
            usecols=['Start_Lng', 'Start_Lat', 'Severity', 'County', 'State', 'Zipcode', 'Start_Time']
            )
    data.dropna(inplace=True)
    return data

def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))


df = read_and_retrieve()
df['Year'] = pd.DatetimeIndex(df['Start_Time']).year

scale = st.radio(
    'What Scale would like to chose?',
    ('County', 'State', 'Zipcode'))
year = st.slider('Year', 2016, 2021, 2016)
df = df.drop(df[df.Year != year].index)

if df.empty:
    st.info("nothing to show!")

agg_df = df.groupby(scale).agg(
        Scale=(scale, 'last'),
        Count=('Severity', 'count'),
        Avg_Severity=('Severity', 'mean'),
        lon=('Start_Lng', 'mean'),
        lat=('Start_Lat', 'mean')
    )

selected_indc = st.selectbox("Indicator",
        ('Count', 'Avg_Severity'))

with st.expander("DataFrame ⤵️"):
    st.dataframe(agg_df)

midpoint = mpoint(agg_df["lat"], agg_df["lon"])

STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

@st.cache
def get_geom_data(category):

    prefix = (
        "https://raw.githubusercontent.com/giswqs/streamlit-geospatial/master/data/"
    )
    links = {
        "national": prefix + "us_nation.geojson",
        "state": prefix + "us_states.geojson",
        "county": prefix + "us_counties.geojson",
        "metro": prefix + "us_metro_areas.geojson",
        "zip": "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_zcta510_500k.zip",
    }

    if category.lower() == "zipcode":
        r = requests.get(links["zip"])
        out_zip = os.path.join(DOWNLOADS_PATH, "cb_2018_us_zcta510_500k.zip")
        with open(out_zip, "wb") as code:
            code.write(r.content)
        zip_ref = zipfile.ZipFile(out_zip, "r")
        zip_ref.extractall(DOWNLOADS_PATH)
        gdf = gpd.read_file(out_zip.replace("zip", "shp"))
    else:
        gdf = gpd.read_file(links[category])
    return gdf

# FIXME: check either can to cache or not
@st.cache
def get_inventory_data(df, scale):
    if scale == "county":
    #     # df["county_fips"] = df["County"].map(str)
    #     # df["county_fips"] = df["county_fips"].str.zfill(5)
        df["county_name"] = df["Scale"]
    elif scale == "state":
        df["STUSPS"] = df["Scale"].str.upper()
    elif scale == "zipcode":
        df["postal_code"] = df["Scale"]
        # df["postal_code"] = df["postal_code"].map(str)
        # df["postal_code"] = df["postal_code"].str.zfill(5)

    return df

def join_attributes(gdf, df, category):

    new_gdf = None
    if category == "county":
        new_gdf = gdf.merge(df, left_on="NAME", right_on="county_name", how="inner")
    elif category == "state":
        new_gdf = gdf.merge(df, left_on="STUSPS", right_on="STUSPS", how="outer")
    # elif category == "national":
    #     if "geo_country" in df.columns.values.tolist():
    #         df["country"] = None
    #         df.loc[0, "country"] = "United States"
    #     new_gdf = gdf.merge(df, left_on="NAME", right_on="country", how="outer")
    # elif category == "metro":
    #     new_gdf = gdf.merge(df, left_on="CBSAFP", right_on="cbsa_code", how="outer")
    elif category == "zipcode":
        new_gdf = gdf.merge(df, left_on="GEOID10", right_on="postal_code", how="outer")
    return new_gdf


def select_non_null(gdf, col_name):
    new_gdf = gdf[~gdf[col_name].isna()]
    return new_gdf

def select_null(gdf, col_name):
    new_gdf = gdf[gdf[col_name].isna()]
    return new_gdf



palettes = cm.list_colormaps()
palette = st.selectbox("Color palette", palettes, index=palettes.index("Blues"))
n_colors = st.slider("Number of colors", min_value=2, max_value=20, value=8)

colors = cm.get_palette(palette, n_colors)
colors = [hex_to_rgb(c) for c in colors]

inventory_df = get_inventory_data(agg_df, scale.lower())

gdf = get_geom_data(scale.lower())
gdf = join_attributes(gdf, inventory_df, scale.lower())


gdf_null = select_null(gdf, selected_indc)
gdf = select_non_null(gdf, selected_indc)

for i, ind in enumerate(gdf.index):
    index = int(i / (len(gdf) / len(colors)))
    if index >= len(colors):
        index = len(colors) - 1
    gdf.loc[ind, "R"] = colors[index][0]
    gdf.loc[ind, "G"] = colors[index][1]
    gdf.loc[ind, "B"] = colors[index][2]


min_value = gdf[selected_indc].min()
max_value = gdf[selected_indc].max()
color = "color"
# color_exp = f"[({selected_indc}-{min_value})/({max_value}-{min_value})*255, 0, 0]"
color_exp = f"[R, G, B]"

geojson = pdk.Layer(
    "GeoJsonLayer",
    gdf,
    pickable=True,
    opacity=0.5,
    stroked=True,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation=selected_indc,
    elevation_scale=1000,
    get_fill_color=color_exp,
    # get_fill_color=color_exp,
    get_line_color=[0, 0, 0],
    get_line_width=2,
    line_width_min_pixels=1,
)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=2.5,
        pitch=40,
    ),
    layers=[geojson],
))

st.write(
    cm.create_colormap(
        palette,
        label=selected_indc.replace("_", " ").title(),
        width=0.2,
        height=3,
        orientation="vertical",
        vmin=min_value,
        vmax=max_value,
        font_size=10,
    )
)
# TODO: by City, Zipcode
# TODO: Clean Design
# TODO: Clean code 
# TODO: Add documentation