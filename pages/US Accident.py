
import pandas as pd
import pydeck as pdk
import streamlit as st
import numpy as np
import geopandas as gpd

# @st.cache
def read_and_retrieve():
    data = pd.read_csv('../US_Accidents_Dec21_updated.csv',
            nrows=1000,
            usecols=['Start_Lng', 'Start_Lat', 'Severity', 'City', 'State']
            )
    data.dropna(inplace=True)
    return data

def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))


df = read_and_retrieve()
df.rename(columns={'Start_Lng':'lon','Start_Lat': 'lat'}, inplace=True)

df = df.groupby('State').agg(
        State=('State', 'last'),
        Count=('Severity', 'count'),
        Avg_Severity=('Severity', 'mean'),
        lon=('lon', 'mean'),
        lat=('lat', 'mean')
    )

with st.expander("DataFrame ⤵️"):
    st.dataframe(df)


midpoint = mpoint(df["lat"], df["lon"])

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

    # if category.lower() == "zip":
    #     r = requests.get(links[category])
    #     out_zip = os.path.join(DOWNLOADS_PATH, "cb_2018_us_zcta510_500k.zip")
    #     with open(out_zip, "wb") as code:
    #         code.write(r.content)
    #     zip_ref = zipfile.ZipFile(out_zip, "r")
    #     zip_ref.extractall(DOWNLOADS_PATH)
    #     gdf = gpd.read_file(out_zip.replace("zip", "shp"))
    # else:
    gdf = gpd.read_file(links[category])
    return gdf

@st.cache
def get_inventory_data(df, scale):
    if "county" == scale:
        df["county_fips"] = df["county_fips"].map(str)
        df["county_fips"] = df["county_fips"].str.zfill(5)
    elif "state" == scale:
        df["STUSPS"] = df["State"].str.upper()
    elif "zip" == scale:
        df["postal_code"] = df["postal_code"].map(str)
        df["postal_code"] = df["postal_code"].str.zfill(5)

    return df

def join_attributes(gdf, df, category):

    new_gdf = None
    if category == "county":
        new_gdf = gdf.merge(df, left_on="GEOID", right_on="county_fips", how="outer")
    elif category == "state":
        new_gdf = gdf.merge(df, left_on="STUSPS", right_on="STUSPS", how="outer")
    elif category == "national":
        if "geo_country" in df.columns.values.tolist():
            df["country"] = None
            df.loc[0, "country"] = "United States"
        new_gdf = gdf.merge(df, left_on="NAME", right_on="country", how="outer")
    elif category == "metro":
        new_gdf = gdf.merge(df, left_on="CBSAFP", right_on="cbsa_code", how="outer")
    elif category == "zip":
        new_gdf = gdf.merge(df, left_on="GEOID10", right_on="postal_code", how="outer")
    return new_gdf


def select_non_null(gdf, col_name):
    new_gdf = gdf[~gdf[col_name].isna()]
    return new_gdf

def select_null(gdf, col_name):
    new_gdf = gdf[gdf[col_name].isna()]
    return new_gdf

inventory_df = get_inventory_data(df, 'state')

gdf = get_geom_data('state')
gdf = join_attributes(gdf, inventory_df, 'state')
gdf_null = select_null(gdf, 'Avg_Severity')
gdf = select_non_null(gdf, 'Avg_Severity')



geojson = pdk.Layer(
    "GeoJsonLayer",
    gdf,
    pickable=True,
    opacity=0.5,
    stroked=True,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation="Count",
    elevation_scale=1000,
    # get_fill_color="color",
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


# TODO: by City, County, State, Zipcode
# TODO: add different color for different scales
# TODO: add year selector
# TODO: Add column selector

