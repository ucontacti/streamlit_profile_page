import numpy as np
import geopandas as gpd

def mpoint(lat, lon):
    return (np.average(lat), np.average(lon))


def get_geom_data(category):

    prefix = (
        "https://raw.githubusercontent.com/giswqs/streamlit-geospatial/master/data/"
    )
    links = {
        "state": prefix + "us_states.geojson",
        "county": prefix + "us_counties.geojson",
    }

    gdf = gpd.read_file(links[category])
    return gdf

def get_inventory_data(df, scale):
    if scale == "county":
        df["county_name"] = df.index
    elif scale == "state":
        df["STUSPS"] = df.index.str.upper()

    return df


def select_non_null(gdf, col_name):
    new_gdf = gdf[~gdf[col_name].isna()]
    return new_gdf


def join_attributes(gdf, df, category):

    new_gdf = None
    if category == "county":
        new_gdf = gdf.merge(df, left_on="NAME", right_on="county_name", how="inner")
    elif category == "state":
        new_gdf = gdf.merge(df, left_on="STUSPS", right_on="STUSPS", how="outer")
    return new_gdf

