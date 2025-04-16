#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bangladesh Trade Dynamics Simulation (2025-2050)

This script serves as the main entry point for the Bangladesh Trade Dynamics
simulation, integrating all model components to project Bangladesh's international
trade ecosystem from 2025-2050, capturing global market forces, trade policy evolution,
export sector transformations, logistics infrastructure, exchange rate dynamics, and
geopolitical shifts.
"""

import os
import sys
import argparse
import json
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Import the simulation engine
from simulation.simulation_engine import TradeSimulationEngine, run_simulation_from_config

# Import visualization tools
from visualization.dashboard import create_dashboard
from visualization.plot_utils import plot_simulation_results


def load_config(config_path):
    """
    Load simulation configuration from YAML file.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    with open(config_path, 'r') as f:
        if config_path.endswith('.json'):
            config = json.load(f)
        elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
            config = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path}")
    
    return config


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Bangladesh Trade Dynamics Simulation (2025-2050)')
    
    # Configuration file
    parser.add_argument('--config', type=str, default='config/default_config.yaml',
                        help='Path to configuration file')
    
    # Simulation parameters
    parser.add_argument('--scenario', type=str, default='baseline',
                        help='Scenario to simulate (baseline, optimistic, pessimistic, etc.)')
    parser.add_argument('--start-year', type=int, default=2025,
                        help='Starting year for simulation')
    parser.add_argument('--end-year', type=int, default=2050,
                        help='Ending year for simulation')
    
    # Output options
    parser.add_argument('--output-dir', type=str, default='results',
                        help='Directory to save results')
    parser.add_argument('--dashboard', action='store_true',
                        help='Launch interactive dashboard after simulation')
    parser.add_argument('--plot', action='store_true',
                        help='Generate static plots of key results')
    
    # Multi-scenario comparison
    parser.add_argument('--compare', action='store_true',
                        help='Run and compare multiple scenarios')
    parser.add_argument('--scenarios', type=str, nargs='+',
                        default=['baseline', 'optimistic', 'pessimistic'],
                        help='List of scenarios to compare')
    
    # Additional options
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed progress during simulation')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility')
    
    return parser.parse_args()


def run_single_scenario(config, args):
    """
    Run a single simulation scenario.
    
    Args:
        config (dict): Configuration dictionary
        args (argparse.Namespace): Command line arguments
        
    Returns:
        dict: Simulation results
    """
    print(f"\nRunning {args.scenario} scenario from {args.start_year} to {args.end_year}...")
    
    # Update config with command line options
    config['random_seed'] = args.seed
    
    # Initialize and run simulation
    simulation = TradeSimulationEngine(
        config=config,
        start_year=args.start_year,
        end_year=args.end_year,
        scenario=args.scenario
    )
    
    # Run the simulation
    results = simulation.run_simulation(verbose=args.verbose)
    
    # Save results
    os.makedirs(args.output_dir, exist_ok=True)
    output_file = os.path.join(args.output_dir, f"simulation_results_{args.scenario}.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {output_file}")
    
    # Generate visualization if requested
    if args.plot:
        plot_file = os.path.join(args.output_dir, f"simulation_plots_{args.scenario}.pdf")
        plot_simulation_results(results, save_path=plot_file)
        print(f"Plots saved to {plot_file}")
    
    return results


def run_scenario_comparison(config, args):
    """
    Run and compare multiple simulation scenarios.
    
    Args:
        config (dict): Configuration dictionary
        args (argparse.Namespace): Command line arguments
    """
    print(f"\nRunning comparison of scenarios: {', '.join(args.scenarios)}")
    
    results_by_scenario = {}
    
    # Run each scenario
    for scenario in args.scenarios:
        print(f"\n{'-'*50}")
        print(f"Starting scenario: {scenario}")
        print(f"{'-'*50}")
        
        # Update config for this scenario
        scenario_config = config.copy()
        if 'scenarios' in config and scenario in config['scenarios']:
            # Override config with scenario-specific settings
            for key, value in config['scenarios'][scenario].items():
                # Handle nested dictionaries
                if isinstance(value, dict) and key in scenario_config:
                    scenario_config[key].update(value)
                else:
                    scenario_config[key] = value
        
        # Run simulation with this scenario
        simulation = TradeSimulationEngine(
            config=scenario_config,
            start_year=args.start_year,
            end_year=args.end_year,
            scenario=scenario
        )
        
        results = simulation.run_simulation(verbose=args.verbose)
        results_by_scenario[scenario] = results
    
    # Save comparative results
    comparison_file = os.path.join(args.output_dir, f"scenario_comparison_{args.start_year}_{args.end_year}.json")
    with open(comparison_file, 'w') as f:
        json.dump({
            'metadata': {
                'scenarios': args.scenarios,
                'start_year': args.start_year,
                'end_year': args.end_year,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'results_by_scenario': results_by_scenario
        }, f, indent=2)
    
    print(f"\nComparison results saved to {comparison_file}")
    
    # Generate comparison plots
    if args.plot:
        # Initialize first simulation object for plotting
        first_scenario = args.scenarios[0]
        simulation = TradeSimulationEngine(
            config=config,
            start_year=args.start_year,
            end_year=args.end_year,
            scenario=first_scenario
        )
        
        # Create list of other simulations
        other_simulations = []
        for scenario in args.scenarios[1:]:
            other_sim = TradeSimulationEngine(
                config=config,
                start_year=args.start_year,
                end_year=args.end_year,
                scenario=scenario
            )
            other_sim.results = results_by_scenario[scenario]
            other_simulations.append(other_sim)
        
        # Run comparison plot
        comparison_plot_file = os.path.join(args.output_dir, f"scenario_comparison_plots.pdf")
        simulation.results = results_by_scenario[first_scenario]
        simulation.run_scenario_comparison(other_simulations, save_path=comparison_plot_file)
        print(f"Comparison plots saved to {comparison_plot_file}")


def main():
    """Main entry point for the simulation"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    print(f"Bangladesh Trade Dynamics Simulation (2025-2050)")
    print(f"Configuration loaded from: {args.config}")
    
    # Run simulation based on requested mode
    if args.compare:
        run_scenario_comparison(config, args)
    else:
        results = run_single_scenario(config, args)
    
    # Launch interactive dashboard if requested
    if args.dashboard:
        print("\nLaunching interactive dashboard...")
        create_dashboard(os.path.join(args.output_dir))
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main() 