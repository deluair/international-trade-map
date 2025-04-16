import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter

class TradeVisualization:
    """
    Visualization tools for the Bangladesh Trade Simulation results.
    Creates various plots, charts, and reports from simulation data.
    """
    
    def __init__(self, results_path=None, simulation_engine=None):
        """
        Initialize the visualization module with either a results file path or a simulation engine.
        
        Args:
            results_path (str, optional): Path to a simulation results JSON file
            simulation_engine (TradeSimulationEngine, optional): A simulation engine instance with results
        """
        self.data = None
        
        if simulation_engine:
            self.data = simulation_engine.results
            self.scenario = simulation_engine.scenario
        elif results_path:
            with open(results_path, 'r') as f:
                self.data = json.load(f)
            self.scenario = self.data['metadata']['scenario']
        else:
            raise ValueError("Either results_path or simulation_engine must be provided")
        
        # Set plot style
        sns.set_style("whitegrid")
        self.colors = sns.color_palette("viridis", 10)
    
    def create_summary_dataframe(self):
        """
        Create a Pandas DataFrame with key metrics from all simulation years.
        
        Returns:
            pd.DataFrame: DataFrame with time series data
        """
        yearly_data = self.data['yearly_data']
        years = sorted([int(year) for year in yearly_data.keys()])
        
        # Initialize DataFrame
        df = pd.DataFrame({'Year': years})
        
        # Extract key metrics
        df['GDP'] = [yearly_data[str(year)]['investment']['gdp'] for year in years]
        df['Total_Exports'] = [yearly_data[str(year)]['export']['total_exports'] for year in years]
        df['Total_Imports'] = [yearly_data[str(year)]['import']['total_imports'] for year in years]
        df['Trade_Balance'] = df['Total_Exports'] - df['Total_Imports']
        df['Trade_to_GDP'] = (df['Total_Exports'] + df['Total_Imports']) / df['GDP']
        
        # Extract export sectors if available
        if 'sector_exports' in yearly_data[str(years[0])]['export']:
            sectors = yearly_data[str(years[0])]['export']['sector_exports'].keys()
            for sector in sectors:
                df[f'Export_{sector}'] = [yearly_data[str(year)]['export']['sector_exports'].get(sector, 0) for year in years]
        
        # Calculate growth rates
        df['GDP_Growth'] = df['GDP'].pct_change() * 100
        df['Export_Growth'] = df['Total_Exports'].pct_change() * 100
        df['Import_Growth'] = df['Total_Imports'].pct_change() * 100
        
        return df
    
    def plot_macro_trends(self, save_path=None):
        """
        Plot key macroeconomic trends from the simulation.
        
        Args:
            save_path (str, optional): Directory to save plots
        """
        df = self.create_summary_dataframe()
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Bangladesh Trade Simulation: Macroeconomic Trends ({self.scenario} scenario)', 
                    fontsize=16, y=0.98)
        
        # GDP and Growth Rate
        ax1 = axes[0, 0]
        ax1b = ax1.twinx()
        ax1.plot(df['Year'], df['GDP'], color=self.colors[0], linewidth=2.5)
        ax1b.plot(df['Year'], df['GDP_Growth'], color=self.colors[1], linewidth=2, linestyle='--')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('GDP (Billion USD)', color=self.colors[0])
        ax1b.set_ylabel('GDP Growth (%)', color=self.colors[1])
        ax1.grid(True, alpha=0.3)
        ax1.set_title('GDP and Growth Rate')
        
        # Trade Balance
        ax2 = axes[0, 1]
        ax2.plot(df['Year'], df['Trade_Balance'], color=self.colors[2], linewidth=2.5)
        ax2.axhline(y=0, color='red', linestyle='-', alpha=0.3)
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Billion USD')
        ax2.grid(True, alpha=0.3)
        ax2.set_title('Trade Balance')
        
        # Exports and Imports
        ax3 = axes[1, 0]
        ax3.plot(df['Year'], df['Total_Exports'], color=self.colors[3], linewidth=2.5, label='Exports')
        ax3.plot(df['Year'], df['Total_Imports'], color=self.colors[4], linewidth=2.5, label='Imports')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Billion USD')
        ax3.grid(True, alpha=0.3)
        ax3.legend()
        ax3.set_title('Total Exports and Imports')
        
        # Trade to GDP Ratio
        ax4 = axes[1, 1]
        ax4.plot(df['Year'], df['Trade_to_GDP'] * 100, color=self.colors[5], linewidth=2.5)
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Percent of GDP')
        ax4.grid(True, alpha=0.3)
        ax4.set_title('Trade Openness (Trade to GDP Ratio)')
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            plt.savefig(os.path.join(save_path, f'macro_trends_{self.scenario}.png'), dpi=300)
        else:
            plt.show()
    
    def plot_export_composition(self, years=None, save_path=None):
        """
        Plot export composition for selected years.
        
        Args:
            years (list, optional): Specific years to plot
            save_path (str, optional): Directory to save plots
        """
        df = self.create_summary_dataframe()
        
        # Find export sector columns
        export_columns = [col for col in df.columns if col.startswith('Export_') and col != 'Export_Growth']
        
        if not export_columns:
            print("No export sector data available")
            return
        
        # Select years to display
        if years is None:
            # Choose initial, middle and final year
            start_year = df['Year'].min()
            end_year = df['Year'].max()
            mid_year = start_year + (end_year - start_year) // 2
            years = [start_year, mid_year, end_year]
        
        # Create figure
        fig, axes = plt.subplots(1, len(years), figsize=(5*len(years), 6))
        if len(years) == 1:
            axes = [axes]  # Make it iterable for a single year
            
        fig.suptitle(f'Bangladesh Export Composition Evolution ({self.scenario} scenario)', fontsize=16, y=0.98)
        
        # Generate pie chart for each year
        for i, year in enumerate(years):
            year_data = df[df['Year'] == year]
            
            if year_data.empty:
                print(f"No data for year {year}")
                continue
                
            # Extract sector values for the year
            values = year_data[export_columns].values[0]
            labels = [col.replace('Export_', '') for col in export_columns]
            
            # Create pie chart
            axes[i].pie(values, labels=None, autopct='%1.1f%%', startangle=90, colors=self.colors)
            axes[i].axis('equal')
            axes[i].set_title(f'Year {year}')
            
        # Add a single legend
        plt.legend(labels, loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            plt.savefig(os.path.join(save_path, f'export_composition_{self.scenario}.png'), dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def plot_sector_growth(self, save_path=None):
        """
        Plot growth trajectories of different export sectors.
        
        Args:
            save_path (str, optional): Directory to save plots
        """
        df = self.create_summary_dataframe()
        
        # Find export sector columns
        export_columns = [col for col in df.columns if col.startswith('Export_') and col != 'Export_Growth']
        
        if not export_columns:
            print("No export sector data available")
            return
        
        plt.figure(figsize=(12, 8))
        
        for i, col in enumerate(export_columns):
            sector_name = col.replace('Export_', '')
            plt.plot(df['Year'], df[col], label=sector_name, color=self.colors[i % len(self.colors)], linewidth=2.5)
        
        plt.title(f'Export Sector Growth ({self.scenario} scenario)', fontsize=14)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Export Value (Billion USD)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            plt.savefig(os.path.join(save_path, f'sector_growth_{self.scenario}.png'), dpi=300)
        else:
            plt.show()
    
    def generate_comparative_heatmap(self, other_results=None, metric='Total_Exports', save_path=None):
        """
        Generate heatmap comparing this scenario with others.
        
        Args:
            other_results (list): List of other visualization objects
            metric (str): Metric to compare
            save_path (str, optional): Directory to save plots
        """
        if not other_results:
            print("No other scenarios provided for comparison")
            return
        
        # Get data for this scenario
        this_df = self.create_summary_dataframe()
        scenarios = [self.scenario]
        
        # Collect data from all scenarios
        all_dfs = [this_df]
        for other in other_results:
            other_df = other.create_summary_dataframe()
            all_dfs.append(other_df)
            scenarios.append(other.scenario)
        
        # Create comparison dataframe
        years = sorted(this_df['Year'].unique())
        comparison_data = np.zeros((len(scenarios), len(years)))
        
        for i, df in enumerate(all_dfs):
            for j, year in enumerate(years):
                year_data = df[df['Year'] == year]
                if not year_data.empty and metric in year_data.columns:
                    comparison_data[i, j] = year_data[metric].values[0]
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(comparison_data, cmap='viridis', annot=True, fmt='.1f',
                   xticklabels=years, yticklabels=scenarios)
        plt.title(f'Scenario Comparison: {metric}', fontsize=14)
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Scenario', fontsize=12)
        
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            plt.savefig(os.path.join(save_path, f'comparison_{metric}.png'), dpi=300)
        else:
            plt.show()
    
    def generate_html_report(self, output_path):
        """
        Generate an HTML report with key findings and visualizations.
        
        Args:
            output_path (str): Path to save the HTML report
        """
        df = self.create_summary_dataframe()
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate plots and save them in a temp directory
        plot_dir = os.path.join(os.path.dirname(output_path), 'plots')
        os.makedirs(plot_dir, exist_ok=True)
        
        self.plot_macro_trends(save_path=plot_dir)
        self.plot_export_composition(save_path=plot_dir)
        self.plot_sector_growth(save_path=plot_dir)
        
        # Calculate key statistics
        start_year = df['Year'].min()
        end_year = df['Year'].max()
        initial_gdp = df[df['Year'] == start_year]['GDP'].values[0]
        final_gdp = df[df['Year'] == end_year]['GDP'].values[0]
        gdp_growth = (final_gdp / initial_gdp - 1) * 100
        
        initial_exports = df[df['Year'] == start_year]['Total_Exports'].values[0]
        final_exports = df[df['Year'] == end_year]['Total_Exports'].values[0]
        export_growth = (final_exports / initial_exports - 1) * 100
        
        avg_trade_balance = df['Trade_Balance'].mean()
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bangladesh Trade Simulation Report: {self.scenario} Scenario</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .visualization {{ margin: 20px 0; text-align: center; }}
                .visualization img {{ max-width: 100%; height: auto; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Bangladesh Trade Simulation Report</h1>
                <p><strong>Scenario:</strong> {self.scenario}</p>
                <p><strong>Simulation Period:</strong> {start_year} to {end_year}</p>
                
                <div class="summary">
                    <h2>Executive Summary</h2>
                    <p>This report presents the results of a comprehensive simulation of Bangladesh's trade dynamics 
                    from {start_year} to {end_year} under the "{self.scenario}" scenario.</p>
                    
                    <h3>Key Findings:</h3>
                    <ul>
                        <li>GDP grew from ${initial_gdp:.2f} billion to ${final_gdp:.2f} billion, a {gdp_growth:.1f}% increase over the period.</li>
                        <li>Exports grew from ${initial_exports:.2f} billion to ${final_exports:.2f} billion, a {export_growth:.1f}% increase.</li>
                        <li>The average trade balance was ${avg_trade_balance:.2f} billion.</li>
                    </ul>
                </div>
                
                <h2>Macroeconomic Trends</h2>
                <div class="visualization">
                    <img src="plots/macro_trends_{self.scenario}.png" alt="Macroeconomic Trends">
                </div>
                
                <h2>Export Composition Evolution</h2>
                <div class="visualization">
                    <img src="plots/export_composition_{self.scenario}.png" alt="Export Composition">
                </div>
                
                <h2>Export Sector Growth</h2>
                <div class="visualization">
                    <img src="plots/sector_growth_{self.scenario}.png" alt="Sector Growth">
                </div>
                
                <h2>Detailed Metrics</h2>
                <table>
                    <tr>
                        <th>Year</th>
                        <th>GDP (B$)</th>
                        <th>Exports (B$)</th>
                        <th>Imports (B$)</th>
                        <th>Trade Balance (B$)</th>
                        <th>Trade/GDP (%)</th>
                    </tr>
        """
        
        # Add table rows for each 5-year interval
        for year in range(start_year, end_year + 1, 5):
            year_data = df[df['Year'] == year]
            if not year_data.empty:
                html_content += f"""
                    <tr>
                        <td>{year}</td>
                        <td>{year_data['GDP'].values[0]:.2f}</td>
                        <td>{year_data['Total_Exports'].values[0]:.2f}</td>
                        <td>{year_data['Total_Imports'].values[0]:.2f}</td>
                        <td>{year_data['Trade_Balance'].values[0]:.2f}</td>
                        <td>{year_data['Trade_to_GDP'].values[0] * 100:.1f}%</td>
                    </tr>
                """
        
        # Close HTML
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report generated at {output_path}")


def compare_scenarios(scenario_results, metrics=None, output_dir=None):
    """
    Compare multiple simulation scenarios and generate comparative visualizations.
    
    Args:
        scenario_results (list): List of paths to result files or TradeVisualization objects
        metrics (list, optional): Metrics to compare
        output_dir (str, optional): Directory to save output visualizations
    """
    if metrics is None:
        metrics = ['GDP', 'Total_Exports', 'Trade_Balance', 'Trade_to_GDP']
    
    # Convert paths to visualization objects if needed
    visualizations = []
    for result in scenario_results:
        if isinstance(result, str):
            visualizations.append(TradeVisualization(results_path=result))
        else:
            visualizations.append(result)
    
    # Create output directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Generate comparative heatmaps for each metric
    for metric in metrics:
        main_vis = visualizations[0]
        other_vis = visualizations[1:]
        main_vis.generate_comparative_heatmap(other_vis, metric=metric, save_path=output_dir)


if __name__ == "__main__":
    # Example usage
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
    
    # Check if results directory exists and contains simulation results
    if os.path.exists(results_dir):
        result_files = [f for f in os.listdir(results_dir) if f.endswith('.json')]
        
        if result_files:
            # Visualize first result file
            vis = TradeVisualization(results_path=os.path.join(results_dir, result_files[0]))
            
            # Generate visualizations
            output_dir = os.path.join(results_dir, 'visualizations')
            os.makedirs(output_dir, exist_ok=True)
            
            vis.plot_macro_trends(save_path=output_dir)
            vis.plot_export_composition(save_path=output_dir)
            vis.plot_sector_growth(save_path=output_dir)
            
            # Generate HTML report
            vis.generate_html_report(os.path.join(output_dir, f'report_{vis.scenario}.html'))
            
            print(f"Visualizations generated in {output_dir}")
        else:
            print("No simulation result files found in the results directory")
    else:
        print("Results directory not found")
