import random
import numpy as np

class ServicesTradeModel:
    """
    Simulates Bangladesh's trade in services across various modes:
    - Mode 1: Cross-border supply (e.g., digital services)
    - Mode 2: Consumption abroad (e.g., tourism)
    - Mode 3: Commercial presence (e.g., foreign companies in Bangladesh)
    - Mode 4: Movement of natural persons (e.g., labor services, remittances)
    """
    
    def __init__(self, config):
        """
        Initialize the services trade model with configuration parameters.
        
        Args:
            config (dict): Configuration dictionary containing services trade parameters
        """
        self.config = config
        
        # Initialize Mode 4 (labor services/remittances)
        self.remittance_inflow = config.get('initial_remittance_inflow', 18.0)  # billion USD
        self.overseas_workers = config.get('initial_overseas_workers', 8.0)     # million people
        self.avg_remittance_per_worker = self.remittance_inflow / self.overseas_workers if self.overseas_workers > 0 else 0
        
        # Initialize Mode 2 (tourism)
        self.tourism_earnings = config.get('initial_tourism_earnings', 0.5)     # billion USD
        self.tourist_arrivals = config.get('initial_tourist_arrivals', 0.8)     # million people
        
        # Initialize Mode 1 (cross-border services)
        self.business_process_exports = config.get('initial_bpo_exports', 1.2)  # billion USD
        self.professional_services_exports = config.get('initial_professional_exports', 0.5)  # billion USD
        
        # Initialize Mode 3 (commercial presence)
        self.service_fdi_inflow = config.get('initial_service_fdi', 1.0)        # billion USD
        
        # Track metrics over time
        self.yearly_metrics = {
            'remittance_inflow': [self.remittance_inflow],
            'overseas_workers': [self.overseas_workers],
            'tourism_earnings': [self.tourism_earnings],
            'tourist_arrivals': [self.tourist_arrivals],
            'business_process_exports': [self.business_process_exports],
            'professional_services_exports': [self.professional_services_exports],
            'service_fdi_inflow': [self.service_fdi_inflow]
        }
    
    def simulate_step(self, year, global_conditions=None):
        """
        Simulate one year of services trade development.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External conditions affecting services trade
        
        Returns:
            dict: Updated services trade metrics
        """
        # Simulate each mode of services trade
        self.simulate_remittances(year, global_conditions)
        self.simulate_tourism(year, global_conditions)
        self.simulate_business_process_services(year, global_conditions)
        self.simulate_professional_services(year, global_conditions)
        self.simulate_service_fdi(year, global_conditions)
        
        # Compile and return results
        current_metrics = {
            'remittance_inflow': self.remittance_inflow,
            'overseas_workers': self.overseas_workers,
            'tourism_earnings': self.tourism_earnings,
            'tourist_arrivals': self.tourist_arrivals,
            'business_process_exports': self.business_process_exports,
            'professional_services_exports': self.professional_services_exports,
            'service_fdi_inflow': self.service_fdi_inflow
        }
        
        # Store metrics for this year
        for key, value in current_metrics.items():
            self.yearly_metrics[key].append(value)
            
        return current_metrics
    
    def simulate_remittances(self, year, global_conditions=None):
        """
        Simulate Mode 4 services: remittances and overseas worker deployments.
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External economic conditions
        """
        # Base growth rate for overseas workers
        base_worker_growth = self.config.get('worker_annual_growth_rate', 0.04)
        
        # Global labor market conditions effect
        global_effect = 0
        if global_conditions and 'global_labor_demand' in global_conditions:
            global_effect = global_conditions['global_labor_demand'] * 0.05
        
        # Skill development effect (gradual shift to higher-skilled workers)
        skill_effect = self.config.get('worker_skill_improvement', 0.02)
        
        # Random variance component
        random_effect = random.uniform(-0.02, 0.03)
        
        # Calculate total growth in overseas workers
        worker_growth_rate = base_worker_growth + global_effect + random_effect
        self.overseas_workers *= (1 + worker_growth_rate)
        
        # Calculate changes in remittance per worker (affected by skill composition)
        remittance_per_worker_growth = skill_effect + random.uniform(-0.01, 0.02)
        self.avg_remittance_per_worker *= (1 + remittance_per_worker_growth)
        
        # Calculate total remittance inflow
        previous_remittance = self.remittance_inflow
        self.remittance_inflow = self.overseas_workers * self.avg_remittance_per_worker
        
        # Apply external shocks from destination economies
        if global_conditions and 'destination_economy_shock' in global_conditions:
            shock_factor = global_conditions['destination_economy_shock']
            self.remittance_inflow *= (1 + shock_factor)
        
        print(f"Year {year}: Remittance inflow: ${self.remittance_inflow:.2f} billion, " +
              f"Growth: {((self.remittance_inflow/previous_remittance)-1)*100:.1f}%")
    
    def simulate_tourism(self, year, global_conditions=None):
        """
        Simulate Mode 2 services: tourism
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External tourism conditions
        """
        # Base growth in tourist arrivals
        base_arrival_growth = self.config.get('tourist_arrival_growth', 0.06)
        
        # Infrastructure effect
        infrastructure_effect = self.config.get('tourism_infrastructure_development', 0.02)
        
        # Marketing effect
        marketing_effect = self.config.get('tourism_marketing_effectiveness', 0.01)
        
        # Global tourism trends
        global_effect = 0
        if global_conditions and 'global_tourism_growth' in global_conditions:
            global_effect = global_conditions['global_tourism_growth'] * 0.8  # Elasticity factor
        
        # Random variance + potential shocks (e.g., security incidents)
        random_effect = random.uniform(-0.08, 0.05)
        
        # Calculate total growth in tourist arrivals
        arrival_growth_rate = base_arrival_growth + infrastructure_effect + marketing_effect + global_effect + random_effect
        previous_arrivals = self.tourist_arrivals
        self.tourist_arrivals *= (1 + arrival_growth_rate)
        
        # Calculate average spending per tourist (gradual improvement with better facilities)
        spending_growth = self.config.get('tourist_spending_growth', 0.03) + random.uniform(-0.01, 0.02)
        avg_spending = self.tourism_earnings / previous_arrivals if previous_arrivals > 0 else 0
        avg_spending *= (1 + spending_growth)
        
        # Calculate total tourism earnings
        self.tourism_earnings = self.tourist_arrivals * avg_spending
        
        print(f"Year {year}: Tourism earnings: ${self.tourism_earnings:.2f} billion, " +
              f"Tourist arrivals: {self.tourist_arrivals:.2f} million")
    
    def simulate_business_process_services(self, year, global_conditions=None):
        """
        Simulate Mode 1 services: business process outsourcing
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External BPO market conditions
        """
        # Base growth rate
        base_growth_rate = self.config.get('bpo_annual_growth_rate', 0.12)
        
        # Digital infrastructure effect
        if 'digital_infrastructure_index' in self.config:
            digital_effect = self.config['digital_infrastructure_index'] * 0.1
        else:
            digital_effect = 0.03  # Default effect
        
        # Skill development effect
        skill_effect = self.config.get('bpo_skill_development', 0.04)
        
        # Global outsourcing demand
        global_effect = 0
        if global_conditions and 'global_outsourcing_demand' in global_conditions:
            global_effect = global_conditions['global_outsourcing_demand'] * 0.08
        
        # Competitive dynamics (how BD compares to other outsourcing hubs)
        competitive_effect = self.config.get('bpo_competitive_position', -0.02)  # Initially negative
        
        # Random variance
        random_effect = random.uniform(-0.04, 0.06)
        
        # Calculate total growth rate
        total_growth_rate = base_growth_rate + digital_effect + skill_effect + global_effect + competitive_effect + random_effect
        
        # Update BPO exports
        self.business_process_exports *= (1 + total_growth_rate)
        
        print(f"Year {year}: Business process service exports: ${self.business_process_exports:.2f} billion")
    
    def simulate_professional_services(self, year, global_conditions=None):
        """
        Simulate Mode 1 services: professional and technical services
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External market conditions
        """
        # Base growth rate
        base_growth_rate = self.config.get('professional_services_growth_rate', 0.09)
        
        # Skill development effect (higher impact for professional services)
        skill_effect = self.config.get('professional_skill_development', 0.05)
        
        # Institutional quality effect (contracts, IP protection, etc.)
        institutional_effect = self.config.get('institutional_quality_effect', 0.01)
        
        # Regional integration effect
        regional_effect = self.config.get('regional_services_integration', 0.02)
        
        # Global demand
        global_effect = 0
        if global_conditions and 'global_services_demand' in global_conditions:
            global_effect = global_conditions['global_services_demand'] * 0.06
        
        # Random variance
        random_effect = random.uniform(-0.03, 0.05)
        
        # Calculate total growth rate
        total_growth_rate = base_growth_rate + skill_effect + institutional_effect + regional_effect + global_effect + random_effect
        
        # Update professional services exports
        self.professional_services_exports *= (1 + total_growth_rate)
        
        print(f"Year {year}: Professional service exports: ${self.professional_services_exports:.2f} billion")
    
    def simulate_service_fdi(self, year, global_conditions=None):
        """
        Simulate Mode 3 services: commercial presence through FDI
        
        Args:
            year (int): The current simulation year
            global_conditions (dict, optional): External investment conditions
        """
        # Base growth rate
        base_growth_rate = self.config.get('service_fdi_growth_rate', 0.07)
        
        # Business environment effect
        business_env_effect = self.config.get('business_environment_quality', 0.01)
        
        # Market size effect (as domestic economy grows)
        market_size_effect = self.config.get('domestic_market_growth', 0.03)
        
        # Policy liberalization effect
        policy_effect = self.config.get('service_sector_liberalization', 0.02)
        
        # Global investment climate
        global_effect = 0
        if global_conditions and 'global_fdi_flows' in global_conditions:
            global_effect = global_conditions['global_fdi_flows'] * 0.1
        
        # Random variance (includes large one-off investments)
        random_effect = random.uniform(-0.15, 0.25)
        
        # Calculate total growth rate
        total_growth_rate = base_growth_rate + business_env_effect + market_size_effect + policy_effect + global_effect + random_effect
        
        # Update service sector FDI
        self.service_fdi_inflow *= (1 + total_growth_rate)
        
        print(f"Year {year}: Service sector FDI: ${self.service_fdi_inflow:.2f} billion")
    
    def get_yearly_metrics(self):
        """
        Return the full history of services trade metrics.
        
        Returns:
            dict: Time series of all tracked metrics
        """
        return self.yearly_metrics
    
    def get_total_service_exports(self, year_index=-1):
        """
        Calculate total service exports across all modes for a given year.
        
        Args:
            year_index (int): Index in the simulation timeline (-1 = latest year)
        
        Returns:
            float: Total service exports in billion USD
        """
        # Mode 1: Cross-border supply (BPO + Professional)
        mode1 = (self.yearly_metrics['business_process_exports'][year_index] + 
                self.yearly_metrics['professional_services_exports'][year_index])
        
        # Mode 2: Tourism
        mode2 = self.yearly_metrics['tourism_earnings'][year_index]
        
        # Mode 4: Remittances (technically not exports in BOP but important service flow)
        mode4 = self.yearly_metrics['remittance_inflow'][year_index]
        
        # Note: Mode 3 (commercial presence) generates domestic activity, not direct exports
        
        return mode1 + mode2 + mode4
