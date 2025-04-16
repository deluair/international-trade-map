import random
import numpy as np

class DigitalTradeModel:
    """
    Simulates Bangladesh's digital trade ecosystem, including e-commerce adoption,
    digital services exports, digital trade policies, and infrastructure development.
    """
    
    def __init__(self, config):
        """
        Initialize the digital trade model with configuration parameters.
        
        Args:
            config (dict): Configuration dictionary containing digital trade parameters
        """
        self.config = config
        self.ecommerce_adoption_rate = config.get('initial_ecommerce_adoption_rate', 0.15)
        self.digital_services_export_value = config.get('initial_digital_services_exports', 1.5)  # in billion USD
        self.digital_infrastructure_index = config.get('initial_digital_infrastructure_index', 0.35)  # 0-1 scale
        self.digital_trade_barriers = config.get('initial_digital_trade_barriers', 0.6)  # 0-1 scale (1 = highest barriers)
        
        # Track metrics over time
        self.yearly_metrics = {
            'ecommerce_adoption_rate': [self.ecommerce_adoption_rate],
            'digital_services_exports': [self.digital_services_export_value],
            'digital_infrastructure_index': [self.digital_infrastructure_index],
            'digital_trade_barriers': [self.digital_trade_barriers]
        }
    
    def simulate_step(self, year, global_conditions=None):
        """
        Simulate one year of digital trade development.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External conditions affecting digital trade
        
        Returns:
            dict: Updated digital trade metrics
        """
        # Simulate the components of digital trade
        self.simulate_ecommerce_adoption(year, global_conditions)
        self.simulate_digital_services_exports(year, global_conditions)
        self.simulate_digital_infrastructure(year)
        self.simulate_digital_trade_policy(year, global_conditions)
        
        # Compile and return results
        current_metrics = {
            'ecommerce_adoption_rate': self.ecommerce_adoption_rate,
            'digital_services_exports': self.digital_services_export_value,
            'digital_infrastructure_index': self.digital_infrastructure_index,
            'digital_trade_barriers': self.digital_trade_barriers
        }
        
        # Store metrics for this year
        for key, value in current_metrics.items():
            self.yearly_metrics[key].append(value)
            
        return current_metrics
    
    def simulate_ecommerce_adoption(self, year, global_conditions=None):
        """
        Simulate changes in e-commerce adoption rates.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External factors affecting e-commerce
        """
        # Base growth rate for e-commerce adoption
        base_growth = self.config.get('ecommerce_annual_growth_rate', 0.08)
        
        # Adjust for digital infrastructure quality
        infrastructure_effect = self.digital_infrastructure_index * 0.05
        
        # Adjust for global e-commerce trends
        global_effect = 0
        if global_conditions and 'global_ecommerce_growth' in global_conditions:
            global_effect = global_conditions['global_ecommerce_growth'] * 0.02
        
        # Random variance component
        random_effect = random.uniform(-0.01, 0.02)
        
        # Calculate total growth and update adoption rate
        total_growth = base_growth + infrastructure_effect + global_effect + random_effect
        
        # Apply S-curve adoption model (slower at extremes, faster in middle)
        s_curve_factor = 4 * self.ecommerce_adoption_rate * (1 - self.ecommerce_adoption_rate)
        adjusted_growth = total_growth * s_curve_factor
        
        self.ecommerce_adoption_rate = min(0.95, self.ecommerce_adoption_rate + adjusted_growth)
        
        print(f"Year {year}: E-commerce adoption rate: {self.ecommerce_adoption_rate:.4f}")
    
    def simulate_digital_services_exports(self, year, global_conditions=None):
        """
        Simulate growth in digital services exports.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External factors affecting digital exports
        """
        # Base growth rate
        base_growth_rate = self.config.get('digital_services_growth_rate', 0.12)
        
        # Adjust for global demand
        global_demand_effect = 0
        if global_conditions and 'global_digital_demand' in global_conditions:
            global_demand_effect = global_conditions['global_digital_demand'] * 0.05
        
        # Adjust for skills development
        skills_effect = self.config.get('digital_skills_development', 0.03)
        
        # Adjust for trade barriers
        barrier_effect = -0.05 * self.digital_trade_barriers
        
        # Random variance
        random_effect = random.uniform(-0.02, 0.04)
        
        # Calculate total growth rate
        total_growth_rate = base_growth_rate + global_demand_effect + skills_effect + barrier_effect + random_effect
        
        # Update digital services export value
        self.digital_services_export_value *= (1 + total_growth_rate)
        
        print(f"Year {year}: Digital services exports: ${self.digital_services_export_value:.2f} billion")
    
    def simulate_digital_infrastructure(self, year):
        """
        Simulate development of digital infrastructure.
        
        Args:
            year (int): The current simulation year
        """
        # Base improvement rate
        base_improvement = self.config.get('digital_infrastructure_annual_improvement', 0.03)
        
        # Government investment effect
        govt_investment = self.config.get('govt_digital_investment', 0.02)
        
        # Private sector investment (affected by economic growth)
        private_investment = self.config.get('private_digital_investment', 0.02)
        
        # Random variance
        random_effect = random.uniform(-0.01, 0.02)
        
        # Calculate total improvement
        total_improvement = base_improvement + govt_investment + private_investment + random_effect
        
        # S-curve improvement model (diminishing returns as infrastructure improves)
        s_curve_factor = 4 * self.digital_infrastructure_index * (1 - self.digital_infrastructure_index)
        adjusted_improvement = total_improvement * s_curve_factor
        
        # Update digital infrastructure index (0-1 scale)
        self.digital_infrastructure_index = min(0.95, self.digital_infrastructure_index + adjusted_improvement)
        
        print(f"Year {year}: Digital infrastructure index: {self.digital_infrastructure_index:.4f}")
    
    def simulate_digital_trade_policy(self, year, global_conditions=None):
        """
        Simulate changes in digital trade policy and barriers.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External policy factors
        """
        # Base policy improvement
        base_improvement = self.config.get('digital_policy_annual_improvement', 0.02)
        
        # Global policy pressure (e.g., WTO e-commerce initiatives)
        global_effect = 0
        if global_conditions and 'global_digital_policy_pressure' in global_conditions:
            global_effect = global_conditions['global_digital_policy_pressure'] * 0.03
        
        # Regional harmonization effect
        regional_effect = self.config.get('regional_digital_harmonization', 0.01)
        
        # Random variance (including policy reversals)
        random_effect = random.uniform(-0.03, 0.02)
        
        # Calculate total reduction in barriers
        total_reduction = base_improvement + global_effect + regional_effect + random_effect
        
        # Update digital trade barriers (lower is better)
        self.digital_trade_barriers = max(0.1, self.digital_trade_barriers - total_reduction)
        
        print(f"Year {year}: Digital trade barriers index: {self.digital_trade_barriers:.4f}")
    
    def get_yearly_metrics(self):
        """
        Return the full history of digital trade metrics.
        
        Returns:
            dict: Time series of all tracked metrics
        """
        return self.yearly_metrics
