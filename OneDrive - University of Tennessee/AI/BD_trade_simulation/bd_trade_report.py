#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bangladesh Trade Report Generator

This script generates an HTML report based on the real Bangladesh trade data.
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from datetime import datetime

# Define paths to mapping files
PRODUCT_CODES_FILE = "data/product_codes_HS92_V202501.csv"
COUNTRY_CODES_FILE = "data/country_codes_V202501.csv"

def load_trade_data(file_path="data/bd_trade_data.csv"):
    """Load and process the Bangladesh trade data from CSV file"""
    print(f"Loading data from {file_path}...")
    
    try:
        # Load the data (use a small sample initially to check structure)
        df = pd.read_csv(file_path)
        print(f"Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"Columns: {', '.join(df.columns)}")
        
        # Check if we have the expected new column structure (t, i, j, k, v, q)
        if all(col in df.columns for col in ['t', 'i', 'j', 'k', 'v', 'q']):
            print("Detected raw data format, will map to standard columns")
            # Map columns to standard names
            # t = year, i = reporter country, j = partner country, k = product code, v = trade value, q = quantity
            df = df.rename(columns={
                't': 'year',
                'i': 'reporter_code',
                'j': 'partner_code',
                'k': 'product_code',
                'v': 'value',
                'q': 'quantity'
            })
            
            # Load product codes
            if os.path.exists(PRODUCT_CODES_FILE):
                print(f"Loading product codes from {PRODUCT_CODES_FILE}")
                product_codes = pd.read_csv(PRODUCT_CODES_FILE, usecols=['code', 'description'])
                product_codes = product_codes.rename(columns={'code': 'product_code', 'description': 'product_name'})
                # Ensure product_code is the same type for merging (assuming int initially)
                try:
                    df['product_code'] = df['product_code'].astype(int)
                    product_codes['product_code'] = product_codes['product_code'].astype(int)
                    df = pd.merge(df, product_codes, on='product_code', how='left')
                    print("Merged product codes successfully.")
                except ValueError:
                     print("Warning: Could not convert product_code to int for merging. Trying string merge.")
                     # Handle cases where product codes might be like 'TOTAL' or non-numeric
                     df['product_code'] = df['product_code'].astype(str)
                     product_codes['product_code'] = product_codes['product_code'].astype(str)
                     df = pd.merge(df, product_codes, on='product_code', how='left')
                     print("Merged product codes using string type.")

            else:
                print(f"Warning: Product codes file not found at {PRODUCT_CODES_FILE}")
                df['product_name'] = 'Unknown' # Add placeholder column

            # Load country codes
            if os.path.exists(COUNTRY_CODES_FILE):
                print(f"Loading country codes from {COUNTRY_CODES_FILE}")
                country_codes = pd.read_csv(COUNTRY_CODES_FILE, usecols=['country_code', 'country_name'])
                country_codes = country_codes.rename(columns={'country_code': 'partner_code', 'country_name': 'partner_name'})
                 # Ensure partner_code is the same type for merging (assuming int)
                try:
                     df['partner_code'] = df['partner_code'].astype(int)
                     country_codes['partner_code'] = country_codes['partner_code'].astype(int)
                     df = pd.merge(df, country_codes, on='partner_code', how='left')
                     print("Merged partner country codes successfully.")
                except ValueError:
                     print("Warning: Could not convert partner_code to int for merging. Trying string merge.")
                     df['partner_code'] = df['partner_code'].astype(str)
                     country_codes['partner_code'] = country_codes['partner_code'].astype(str)
                     df = pd.merge(df, country_codes, on='partner_code', how='left')
                     print("Merged partner country codes using string type.")

                # Merge again for reporter country name (using the same country code file)
                country_codes = country_codes.rename(columns={'partner_code': 'reporter_code', 'partner_name': 'reporter_name'})
                try:
                     df['reporter_code'] = df['reporter_code'].astype(int)
                     country_codes['reporter_code'] = country_codes['reporter_code'].astype(int)
                     df = pd.merge(df, country_codes, on='reporter_code', how='left')
                     print("Merged reporter country codes successfully.")
                except ValueError:
                     print("Warning: Could not convert reporter_code to int for merging. Trying string merge.")
                     df['reporter_code'] = df['reporter_code'].astype(str)
                     country_codes['reporter_code'] = country_codes['reporter_code'].astype(str)
                     df = pd.merge(df, country_codes, on='reporter_code', how='left')
                     print("Merged reporter country codes using string type.")

            else:
                 print(f"Warning: Country codes file not found at {COUNTRY_CODES_FILE}")
                 df['partner_name'] = 'Unknown' # Add placeholder columns
                 df['reporter_name'] = 'Unknown'
                 
            # Bangladesh code is 50 based on observation
            # If j=50, it's an import to Bangladesh
            # If i=50, it's an export from Bangladesh
            df['trade_type'] = 'unknown'
            df.loc[df['reporter_code'] == 50, 'trade_type'] = 'export'
            df.loc[df['partner_code'] == 50, 'trade_type'] = 'import'
            
            # Create export and import value columns
            df['export_value'] = 0.0
            df['import_value'] = 0.0
            
            df.loc[df['trade_type'] == 'export', 'export_value'] = df.loc[df['trade_type'] == 'export', 'value']
            df.loc[df['trade_type'] == 'import', 'import_value'] = df.loc[df['trade_type'] == 'import', 'value']
            
            # Add a consolidated country_name column for partner countries (where trade_type is import)
            # or reporter countries (where trade_type is export, but partner matters more)
            # We need partner name for exports/imports from Bangladesh perspective
            # df['country_name'] = df['partner_name'] 
            
            print(f"Data mapped and merged. Sample: {df.head().to_dict()}")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        if not os.path.exists(file_path):
            print(f"File {file_path} not found")
        return pd.DataFrame()

def prepare_data_for_report(df):
    """Prepare the data for the report"""
    if df.empty:
        print("No data to prepare")
        return pd.DataFrame()
    
    # Check for expected columns after mapping
    if 'year' in df.columns and 'export_value' in df.columns and 'import_value' in df.columns:
        # Group by year and calculate totals
        print("Calculating yearly export and import totals...")
        try:
            yearly_data = df.groupby('year').agg({
                'export_value': 'sum',
                'import_value': 'sum'
            }).reset_index()
            
            # Calculate trade balance and other metrics
            yearly_data['trade_balance'] = yearly_data['export_value'] - yearly_data['import_value']
            yearly_data['export_billion'] = yearly_data['export_value'] / 1e6
            yearly_data['import_billion'] = yearly_data['import_value'] / 1e6
            yearly_data['trade_balance_billion'] = yearly_data['trade_balance'] / 1e6
            
            print(f"Yearly data calculated for {len(yearly_data)} years")
            return yearly_data
        except Exception as e:
            print(f"Error preparing data: {e}")
    else:
        # Try to identify export and import columns if they have different names
        value_columns = [col for col in df.columns if 'value' in col.lower()]
        print(f"Potential value columns: {value_columns}")
        
        # If we have a single value column, try to separate by trade flow
        if len(value_columns) == 1 and 'trade_type' in df.columns:
            print("Trying to separate value by trade flow...")
            value_col = value_columns[0]
            pivot_df = df.pivot_table(
                index='year', 
                columns='trade_type', 
                values=value_col,
                aggfunc='sum'
            ).reset_index()
            
            if 'export' in pivot_df.columns and 'import' in pivot_df.columns:
                pivot_df['trade_balance'] = pivot_df['export'] - pivot_df['import']
                pivot_df['export_billion'] = pivot_df['export'] / 1e6
                pivot_df['import_billion'] = pivot_df['import'] / 1e6
                pivot_df['trade_balance_billion'] = pivot_df['trade_balance'] / 1e6
                
                # Rename columns to match expected format
                pivot_df = pivot_df.rename(columns={
                    'export': 'export_value',
                    'import': 'import_value'
                })
                
                return pivot_df
    
    print("Could not prepare data in expected format")            
    return pd.DataFrame()

def get_top_products_and_partners(df, year=None, n=10):
    """Get the top products and trading partners for a given year"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    results = {
        'top_exports': pd.DataFrame(),
        'top_imports': pd.DataFrame(),
        'top_export_partners': pd.DataFrame(),
        'top_import_partners': pd.DataFrame()
    }

    try:
        # Filter for the specified year if provided
        if year and 'year' in df.columns:
            year_df = df[df['year'] == year]
        else:
            # Use the most recent year in the data
            if 'year' in df.columns:
                recent_year = df['year'].max()
                year_df = df[df['year'] == recent_year]
                print(f"Using most recent year: {recent_year}")
            else:
                year_df = df
        
        # Get top export products
        # Ensure 'product_name' exists before grouping
        if 'product_code' in year_df.columns and 'export_value' in year_df.columns and 'product_name' in year_df.columns:
            top_exports = year_df.groupby(['product_code', 'product_name'])['export_value'].sum().reset_index()
            top_exports = top_exports.sort_values('export_value', ascending=False).head(n)
            top_exports['export_billion'] = top_exports['export_value'] / 1e6
            # Ensure sum is not zero before calculating share
            total_top_export_value = top_exports['export_value'].sum()
            top_exports['share'] = (top_exports['export_value'] / total_top_export_value * 100) if total_top_export_value else 0
            results['top_exports'] = top_exports
        else:
            print("Warning: Could not calculate top export products. Missing columns: " + 
                  f"{'product_code ' if 'product_code' not in year_df.columns else ''}" +
                  f"{'product_name ' if 'product_name' not in year_df.columns else ''}" +
                  f"{'export_value' if 'export_value' not in year_df.columns else ''}")
            
        
        # Get top import products
        # Ensure 'product_name' exists before grouping
        if 'product_code' in year_df.columns and 'import_value' in year_df.columns and 'product_name' in year_df.columns:
            top_imports = year_df.groupby(['product_code', 'product_name'])['import_value'].sum().reset_index()
            top_imports = top_imports.sort_values('import_value', ascending=False).head(n)
            top_imports['import_billion'] = top_imports['import_value'] / 1e6
            # Ensure sum is not zero before calculating share
            total_top_import_value = top_imports['import_value'].sum()
            top_imports['share'] = (top_imports['import_value'] / total_top_import_value * 100) if total_top_import_value else 0
            results['top_imports'] = top_imports
        else:
             print("Warning: Could not calculate top import products. Missing columns: " + 
                  f"{'product_code ' if 'product_code' not in year_df.columns else ''}" +
                  f"{'product_name ' if 'product_name' not in year_df.columns else ''}" +
                  f"{'import_value' if 'import_value' not in year_df.columns else ''}")

        
        # Get top export partners
        # Ensure 'partner_name' exists before grouping
        if 'partner_code' in year_df.columns and 'export_value' in year_df.columns and 'partner_name' in year_df.columns:
             # Filter for exports only when grouping partners
            export_df = year_df[year_df['trade_type'] == 'export']
            top_export_partners = export_df.groupby(['partner_code', 'partner_name'])['export_value'].sum().reset_index()
            top_export_partners = top_export_partners.rename(columns={'partner_code': 'country_code', 'partner_name': 'country_name'})
            top_export_partners = top_export_partners.sort_values('export_value', ascending=False).head(n)
            top_export_partners['export_billion'] = top_export_partners['export_value'] / 1e6
            # Ensure sum is not zero before calculating share
            total_top_export_partner_value = top_export_partners['export_value'].sum()
            top_export_partners['share'] = (top_export_partners['export_value'] / total_top_export_partner_value * 100) if total_top_export_partner_value else 0
            results['top_export_partners'] = top_export_partners
        else:
            print("Warning: Could not calculate top export partners. Missing columns: " +
                  f"{'partner_code ' if 'partner_code' not in year_df.columns else ''}" +
                  f"{'country_name ' if 'country_name' not in year_df.columns else ''}" +
                  f"{'export_value' if 'export_value' not in year_df.columns else ''}")

        
        # Get top import partners
        # Ensure 'reporter_name' exists before grouping
        if 'reporter_code' in year_df.columns and 'import_value' in year_df.columns and 'reporter_name' in year_df.columns:
             # Filter for imports only when grouping partners
            import_df = year_df[year_df['trade_type'] == 'import']
            top_import_partners = import_df.groupby(['reporter_code', 'reporter_name'])['import_value'].sum().reset_index()
            top_import_partners = top_import_partners.rename(columns={'reporter_code': 'country_code', 'reporter_name': 'country_name'})
            top_import_partners = top_import_partners.sort_values('import_value', ascending=False).head(n)
            top_import_partners['import_billion'] = top_import_partners['import_value'] / 1e6
            # Ensure sum is not zero before calculating share
            total_top_import_partner_value = top_import_partners['import_value'].sum()
            top_import_partners['share'] = (top_import_partners['import_value'] / total_top_import_partner_value * 100) if total_top_import_partner_value else 0
            results['top_import_partners'] = top_import_partners
        else:
             print("Warning: Could not calculate top import partners. Missing columns: " +
                  f"{'reporter_code ' if 'reporter_code' not in year_df.columns else ''}" +
                  f"{'reporter_name ' if 'reporter_name' not in year_df.columns else ''}" +
                  f"{'import_value' if 'import_value' not in year_df.columns else ''}")

        
        return results # Return the dictionary
    except Exception as e:
        print(f"Error getting top products and partners: {e}")
        # Return the dictionary with empty DataFrames in case of error
        return results

def generate_plotly_figures(yearly_data, top_data):
    """Generate plotly figures for the report"""
    figures = []
    
    if yearly_data.empty:
        print("No yearly data available for generating figures")
        return figures
    
    # 1. Trade Overview (Exports, Imports, Balance)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=yearly_data['year'], y=yearly_data['export_billion'], 
                              mode='lines+markers', name='Exports', line=dict(color='#1f77b4')))
    fig1.add_trace(go.Scatter(x=yearly_data['year'], y=yearly_data['import_billion'], 
                              mode='lines+markers', name='Imports', line=dict(color='#ff7f0e')))
    fig1.add_trace(go.Scatter(x=yearly_data['year'], y=yearly_data['trade_balance_billion'], 
                              mode='lines+markers', name='Trade Balance', line=dict(color='#2ca02c')))
    
    # Add a horizontal line at y=0 for trade balance reference
    fig1.add_shape(type="line", x0=yearly_data['year'].min(), x1=yearly_data['year'].max(), 
                  y0=0, y1=0, line=dict(color="black", width=1, dash="dash"))
    
    fig1.update_layout(
        title='Bangladesh Trade Overview',
        xaxis_title='Year',
        yaxis_title='Billion USD',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white'
    )
    figures.append(fig1)
    
    # 2. Top Export Products (if available)
    top_exports_df = top_data.get('top_exports', pd.DataFrame()) # Safely get the DataFrame
    if not top_exports_df.empty and 'product_name' in top_exports_df.columns: # Check column exists
        fig2 = go.Figure(data=[go.Pie(
            labels=top_exports_df['product_name'],
            values=top_exports_df['export_value'],
            hole=0.3,
            textinfo='label+percent',
            insidetextorientation='radial'
        )])
        
        recent_year = yearly_data['year'].max()
        fig2.update_layout(
            title=f'Top Export Products ({recent_year})',
            template='plotly_white'
        )
        figures.append(fig2)
    
    # 3. Top Import Products (if available)
    top_imports_df = top_data.get('top_imports', pd.DataFrame()) # Safely get the DataFrame
    if not top_imports_df.empty and 'product_name' in top_imports_df.columns: # Check column exists
        fig3 = go.Figure(data=[go.Pie(
            labels=top_imports_df['product_name'],
            values=top_imports_df['import_value'],
            hole=0.3,
            textinfo='label+percent',
            insidetextorientation='radial'
        )])
        
        recent_year = yearly_data['year'].max()
        fig3.update_layout(
            title=f'Top Import Products ({recent_year})',
            template='plotly_white'
        )
        figures.append(fig3)
    
    # 4. Top Export Partners (if available)
    top_export_partners_df = top_data.get('top_export_partners', pd.DataFrame()) # Safely get the DataFrame
    if not top_export_partners_df.empty and 'country_name' in top_export_partners_df.columns: # Check column exists
        fig4 = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                          subplot_titles=('Top Export Partners', 'Top Import Partners'))
        
        fig4.add_trace(go.Pie(
            labels=top_export_partners_df['country_name'],
            values=top_export_partners_df['export_value'],
            textinfo='label+percent',
            name='Exports'
        ), 1, 1)
        
        fig4.add_trace(go.Pie(
            labels=top_data['top_import_partners']['country_name'],
            values=top_data['top_import_partners']['import_value'],
            textinfo='label+percent',
            name='Imports'
        ), 1, 2)
        
        recent_year = yearly_data['year'].max()
        fig4.update_layout(
            title=f'Top Trading Partners ({recent_year})',
            template='plotly_white'
        )
        figures.append(fig4)
    
    # 5. Trade Balance Trend
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=yearly_data['year'],
        y=yearly_data['trade_balance_billion'],
        marker_color=['red' if x < 0 else 'green' for x in yearly_data['trade_balance_billion']]
    ))
    
    fig5.update_layout(
        title='Bangladesh Trade Balance Trend',
        xaxis_title='Year',
        yaxis_title='Trade Balance (Billion USD)',
        template='plotly_white'
    )
    figures.append(fig5)
    
    return figures

def create_html_report(yearly_data, top_data, figures):
    """Create an HTML report with the trade data"""
    # Create HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bangladesh Trade Analysis Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }
            h1, h2, h3 {
                color: #2c3e50;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }
            .figure-container {
                margin-bottom: 40px;
            }
            .metrics-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin-bottom: 30px;
            }
            .metric-box {
                width: 23%;
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
                color: #3498db;
            }
            .metric-title {
                font-size: 14px;
                color: #7f8c8d;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 30px;
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .footer {
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #7f8c8d;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Bangladesh Trade Analysis Report</h1>
            <p>Report generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </div>
        
        <h2>Executive Summary</h2>
        <p>
            This report presents an analysis of Bangladesh's international trade data. The analysis captures
            trade flows, major export and import products, key trading partners, and trade balance trends.
        </p>
    """
    
    # Add key metrics if data is available
    if not yearly_data.empty:
        recent_data = yearly_data.iloc[-1]
        first_data = yearly_data.iloc[0]
        
        # Calculate growth rates if we have multiple years
        if len(yearly_data) > 1:
            years_diff = recent_data['year'] - first_data['year']
            if years_diff > 0:
                export_growth = ((recent_data['export_value'] / first_data['export_value']) ** (1 / years_diff) - 1) * 100
                import_growth = ((recent_data['import_value'] / first_data['import_value']) ** (1 / years_diff) - 1) * 100
            else:
                export_growth = 0
                import_growth = 0
        else:
            export_growth = 0
            import_growth = 0
        
        html_content += """
        <div class="metrics-container">
            <div class="metric-box">
                <div class="metric-title">Recent Year Exports</div>
                <div class="metric-value">$""" + f"{recent_data['export_billion']:.2f}B" + """</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Recent Year Imports</div>
                <div class="metric-value">$""" + f"{recent_data['import_billion']:.2f}B" + """</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Recent Year Trade Balance</div>
                <div class="metric-value">$""" + f"{recent_data['trade_balance_billion']:.2f}B" + """</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Avg Annual Export Growth</div>
                <div class="metric-value">""" + f"{export_growth:.1f}%" + """</div>
            </div>
        </div>
        """
    
    # Add figures
    html_content += """
        <h2>Trade Overview</h2>
    """
    
    for i, fig in enumerate(figures):
        # Convert the figure to HTML
        fig_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        html_content += f"""
        <div class="figure-container">
            {fig_html}
        </div>
        """
    
    # Add top export products table if available
    if not top_data['top_exports'].empty:
        html_content += """
        <h2>Top Export Products</h2>
        <table>
            <tr>
                <th>Product</th>
                <th>Value (Billion USD)</th>
                <th>Share (%)</th>
            </tr>
        """
        
        for _, row in top_data['top_exports'].iterrows():
            html_content += f"""
            <tr>
                <td>{row['product_name']}</td>
                <td>${row['export_billion']:.2f}B</td>
                <td>{row['share']:.1f}%</td>
            </tr>
            """
        
        html_content += """
        </table>
        """
    
    # Add top import products table if available
    if not top_data['top_imports'].empty:
        html_content += """
        <h2>Top Import Products</h2>
        <table>
            <tr>
                <th>Product</th>
                <th>Value (Billion USD)</th>
                <th>Share (%)</th>
            </tr>
        """
        
        for _, row in top_data['top_imports'].iterrows():
            html_content += f"""
            <tr>
                <td>{row['product_name']}</td>
                <td>${row['import_billion']:.2f}B</td>
                <td>{row['share']:.1f}%</td>
            </tr>
            """
        
        html_content += """
        </table>
        """
    
    # Add top trading partners tables if available
    if not top_data['top_export_partners'].empty:
        html_content += """
        <h2>Top Export Partners</h2>
        <table>
            <tr>
                <th>Country</th>
                <th>Value (Billion USD)</th>
                <th>Share (%)</th>
            </tr>
        """
        
        for _, row in top_data['top_export_partners'].iterrows():
            html_content += f"""
            <tr>
                <td>{row['country_name']}</td>
                <td>${row['export_billion']:.2f}B</td>
                <td>{row['share']:.1f}%</td>
            </tr>
            """
        
        html_content += """
        </table>
        """
    
    if not top_data['top_import_partners'].empty:
        html_content += """
        <h2>Top Import Partners</h2>
        <table>
            <tr>
                <th>Country</th>
                <th>Value (Billion USD)</th>
                <th>Share (%)</th>
            </tr>
        """
        
        for _, row in top_data['top_import_partners'].iterrows():
            html_content += f"""
            <tr>
                <td>{row['country_name']}</td>
                <td>${row['import_billion']:.2f}B</td>
                <td>{row['share']:.1f}%</td>
            </tr>
            """
        
        html_content += """
        </table>
        """
    
    # Add conclusions
    html_content += """
        <h2>Key Findings</h2>
        <ul>
    """
    
    if not yearly_data.empty:
        recent_year = yearly_data['year'].max()
        first_year = yearly_data['year'].min()
        
        recent_data = yearly_data[yearly_data['year'] == recent_year].iloc[0]
        first_data = yearly_data[yearly_data['year'] == first_year].iloc[0]
        
        trade_balance_status = "deficit" if recent_data['trade_balance'] < 0 else "surplus"
        trade_balance_trend = ""
        
        if len(yearly_data) > 5:
            recent_5yr = yearly_data.tail(5)
            if (recent_5yr['trade_balance'] < 0).all():
                trade_balance_trend = "consistent trade deficit"
            elif (recent_5yr['trade_balance'] > 0).all():
                trade_balance_trend = "consistent trade surplus"
            elif recent_5yr['trade_balance'].iloc[-1] > recent_5yr['trade_balance'].iloc[0]:
                trade_balance_trend = "improving trade balance"
            else:
                trade_balance_trend = "worsening trade balance"
        
        html_content += f"""
            <li>Bangladesh's exports grew from ${first_data['export_billion']:.2f} billion in {int(first_year)} to ${recent_data['export_billion']:.2f} billion in {int(recent_year)}.</li>
            <li>The country has a trade {trade_balance_status} of ${abs(recent_data['trade_balance_billion']):.2f} billion in {int(recent_year)}.</li>
        """
        
        if trade_balance_trend:
            html_content += f"<li>The data shows a {trade_balance_trend} in recent years.</li>"
    
    # Add product-specific findings if available
    if not top_data['top_exports'].empty:
        top_product = top_data['top_exports'].iloc[0]
        html_content += f"""
            <li>The largest export product is {top_product['product_name']}, accounting for {top_product['share']:.1f}% of total exports.</li>
        """
    
    # Add partner-specific findings if available
    if not top_data['top_export_partners'].empty:
        top_partner = top_data['top_export_partners'].iloc[0]
        html_content += f"""
            <li>The largest export market is {top_partner['country_name']}, accounting for {top_partner['share']:.1f}% of total exports.</li>
        """
    
    html_content += """
        </ul>
        
        <h2>Policy Implications</h2>
        <p>
            Based on the analysis of trade data, the following policy recommendations can be considered:
        </p>
        <ul>
            <li>Continue to focus on export diversification to reduce dependency on a limited number of products and markets.</li>
            <li>Invest in logistics infrastructure to improve trade facilitation and reduce costs.</li>
            <li>Develop strategic trade agreements to expand market access and improve terms of trade.</li>
            <li>Enhance competitiveness through technology adoption, skill development, and quality improvements.</li>
            <li>Strengthen backward linkages to reduce import dependency for export production.</li>
        </ul>
        
        <div class="footer">
            <p>Bangladesh Trade Analysis Report</p>
            <p>© 2023 All Rights Reserved</p>
        </div>
    </body>
    </html>
    """
    
    # Write HTML report to file
    os.makedirs('reports', exist_ok=True)
    output_file = f"reports/bangladesh_trade_analysis_report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {output_file}")
    return output_file

def main():
    """Main function to load data, generate report, and open it"""
    print("Generating Bangladesh Trade Analysis Report")
    trade_data = load_trade_data()
    
    if not trade_data.empty:
        yearly_data = prepare_data_for_report(trade_data)
        
        # Use the most recent year for top products/partners
        recent_year = trade_data['year'].max() if 'year' in trade_data.columns else None
        
        top_data = get_top_products_and_partners(trade_data, year=recent_year)
        
        if not yearly_data.empty:
            figures = generate_plotly_figures(yearly_data, top_data)
            report_file = create_html_report(yearly_data, top_data, figures)
            
            # Try to open the report in a web browser
            print("Attempting to open the report in your web browser...")
            try:
                import webbrowser # Import locally to avoid error if not used elsewhere
                webbrowser.open('file://' + os.path.abspath(report_file))
            except Exception as e:
                print(f"Error opening report in browser: {e}")
                print(f"Please open the report manually: {report_file}")
        else:
            print("No yearly data processed to generate report.")
    else:
        print("Could not load trade data.")

if __name__ == "__main__":
    main() 