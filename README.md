# International Trade Map Visualization

An interactive visualization tool that displays global trade relationships between countries in a beautiful and informative way.

![International Trade Map Preview](preview.png)

## Overview

This project creates an interactive web-based visualization of international trade data. The map shows trade relationships between countries with:

- Color-coded countries based on total export volume
- Interactive connections between trading partners
- Detailed information on hover and click
- Multiple map styles and visualization options

## Features

- **Multiple map styles**: Dark mode, Light mode, Terrain view, Toner, and Watercolor
- **Rich data visualization**: Countries colored by trade volume using gradient-based choropleth
- **Interactive connections**: Trade flows shown with lines of varying thickness
- **Detailed tooltips**: Hover over countries to see names and basic trade information
- **Comprehensive popups**: Click on countries to view detailed trade statistics
- **Trade categories**: Visualize trade in Electronics, Automotive, Agriculture, Pharmaceuticals, Energy, Textiles, Machinery, and Raw Materials
- **Layer control**: Toggle between different visualization layers
- **Full-screen capability**: View the map in immersive full-screen mode
- **Professional legend**: Clear visualization of data scale and meaning

## Technologies Used

- **Python 3**: Core programming language
- **Folium**: Python library for creating interactive maps
- **Pandas**: Data manipulation and analysis
- **Country Converter & pycountry**: Country code handling and information
- **HTML/CSS/JavaScript**: Web-based visualization
- **Leaflet.js**: (via Folium) The underlying interactive mapping library

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/international-trade-map.git
cd international-trade-map
```

2. Create a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```
pip install folium pandas country_converter pycountry
```

## Usage

1. Run the Python script to generate the HTML map:
```
python international_trade_map.py
```

2. Open the generated HTML file in your web browser:
```
# On Windows
Start-Process international_trade_map.html

# On macOS
open international_trade_map.html

# On Linux
xdg-open international_trade_map.html
```

3. Interact with the map:
- Toggle between different map styles using the layer control
- Hover over countries to see basic information
- Click on countries to see detailed trade statistics
- Use the zoom controls to explore specific regions

## Data Sources

The current implementation uses sample data for demonstration purposes. To use real trade data, you can:

1. Import CSV data from sources like:
- UN Comtrade (https://comtrade.un.org/)
- World Bank (https://data.worldbank.org/)
- Observatory of Economic Complexity (https://oec.world/)

2. Modify the data loading section in `international_trade_map.py` to work with your data format

## Customization

You can customize the visualization by modifying the script:

- Change the color schemes in the choropleth map
- Adjust the line thickness and colors for trade connections
- Add or remove trade categories
- Modify popup content and styling
- Change the default map style and center position

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Map tiles by Stamen Design, under CC BY 3.0
- Data by OpenStreetMap, under ODbL
- Icons and additional styling elements from various open-source projects

