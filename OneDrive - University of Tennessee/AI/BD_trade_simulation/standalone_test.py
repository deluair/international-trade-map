"""
Standalone test for the structural transformation model.
This script contains all necessary code and doesn't rely on imports.
"""
import os
import pandas as pd
import numpy as np
import random


class SimpleStructuralTransformationModel:
    """
    Simplified structural transformation model for testing with real data.
    """
    
    def __init__(self, export_data=None):
        """
        Initialize the model.
        
        Args:
            export_data (dict, optional): Pre-loaded export data by sector
        """
        # Initial sector data (will be overridden if real data is provided)
        self.export_sectors = {
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
        }
        
        # Initialize metrics storage
        self.yearly_metrics = {
            'export_diversity_hhi': [],
            'export_diversity_sectors': [],
            'value_chain_position': {},
            'capability_index': 0.35,  # Initial capability index (0-1)
            'industrial_policy_effectiveness': 0.5,  # Initial policy effectiveness (0-1)
        }
        
        # Update with real data if provided
        if export_data:
            for sector, value in export_data.items():
                if sector in self.export_sectors:
                    self.export_sectors[sector]['value'] = value
    
    def simulate_step(self, year):
        """
        Simulate one step (year) of structural transformation.
        """
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
    
    def calculate_export_diversification(self, year):
        """
        Calculate export diversification metrics using HHI.
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


def process_trade_data(csv_path, year=2023, bangladesh_code=50):
    """
    Process trade data from CSV to get export values by sector.
    
    Args:
        csv_path (str): Path to the trade data CSV
        year (int): Year to filter for
        bangladesh_code (int): Country code for Bangladesh
        
    Returns:
        dict: Sector export values in billion USD
    """
    print(f"Processing trade data from {csv_path} for year {year}")
    
    # Define sector mappings (HS chapter -> sector)
    sector_mappings = {
        # RMG (Ready-Made Garments)
        61: 'rmg',  # Articles of apparel, knitted or crocheted
        62: 'rmg',  # Articles of apparel, not knitted or crocheted
        
        # Leather
        41: 'leather',  # Raw hides and skins
        42: 'leather',  # Articles of leather
        43: 'leather',  # Furskins and artificial fur
        64: 'leather',  # Footwear
        
        # Jute
        53: 'jute',  # Other vegetable textile fibers; paper yarn
        
        # Frozen food
        3: 'frozen_food',  # Fish and crustaceans
        16: 'frozen_food',  # Preparations of meat, fish
        
        # Pharma
        30: 'pharma',  # Pharmaceutical products
        
        # IT services
        85: 'it_services',  # Electrical machinery and equipment
        
        # Light engineering
        73: 'light_engineering',  # Articles of iron or steel
        76: 'light_engineering',  # Aluminum and articles thereof
        84: 'light_engineering',  # Machinery and mechanical appliances
        87: 'light_engineering',  # Vehicles other than railway
        
        # Agro processing
        7: 'agro_processing',  # Edible vegetables
        8: 'agro_processing',  # Edible fruit and nuts
        15: 'agro_processing',  # Animal or vegetable fats and oils
        17: 'agro_processing',  # Sugars and sugar confectionery
        19: 'agro_processing',  # Preparations of cereals, flour, starch or milk
        20: 'agro_processing',  # Preparations of vegetables, fruit, nuts
        21: 'agro_processing',  # Miscellaneous edible preparations
        
        # Home textiles
        63: 'home_textiles',  # Other made-up textile articles
        
        # Shipbuilding
        89: 'shipbuilding',  # Ships, boats and floating structures
    }
    
    # Process in chunks to avoid memory issues
    print("Reading data in chunks...")
    export_totals = {}
    
    # Initialize sector totals to zero
    for sector in set(sector_mappings.values()):
        export_totals[sector] = 0.0
    
    chunk_count = 0
    records_processed = 0
    
    for chunk in pd.read_csv(csv_path, chunksize=100000):
        chunk_count += 1
        
        # Filter for the specified year
        year_data = chunk[chunk['t'] == year]
        
        # Filter for Bangladesh exports (where i = Bangladesh)
        exports = year_data[year_data['i'] == bangladesh_code]
        
        records_processed += len(exports)
        
        # Process export records
        for _, row in exports.iterrows():
            # Get HS chapter (first 2 digits of product code)
            try:
                hs_code = str(int(row['k']))
                chapter = int(hs_code[:2]) if len(hs_code) >= 2 else 0
                
                # Check if we have a mapping for this chapter
                if chapter in sector_mappings:
                    sector = sector_mappings[chapter]
                    # Convert from thousands to billions
                    value_billions = row['v'] / 1_000_000
                    export_totals[sector] += value_billions
            except (ValueError, TypeError):
                continue
        
        # Print progress
        if chunk_count % 10 == 0:
            print(f"Processed {chunk_count} chunks, {records_processed} export records so far")
    
    print(f"Completed processing {chunk_count} chunks, {records_processed} total export records")
    return export_totals


def main():
    """Run the standalone structural transformation test."""
    print("=" * 50)
    print("STANDALONE STRUCTURAL TRANSFORMATION TEST")
    print("=" * 50)
    
    # Path to trade data CSV
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'bd_trade_data.csv')
    
    if not os.path.exists(data_path):
        print(f"Error: Trade data file not found at {data_path}")
        print("Running with synthetic data only")
        export_data = None
    else:
        # Process trade data for 2023
        try:
            export_data = process_trade_data(data_path, year=2023)
            print("\nExport data by sector (billion USD):")
            for sector, value in sorted(export_data.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {sector}: ${value:.3f} billion")
        except Exception as e:
            print(f"Error processing trade data: {e}")
            print("Running with synthetic data only")
            export_data = None
    
    # Create and initialize model
    model = SimpleStructuralTransformationModel(export_data)
    
    # Test for the year 2023
    print("\n" + "=" * 50)
    print("SIMULATING YEAR 2023")
    print("=" * 50)
    
    # Run simulation
    results = model.simulate_step(2023)
    
    # Display results
    print("\nSummary of Results:")
    print(f"Export Diversification HHI: {results['export_diversity_hhi']:.4f}")
    print(f"Capability Index: {results['capability_index']:.4f}")
    print(f"Industrial Policy Effectiveness: {results['industrial_policy_effectiveness']:.4f}")
    
    print("\nExport Values by Sector (billion USD):")
    for sector, value in sorted(results['export_sectors'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {sector}: ${value:.3f} billion")


if __name__ == "__main__":
    main()
