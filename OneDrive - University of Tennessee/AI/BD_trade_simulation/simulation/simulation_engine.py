import os
import sys
import json
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models
from models.export_sector import ExportSectorModel
from models.import_dependency import ImportDependencyModel
from models.trade_policy import TradePolicyModel
from models.logistics import LogisticsModel
from models.exchange_rate import ExchangeRateModel
from models.global_market import GlobalMarketModel
from models.geopolitical import GeopoliticalModel
from models.compliance import ComplianceModel
from models.structural_transformation import StructuralTransformationModel
from models.digital_trade import DigitalTradeModel
from models.services_trade import ServicesTradeModel
from models.investment import InvestmentModel
# Import from project root instead of data directory
from data_handler import TradeDataHandler as DataHandler


class TradeSimulationEngine:
    """
    Main simulation engine for the Bangladesh Trade Dynamics Simulation.
    Integrates all individual models and manages the overall simulation flow.
    """
    
    def __init__(self, config, start_year=2025, end_year=2050, scenario="baseline"):
        """
        Initialize the simulation engine.
        
        Args:
            config (dict): Configuration dictionary with parameters for all models
            start_year (int): Starting year for the simulation
            end_year (int): Ending year for the simulation
            scenario (str): Name of the scenario to simulate
        """
        self.config = config
        self.start_year = start_year
        self.end_year = end_year
        self.scenario = scenario
        self.current_year = start_year
        
        # Set random seed for reproducibility
        random.seed(config.get('random_seed', 42))
        np.random.seed(config.get('random_seed', 42))
        
        # Initialize data handler
        self.data_handler = DataHandler(config.get('data_config', {}))
        
        # Initialize models dictionary
        self.models = {} # General dictionary for all models
        self.export_models = {} # Specific dictionary for export sector models
        self.import_models = {} # Specific dictionary for import category models
        
        # Initialize models
        self.initialize_models()
        
        # Store simulation results
        self.results = {
            'metadata': {
                'scenario': scenario,
                'start_year': start_year,
                'end_year': end_year,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'yearly_data': {}
        }
    
    def initialize_models(self):
        """Initialize all simulation models"""
        
        # Initialize Export Sector Models (Modified Logic)
        export_config = self.config.get('export_sector_config', {})
        sectors_config = export_config.get('sectors', {})
        if not sectors_config:
            print("Warning: No export sectors defined in the configuration.")
        else:
            print(f"Initializing {len(sectors_config)} export sectors...")
            for sector_name, sector_cfg in sectors_config.items():
                print(f"  - Initializing sector: {sector_name}")
                try:
                    # Add sector_name to the config dict for the model
                    sector_cfg['sector_name'] = sector_name 
                    # TODO: Ideally, select specific subclass (RMGSectorModel etc.) based on config?
                    # For now, assume ExportSectorModel needs modification or handles dict.
                    # Let's try initializing the base model assuming it expects a dict now (needs fix in ExportSectorModel too)
                    # self.export_models[sector_name] = ExportSectorModel(sector_cfg) 
                    
                    # TEMPORARY FIX: Instantiate base model using individual args extracted from dict
                    # This avoids changing ExportSectorModel.__init__ for now, but is less clean.
                    self.export_models[sector_name] = ExportSectorModel(
                        sector_name=sector_name,
                        current_volume=sector_cfg.get('current_volume', 0),
                        growth_trajectory=sector_cfg.get('growth_trajectory', 0),
                        global_market_share=sector_cfg.get('global_market_share', 0),
                        value_chain_position=sector_cfg.get('value_chain_position', 'unknown'),
                        competitiveness_factors=sector_cfg.get('competitiveness_factors', {}),
                        tariff_exposure=sector_cfg.get('tariff_exposure', 0),
                        subsectors=sector_cfg.get('subsectors', [])
                    )
                    
                except Exception as e:
                    print(f"  - ERROR initializing sector {sector_name}: {e}")
            print("Export sectors initialized.")

        # Initialize Import Category Models (Modified Logic Again)
        import_config = self.config.get('import_dependency_config', {})
        categories_config = import_config.get('categories', {})
        if not categories_config:
            print("Warning: No import categories defined in the configuration.")
        else:
            print(f"Initializing {len(categories_config)} import categories...")
            for category_name, category_cfg in categories_config.items():
                print(f"  - Initializing category: {category_name}")
                try:
                    # TEMPORARY FIX: Instantiate base model using individual args extracted from dict
                    self.import_models[category_name] = ImportDependencyModel(
                        category_name=category_name,
                        current_volume=category_cfg.get('current_volume', 0),
                        domestic_production_ratio=category_cfg.get('domestic_production_ratio', 0),
                        growth_trajectory=category_cfg.get('growth_trajectory', 0),
                        price_sensitivity=category_cfg.get('price_sensitivity', 0.5),
                        substitution_elasticity=category_cfg.get('substitution_elasticity', 0.5)
                    )
                except Exception as e:
                    print(f"  - ERROR initializing category {category_name}: {e}")
            print("Import categories initialized.")

        # Initialize other models (Remove import from model_configs)
        print("Initializing other models...")
        model_configs = {
            # 'import': ('import_dependency_config', ImportDependencyModel), # Handled above
            'trade_policy': ('trade_policy_config', TradePolicyModel),
            'logistics': ('logistics_config', LogisticsModel),
            'exchange_rate': ('exchange_rate_config', ExchangeRateModel),
            'global_market': ('global_market_config', GlobalMarketModel),
            'geopolitical': ('geopolitical_config', GeopoliticalModel),
            'compliance': ('compliance_config', ComplianceModel),
            'structural': ('structural_transformation_config', StructuralTransformationModel),
            'digital_trade': ('digital_trade_config', DigitalTradeModel),
            'services_trade': ('services_trade_config', ServicesTradeModel),
            'investment': ('investment_config', InvestmentModel)
        }

        # Initialize remaining models using the loop
        for model_key, (config_key, ModelClass) in model_configs.items():
            try:
                cfg = self.config.get(config_key, {})
                self.models[model_key] = ModelClass(cfg)
                print(f"  - Initialized {model_key} model.")
            except Exception as e:
                print(f"  - ERROR initializing {model_key} model ({ModelClass.__name__}): {e}")
        
        print(f"All models initialized for {self.scenario} scenario")
    
    def run_simulation(self, verbose=True):
        """
        Run the complete simulation from start_year to end_year.
        
        Args:
            verbose (bool): Whether to print detailed progress
        
        Returns:
            dict: Simulation results
        """
        if verbose:
            print(f"Starting {self.scenario} simulation from {self.start_year} to {self.end_year}")
        
        # Simulate each year sequentially
        for year in range(self.start_year, self.end_year + 1):
            self.current_year = year
            
            if verbose:
                print(f"\n{'='*50}")
                print(f"Simulating year {year} | Scenario: {self.scenario}")
                print(f"{'='*50}")
            
            # Run a single year of simulation
            year_results = self.simulate_year(year, verbose)
            
            # Store results for this year
            self.results['yearly_data'][year] = year_results
            
            # Optional: save intermediate results
            if year % 5 == 0 and self.config.get('save_intermediate_results', False):
                self.save_results(f"intermediate_{self.scenario}_{year}")
        
        if verbose:
            print(f"\nSimulation complete: {self.scenario} scenario from {self.start_year} to {self.end_year}")
        
        return self.results
    
    def simulate_year(self, year, verbose=True):
        """
        Simulate a single year across all models.
        The order of model execution matters due to interdependencies.
        
        Args:
            year (int): Year to simulate
            verbose (bool): Whether to print detailed progress
        
        Returns:
            dict: Results from all models for this year
        """
        year_results = {}
        year_index = year - self.start_year # Calculate year_index
        
        # Step 1: Simulate external conditions first
        try: 
            # Corrected arguments for simulate_global_markets
            global_conditions = self.models['global_market'].simulate_global_markets(year_index, year, self.scenario)
            year_results['global_market'] = global_conditions
        except Exception as e:
             print(f"  - ERROR simulating global_market model: {e}")
             global_conditions = {} # Set default if error
             year_results['global_market'] = {'error': str(e)}
        
        try:
            # Corrected arguments for simulate_geopolitical_environment
            geopolitical_conditions = self.models['geopolitical'].simulate_geopolitical_environment(year_index, year)
            year_results['geopolitical'] = geopolitical_conditions
        except Exception as e:
            print(f"  - ERROR simulating geopolitical model: {e}")
            geopolitical_conditions = {}
            year_results['geopolitical'] = {'error': str(e)}
        
        # Step 2: Simulate investment flows
        try:
            # Assuming investment model needs combined external conditions
            combined_external = {**global_conditions, **geopolitical_conditions}
            investment_results = self.models['investment'].simulate_step(year, combined_external)
            year_results['investment'] = investment_results
        except Exception as e:
            print(f"  - ERROR simulating investment model: {e}")
            investment_results = {}
            year_results['investment'] = {'error': str(e)}
        
        # Step 3: Simulate policy and business environment factors
        try:
            # Call the correct method for TradePolicyModel
            trade_policy_results = self.models['trade_policy'].get_overall_policy_environment(year_index, year)
            year_results['trade_policy'] = trade_policy_results
        except Exception as e:
            print(f"  - ERROR simulating trade_policy model: {e}")
            trade_policy_results = {}
            year_results['trade_policy'] = {'error': str(e)}
        
        try:
            # Call the correct method for LogisticsModel
            # Args: year_index, simulation_year, trade_volume, infrastructure_investment, policy_effectiveness
            # Need to get/estimate trade_volume, infra_investment, policy_effectiveness
            # Using placeholders for now - THESE NEED REAL VALUES FROM OTHER MODELS
            trade_volume_estimate = 100000 # Placeholder - e.g., from prev year total exports+imports?
            infra_investment_estimate = 0.5 # Placeholder - from InvestmentModel?
            policy_effectiveness_estimate = 0.6 # Placeholder - from TradePolicyModel?
            logistics_results = self.models['logistics'].simulate_logistics_performance(
                year_index, year, trade_volume_estimate, infra_investment_estimate, policy_effectiveness_estimate
            )
            year_results['logistics'] = logistics_results
        except Exception as e:
            print(f"  - ERROR simulating logistics model: {e}")
            logistics_results = {}
            year_results['logistics'] = {'error': str(e)}
        
        try:
            # Call the correct method for ExchangeRateModel
            # Args: year_index, balance_of_payments, central_bank_policy, global_conditions
            # Need to construct these dictionaries - using placeholders for now
            bop_estimate = { # Placeholder - needs values from trade, investment etc.
                'exports': 50000, 'imports': 60000, 'remittances': 20000, 'fdi': 3000, 
                'aid_loans': 1000, 'profit_repatriation': 1500, 'other_outflows': 500
            }
            cb_policy_estimate = { # Placeholder - could come from config or another model
                'intervention_stance': 0.5, 'reserve_threshold': 3.5, 'interest_rate_differential': 0.02
            }
            exchange_rate_results = self.models['exchange_rate'].simulate_exchange_rate(
                year_index, bop_estimate, cb_policy_estimate, global_conditions
            )
            year_results['exchange_rate'] = exchange_rate_results
        except Exception as e:
            print(f"  - ERROR simulating exchange_rate model: {e}")
            exchange_rate_results = {}
            year_results['exchange_rate'] = {'error': str(e)}
        
        try:
            # Call the correct method for ComplianceModel
            # Args: year_index, simulation_year, regulatory_developments, buyer_requirements
            # Need to get/estimate regulatory_developments, buyer_requirements
            # Using placeholders for now - THESE NEED REAL VALUES FROM OTHER MODELS/CONFIG
            regulatory_dev_estimate = 0.6 # Placeholder
            buyer_req_estimate = 0.7 # Placeholder
            compliance_results = self.models['compliance'].simulate_compliance_environment(
                year_index, year, regulatory_dev_estimate, buyer_req_estimate
            )
            year_results['compliance'] = compliance_results
        except Exception as e:
            print(f"  - ERROR simulating compliance model: {e}")
            compliance_results = {}
            year_results['compliance'] = {'error': str(e)}
        
        # Step 4: Simulate structural transformation and digital/services components
        try:
            structural_transformation_results = self.models['structural'].simulate_step(year)
            year_results['structural_transformation'] = structural_transformation_results
        except Exception as e:
            print(f"  - ERROR simulating structural model: {e}")
            structural_transformation_results = {}
            year_results['structural_transformation'] = {'error': str(e)}
            
        try:
            digital_trade_results = self.models['digital_trade'].simulate_step(year, global_conditions)
            year_results['digital_trade'] = digital_trade_results
        except Exception as e:
            print(f"  - ERROR simulating digital_trade model: {e}")
            digital_trade_results = {}
            year_results['digital_trade'] = {'error': str(e)}
            
        try:
            services_trade_results = self.models['services_trade'].simulate_step(year, global_conditions)
            year_results['services_trade'] = services_trade_results
        except Exception as e:
            print(f"  - ERROR simulating services_trade model: {e}")
            services_trade_results = {}
            year_results['services_trade'] = {'error': str(e)}
        
        # Step 5: Simulate imports and exports, which depend on all previous factors
        # Combine all conditions that might affect exports and imports
        trade_environment = {
            **global_conditions,
            **geopolitical_conditions,
            **trade_policy_results,
            **logistics_results,
            **exchange_rate_results,
            **compliance_results,
            'digital_adoption': digital_trade_results.get('overall_adoption_rate', 0.5),
            'investment_levels': investment_results,
            'structural_factors': structural_transformation_results
        }
        
        # Simulate each export sector
        all_export_results = {}
        total_exports = 0
        print(f"  Simulating {len(self.export_models)} export sectors...")
        for sector_name, sector_model in self.export_models.items():
            # Prepare inputs specific to this sector model's simulate_year method
            # Note: The ExportSectorModel.simulate_year signature needs specific args
            # We need to map the available results (global, policy, etc.) to these args.
            # This mapping might need refinement based on ExportSectorModel details.
            sector_inputs = {
                'global_demand_growth': global_conditions.get('demand_growth_rate', 0.03),
                'tariff_changes': trade_policy_results.get('effective_tariffs', {}), # Dict by market?
                'exchange_rate_impact': exchange_rate_results.get('impact_factor', 0), # Scaled impact?
                'logistics_performance': logistics_results.get('performance_index', 0.6),
                'trade_policy_impact': trade_policy_results.get('net_impact', 0),
                'compliance_impact': compliance_results.get('net_impact', 0),
                'digital_adoption': digital_trade_results.get('overall_adoption_rate', 0.5),
                'competitor_growth': global_conditions.get('competitor_growth', {}) # Dict by competitor?
            }
            
            try:
                # Use year - start_year as year_index for the model's internal tracking
                year_index = year - self.start_year 
                sector_result = sector_model.simulate_year(year_index, **sector_inputs) 
                all_export_results[sector_name] = sector_result
                total_exports += sector_result.get('export_volume', 0)
                if verbose:
                    print(f"    - {sector_name}: ${sector_result.get('export_volume', 0):.2f} billion (Growth: {sector_result.get('growth_rate', 0)*100:.2f}%)")
            except Exception as e:
                 print(f"    - ERROR simulating sector {sector_name}: {e}")
                 all_export_results[sector_name] = {'error': str(e)}

        # Aggregate export results
        final_export_summary = {
            'total_exports': total_exports,
            'sector_details': all_export_results
            # Add other aggregate metrics if needed (e.g., diversification HHI)
        }
        year_results['export'] = final_export_summary
        
        # Simulate imports (depends on total exports for things like intermediate goods demand)
        # Pass the aggregated export summary
        all_import_results = {}
        total_imports = 0
        print(f"  Simulating {len(self.import_models)} import categories...")
        if self.import_models:
             for category_name, category_model in self.import_models.items():
                 # Prepare inputs specific to simulate_import_needs
                 category_inputs = {
                    # Args: domestic_production_growth, consumption_demand_growth, exchange_rate_impact, 
                    # tariff_changes, global_price_changes, logistics_cost, domestic_capacity_investment
                    # Need to get these from other model results - using placeholders
                    'domestic_production_growth': investment_results.get('domestic_growth_rate', 0.05), # Placeholder
                    'consumption_demand_growth': global_conditions.get('consumption_growth', 0.04), # Placeholder
                    'exchange_rate_impact': exchange_rate_results.get('import_impact', 0), # From exch rate model
                    'tariff_changes': trade_policy_results.get('import_tariff_change', 0), # Placeholder
                    'global_price_changes': global_conditions.get('global_price_changes', {}), # Placeholder
                    'logistics_cost': logistics_results.get('logistics_cost_factor', 0.1), # Placeholder
                    'domestic_capacity_investment': investment_results.get('domestic_investment_level', 0.5) # Placeholder
                 }
                 try:
                     # Call the correct method: simulate_import_needs
                     category_result = category_model.simulate_import_needs(year_index, **category_inputs)
                     all_import_results[category_name] = category_result
                     total_imports += category_result.get('import_volume', 0)
                     if verbose:
                          print(f"    - {category_name}: ${category_result.get('import_volume', 0):.2f} billion")
                 except Exception as e:
                     print(f"    - ERROR simulating category {category_name}: {e}")
                     all_import_results[category_name] = {'error': str(e)}
        else:
            print("  Skipping import simulation as models failed to initialize.")

        # Aggregate import results
        final_import_summary = {
            'total_imports': total_imports,
            'category_details': all_import_results
        }
        year_results['import'] = final_import_summary
        
        # Step 6: Calculate aggregate trade metrics (using updated summaries)
        gdp = investment_results.get('gdp', 1)
        trade_balance = final_export_summary.get('total_exports', 0) - final_import_summary.get('total_imports', 0)
        trade_openness = (final_export_summary.get('total_exports', 0) + final_import_summary.get('total_imports', 0)) / gdp
        
        year_results['aggregate_metrics'] = {
            'trade_balance': trade_balance,
            'trade_openness': trade_openness,
            'export_to_gdp': final_export_summary.get('total_exports', 0) / gdp,
            'import_to_gdp': final_import_summary.get('total_imports', 0) / gdp
        }
        
        if verbose:
            print(f"\nYear {year} Summary:")
            print(f"GDP: ${gdp:.2f} billion") # Use captured gdp
            print(f"Total Exports: ${final_export_summary.get('total_exports', 0):.2f} billion")
            print(f"Total Imports: ${final_import_summary.get('total_imports', 0):.2f} billion")
            print(f"Trade Balance: ${trade_balance:.2f} billion")
            print(f"Trade Openness: {trade_openness*100:.1f}%")
        
        return year_results
    
    def save_results(self, filename=None):
        """
        Save simulation results to a file.
        
        Args:
            filename (str, optional): Custom filename, otherwise uses scenario name
        """
        if filename is None:
            filename = f"simulation_results_{self.scenario}"
        
        # Ensure results directory exists
        results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Save as JSON
        with open(os.path.join(results_dir, f"{filename}.json"), 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Simulation results saved to {filename}.json")
    
    def generate_summary_dataframe(self):
        """
        Generate a Pandas DataFrame with key metrics for all years.
        
        Returns:
            pd.DataFrame: Summary DataFrame with yearly data
        """
        years = list(self.results['yearly_data'].keys())
        
        # Extract key metrics from each year's results
        data = {
            'Year': years,
            'GDP': [self.results['yearly_data'][y]['investment']['gdp'] for y in years],
            'Total_Exports': [self.results['yearly_data'][y]['export']['total_exports'] for y in years],
            'Total_Imports': [self.results['yearly_data'][y]['import']['total_imports'] for y in years],
            'Trade_Balance': [self.results['yearly_data'][y]['aggregate_metrics']['trade_balance'] for y in years],
            'Trade_Openness': [self.results['yearly_data'][y]['aggregate_metrics']['trade_openness'] for y in years],
        }
        
        # Add export sector data
        for sector in self.export_models.values():
            data[f'Export_{sector.sector_name}'] = [self.results['yearly_data'][y]['export']['sector_exports'].get(sector.sector_name, 0) for y in years]
        
        # Create DataFrame
        df = pd.DataFrame(data)
        return df
    
    def plot_key_metrics(self, metrics=None, save_path=None):
        """
        Generate plots for key metrics over the simulation period.
        
        Args:
            metrics (list, optional): List of metrics to plot
            save_path (str, optional): Path to save the plots
        """
        df = self.generate_summary_dataframe()
        
        if metrics is None:
            metrics = ['GDP', 'Total_Exports', 'Total_Imports', 'Trade_Balance']
        
        # Create directory for plots if saving
        if save_path:
            os.makedirs(save_path, exist_ok=True)
        
        # Plot each metric
        for metric in metrics:
            if metric in df.columns:
                plt.figure(figsize=(10, 6))
                plt.plot(df['Year'], df[metric])
                plt.title(f'{metric} Evolution ({self.start_year}-{self.end_year})')
                plt.xlabel('Year')
                plt.ylabel(metric.replace('_', ' '))
                plt.grid(True, linestyle='--', alpha=0.7)
                
                if save_path:
                    plt.savefig(os.path.join(save_path, f"{metric.lower()}_{self.scenario}.png"))
                    plt.close()
                else:
                    plt.show()
            else:
                print(f"Metric {metric} not found in simulation results")
    
    def run_scenario_comparison(self, other_simulations, metrics=None, save_path=None):
        """
        Compare results across multiple simulation scenarios.
        
        Args:
            other_simulations (list): List of other TradeSimulationEngine instances
            metrics (list, optional): List of metrics to compare
            save_path (str, optional): Path to save the comparison plots
        """
        if metrics is None:
            metrics = ['GDP', 'Total_Exports', 'Total_Imports', 'Trade_Balance']
        
        # Get data for this simulation
        this_df = self.generate_summary_dataframe()
        
        # Create directory for plots if saving
        if save_path:
            os.makedirs(save_path, exist_ok=True)
        
        # Plot each metric across scenarios
        for metric in metrics:
            plt.figure(figsize=(12, 7))
            
            # Plot this scenario
            plt.plot(this_df['Year'], this_df[metric], label=f"{self.scenario}")
            
            # Plot other scenarios
            for sim in other_simulations:
                other_df = sim.generate_summary_dataframe()
                plt.plot(other_df['Year'], other_df[metric], label=f"{sim.scenario}")
            
            plt.title(f'{metric} Comparison Across Scenarios')
            plt.xlabel('Year')
            plt.ylabel(metric.replace('_', ' '))
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()
            
            if save_path:
                plt.savefig(os.path.join(save_path, f"{metric.lower()}_comparison.png"))
                plt.close()
            else:
                plt.show()


def run_simulation_from_config(config_path, scenario="baseline", start_year=2025, end_year=2050):
    """
    Helper function to run a simulation from a configuration file.
    
    Args:
        config_path (str): Path to the configuration file
        scenario (str): Name of the scenario to simulate
        start_year (int): Starting year for the simulation
        end_year (int): Ending year for the simulation
    
    Returns:
        TradeSimulationEngine: Simulation engine with results
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize and run simulation
    simulation = TradeSimulationEngine(config, start_year, end_year, scenario)
    simulation.run_simulation()
    
    # Save results
    simulation.save_results()
    
    return simulation


if __name__ == "__main__":
    # Example usage
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'config', 'simulation_config.json')
    
    # Check if configuration file exists, otherwise use Python config
    if not os.path.exists(config_path):
        import sys
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config'))
        from simulation_config import CONFIG as config
    else:
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    # Run simulation
    simulation = TradeSimulationEngine(config, 2025, 2050, "baseline")
    simulation.run_simulation()
    
    # Generate and save plots
    simulation.plot_key_metrics(save_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                                     'results', 'plots'))
