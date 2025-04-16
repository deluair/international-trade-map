#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bangladesh Trade Dynamics Future Projection (2023-2030)

This script runs the Bangladesh trade simulation using real historical data (2021-2023)
and then projects future scenarios up to 2030. It generates a comprehensive HTML report
with visualizations of the results.
"""

import os
import sys
import importlib.util
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
from datetime import datetime
import argparse # Import argparse

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import data handler directly
from data_handler import TradeDataHandler

# Function to dynamically load modules
def load_module(file_path, module_name):
    """Dynamically load a module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def load_scenario_config(scenario_name):
    """Load scenario configuration from a JSON file"""
    scenario_file = os.path.join(project_root, 'scenarios', f"{scenario_name}.json")
    if not os.path.exists(scenario_file):
        print(f"Error: Scenario file not found: {scenario_file}")
        print("Falling back to default baseline parameters.")
        # Provide default baseline parameters if file not found
        return {
            "annual_changes": {
                "export_diversity_hhi": -0.015,
                "capability_index": 0.025,
                "rmg_share": -0.015,
                "it_services_growth": 0.18,
                "pharma_growth": 0.20,
                "light_engineering_growth": 0.15,
                "jute_growth": 0.04,
                "leather_growth": 0.08,
                "agro_processing_growth": 0.12,
                "default_sector_growth": 0.05,
                "rmg_growth": 0.03
            },
            "policy_effectiveness_increase": 0.03
        }
    try:
        with open(scenario_file, 'r') as f:
            config = json.load(f)
            print(f"Loaded scenario configuration from {scenario_file}")
            return config.get('parameters', {}) # Return the parameters dictionary
    except Exception as e:
        print(f"Error loading scenario file {scenario_file}: {e}")
        sys.exit(1)

