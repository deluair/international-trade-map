import folium
import pandas as pd
import random
import country_converter as coco
import numpy as np
from folium.plugins import FloatImage, Fullscreen, HeatMap, MarkerCluster
from folium.features import DivIcon
import branca.colormap as cm
import pycountry
import colorsys

# Create enhanced sample trade data
countries = [
    'USA', 'China', 'Germany', 'Japan', 'UK', 'France', 'India', 'Brazil', 
    'Russia', 'South Korea', 'Canada', 'Mexico', 'Australia', 'Indonesia', 
    'Turkey', 'Saudi Arabia', 'Italy', 'Spain', 'Netherlands', 'Switzerland'
]

# Trade categories with color mapping
trade_categories = {
    'Electronics': '#e41a1c',
    'Automotive': '#377eb8',
    'Agriculture': '#4daf4a',
    'Pharmaceuticals': '#984ea3',
    'Energy': '#ff7f00',
    'Textiles': '#ffff33',
    'Machinery': '#a65628',
    'Raw Materials': '#f781bf'
}

# Generate sample trade flows
trade_data = []
for exporter in countries:
    # Create a preference bias for more realistic trade patterns
    regional_bias = {}
    for importer in countries:
        if importer != exporter:
            # Geographic proximity bias (simplified)
            regional_bias[importer] = random.uniform(0.5, 2.0)
            
    for importer in countries:
        if exporter != importer:
            # Generate multiple trade categories between country pairs
            for category, color in trade_categories.items():
                # Create realistic variations in trade volume
                base_volume = random.randint(50, 2000)
                
                # Apply regional bias for more realistic patterns
                if importer in regional_bias:
                    volume = int(base_volume * regional_bias[importer])
                else:
                    volume = base_volume
                
                # Some categories might have no trade between certain countries
                if random.random() > 0.7:  # 30% chance of no trade in a category
                    trade_data.append({
                        'exporter': exporter,
                        'importer': importer,
                        'category': category,
                        'color': color,
                        'volume': volume
                    })

# Convert to DataFrame
df = pd.DataFrame(trade_data)

# Calculate total export volume for each country
# Calculate total export volume for each country
country_volumes = df.groupby('exporter')['volume'].sum().reset_index()
country_volumes.columns = ['country', 'total_volume']

# Calculate category distribution for each country
category_by_country = df.groupby(['exporter', 'category'])['volume'].sum().reset_index()

# Calculate global trade statistics
total_global_trade = df['volume'].sum()
avg_trade_vol = df['volume'].mean()
max_trade_vol = df['volume'].max()

# Get country coordinates (approximate centers)
country_coords = {
    'USA': [37.0902, -95.7129],
    'China': [35.8617, 104.1954],
    'Germany': [51.1657, 10.4515],
    'Japan': [36.2048, 138.2529],
    'UK': [55.3781, -3.4360],
    'France': [46.2276, 2.2137],
    'India': [20.5937, 78.9629],
    'Brazil': [-14.2350, -51.9253],
    'Russia': [61.5240, 105.3188],
    'South Korea': [35.9078, 127.7669],
    'Canada': [56.1304, -106.3468],
    'Mexico': [23.6345, -102.5528],
    'Australia': [-25.2744, 133.7751],
    'Indonesia': [-0.7893, 113.9213],
    'Turkey': [38.9637, 35.2433],
    'Saudi Arabia': [23.8859, 45.0792],
    'Italy': [41.8719, 12.5674],
    'Spain': [40.4637, -3.7492],
    'Netherlands': [52.1326, 5.2913],
    'Switzerland': [46.8182, 8.2275]
}

# Get additional country information for visualization
country_info = {}
for country in countries:
    try:
        # Try to get country information from pycountry
        country_data = pycountry.countries.get(name=country)
        if not country_data and country == 'USA':
            country_data = pycountry.countries.get(alpha_3='USA')
        if not country_data and country == 'UK':
            country_data = pycountry.countries.get(alpha_3='GBR')
            
        if country_data:
            country_info[country] = {
                'alpha2': country_data.alpha_2,
                'alpha3': country_data.alpha_3,
                'flag': country_data.alpha_2.lower()
            }
    except:
        # Fallback for countries that might not be found
        iso3 = coco.convert(names=country, to='ISO3')
        country_info[country] = {
            'alpha3': iso3,
            'flag': 'unknown'
        }

# Convert country names to ISO3 codes for map
iso3_codes = {}
for country in countries:
    iso3 = coco.convert(names=country, to='ISO3')
    iso3_codes[country] = iso3
    
