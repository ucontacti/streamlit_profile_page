
import pandas as pd
import pydeck as pdk
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
from utils.pydeck_util import mpoint, get_geom_data, \
                            get_inventory_data, select_non_null,\
                            join_attributes

st.set_page_config(layout="wide")

@st.cache
def read_and_retrieve():
    data = pd.read_csv('../US_Accidents_Dec21_updated.csv',
            nrows=10000,
            usecols=['Start_Lng', 'Start_Lat', 'Severity', 'County', 'State', 'Zipcode', 'Start_Time']
            )
    data.dropna(inplace=True)
    data['Year'] = pd.DatetimeIndex(data['Start_Time']).year
    return data


df = read_and_retrieve()


row1_col1, row1_col2, row1_col3 = st.columns(
    [2, 3, 2]
)

with row1_col1:
    scale = st.radio(
        'What Scale would like to chose?',
        ('County', 'State'))

with row1_col2:
    year = st.slider('Year', 2016, 2021, 2016)

with row1_col3:
    selected_indc = st.selectbox("Indicator",
            ('number_of_incidents', 'avg_severity'))

agg_df = df[df.Year == year].groupby(scale).agg(
        Name=(scale, 'last'),
        number_of_incidents=('Severity', 'count'),
        avg_severity=('Severity', 'mean'),
        lon=('Start_Lng', 'mean'),
        lat=('Start_Lat', 'mean')
    )

if agg_df.empty:
    st.info("nothing to show!")

with st.expander("DataFrame ⤵️"):
    st.dataframe(agg_df)

midpoint = mpoint(agg_df["lat"], agg_df["lon"])





row2_col1, row2_col2, row2_col3 = st.columns(
    [1, 2, 1]
)

palettes = cm.list_colormaps()
with row2_col1:
    palette = st.selectbox("Color palette", palettes, index=palettes.index("Blues"))
with row2_col2:
    n_colors = st.slider("Number of colors", min_value=2, max_value=20, value=8)
with row2_col3:
    st.info("Hold CTRL and Left Click to rotate the view!")

colors = cm.get_palette(palette, n_colors)
colors = [hex_to_rgb(c) for c in colors]

inventory_df = get_inventory_data(agg_df, scale.lower())

gdf = get_geom_data(scale.lower())
gdf = join_attributes(gdf, inventory_df, scale.lower())


gdf = select_non_null(gdf, selected_indc)
gdf = gdf.sort_values(by=selected_indc, ascending=True)

for i, ind in enumerate(gdf.index):
    index = int(i / (len(gdf) / len(colors)))
    if index >= len(colors):
        index = len(colors) - 1
    gdf.loc[ind, "R"] = colors[index][0]
    gdf.loc[ind, "G"] = colors[index][1]
    gdf.loc[ind, "B"] = colors[index][2]


min_value = gdf[selected_indc].min()
max_value = gdf[selected_indc].max()
color_exp = f"[R, G, B]"

elevation = 300 if selected_indc == 'number_of_incidents' else 50000
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
    elevation_scale=elevation,
    get_fill_color=color_exp,
    get_line_color=[0, 0, 0],
    get_line_width=2,
    line_width_min_pixels=1,
)


row3_col1, row3_col2 = st.columns(
    [6, 1]
)

# tooltip_value = f"<b>Value:</b> {median_listing_price}""
tooltip = {
    "html": "<b>Name:</b> {Name}<br><b>Value:</b> {"
    + selected_indc
    + "}",
    "style": {"backgroundColor": "steelblue", "color": "white"},
}

with row3_col1:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=3.35,
            pitch=40,
        ),
        layers=[geojson],
        tooltip=tooltip
    ))

with row3_col2:
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
# TODO: Clean code 
# TODO: Add documentation
# TODO: Add more columns