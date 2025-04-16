import random
import numpy as np

class InvestmentModel:
    """
    Simulates investment flows affecting Bangladesh's trade capacity development,
    including foreign direct investment, domestic investment, special economic zones,
    and investment policy effects.
    """
    
    def __init__(self, config):
        """
        Initialize the investment model with configuration parameters.
        
        Args:
            config (dict): Configuration dictionary containing investment parameters
        """
        self.config = config
        
        # FDI Parameters
        self.fdi_inflow = config.get('initial_fdi_inflow', 3.5)  # billion USD
        self.fdi_sectors = config.get('initial_fdi_sectors', {
            'manufacturing': 0.45,  # share of total FDI
            'services': 0.30,
            'energy': 0.15,
            'infrastructure': 0.10
        })
        
        # Domestic Investment Parameters
        self.domestic_investment_rate = config.get('initial_domestic_investment_rate', 0.32)  # % of GDP
        self.gdp = config.get('initial_gdp', 350)  # billion USD
        self.domestic_investment = self.domestic_investment_rate * self.gdp
        self.domestic_sectors = config.get('initial_domestic_sectors', {
            'manufacturing': 0.30,  # share of total domestic investment
            'services': 0.35,
            'agriculture': 0.15,
            'infrastructure': 0.20
        })
        
        # Special Economic Zone Parameters
        self.active_sezs = config.get('initial_active_sezs', 8)  # number of operational SEZs
        self.sez_utilization = config.get('initial_sez_utilization', 0.40)  # capacity utilization
        self.sez_exports = config.get('initial_sez_exports', 4.5)  # billion USD
        
        # Investment Policy Parameters
        self.investment_policy_index = config.get('initial_investment_policy_index', 0.55)  # 0-1 scale (1 = best)
        self.repatriation_restrictions = config.get('initial_repatriation_restrictions', 0.40)  # 0-1 scale (0 = no restrictions)
        self.investment_incentives = config.get('initial_investment_incentives', 0.50)  # 0-1 scale (1 = highest)
        
        # Track metrics over time
        self.yearly_metrics = {
            'fdi_inflow': [self.fdi_inflow],
            'domestic_investment': [self.domestic_investment],
            'sez_exports': [self.sez_exports],
            'active_sezs': [self.active_sezs],
            'investment_policy_index': [self.investment_policy_index],
            'fdi_sectors': [self.fdi_sectors.copy()],
            'domestic_sectors': [self.domestic_sectors.copy()],
            'gdp': [self.gdp]
        }
    
    def simulate_step(self, year, global_conditions=None):
        """
        Simulate one year of investment developments.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External conditions affecting investment
        
        Returns:
            dict: Updated investment metrics
        """
        # Update GDP
        self.update_gdp(year, global_conditions)
        
        # Simulate each component of investment
        self.simulate_fdi(year, global_conditions)
        self.simulate_domestic_investment(year, global_conditions)
        self.simulate_sez_development(year)
        self.simulate_investment_policy(year, global_conditions)
        
        # Compile and return results
        current_metrics = {
            'fdi_inflow': self.fdi_inflow,
            'domestic_investment': self.domestic_investment,
            'sez_exports': self.sez_exports,
            'active_sezs': self.active_sezs,
            'investment_policy_index': self.investment_policy_index,
            'fdi_sectors': self.fdi_sectors.copy(),
            'domestic_sectors': self.domestic_sectors.copy(),
            'gdp': self.gdp
        }
        
        # Store metrics for this year
        for key, value in current_metrics.items():
            self.yearly_metrics[key].append(value)
            
        return current_metrics
    
    def update_gdp(self, year, global_conditions=None):
        """
        Update GDP for the current year
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External economic conditions
        """
        # Base growth rate
        base_growth = self.config.get('gdp_annual_growth_rate', 0.06)
        
        # Investment effect on growth
        investment_effect = 0.4 * ((self.fdi_inflow / self.gdp) + 
                                  (self.domestic_investment / self.gdp) - 0.3)
        
        # Global economic conditions effect
        global_effect = 0
        if global_conditions and 'global_economic_growth' in global_conditions:
            global_effect = 0.5 * global_conditions['global_economic_growth']
        
        # Random component (external shocks, weather, etc.)
        random_effect = random.uniform(-0.01, 0.02)
        
        # Calculate total growth
        gdp_growth = base_growth + investment_effect + global_effect + random_effect
        
        # Update GDP
        previous_gdp = self.gdp
        self.gdp *= (1 + gdp_growth)
        
        print(f"Year {year}: GDP: ${self.gdp:.2f} billion, Growth: {gdp_growth*100:.2f}%")
    
    def simulate_fdi(self, year, global_conditions=None):
        """
        Simulate foreign direct investment flows.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External investment conditions
        """
        # Base FDI growth
        base_growth = self.config.get('fdi_base_growth', 0.08)
        
        # Policy effect
        policy_effect = (self.investment_policy_index - 0.5) * 0.2
        
        # Repatriation effect (negative effect of restrictions)
        repatriation_effect = -0.1 * self.repatriation_restrictions
        
        # Infrastructure quality effect
        infrastructure_effect = self.config.get('infrastructure_quality', 0.4) * 0.05
        
        # Global FDI flows effect
        global_effect = 0
        if global_conditions and 'global_fdi_flows' in global_conditions:
            global_effect = global_conditions['global_fdi_flows'] * 0.8  # High elasticity
        
        # Regional competitiveness effect
        regional_effect = self.config.get('regional_investment_competitiveness', -0.02)
        
        # Random variance (significant for FDI - includes one-off large projects)
        random_effect = random.uniform(-0.15, 0.25)
        
        # Calculate total FDI growth
        fdi_growth = base_growth + policy_effect + repatriation_effect + infrastructure_effect + global_effect + regional_effect + random_effect
        
        # Update FDI inflow
        self.fdi_inflow *= (1 + fdi_growth)
        
        # Evolve sectoral distribution
        self.evolve_fdi_sectors(year)
        
        print(f"Year {year}: FDI inflow: ${self.fdi_inflow:.2f} billion")
    
    def evolve_fdi_sectors(self, year):
        """
        Evolve the sectoral distribution of FDI over time.
        
        Args:
            year (int): The current simulation year
        """
        # Gradual shift towards services and high-tech manufacturing
        services_shift = random.uniform(0.002, 0.008)
        manufacturing_shift = random.uniform(-0.005, 0.005)
        energy_shift = random.uniform(-0.005, 0.003)
        infrastructure_shift = random.uniform(-0.002, 0.007)
        
        # Policy influence on sectoral shifts
        policy_emphasis = self.config.get('fdi_policy_sector_emphasis', 'balanced')
        
        if policy_emphasis == 'manufacturing':
            manufacturing_shift += 0.01
        elif policy_emphasis == 'services':
            services_shift += 0.01
        elif policy_emphasis == 'infrastructure':
            infrastructure_shift += 0.01
        elif policy_emphasis == 'energy':
            energy_shift += 0.01
        
        # Apply shifts
        self.fdi_sectors['services'] += services_shift
        self.fdi_sectors['manufacturing'] += manufacturing_shift
        self.fdi_sectors['energy'] += energy_shift
        self.fdi_sectors['infrastructure'] += infrastructure_shift
        
        # Normalize to ensure total is 1.0
        total = sum(self.fdi_sectors.values())
        for sector in self.fdi_sectors:
            self.fdi_sectors[sector] /= total
    
    def simulate_domestic_investment(self, year, global_conditions=None):
        """
        Simulate domestic investment flows.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External conditions
        """
        # Base change in investment rate
        base_change = self.config.get('domestic_investment_rate_change', 0.002)
        
        # Interest rate effect
        interest_rate = self.config.get('interest_rate', 0.08)
        interest_effect = -0.05 * (interest_rate - 0.06)  # Negative effect of high rates
        
        # Business confidence effect
        business_confidence = self.config.get('business_confidence', 0.6)
        confidence_effect = 0.1 * (business_confidence - 0.5)
        
        # Monetary conditions
        monetary_effect = 0
        if global_conditions and 'monetary_conditions' in global_conditions:
            monetary_effect = 0.05 * global_conditions['monetary_conditions']
        
        # Random variance
        random_effect = random.uniform(-0.01, 0.01)
        
        # Calculate total change in investment rate
        rate_change = base_change + interest_effect + confidence_effect + monetary_effect + random_effect
        
        # Update investment rate
        self.domestic_investment_rate = max(0.25, min(0.40, self.domestic_investment_rate + rate_change))
        
        # Calculate domestic investment
        self.domestic_investment = self.domestic_investment_rate * self.gdp
        
        # Evolve sectoral distribution
        self.evolve_domestic_sectors(year)
        
        print(f"Year {year}: Domestic investment: ${self.domestic_investment:.2f} billion ({self.domestic_investment_rate*100:.1f}% of GDP)")
    
    def evolve_domestic_sectors(self, year):
        """
        Evolve the sectoral distribution of domestic investment over time.
        
        Args:
            year (int): The current simulation year
        """
        # Gradual economic transformation
        services_shift = random.uniform(0.003, 0.007)
        manufacturing_shift = random.uniform(-0.003, 0.005)
        agriculture_shift = random.uniform(-0.008, -0.002)
        infrastructure_shift = random.uniform(-0.002, 0.005)
        
        # Development stage influence
        development_stage = self.config.get('development_stage', 'early_industrial')
        
        if development_stage == 'early_industrial':
            manufacturing_shift += 0.005
        elif development_stage == 'industrial':
            services_shift += 0.003
            manufacturing_shift += 0.002
        elif development_stage == 'post_industrial':
            services_shift += 0.008
            agriculture_shift += 0.002  # Modern agriculture investment increases
        
        # Apply shifts
        self.domestic_sectors['services'] += services_shift
        self.domestic_sectors['manufacturing'] += manufacturing_shift
        self.domestic_sectors['agriculture'] += agriculture_shift
        self.domestic_sectors['infrastructure'] += infrastructure_shift
        
        # Normalize to ensure total is 1.0
        total = sum(self.domestic_sectors.values())
        for sector in self.domestic_sectors:
            self.domestic_sectors[sector] /= total
    
    def simulate_sez_development(self, year):
        """
        Simulate special economic zone development and performance.
        
        Args:
            year (int): The current simulation year
        """
        # New SEZ development
        new_sez_probability = self.config.get('annual_new_sez_probability', 0.4)
        
        if random.random() < new_sez_probability:
            new_sezs = random.randint(1, 2)
            self.active_sezs += new_sezs
            print(f"Year {year}: {new_sezs} new Special Economic Zone(s) became operational")
        
        # SEZ utilization improvement
        base_utilization_improvement = self.config.get('sez_utilization_improvement', 0.04)
        policy_effect = self.investment_policy_index * 0.03
        infrastructure_effect = self.config.get('infrastructure_quality', 0.4) * 0.02
        
        utilization_improvement = base_utilization_improvement + policy_effect + infrastructure_effect + random.uniform(-0.02, 0.03)
        
        # Update SEZ utilization with S-curve pattern
        current_gap = 1.0 - self.sez_utilization
        self.sez_utilization += utilization_improvement * current_gap
        
        # Calculate SEZ exports
        export_per_sez = self.config.get('export_per_fully_utilized_sez', 1.2)  # billion USD
        self.sez_exports = self.active_sezs * self.sez_utilization * export_per_sez
        
        print(f"Year {year}: SEZ exports: ${self.sez_exports:.2f} billion, Utilization: {self.sez_utilization*100:.1f}%")
    
    def simulate_investment_policy(self, year, global_conditions=None):
        """
        Simulate investment policy evolution.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External policy pressures
        """
        # Base policy improvement
        base_improvement = self.config.get('investment_policy_annual_improvement', 0.01)
        
        # Reform momentum (varies over time)
        reform_cycle_position = (year - 2025) % 5  # 5-year reform cycles
        if reform_cycle_position <= 1:  # Early in cycle - higher momentum
            reform_momentum = 0.02
        else:
            reform_momentum = 0.005
        
        # External policy pressure (international organizations, trade partners)
        external_pressure = 0
        if global_conditions and 'investment_policy_pressure' in global_conditions:
            external_pressure = global_conditions['investment_policy_pressure'] * 0.01
        
        # Random component (political factors, bureaucratic resistance)
        random_effect = random.uniform(-0.03, 0.03)
        
        # Calculate total policy change
        policy_change = base_improvement + reform_momentum + external_pressure + random_effect
        
        # Update investment policy index
        self.investment_policy_index = max(0.3, min(0.95, self.investment_policy_index + policy_change))
        
        # Update repatriation restrictions (downward trend)
        repatriation_change = -0.02 + random.uniform(-0.02, 0.04)  # Mostly decreasing with occasional reversals
        self.repatriation_restrictions = max(0.05, min(0.7, self.repatriation_restrictions + repatriation_change))
        
        # Update investment incentives (cyclical)
        incentive_cycle = 0.01 * np.sin((year - 2025) * 0.6)  # Cyclical component
        incentive_change = 0.005 + incentive_cycle + random.uniform(-0.02, 0.02)
        self.investment_incentives = max(0.3, min(0.8, self.investment_incentives + incentive_change))
        
        print(f"Year {year}: Investment Policy Index: {self.investment_policy_index:.2f}")
    
    def get_yearly_metrics(self):
        """
        Return the full history of investment metrics.
        
        Returns:
            dict: Time series of all tracked metrics
        """
        return self.yearly_metrics
    
    def get_investment_capital_formation(self):
        """
        Calculate gross fixed capital formation from investments.
        
        Returns:
            float: Total capital formation (domestic + foreign) in billion USD
        """
        return self.domestic_investment + self.fdi_inflow
