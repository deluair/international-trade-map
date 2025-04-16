"""
Utility functions for generating plots of simulation results.
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec


def create_dataframe_from_results(results):
    """
    Create a pandas DataFrame from simulation results.
    
    Args:
        results (dict): Simulation results dictionary
        
    Returns:
        pd.DataFrame: DataFrame with simulation results
    """
    # Extract metadata
    scenario = results['metadata']['scenario']
    # --- Start Modification: Infer start/end year from data keys ---
    # start_year = results['metadata']['start_year']
    # end_year = results['metadata']['end_year']
    years_in_data = [int(y) for y in results['yearly_data'].keys()]
    if not years_in_data:
        print("Warning: No years found in yearly_data keys.")
        return pd.DataFrame() # Return empty DataFrame if no years
    start_year = min(years_in_data)
    end_year = max(years_in_data)
    # --- End Modification ---
    
    # Create DataFrame
    yearly_data = []
    
    for year, year_data in results['yearly_data'].items():
        year = int(year)
        
        # Extract key metrics for this year - using .get() for top-level keys
        # Get nested dictionaries safely
        investment_data = year_data.get('investment', {})
        export_data = year_data.get('export', {})
        import_data = year_data.get('import', {})
        agg_metrics_data = year_data.get('aggregate_metrics', {})
        exchange_rate_data = year_data.get('exchange_rate', {})
        structural_data = year_data.get('structural_transformation', {}) # Added for projection data

        row = {
            'Year': year,
            'Scenario': scenario,
            'GDP (billion USD)': investment_data.get('gdp', pd.NA), # Use pd.NA for missing numeric
            'Total Exports (billion USD)': export_data.get('total_exports', structural_data.get('total_exports', pd.NA)), # Try structural if export missing
            'Total Imports (billion USD)': import_data.get('total_imports', pd.NA),
            'Trade Balance (billion USD)': agg_metrics_data.get('trade_balance', pd.NA),
            'Trade Openness (%)': agg_metrics_data.get('trade_openness', pd.NA) * 100 if pd.notna(agg_metrics_data.get('trade_openness')) else pd.NA,
            'Export to GDP (%)': agg_metrics_data.get('export_to_gdp', pd.NA) * 100 if pd.notna(agg_metrics_data.get('export_to_gdp')) else pd.NA,
            'Import to GDP (%)': agg_metrics_data.get('import_to_gdp', pd.NA) * 100 if pd.notna(agg_metrics_data.get('import_to_gdp')) else pd.NA,
            'Exchange Rate (BDT/USD)': exchange_rate_data.get('exchange_rate', pd.NA),
            # Add metrics from structural_transformation if present
            'Export Diversification HHI': structural_data.get('export_diversity_hhi', pd.NA),
            'Capability Index': structural_data.get('capability_index', pd.NA),
            'Industrial Policy Effectiveness': structural_data.get('industrial_policy_effectiveness', pd.NA),
        }
        
        # Add sector-specific exports if available (prefer structural, fallback to export)
        sector_source = structural_data.get('export_sectors', export_data.get('sector_data', {}))
        if sector_source: # Check if sector_source is not empty
             total_exports_for_share = row['Total Exports (billion USD)']
             # Convert sector data (which might be millions or billions) appropriately
             # NOTE: This assumes structural sectors are in billions, export->sector_data are in millions
             is_structural = 'export_sectors' in structural_data
             divisor = 1 if is_structural else 1000 # convert millions to billions if from export->sector_data
             
             for sector, sector_value in sector_source.items():
                 # Handle cases where sector_value might be a dictionary (from older format?)
                 if isinstance(sector_value, dict):
                     volume = sector_value.get('export_volume', 0)
                 else:
                     volume = sector_value # Assume direct value (billions if structural)
                 
                 # Store volume in billions
                 volume_billion = volume / divisor
                 row[f'{sector.replace("_", " ").title()} Exports (billion USD)'] = volume_billion
                 
                 # Calculate share if total exports is valid
                 if pd.notna(total_exports_for_share) and total_exports_for_share > 0:
                     row[f'{sector.replace("_", " ").title()} Share (%)'] = (volume_billion / total_exports_for_share) * 100
                 else:
                     row[f'{sector.replace("_", " ").title()} Share (%)'] = 0

        
        yearly_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(yearly_data)
    
    return df


def plot_simulation_results(results, save_path=None):
    """
    Generate plots of simulation results.
    
    Args:
        results (dict): Simulation results dictionary
        save_path (str, optional): Path to save the plots
        
    Returns:
        bool: True if plots were successfully generated
    """
    # Convert results to DataFrame
    df = create_dataframe_from_results(results)
    
    if df.empty:
        print("No data to plot")
        return False
    
    # Create PDF to save all plots
    if save_path:
        pdf = PdfPages(save_path)
    
    # Set consistent colors and styles
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    color_main = '#1f77b4'  # Blue
    color_second = '#ff7f0e'  # Orange
    color_third = '#2ca02c'  # Green
    
    # Extract metadata
    scenario = results['metadata']['scenario']
    start_year = results['metadata']['start_year']
    end_year = results['metadata']['end_year']
    
    # 1. Trade Overview (Exports, Imports, Balance)
    fig1, ax1 = plt.subplots()
    ax1.plot(df['Year'], df['Total Exports (billion USD)'], marker='o', color=color_main, label='Exports')
    ax1.plot(df['Year'], df['Total Imports (billion USD)'], marker='s', color=color_second, label='Imports')
    ax1.plot(df['Year'], df['Trade Balance (billion USD)'], marker='^', color=color_third, label='Trade Balance')
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    
    ax1.set_title(f'Bangladesh Trade Overview ({start_year}-{end_year}) - {scenario} Scenario')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Billion USD')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Add text annotations for start and end points
    for col in ['Total Exports (billion USD)', 'Total Imports (billion USD)', 'Trade Balance (billion USD)']:
        start_val = df.loc[df['Year'] == start_year, col].values[0]
        end_val = df.loc[df['Year'] == end_year, col].values[0]
        growth = ((end_val - start_val) / start_val) * 100 if start_val != 0 else 0
        
        ax1.annotate(f'{end_val:.1f}B\n({growth:.1f}%)', 
                    xy=(end_year, end_val),
                    xytext=(10, 0),
                    textcoords='offset points',
                    fontsize=8)
    
    if save_path:
        pdf.savefig(fig1)
    
    # 2. Export Composition (Stacked Area Chart)
    export_columns = [col for col in df.columns if 'Exports (billion USD)' in col]
    
    if export_columns:
        fig2, ax2 = plt.subplots()
        
        # Convert from billion to million for consistency
        export_data = df[export_columns].copy() * 1000
        
        # Create stacked area chart
        ax2.stackplot(df['Year'], 
                     [export_data[col] for col in export_columns],
                     labels=[col.split(' Exports')[0] for col in export_columns],
                     alpha=0.7)
        
        ax2.set_title(f'Bangladesh Export Composition ({start_year}-{end_year}) - {scenario} Scenario')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Million USD')
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper left')
        
        if save_path:
            pdf.savefig(fig2)
    
    # 3. Trade Indicators (Trade Openness, Export/Import to GDP)
    fig3, ax3 = plt.subplots()
    ax3.plot(df['Year'], df['Trade Openness (%)'], marker='o', color=color_main, label='Trade Openness')
    ax3.plot(df['Year'], df['Export to GDP (%)'], marker='s', color=color_second, label='Export to GDP')
    ax3.plot(df['Year'], df['Import to GDP (%)'], marker='^', color=color_third, label='Import to GDP')
    
    ax3.set_title(f'Bangladesh Trade Indicators ({start_year}-{end_year}) - {scenario} Scenario')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Percentage (%)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    if save_path:
        pdf.savefig(fig3)
    
    # 4. Combined Dashboard (2x2 grid)
    fig4 = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 2, figure=fig4)
    
    # 4.1 Trade Balance
    ax4_1 = fig4.add_subplot(gs[0, 0])
    ax4_1.plot(df['Year'], df['Trade Balance (billion USD)'], marker='o', color=color_main)
    ax4_1.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    ax4_1.set_title('Trade Balance')
    ax4_1.set_xlabel('Year')
    ax4_1.set_ylabel('Billion USD')
    ax4_1.grid(True, alpha=0.3)
    
    # 4.2 Exchange Rate
    ax4_2 = fig4.add_subplot(gs[0, 1])
    ax4_2.plot(df['Year'], df['Exchange Rate (BDT/USD)'], marker='s', color=color_second)
    ax4_2.set_title('Exchange Rate (BDT/USD)')
    ax4_2.set_xlabel('Year')
    ax4_2.set_ylabel('BDT per USD')
    ax4_2.grid(True, alpha=0.3)
    
    # 4.3 Export Composition (Pie Chart for final year)
    ax4_3 = fig4.add_subplot(gs[1, 0])
    if export_columns:
        final_year_data = df[df['Year'] == end_year][export_columns].iloc[0]
        ax4_3.pie(final_year_data, 
                 labels=[col.split(' Exports')[0] for col in export_columns],
                 autopct='%1.1f%%',
                 startangle=90)
        ax4_3.set_title(f'Export Composition in {end_year}')
    
    # 4.4 Trade Openness
    ax4_4 = fig4.add_subplot(gs[1, 1])
    ax4_4.plot(df['Year'], df['Trade Openness (%)'], marker='^', color=color_third)
    ax4_4.set_title('Trade Openness')
    ax4_4.set_xlabel('Year')
    ax4_4.set_ylabel('Percentage (%)')
    ax4_4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    fig4.suptitle(f'Bangladesh Trade Dynamics ({start_year}-{end_year}) - {scenario} Scenario', fontsize=16, y=1.02)
    
    if save_path:
        pdf.savefig(fig4)
        pdf.close()
        print(f"Plots saved to {save_path}")
    else:
        plt.show()
    
    return True


def plot_scenario_comparison(scenarios_data, metrics=None, save_path=None):
    """
    Generate comparison plots for multiple scenarios.
    
    Args:
        scenarios_data (dict): Dictionary with scenarios as keys and result DataFrames as values
        metrics (list, optional): List of metrics to compare
        save_path (str, optional): Path to save the plots
        
    Returns:
        bool: True if plots were successfully generated
    """
    if not scenarios_data:
        print("No scenario data to plot")
        return False
    
    # Set default metrics if not provided
    if metrics is None:
        metrics = [
            'Total Exports (billion USD)',
            'Total Imports (billion USD)',
            'Trade Balance (billion USD)',
            'Trade Openness (%)'
        ]
    
    # Create PDF to save all plots
    if save_path:
        pdf = PdfPages(save_path)
    
    # Set consistent colors and styles
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    
    # Scenario colors
    colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios_data)))
    
    # Plot each metric
    for metric in metrics:
        fig, ax = plt.subplots()
        
        for i, (scenario, df) in enumerate(scenarios_data.items()):
            if metric in df.columns:
                # --- Start Modification: Handle NA/NaN before plotting ---
                plot_df = df[['Year', metric]].copy()
                # Convert metric column to numeric, coercing errors to NaN
                plot_df[metric] = pd.to_numeric(plot_df[metric], errors='coerce')
                # Drop rows where the metric is NaN for line plotting
                plot_df = plot_df.dropna(subset=[metric])
                if not plot_df.empty:
                    ax.plot(plot_df['Year'], plot_df[metric], marker='o', color=colors[i], label=scenario)
                # --- End Modification ---
        
        ax.set_title(f'Comparison of {metric} Across Scenarios')
        ax.set_xlabel('Year')
        ax.set_ylabel(metric)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        if save_path:
            pdf.savefig(fig)
    
    # Create radar chart for final year comparison
    if scenarios_data and all(len(df) > 0 for df in scenarios_data.values()):
        # Get the final year
        sample_df = next(iter(scenarios_data.values()))
        final_year = sample_df['Year'].max()
        
        # Prepare data for radar chart
        radar_metrics = [m for m in metrics if 'Balance' not in m]  # Exclude balance which can be negative
        
        if radar_metrics:
            fig = plt.figure(figsize=(10, 10))
            ax = fig.add_subplot(111, polar=True)
            
            # Number of variables
            N = len(radar_metrics)
            
            # Angle of each axis
            angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
            angles += angles[:1]  # Close the loop
            
            # Add axes and labels
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            plt.xticks(angles[:-1], radar_metrics)
            
            # Draw the chart for each scenario
            for i, (scenario, df) in enumerate(scenarios_data.items()):
                final_year_data = df[df['Year'] == final_year][radar_metrics].iloc[0]
                
                # --- Start Modification: Handle NA/NaN before normalizing ---
                # Replace NA/NaN with 0 for normalization/radar plot
                max_values = {}
                for m in radar_metrics:
                     # Calculate max only from valid numeric data across scenarios
                     valid_data = [s_df[s_df['Year'] == final_year][m].pipe(pd.to_numeric, errors='coerce').max()
                                   for s_df in scenarios_data.values() if m in s_df.columns]
                     max_values[m] = max([v for v in valid_data if pd.notna(v)], default=1) # default=1 prevents division by zero
                
                normalized_values = []
                for m in radar_metrics:
                    metric_val = pd.to_numeric(final_year_data.get(m), errors='coerce') # Ensure numeric
                    metric_val = 0 if pd.isna(metric_val) else metric_val # Replace NaN with 0
                    max_val = max_values.get(m, 1) # Default to 1 if metric somehow missing from max_values
                    normalized_values.append(metric_val / max_val if max_val > 0 else 0)
                # --- End Modification ---
                
                normalized_values += normalized_values[:1]  # Close the loop
                
                ax.plot(angles, normalized_values, color=colors[i], linewidth=2, label=scenario)
                ax.fill(angles, normalized_values, color=colors[i], alpha=0.25)
            
            ax.set_title(f'Scenario Comparison in {final_year} (Normalized Values)')
            ax.legend(loc='upper right')
            
            if save_path:
                pdf.savefig(fig)
    
    # Final comparison dashboard
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 2, figure=fig)
    
    # Export growth rates
    ax1 = fig.add_subplot(gs[0, 0])
    for i, (scenario, df) in enumerate(scenarios_data.items()):
        # --- Start Modification: Handle NA/NaN before calculating index ---
        if 'Total Exports (billion USD)' in df.columns:
            plot_df = df[['Year', 'Total Exports (billion USD)']].copy()
            plot_df['Total Exports (billion USD)'] = pd.to_numeric(plot_df['Total Exports (billion USD)'], errors='coerce')
            plot_df = plot_df.dropna(subset=['Total Exports (billion USD)'])
            if not plot_df.empty:
                start_year_val = plot_df['Year'].min()
                start_exports = plot_df[plot_df['Year'] == start_year_val]['Total Exports (billion USD)'].values[0]
                if start_exports > 0:
                     plot_df['Export Growth Index'] = plot_df['Total Exports (billion USD)'] / start_exports * 100
                     ax1.plot(plot_df['Year'], plot_df['Export Growth Index'], marker='o', color=colors[i], label=scenario)
        # --- End Modification ---
    
    ax1.set_title('Export Growth Index (Base Year = 100)')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Index Value')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Trade balance comparison
    ax2 = fig.add_subplot(gs[0, 1])
    for i, (scenario, df) in enumerate(scenarios_data.items()):
        # --- Start Modification: Handle NA/NaN before plotting ---
        if 'Trade Balance (billion USD)' in df.columns:
            plot_df = df[['Year', 'Trade Balance (billion USD)']].copy()
            plot_df['Trade Balance (billion USD)'] = pd.to_numeric(plot_df['Trade Balance (billion USD)'], errors='coerce')
            plot_df = plot_df.dropna(subset=['Trade Balance (billion USD)'])
            if not plot_df.empty:
                ax2.plot(plot_df['Year'], plot_df['Trade Balance (billion USD)'], marker='s', color=colors[i], label=scenario)
        # --- End Modification ---
    
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.3)
    ax2.set_title('Trade Balance Comparison')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Billion USD')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Final year export comparison (bar chart)
    ax3 = fig.add_subplot(gs[1, 0])
    
    if scenarios_data:
        # --- Start Modification: Handle NA/NaN before plotting ---
        final_year_exports = {}
        for scenario, df in scenarios_data.items():
             if 'Total Exports (billion USD)' in df.columns and not df.empty:
                 final_year = df['Year'].max()
                 export_val = df[df['Year'] == final_year]['Total Exports (billion USD)'].pipe(pd.to_numeric, errors='coerce').iloc[0]
                 final_year_exports[scenario] = 0 if pd.isna(export_val) else export_val
             else:
                 final_year_exports[scenario] = 0 # Default to 0 if column missing or df empty
        # --- End Modification ---
                 
        scenarios_list = list(final_year_exports.keys())
        exports_list = list(final_year_exports.values())
        
        ax3.bar(scenarios_list, exports_list, color=colors[:len(scenarios_list)])
        ax3.set_title(f'Total Exports in {final_year}')
        ax3.set_xlabel('Scenario')
        ax3.set_ylabel('Billion USD')
        ax3.grid(True, alpha=0.3, axis='y')
    
    # Trade openness comparison
    ax4 = fig.add_subplot(gs[1, 1])
    for i, (scenario, df) in enumerate(scenarios_data.items()):
         # --- Start Modification: Handle NA/NaN before plotting ---
         if 'Trade Openness (%)' in df.columns:
            plot_df = df[['Year', 'Trade Openness (%)']].copy()
            plot_df['Trade Openness (%)'] = pd.to_numeric(plot_df['Trade Openness (%)'], errors='coerce')
            plot_df = plot_df.dropna(subset=['Trade Openness (%)'])
            if not plot_df.empty:
                ax4.plot(plot_df['Year'], plot_df['Trade Openness (%)'], marker='^', color=colors[i], label=scenario)
         # --- End Modification ---
    
    ax4.set_title('Trade Openness Comparison')
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Percentage (%)')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    fig.suptitle('Scenario Comparison - Bangladesh Trade Dynamics', fontsize=16, y=1.02)
    
    if save_path:
        pdf.savefig(fig)
        pdf.close()
        print(f"Comparison plots saved to {save_path}")
    else:
        plt.show()
    
    return True


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        result_file = sys.argv[1]
        with open(result_file, 'r') as f:
            results = json.load(f)
        
        output_file = result_file.replace('.json', '_plots.pdf')
        plot_simulation_results(results, save_path=output_file) 