# Helper function to generate gradient colors for flow lines
def generate_gradient_color(start_color, end_color, n_steps=10):
    # Convert hex to RGB
    start_rgb = tuple(int(start_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    end_rgb = tuple(int(end_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Convert RGB to HSV
    start_hsv = colorsys.rgb_to_hsv(start_rgb[0]/255, start_rgb[1]/255, start_rgb[2]/255)
    end_hsv = colorsys.rgb_to_hsv(end_rgb[0]/255, end_rgb[1]/255, end_rgb[2]/255)
    
    # Generate n_steps HSV colors
    hsv_colors = []
    for i in range(n_steps):
        frac = i / (n_steps - 1)
        h = start_hsv[0] + frac * (end_hsv[0] - start_hsv[0])
        s = start_hsv[1] + frac * (end_hsv[1] - start_hsv[1])
        v = start_hsv[2] + frac * (end_hsv[2] - start_hsv[2])
        hsv_colors.append((h, s, v))
    
    # Convert back to RGB hex
    gradient_colors = []
    for hsv in hsv_colors:
        r, g, b = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
        hex_color = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))
        gradient_colors.append(hex_color)
        
    return gradient_colors

# Create map with a more attractive style
map_styles = {
    'Default': 'cartodb positron',
    'Dark': 'cartodbdark_matter', 
    'Terrain': 'Stamen Terrain',
    'Toner': 'Stamen Toner',
    'Watercolor': 'Stamen Watercolor'
}

# Create the base map
m = folium.Map(
    location=[20, 0], 
    zoom_start=2.5, 
    tiles=map_styles['Dark'],
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    control_scale=True
)

# Add full screen control
Fullscreen().add_to(m)

# Create a layer control to toggle between different map styles
folium.TileLayer(
    map_styles['Default'], 
    name='Light Map',
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
).add_to(m)

folium.TileLayer(
    map_styles['Dark'], 
    name='Dark Map',
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
).add_to(m)

folium.TileLayer(
    map_styles['Terrain'], 
    name='Terrain Map',
    attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>'
).add_to(m)

folium.TileLayer(
    map_styles['Toner'], 
    name='Toner Map',
    attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>'
).add_to(m)

folium.TileLayer(
    map_styles['Watercolor'], 
    name='Watercolor Map',
    attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>. Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://www.openstreetmap.org/copyright">ODbL</a>'
).add_to(m)

# Add choropleth layer
country_volumes['iso3'] = country_volumes['country'].map(iso3_codes)

# Create a more visually appealing colormap
colormap = cm.linear.YlOrRd_09.scale(
    country_volumes['total_volume'].min(),
    country_volumes['total_volume'].max()
)
colormap.caption = 'Total Export Volume (Million USD)'

# Add enhanced choropleth layer
choropleth = folium.Choropleth(
    geo_data='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json',
    name='Trade Volume',
    data=country_volumes,
    columns=['iso3', 'total_volume'],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    highlight=True,
    legend_name='Total Export Volume (Million USD)'
).add_to(m)

# Add colormap to the map
m.add_child(colormap)

# Add tooltips to the choropleth
choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['name'], labels=False)
)

# Create flow line groups by category
flow_layers = {}
for category in trade_categories:
    flow_layers[category] = folium.FeatureGroup(name=f"{category} Trade Flows")
    
# Process significant trade connections
threshold = df['volume'].quantile(0.7)  # Only show top 30% of connections
filtered_df = df[df['volume'] > threshold]

# Group by exporter-importer pairs to combine categories
pair_summary = filtered_df.groupby(['exporter', 'importer'])['volume'].sum().reset_index()

# Add gradient flow lines with arrows for direction
for _, row in pair_summary.iterrows():
    exporter = row['exporter']
    importer = row['importer']
    total_volume = row['volume']

# Add markers for each country with trade info
for country, coords in country_coords.items():
    # Get export data for this country
    exports = df[df['exporter'] == country]
    total_exports = exports['volume'].sum()
    
    # Get top trading partners
    top_partners = exports.sort_values('volume', ascending=False).head(3)
    partners_info = "<br>".join([f"{row['importer']}: {row['volume']} million USD" for _, row in top_partners.iterrows()])
    
    # Create popup HTML
    popup_html = f"""
    <h4>{country}</h4>
    <b>Total Exports:</b> {total_exports} million USD<br>
    <b>Top Export Destinations:</b><br>
    {partners_info}
    """
    
    # Add marker
    folium.CircleMarker(
        location=coords,
        radius=total_exports / 200,
        color='red',
        fill=True,
        fill_color='red',
        fill_opacity=0.4,
        popup=folium.Popup(popup_html, max_width=300)
    ).add_to(m)

# Add a title
title_html = '''
            <h3 align="center" style="font-size:20px"><b>International Trade Map</b></h3>
            <h4 align="center" style="font-size:16px"><i>Sample Trade Data Visualization</i></h4>
            '''
m.get_root().html.add_child(folium.Element(title_html))

# Add a legend for the line thickness
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 150px; height: 90px; 
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white;
            padding: 10px;
            ">
<p><b>Trade Volume</b></p>
<p>
<i style="background: blue; width: 10px; height: 2px; display: inline-block;"></i> Low<br>
<i style="background: blue; width: 10px; height: 4px; display: inline-block;"></i> Medium<br>
<i style="background: blue; width: 10px; height: 6px; display: inline-block;"></i> High
</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map to an HTML file
m.save('international_trade_map.html')

print("Map created successfully! Open 'international_trade_map.html' in your browser to view it.")

