"""
Export sector model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class ExportSectorModel:
    """
    Model individual export sectors with unique parameters
    
    This class handles the simulation of export sectors like RMG, pharmaceuticals,
    IT services, leather goods, jute products, and agricultural products.
    """
    
    def __init__(self, 
                 sector_name: str,
                 current_volume: float,
                 growth_trajectory: float,
                 global_market_share: float,
                 value_chain_position: str,
                 competitiveness_factors: Dict[str, float],
                 tariff_exposure: float,
                 subsectors: Optional[List[str]] = None):
        """
        Initialize an export sector model
        
        Args:
            sector_name: Name of the export sector
            current_volume: Current export volume in million USD
            growth_trajectory: Base annual growth rate
            global_market_share: Current global market share (0-1)
            value_chain_position: Position in global value chain (low, low_to_mid, mid, mid_to_high, high)
            competitiveness_factors: Dict of factors affecting competitiveness with values (0-1)
            tariff_exposure: Vulnerability to tariff changes (0-1)
            subsectors: List of subsectors within this export sector
        """
        self.sector_name = sector_name
        self.current_volume = current_volume
        self.base_growth_rate = growth_trajectory
        self.global_market_share = global_market_share
        self.value_chain_position = value_chain_position
        self.competitiveness_factors = competitiveness_factors
        self.tariff_exposure = tariff_exposure
        self.subsectors = subsectors or []
        
        # Initialize historical data storage
        self.historical_volumes = {0: current_volume}  # year 0 = start_year
        self.historical_market_shares = {0: global_market_share}
        self.historical_competitiveness = {0: self._calculate_overall_competitiveness()}
        
        # Initialize subsector models if applicable
        self.subsector_models = {}
        if subsectors:
            # In a real implementation, we would initialize subsector models here
            pass
    
    def _calculate_overall_competitiveness(self) -> float:
        """
        Calculate overall competitiveness score based on competitiveness factors
        
        Returns:
            float: Overall competitiveness score (0-1)
        """
        if not self.competitiveness_factors:
            return 0.5
        
        return sum(self.competitiveness_factors.values()) / len(self.competitiveness_factors)
    
    def simulate_year(self, 
                     year_index: int,
                     global_demand_growth: float,
                     tariff_changes: Dict[str, float],
                     exchange_rate_impact: float,
                     logistics_performance: float,
                     trade_policy_impact: float,
                     compliance_impact: float,
                     digital_adoption: float,
                     competitor_growth: Dict[str, float]) -> Dict[str, Any]:
        """
        Simulate this export sector for one year
        
        Args:
            year_index: Year index from simulation start (0 = start_year)
            global_demand_growth: Global demand growth rate
            tariff_changes: Tariff changes by destination market
            exchange_rate_impact: Impact of exchange rate movements (-1 to 1 scale)
            logistics_performance: Logistics performance index (0-1)
            trade_policy_impact: Net impact of trade policies (-1 to 1 scale)
            compliance_impact: Net impact of compliance requirements (-1 to 1 scale)
            digital_adoption: Level of digital technology adoption (0-1)
            competitor_growth: Growth rates of competitor countries
            
        Returns:
            Dict with simulation results for this year
        """
        # Get previous year's volume
        prev_volume = self.historical_volumes.get(year_index - 1, self.current_volume)
        prev_competitiveness = self.historical_competitiveness.get(year_index - 1, 
                                                                  self._calculate_overall_competitiveness())
        prev_market_share = self.historical_market_shares.get(year_index - 1, self.global_market_share)
        
        # Calculate base growth adjusted for global demand
        adjusted_growth = self.base_growth_rate * (1 + 0.5 * (global_demand_growth - 0.03))
        
        # Calculate tariff impact
        if tariff_changes:
            weighted_tariff_impact = -sum(tariff_changes.values()) / len(tariff_changes) * self.tariff_exposure
        else:
            weighted_tariff_impact = 0.0
        
        # Calculate competitiveness evolution
        competitiveness_change = (
            0.2 * exchange_rate_impact +
            0.3 * (logistics_performance - 0.6) +  # Assuming 0.6 is the baseline logistics performance
            0.2 * trade_policy_impact +
            0.1 * digital_adoption +
            -0.2 * compliance_impact  # Compliance has cost implications initially
        )
        
        # Apply competitiveness change with constraints
        new_competitiveness = max(0.1, min(1.0, prev_competitiveness + competitiveness_change * 0.1))
        
        # Calculate competitor impact
        competitor_impact = 0
        for competitor, growth in competitor_growth.items():
            competitor_impact -= (growth - self.base_growth_rate) * 0.2
        
        # Calculate total growth rate
        effective_growth_rate = (
            adjusted_growth +
            weighted_tariff_impact +
            (new_competitiveness - prev_competitiveness) * 2 +  # Competitiveness has strong impact
            competitor_impact
        )
        
        # Apply some random variation (economic shocks, etc.)
        random_variation = np.random.normal(0, 0.02)  # 2% standard deviation
        effective_growth_rate += random_variation
        
        # Calculate new volume
        new_volume = prev_volume * (1 + effective_growth_rate)
        
        # Calculate new market share based on growth differential with global market
        global_market_growth = global_demand_growth
        market_share_change = 0.2 * (effective_growth_rate - global_market_growth)
        new_market_share = max(0, min(1, prev_market_share * (1 + market_share_change)))
        
        # Store historical data
        self.historical_volumes[year_index] = new_volume
        self.historical_market_shares[year_index] = new_market_share
        self.historical_competitiveness[year_index] = new_competitiveness
        
        # Return results
        return {
            'sector_name': self.sector_name,
            'year_index': year_index,
            'export_volume': new_volume,
            'growth_rate': effective_growth_rate,
            'global_market_share': new_market_share,
            'competitiveness': new_competitiveness,
            'value_chain_position': self.value_chain_position,  # This could evolve in a more sophisticated model
            'tariff_impact': weighted_tariff_impact,
            'exchange_rate_impact': exchange_rate_impact,
            'logistics_impact': logistics_performance - 0.6,
            'trade_policy_impact': trade_policy_impact,
            'compliance_impact': compliance_impact,
            'competitor_impact': competitor_impact,
            'random_variation': random_variation
        }
    
    def simulate_subsectors(self, year_index, **kwargs):
        """
        Simulate all subsectors for this export sector
        
        Args:
            year_index: Year index from simulation start
            **kwargs: Parameters to pass to subsector simulation
            
        Returns:
            Dict of simulation results by subsector
        """
        if not self.subsector_models:
            return {}
        
        subsector_results = {}
        for name, model in self.subsector_models.items():
            subsector_results[name] = model.simulate_year(year_index, **kwargs)
        
        return subsector_results


class RMGSectorModel(ExportSectorModel):
    """
    Ready-Made Garment industry specific model
    """
    
    def __init__(self, config):
        """
        Initialize RMG sector model with additional RMG-specific parameters
        
        Args:
            config: Configuration dictionary for RMG sector
        """
        super().__init__(
            sector_name=config['name'],
            current_volume=config['current_volume'],
            growth_trajectory=config['growth_trajectory'],
            global_market_share=config['global_market_share'],
            value_chain_position=config['value_chain_position'],
            competitiveness_factors=config['competitiveness_factors'],
            tariff_exposure=config['tariff_exposure'],
            subsectors=config['subsectors']
        )
        
        # RMG-specific attributes
        self.buyer_concentration = 0.7  # High concentration in US and EU markets
        self.fashion_responsiveness = 0.6  # Moderate ability to respond to fashion cycles
        self.compliance_cost_structure = {
            'labor': 0.5,
            'environmental': 0.3,
            'safety': 0.4
        }
        self.backward_linkage_development = 0.4  # Moderate backward linkage development
        self.foreign_ownership = 0.3  # 30% foreign ownership
    
    def simulate_year(self, year_index, **kwargs):
        """
        Extend the base simulation with RMG-specific factors
        """
        # Get base simulation results
        results = super().simulate_year(year_index, **kwargs)
        
        # Add RMG-specific simulation factors
        
        # Simulate fashion cycle responsiveness improvement
        self.fashion_responsiveness = min(0.9, self.fashion_responsiveness + 0.02)
        
        # Simulate backward linkage development
        self.backward_linkage_development = min(0.8, self.backward_linkage_development + 0.015)
        
        # Impact of compliance costs
        compliance_cost_impact = -(sum(self.compliance_cost_structure.values()) / len(self.compliance_cost_structure)) * 0.1
        
        # Adjust results with RMG-specific factors
        results['export_volume'] *= (1 + compliance_cost_impact)
        results['fashion_responsiveness'] = self.fashion_responsiveness
        results['backward_linkage_development'] = self.backward_linkage_development
        results['buyer_concentration'] = max(0.5, self.buyer_concentration - 0.01)  # Gradual diversification
        
        return results


class EmergingSectorModel(ExportSectorModel):
    """
    Model for emerging export sectors (pharmaceuticals, IT services, etc.)
    """
    
    def __init__(self, config):
        """
        Initialize emerging sector model with additional parameters
        
        Args:
            config: Configuration dictionary for the emerging sector
        """
        super().__init__(
            sector_name=config['name'],
            current_volume=config['current_volume'],
            growth_trajectory=config['growth_trajectory'],
            global_market_share=config['global_market_share'],
            value_chain_position=config['value_chain_position'],
            competitiveness_factors=config['competitiveness_factors'],
            tariff_exposure=config['tariff_exposure'],
            subsectors=config['subsectors']
        )
        
        # Emerging sector specific attributes
        self.niche_market_penetration = 0.3
        self.product_quality_level = 0.6
        self.knowledge_spillover_coefficient = 0.4
        self.skill_premium = 0.2  # Premium paid for skilled workers
        self.patent_count = 5  # Initial patents
        self.global_reputation = 0.4  # Initial global reputation
    
    def simulate_year(self, year_index, **kwargs):
        """
        Extend the base simulation with emerging sector specific factors
        """
        # Get base simulation results
        results = super().simulate_year(year_index, **kwargs)
        
        # Simulate quality improvement
        quality_improvement = 0.03 * (kwargs.get('r_and_d_investment', 0.5))
        self.product_quality_level = min(0.95, self.product_quality_level + quality_improvement)
        
        # Simulate niche market penetration
        market_penetration_growth = 0.04 * self.product_quality_level
        self.niche_market_penetration = min(0.8, self.niche_market_penetration + market_penetration_growth)
        
        # Simulate patent development
        new_patents = np.random.poisson(1 + self.knowledge_spillover_coefficient * 2)
        self.patent_count += new_patents
        
        # Simulate reputation growth
        reputation_growth = 0.03 * self.product_quality_level
        self.global_reputation = min(0.9, self.global_reputation + reputation_growth)
        
        # Adjust results with sector-specific factors
        premium_factor = 1 + (self.global_reputation * 0.2)
        results['export_volume'] *= premium_factor
        
        # Add sector-specific metrics to results
        results['product_quality'] = self.product_quality_level
        results['niche_market_penetration'] = self.niche_market_penetration
        results['patent_count'] = self.patent_count
        results['global_reputation'] = self.global_reputation
        
        return results


class TraditionalSectorModel(ExportSectorModel):
    """
    Model for traditional export sectors (jute, tea, agricultural products)
    """
    
    def __init__(self, config):
        """
        Initialize traditional sector model with additional parameters
        
        Args:
            config: Configuration dictionary for the traditional sector
        """
        super().__init__(
            sector_name=config['name'],
            current_volume=config['current_volume'],
            growth_trajectory=config['growth_trajectory'],
            global_market_share=config['global_market_share'],
            value_chain_position=config['value_chain_position'],
            competitiveness_factors=config['competitiveness_factors'],
            tariff_exposure=config['tariff_exposure'],
            subsectors=config['subsectors']
        )
        
        # Traditional sector specific attributes
        self.commodity_price_sensitivity = 0.8  # High sensitivity to commodity prices
        self.seasonal_volatility = 0.15  # Seasonal production volatility
        self.processing_technology_level = 0.4  # Processing technology level
        self.certification_coverage = 0.2  # Coverage of certifications (organic, fair trade)
        self.specialty_market_share = 0.1  # Share in specialty/premium markets
        self.climate_vulnerability = 0.7  # Vulnerability to climate change
    
    def simulate_year(self, year_index, **kwargs):
        """
        Extend the base simulation with traditional sector specific factors
        """
        # Get base simulation results
        results = super().simulate_year(year_index, **kwargs)
        
        # Simulate commodity price fluctuations
        price_fluctuation = np.random.normal(0, 0.1) * self.commodity_price_sensitivity
        
        # Simulate seasonal volatility 
        seasonal_effect = np.random.uniform(-self.seasonal_volatility, self.seasonal_volatility)
        
        # Simulate processing technology improvement
        tech_improvement = 0.02 * kwargs.get('technology_investment', 0.5)
        self.processing_technology_level = min(0.9, self.processing_technology_level + tech_improvement)
        
        # Simulate certification growth
        cert_growth = 0.03 * kwargs.get('sustainability_focus', 0.5)
        self.certification_coverage = min(0.8, self.certification_coverage + cert_growth)
        
        # Simulate specialty market growth
        specialty_growth = 0.04 * self.certification_coverage
        self.specialty_market_share = min(0.6, self.specialty_market_share + specialty_growth)
        
        # Climate impact
        climate_impact = -0.05 * self.climate_vulnerability * kwargs.get('climate_severity', 0.5)
        
        # Combine all factors
        combined_effect = price_fluctuation + seasonal_effect + climate_impact
        
        # Certification premium
        certification_premium = self.certification_coverage * 0.3
        
        # Adjust results with sector-specific factors
        results['export_volume'] *= (1 + combined_effect + certification_premium)
        
        # Add sector-specific metrics to results
        results['price_effect'] = price_fluctuation
        results['seasonal_effect'] = seasonal_effect
        results['climate_impact'] = climate_impact
        results['certification_premium'] = certification_premium
        results['processing_technology'] = self.processing_technology_level
        results['specialty_market_share'] = self.specialty_market_share
        
        return results
