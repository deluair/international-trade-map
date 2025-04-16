import pandas as pd
import numpy as np
import random
import os
import sys

# Add project root to path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import our modules
try:
    # Import from project root instead of data directory
    from data_handler import TradeDataHandler
    # Import SectorMapper directly
    import importlib.util
    sector_mapper_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sector_mapper.py')
    spec = importlib.util.spec_from_file_location('sector_mapper', sector_mapper_path)
    sector_mapper_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sector_mapper_module)
    SectorMapper = sector_mapper_module.SectorMapper
except ImportError as e:
    print(f"Import error: {e}")
    print("Continuing with limited functionality")
    TradeDataHandler = None
    SectorMapper = None


class StructuralTransformationModel:
    """
    Models economic structural transformation in Bangladesh, focusing on:
    - Export diversification metrics and trajectories
    - Value chain positioning and upgrading
    - Industrial policy effectiveness
    - Capability development over time
    """
    
    def __init__(self, config):
        """
        Initialize the structural transformation model.
        
        Args:
            config (dict): Configuration parameters for the model
        """
        self.config = config
        
        # Initialize data handler
        self.data_handler = None
        if 'data_path' in config:
            self.data_handler = TradeDataHandler(config['data_path'])
            try:
                self.data_handler.load_data()
            except Exception as e:
                print(f"Warning: Could not load data: {e}")
                print("Using simulated data instead.")
                
        # Initialize sector mapper for real trade data
        self.sector_mapper = None
        try:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
            self.sector_mapper = SectorMapper(data_dir)
            print("Successfully initialized sector mapper for trade data")
        except Exception as e:
            print(f"Warning: Could not initialize sector mapper: {e}")
            print("Will rely on synthetic data")
        
        # Initialize metrics storage
        self.yearly_metrics = {
            'export_diversity_hhi': [],
            'export_diversity_sectors': [],
            'value_chain_position': {},
            'capability_index': 0.35,  # Initial capability index (0-1)
            'industrial_policy_effectiveness': 0.5,  # Initial policy effectiveness (0-1)
        }
        
        # Initial sector data
        self.export_sectors = config.get('export_sectors', {
            'rmg': {'value': 38.0, 'complexity': 0.3, 'value_chain_position': 0.25},
            'leather': {'value': 1.8, 'complexity': 0.4, 'value_chain_position': 0.3},
            'jute': {'value': 1.2, 'complexity': 0.2, 'value_chain_position': 0.4},
            'frozen_food': {'value': 0.7, 'complexity': 0.3, 'value_chain_position': 0.35},
            'pharma': {'value': 0.16, 'complexity': 0.7, 'value_chain_position': 0.45},
            'it_services': {'value': 1.3, 'complexity': 0.8, 'value_chain_position': 0.6},
            'light_engineering': {'value': 0.5, 'complexity': 0.5, 'value_chain_position': 0.4},
            'agro_processing': {'value': 0.8, 'complexity': 0.4, 'value_chain_position': 0.35},
            'home_textiles': {'value': 1.0, 'complexity': 0.35, 'value_chain_position': 0.3},
            'shipbuilding': {'value': 0.3, 'complexity': 0.6, 'value_chain_position': 0.5}
        })

    def simulate_step(self, year):
        """
        Simulate one step (year) of structural transformation.
        
        Args:
            year (int): The current simulation year
            
        Returns:
            dict: Updated structural transformation metrics
        """
        # Get data for this year using sector mapper (if available)
        if self.sector_mapper is not None:
            try:
                print(f"Attempting to use real trade data for year {year}")
                export_data, _ = self.sector_mapper.process_trade_data(year=year)
                if not export_data.empty:
                    print(f"Using real trade data for year {year}")
                    self.update_from_sector_data(export_data)
                else:
                    print(f"No real trade data found for year {year}")
                    self.simulate_with_synthetic_data(year)
            except Exception as e:
                print(f"Error processing real trade data: {e}")
                self.simulate_with_synthetic_data(year)
        # Fallback to data handler if sector mapper is not available
        elif self.data_handler and self.data_handler.data is not None:
            try:
                year_data = self.data_handler.get_data_by_year(year)
                if not year_data.empty:
                    print(f"Using data handler for year {year}")
                    self.update_from_real_data(year_data)
                else:
                    self.simulate_with_synthetic_data(year)
            except Exception as e:
                print(f"Error processing data handler data: {e}")
                self.simulate_with_synthetic_data(year)
        else:
            self.simulate_with_synthetic_data(year)
        
        # Calculate metrics based on current state
        diversity_hhi = self.calculate_export_diversification(year)
        value_chain_metrics = self.simulate_value_chain_upgrading(year)
        capability_metrics = self.simulate_capability_development(year)
        policy_metrics = self.integrate_industrial_policy(year)
        
        # Compile and return results
        return {
            'export_diversity_hhi': diversity_hhi,
            'export_sectors': {k: v['value'] for k, v in self.export_sectors.items()},
            'value_chain_position': value_chain_metrics,
            'capability_index': capability_metrics,
            'industrial_policy_effectiveness': policy_metrics
        }
    
    def update_from_sector_data(self, export_data):
        """
        Update model state using processed sector export data.
        
        Args:
            export_data (pd.DataFrame): Processed export data by sector
        """
        # Update sector export values from real trade data
        sectors_dict = dict(zip(export_data['sector'], export_data['export_value']))
        
        print(f"Real trade data contains {len(sectors_dict)} sectors")
        print("Top export sectors from real data:")
        for sector, value in sorted(sectors_dict.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  - {sector}: ${value:.3f} billion")
        
        # Update export sector values in our model
        for sector, data in self.export_sectors.items():
            if sector in sectors_dict:
                # Use real value from trade data
                data['value'] = sectors_dict[sector]
                print(f"Updated {sector} with real value: ${data['value']:.3f} billion")
            else:
                print(f"No real data for {sector}, keeping synthetic value: ${data['value']:.3f} billion")
    
    def update_from_real_data(self, data):
        """
        Update model state using data from the data handler.
        This is a fallback when the sector mapper isn't available.
        
        Args:
            data (pd.DataFrame): Data for the current year
        """
        # Implementation depends on actual data structure
        if 'sector' in data.columns and 'export_value' in data.columns:
            # Update sector export values from real data
            sectors = data.groupby('sector')['export_value'].sum().to_dict()
            for sector, value in sectors.items():
                if sector in self.export_sectors:
                    self.export_sectors[sector]['value'] = value
        
        # Other updates based on available data columns
        if 'value_chain_position' in data.columns:
            for sector in self.export_sectors:
                sector_data = data[data['sector'] == sector]
                if not sector_data.empty and 'value_chain_position' in sector_data.columns:
                    self.export_sectors[sector]['value_chain_position'] = sector_data['value_chain_position'].mean()
    
    def simulate_with_synthetic_data(self, year):
        """
        Update model using synthetic data when real data is unavailable.
        
        Args:
            year (int): The current simulation year
        """
        # Base growth rate for all sectors
        base_growth = 0.05
        
        # Sector-specific growth adjustments
        for sector, data in self.export_sectors.items():
            # Higher capability sectors grow faster
            capability_effect = data['complexity'] * 0.05
            
            # Value chain position effect (higher position = higher growth)
            vcp_effect = data['value_chain_position'] * 0.04
            
            # Random component
            random_effect = random.uniform(-0.04, 0.08)
            
            # Calculate total growth rate
            growth_rate = base_growth + capability_effect + vcp_effect + random_effect
            
            # Industrial policy effect
            if self.yearly_metrics['industrial_policy_effectiveness'] > 0.6:
                # Higher-tech sectors benefit more from effective policy
                if data['complexity'] > 0.5:
                    growth_rate += 0.03
            
            # Update export value
            data['value'] *= (1 + growth_rate)
    
    def calculate_export_diversification(self, year):
        """
        Calculate export diversification metrics using HHI (Herfindahl-Hirschman Index).
        Lower HHI means more diversified exports.
        
        Args:
            year (int): The current simulation year
            
        Returns:
            float: HHI diversification index (0-1)
        """
        # Extract export values
        export_values = {sector: data['value'] for sector, data in self.export_sectors.items()}
        
        # Calculate total exports
        total_exports = sum(export_values.values())
        
        # Calculate HHI
        hhi = 0
        sector_shares = {}
        
        for sector, value in export_values.items():
            share = value / total_exports
            sector_shares[sector] = share
            hhi += share ** 2
        
        # Store results
        self.yearly_metrics['export_diversity_hhi'].append(hhi)
        self.yearly_metrics['export_diversity_sectors'].append(sector_shares)
        
        print(f"Year {year}: Export Diversification HHI = {hhi:.4f}")
        
        # Print top 3 export sectors
        sorted_sectors = sorted(sector_shares.items(), key=lambda x: x[1], reverse=True)
        print("Top export sectors:")
        for sector, share in sorted_sectors[:3]:
            print(f"  - {sector}: {share*100:.1f}% (${self.export_sectors[sector]['value']:.2f} billion)")
        
        return hhi

    def simulate_value_chain_upgrading(self, year):
        """
        Simulate value chain upgrading across sectors.
        Higher value chain position means more value added and higher-tier activities.
        
        Args:
            year (int): The current simulation year
            
        Returns:
            dict: Value chain positions by sector
        """
        # Base upgrade rate
        base_upgrade = 0.01
        
        # Capability effect on upgrading (higher capability = faster upgrading)
        capability_effect = self.yearly_metrics['capability_index'] * 0.02
        
        # Apply upgrading to each sector
        value_chain_positions = {}
        for sector, data in self.export_sectors.items():
            # Sector-specific factors
            complexity_effect = data['complexity'] * 0.01
            
            # Random component
            random_effect = random.uniform(-0.005, 0.015)
            
            # Calculate total upgrade
            total_upgrade = base_upgrade + capability_effect + complexity_effect + random_effect
            
            # Higher sectors upgrade more slowly (diminishing returns)
            diminishing_factor = 1 - (data['value_chain_position'] * 0.7)
            total_upgrade *= diminishing_factor
            
            # Update value chain position (0-1 scale)
            data['value_chain_position'] = min(0.95, data['value_chain_position'] + total_upgrade)
            
            value_chain_positions[sector] = data['value_chain_position']
        
        # Store in yearly metrics
        self.yearly_metrics['value_chain_position'][year] = value_chain_positions
        
        # Print summary
        avg_position = sum(value_chain_positions.values()) / len(value_chain_positions)
        print(f"Year {year}: Avg. Value Chain Position = {avg_position:.4f}")
        
        # Find sector with highest position
        top_sector = max(value_chain_positions.items(), key=lambda x: x[1])
        print(f"Highest value chain position: {top_sector[0]} at {top_sector[1]:.4f}")
        
        return value_chain_positions

    def simulate_capability_development(self, year):
        """
        Simulate capability development over time.
        Higher capability index means better ability to produce complex products.
        
        Args:
            year (int): The current simulation year
            
        Returns:
            float: Updated capability index
        """
        # Base development rate
        base_development = 0.008
        
        # Current value chain effect (feedback loop - higher positions build capabilities)
        vcp_values = [data['value_chain_position'] for data in self.export_sectors.values()]
        vcp_effect = (sum(vcp_values) / len(vcp_values)) * 0.01
        
        # Policy effect
        policy_effect = self.yearly_metrics['industrial_policy_effectiveness'] * 0.01
        
        # Random component
        random_effect = random.uniform(-0.005, 0.01)
        
        # Calculate total capability improvement
        total_improvement = base_development + vcp_effect + policy_effect + random_effect
        
        # Update capability index (0-1 scale with diminishing returns)
        current_capability = self.yearly_metrics['capability_index']
        diminishing_factor = 1 - (current_capability * 0.5)
        
        new_capability = min(0.95, current_capability + (total_improvement * diminishing_factor))
        self.yearly_metrics['capability_index'] = new_capability
        
        print(f"Year {year}: Capability Index = {new_capability:.4f}")
        
        return new_capability

    def integrate_industrial_policy(self, year):
        """
        Simulate the effectiveness of industrial policy over time.
        
        Args:
            year (int): The current simulation year
            
        Returns:
            float: Updated industrial policy effectiveness
        """
        # Base policy improvement
        base_improvement = 0.01
        
        # Reform cycles (policy effectiveness is cyclical with election cycles)
        policy_cycle = 0.02 * np.sin((year - 2025) * 0.5)
        
        # Random component (political factors, implementation challenges)
        random_effect = random.uniform(-0.04, 0.04)
        
        # Calculate total policy change
        total_change = base_improvement + policy_cycle + random_effect
        
        # Update policy effectiveness (0-1 scale)
        current_effectiveness = self.yearly_metrics['industrial_policy_effectiveness']
        new_effectiveness = max(0.2, min(0.9, current_effectiveness + total_change))
        self.yearly_metrics['industrial_policy_effectiveness'] = new_effectiveness
        
        # Determine policy regime type
        if new_effectiveness < 0.4:
            regime_type = "Weak interventions"
        elif new_effectiveness < 0.6:
            regime_type = "Moderate support"
        else:
            regime_type = "Strong industrial policy"
        
        print(f"Year {year}: Industrial Policy Effectiveness = {new_effectiveness:.4f} ({regime_type})")
        
        return new_effectiveness