def main(scenario_name):
    """Run the Bangladesh trade simulation with historical data and future projections"""
    print("=" * 80)
    print(f"BANGLADESH TRADE DYNAMICS SIMULATION AND PROJECTION (2021-2030) - SCENARIO: {scenario_name.upper()}")
    print("Using real trade data for historical years and projections for future years")
    print("=" * 80)
    
    # Load necessary modules dynamically
    print("\nLoading simulation modules...")
    
    # Core models
    modules = {}
    model_files = {
        'structural_transformation': os.path.join(project_root, 'models', 'structural_transformation.py'),
        'export_sector': os.path.join(project_root, 'models', 'export_sector.py'),
        'global_market': os.path.join(project_root, 'models', 'global_market.py'),
    }
    
    # Load all model modules
    for name, path in model_files.items():
        try:
            modules[name] = load_module(path, name)
            print(f"  ✓ Loaded {name} model")
        except Exception as e:
            print(f"  ✗ Error loading {name} model: {e}")
            modules[name] = None
    
    # Load scenario configuration
    print(f"\nLoading scenario parameters for '{scenario_name}'...")
    scenario_params = load_scenario_config(scenario_name)
    annual_changes = scenario_params.get('annual_changes', {}) # Get annual changes dict
    policy_increase = scenario_params.get('policy_effectiveness_increase', 0.03) # Get policy increase
    growth_decay_rate = scenario_params.get('growth_decay_rate', 1.0) # Default to 1.0 (no decay)
    print(f"Using growth decay rate: {growth_decay_rate}")
    
    # Create base configuration
    config = {
        'data_path': os.path.join(project_root, 'data', 'bd_trade_data.csv'),
        'random_seed': 42,
        'verbose': True,
    }
    
    # Load real trade data
    print("\nLoading real trade data...")
    try:
        data_handler = TradeDataHandler(config['data_path'])
        trade_data = data_handler.load_data()
        print(f"Successfully loaded {len(trade_data)} trade records")
    except Exception as e:
        print(f"Error loading trade data: {e}")
        print("Will proceed with synthetic data where real data is unavailable")
    
    # Initialize models
    print("\nInitializing models...")
    models = {}
    
    # Initialize structural transformation model which we've verified works
    if modules['structural_transformation']:
        try:
            models['structural'] = modules['structural_transformation'].StructuralTransformationModel(config)
            print("  ✓ Initialized structural transformation model")
        except Exception as e:
            print(f"  ✗ Error initializing structural transformation model: {e}")
    
    # Historical years with real data
    historical_years = [2023, 2022, 2021]
    
    # Future years to project (Adjusted to 2025-2030)
    # We still need 2024 calculation as the base for 2025 unless historical data extends to 2024
    projection_start_year = 2024 
    projection_end_year = 2030
    future_years = list(range(projection_start_year, projection_end_year + 1))
    
    # All simulation years
    all_years = historical_years + future_years
    all_years.sort()  # Sort in ascending order for the simulation
    
    # Initialize results storage
    results = {
        'metadata': {
            'simulation_type': 'Bangladesh Trade Dynamics with Future Projections',
            'simulation_years': all_years,
            'historical_years': historical_years,
            'projection_years': future_years,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'scenario': scenario_name # Use loaded scenario name
        },
        'yearly_data': {}
    }
    
    # Run simulation for historical years first
    print("\nSimulating historical years with real data...")
    for year in historical_years:
        print(f"\n{'='*50}")
        print(f"SIMULATING HISTORICAL YEAR {year}")
        print(f"{'='*50}")
        
        year_results = {}
        
        # Run structural transformation model for historical year
        if 'structural' in models:
            try:
                print(f"Simulating structural transformation for {year}...")
                structural_results = models['structural'].simulate_step(year)
                year_results['structural_transformation'] = structural_results
                
                # Store top sectors for historical reference
                results['yearly_data'][year] = year_results
                
                # Display key results
                print(f"Export Diversification HHI: {structural_results['export_diversity_hhi']:.4f}")
                print(f"Capability Index: {structural_results['capability_index']:.4f}")
            except Exception as e:
                print(f"Error in structural transformation model: {e}")
    
    # Project future years
    print("\nProjecting future years...")
    
    # Extract the most recent year's data as starting point for projections
    latest_year = max(historical_years)  # Get the most recent year (should be integer)
    if latest_year in results['yearly_data']:
        latest_data = results['yearly_data'][latest_year]
        print(f"Using {latest_year} as base for future projections")
    else:
        print(f"No data found for latest year {latest_year}, using default values")
        latest_data = {}
    
    for year in future_years:
        print(f"\n{'='*50}")
        print(f"PROJECTING FUTURE YEAR {year}")
        print(f"{'='*50}")
        
        year_results = {}
        year_structural = {}
        
        # Start with the latest known data 
        if 'structural_transformation' in latest_data:
            base_structural = latest_data['structural_transformation']
            years_forward = year - latest_year
            print(f"Projecting {years_forward} years forward from {latest_year} to {year}")
            
            # Project key metrics forward
            export_diversity_hhi = base_structural['export_diversity_hhi'] * (1 + annual_changes.get('export_diversity_hhi', 0)) ** years_forward
            export_diversity_hhi = max(0.2, min(0.9, export_diversity_hhi))  # Cap between 0.2 and 0.9
            
            capability_index = base_structural['capability_index'] * (1 + annual_changes.get('capability_index', 0)) ** years_forward
            capability_index = max(0.2, min(0.8, capability_index))  # Cap between 0.2 and 0.8
            
            # Project export sectors
            export_sectors = {}
            total_exports = 0
            default_growth = annual_changes.get('default_sector_growth', 0.05)
            
            # Start with base sectors and apply growth rates
            for sector, value in base_structural['export_sectors'].items():
                # Apply decay to growth rates
                initial_growth_rate = default_growth # Default growth rate from scenario
                
                # Apply sector-specific growth rates from scenario
                if sector == 'rmg':
                    initial_growth_rate = annual_changes.get('rmg_growth', default_growth)
                elif sector == 'it_services':
                    initial_growth_rate = annual_changes.get('it_services_growth', default_growth)
                elif sector == 'pharma':
                    initial_growth_rate = annual_changes.get('pharma_growth', default_growth)
                elif sector == 'light_engineering':
                    initial_growth_rate = annual_changes.get('light_engineering_growth', default_growth)
                elif sector == 'jute':
                    initial_growth_rate = annual_changes.get('jute_growth', default_growth)
                elif sector == 'leather':
                    initial_growth_rate = annual_changes.get('leather_growth', default_growth)
                elif sector == 'agro_processing':
                    initial_growth_rate = annual_changes.get('agro_processing_growth', default_growth)
                
                # Apply decay factor (starts decaying from year 2 onwards)
                decay_exponent = max(0, years_forward - 1)
                effective_growth_rate = initial_growth_rate * (growth_decay_rate ** decay_exponent)
                
                # Calculate new value with compound growth using the initial rate (compounding handles the year effect)
                compounded_value_initial = value * (1 + initial_growth_rate) ** years_forward
                
                # Now, let's apply an overall decay based on the number of years? Still tricky.
                
                # FINAL ATTEMPT: Calculate year-on-year growth with decay
                # We need the previous year's value. Let's fetch it or start from base.
                if years_forward == 1:
                    prev_year_value = value # Base value from latest_year
                else:
                    prev_year_results = results['yearly_data'][year-1]
                    prev_year_structural = prev_year_results.get('structural_transformation', {})
                    prev_year_sectors = prev_year_structural.get('export_sectors', {})
                    prev_year_value = prev_year_sectors.get(sector, 0) # Get previous projected value
                
                # Calculate the effective growth rate for this specific year transition
                # Growth rate for year `y` = initial_growth_rate * decay^(y - base_year - 1)
                current_year_growth_rate = initial_growth_rate * (growth_decay_rate ** max(0, year - latest_year - 1))
                
                # Calculate new value based on previous year and this year's decayed rate
                new_value = prev_year_value * (1 + current_year_growth_rate)
                
                export_sectors[sector] = new_value
                total_exports += new_value
            
            # Store projected data
            year_structural = {
                'export_diversity_hhi': export_diversity_hhi,
                'capability_index': capability_index,
                'industrial_policy_effectiveness': min(0.85, 0.5 + (years_forward * policy_increase)),  # Use policy increase from scenario
                'export_sectors': export_sectors,
                'total_exports': total_exports,
                'is_projected': True  # Flag to identify this as projected data
            }
            
            # Display projected results
            print(f"Projected Export Diversification HHI: {year_structural['export_diversity_hhi']:.4f}")
            print(f"Projected Capability Index: {year_structural['capability_index']:.4f}")
            print(f"Projected Total Exports: ${year_structural['total_exports']:.3f} billion")
            
            print("\nTop Projected Export Sectors:")
            for sector, value in sorted(year_structural['export_sectors'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {sector}: ${value:.3f} billion")
            
            # Store this year's projections
            year_results['structural_transformation'] = year_structural
            results['yearly_data'][year] = year_results
            
            # Update the latest data for next iteration
            latest_data = year_results
    
    # Save simulation results with projections
    results_dir = os.path.join(project_root, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # --- Start Modification: Include scenario in filename ---
    results_file = os.path.join(results_dir, f"bd_projection_results_{scenario_name}_{timestamp}.json")
    # --- End Modification ---
    
    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSimulation results saved to {results_file}")
    except Exception as e:
        print(f"Error saving results: {e}")
    
    # Generate HTML report
    print("\nGenerating HTML report...")
    try:
        # Import the HTML report generator
        from generate_html_report import create_html_report
        
        # Create the report
        report_file = create_html_report(results_file)
        
        # Try to open the report in a web browser
        print("Attempting to open the report in your web browser...")
        try:
            webbrowser.open('file://' + os.path.abspath(report_file))
        except Exception as e:
            print(f"Error opening report in browser: {e}")
            print(f"Please open the report manually: {report_file}")
    except Exception as e:
        print(f"Error generating HTML report: {e}")
        print("Proceeding without report generation")
    
    print("\nSimulation and projection complete!")

if __name__ == "__main__":
    # --- Start Modification: Add Argument Parser ---
    parser = argparse.ArgumentParser(description="Run Bangladesh trade projection simulation for a specific scenario.")
    parser.add_argument('--scenario', type=str, default='baseline', 
                        help='Name of the scenario to run (must correspond to a file in scenarios/, e.g., baseline)')
    args = parser.parse_args()
    
    main(args.scenario)
    # --- End Modification ---
