#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Run Bangladesh Trade Dynamics Simulation

This script provides a simple command-line interface to run 
the Bangladesh Trade Dynamics simulation with different scenarios.
"""

import os
import sys
import argparse
from main import load_config, run_single_scenario, run_scenario_comparison


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='Run Bangladesh Trade Dynamics Simulation')
    
    # Select simulation mode
    parser.add_argument('--mode', type=str, choices=['single', 'compare', 'all'], 
                       default='single', help='Simulation mode')
    
    # For single mode
    parser.add_argument('--scenario', type=str, default='baseline',
                       help='Scenario to simulate (single mode only)')
    
    # For compare mode
    parser.add_argument('--scenarios', type=str, nargs='+',
                       default=['baseline', 'optimistic', 'pessimistic'],
                       help='Scenarios to compare (compare mode only)')
    
    # Common options
    parser.add_argument('--start-year', type=int, default=2025,
                       help='Starting year for simulation')
    parser.add_argument('--end-year', type=int, default=2050,
                       help='Ending year for simulation')
    parser.add_argument('--config', type=str, default='config/default_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--output', type=str, default='results',
                       help='Directory to save results')
    parser.add_argument('--plot', action='store_true',
                       help='Generate plots')
    parser.add_argument('--verbose', action='store_true',
                       help='Print detailed progress')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)
    
    # Load configuration
    config = load_config(args.config)
    print(f"Configuration loaded from: {args.config}")
    
    # Update the config with command line options
    args_dict = vars(args)
    
    # Run the selected mode
    if args.mode == 'single':
        print(f"\nRunning single scenario: {args.scenario}")
        run_single_scenario(config, args)
        
    elif args.mode == 'compare':
        print(f"\nComparing scenarios: {', '.join(args.scenarios)}")
        args.compare = True  # Enable comparison mode for main functions
        run_scenario_comparison(config, args)
        
    elif args.mode == 'all':
        print("\nRunning all available scenarios")
        # Get all scenario names from the config
        all_scenarios = list(config.get('scenarios', {}).keys())
        if not all_scenarios:
            print("No scenarios found in configuration file.")
            return
            
        print(f"Found scenarios: {', '.join(all_scenarios)}")
        args.scenarios = all_scenarios
        args.compare = True  # Enable comparison mode for main functions
        run_scenario_comparison(config, args)
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main() 