"""
Global market model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class GlobalMarketModel:
    """
    Model external market conditions affecting Bangladeshi trade
    
    This class simulates global market conditions, including demand in key markets,
    competitor dynamics, and supply chain reconfigurations.
    """
    
    def __init__(self, config):
        """
        Initialize global market model
        
        Args:
            config: Configuration dictionary for global market parameters
        """
        # GDP growth rates for key markets
        self.gdp_growth = config.get('gdp_growth', {})
        
        # Market demand growth by sector
        self.market_demand_growth = config.get('market_demand_growth', {})
        
        # Competitor growth rates
        self.competitor_growth = config.get('competitor_growth', {})
        
        # Supply chain reconfiguration parameters
        self.supply_chain_reconfiguration = config.get('supply_chain_reconfiguration', {})
        
        # Initialize sub-models
        self.key_markets = KeyMarketsModel(self.gdp_growth)
        self.competitors = CompetitorDynamicsModel(self.competitor_growth)
        self.supply_chain = SupplyChainModel(self.supply_chain_reconfiguration)
        
        # Historical data
        self.historical_conditions = {}
    
    def simulate_global_markets(self, 
                              year_index: int, 
                              simulation_year: int,
                              global_scenario: str = 'baseline') -> Dict[str, Any]:
        """
        Simulate global market conditions for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            global_scenario: Global scenario to simulate ('baseline', 'optimistic', 'pessimistic')
            
        Returns:
            Dict with global market simulation results
        """
        # Apply scenario adjustments
        gdp_multiplier = 1.0
        demand_multiplier = 1.0
        competitor_multiplier = 1.0
        supply_chain_multiplier = 1.0
        
        if global_scenario == 'optimistic':
            gdp_multiplier = 1.2
            demand_multiplier = 1.3
            competitor_multiplier = 0.9  # Lower competitor growth is better for Bangladesh
            supply_chain_multiplier = 1.2
        elif global_scenario == 'pessimistic':
            gdp_multiplier = 0.7
            demand_multiplier = 0.6
            competitor_multiplier = 1.2  # Higher competitor growth is worse for Bangladesh
            supply_chain_multiplier = 0.8
        
        # Simulate key market conditions
        markets_result = self.key_markets.simulate_markets(
            year_index=year_index,
            simulation_year=simulation_year,
            gdp_multiplier=gdp_multiplier,
            demand_multiplier=demand_multiplier
        )
        
        # Simulate competitor dynamics
        competitors_result = self.competitors.simulate_competitors(
            year_index=year_index,
            simulation_year=simulation_year,
            gdp_growth=markets_result['gdp_growth'],
            competitor_multiplier=competitor_multiplier
        )
        
        # Simulate supply chain reconfiguration
        supply_chain_result = self.supply_chain.simulate_reconfiguration(
            year_index=year_index,
            simulation_year=simulation_year,
            global_tensions=0.5,  # Placeholder, should come from geopolitical model
            supply_chain_multiplier=supply_chain_multiplier
        )
        
        # Calculate overall market conditions
        market_opportunity = markets_result['weighted_growth'] * 0.6 - competitors_result['weighted_growth'] * 0.4
        supply_chain_opportunity = supply_chain_result['china_plus_one_benefit'] - supply_chain_result['nearshoring_impact']
        
        # Calculate sector-specific demand conditions
        sector_demand = {}
        for sector, base_growth in self.market_demand_growth.items():
            # Adjust sector growth based on market and competitor conditions
            sector_growth = base_growth * demand_multiplier
            
            # Competitor impact varies by sector
            competitor_impact = 0
            for competitor, growth_rates in self.competitor_growth.items():
                if sector in growth_rates:
                    competitor_impact -= (growth_rates[sector] * competitor_multiplier - base_growth) * 0.2
            
            # Supply chain impact varies by sector
            if sector == 'rmg':
                sc_impact = supply_chain_opportunity * 0.8  # RMG benefits strongly from supply chain shifts
            elif sector in ['leather', 'footwear']:
                sc_impact = supply_chain_opportunity * 0.6  # Leather also benefits
            elif sector in ['electronics', 'light_engineering']:
                sc_impact = supply_chain_opportunity * 0.4  # Some benefit
            else:
                sc_impact = supply_chain_opportunity * 0.2  # Limited benefit
            
            # Calculate effective sector growth
            effective_growth = sector_growth + competitor_impact + sc_impact
            
            # Add random variation
            random_variation = np.random.normal(0, 0.01)
            effective_growth += random_variation
            
            sector_demand[sector] = {
                'base_growth': base_growth,
                'effective_growth': effective_growth,
                'competitor_impact': competitor_impact,
                'supply_chain_impact': sc_impact,
                'random_variation': random_variation,
            }
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'global_scenario': global_scenario,
            'key_markets': markets_result,
            'competitors': competitors_result,
            'supply_chain': supply_chain_result,
            'market_opportunity': market_opportunity,
            'supply_chain_opportunity': supply_chain_opportunity,
            'sector_demand': sector_demand,
        }
        
        # Store historical data
        self.historical_conditions[year_index] = results
        
        return results
        
        
class KeyMarketsModel:
    """
    Model demand conditions in key export markets
    """
    
    def __init__(self, gdp_growth_config):
        """
        Initialize key markets model
        
        Args:
            gdp_growth_config: Configuration dictionary for GDP growth rates
        """
        self.base_gdp_growth = gdp_growth_config
        
        # Market importance for Bangladesh exports
        self.market_weights = {
            'usa': 0.25,
            'eu': 0.55,
            'china': 0.03,
            'india': 0.02,
            'japan': 0.03,
            'asean': 0.04,
            'other': 0.08,
        }
        
        # Market characteristics
        self.market_characteristics = {
            'usa': {
                'price_sensitivity': 0.6,
                'quality_sensitivity': 0.7,
                'lead_time_sensitivity': 0.8,
                'compliance_sensitivity': 0.9,
                'e_commerce_penetration': 0.7,
                'ethical_consumption_premium': 0.6,
            },
            'eu': {
                'price_sensitivity': 0.5,
                'quality_sensitivity': 0.8,
                'lead_time_sensitivity': 0.7,
                'compliance_sensitivity': 0.9,
                'e_commerce_penetration': 0.7,
                'ethical_consumption_premium': 0.8,
            },
            'china': {
                'price_sensitivity': 0.8,
                'quality_sensitivity': 0.6,
                'lead_time_sensitivity': 0.7,
                'compliance_sensitivity': 0.4,
                'e_commerce_penetration': 0.8,
                'ethical_consumption_premium': 0.3,
            },
            'india': {
                'price_sensitivity': 0.9,
                'quality_sensitivity': 0.5,
                'lead_time_sensitivity': 0.6,
                'compliance_sensitivity': 0.3,
                'e_commerce_penetration': 0.5,
                'ethical_consumption_premium': 0.2,
            },
            'japan': {
                'price_sensitivity': 0.4,
                'quality_sensitivity': 0.9,
                'lead_time_sensitivity': 0.8,
                'compliance_sensitivity': 0.8,
                'e_commerce_penetration': 0.6,
                'ethical_consumption_premium': 0.7,
            },
            'asean': {
                'price_sensitivity': 0.7,
                'quality_sensitivity': 0.6,
                'lead_time_sensitivity': 0.7,
                'compliance_sensitivity': 0.5,
                'e_commerce_penetration': 0.6,
                'ethical_consumption_premium': 0.4,
            },
            'other': {
                'price_sensitivity': 0.7,
                'quality_sensitivity': 0.6,
                'lead_time_sensitivity': 0.6,
                'compliance_sensitivity': 0.5,
                'e_commerce_penetration': 0.5,
                'ethical_consumption_premium': 0.4,
            },
        }
        
        # Historical data
        self.historical_markets = {}
    
    def simulate_markets(self,
                        year_index: int,
                        simulation_year: int,
                        gdp_multiplier: float = 1.0,
                        demand_multiplier: float = 1.0) -> Dict[str, Any]:
        """
        Simulate key market conditions for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            gdp_multiplier: Multiplier for GDP growth rates
            demand_multiplier: Multiplier for demand growth
            
        Returns:
            Dict with key markets simulation results
        """
        # Calculate current GDP growth rates
        gdp_growth = {}
        for market, base_growth in self.base_gdp_growth.items():
            # Apply multiplier with some random variation
            random_variation = np.random.normal(0, 0.005)
            effective_growth = base_growth * gdp_multiplier + random_variation
            gdp_growth[market] = effective_growth
        
        # Market characteristic evolution
        for market, chars in self.market_characteristics.items():
            # E-commerce penetration increases over time
            chars['e_commerce_penetration'] = min(0.98, chars['e_commerce_penetration'] + 0.02)
            
            # Ethical consumption premium increases in developed markets
            if market in ['usa', 'eu', 'japan']:
                chars['ethical_consumption_premium'] = min(0.95, chars['ethical_consumption_premium'] + 0.01)
            else:
                chars['ethical_consumption_premium'] = min(0.7, chars['ethical_consumption_premium'] + 0.02)
            
            # Quality sensitivity generally increases
            chars['quality_sensitivity'] = min(0.95, chars['quality_sensitivity'] + 0.01)
            
            # Compliance sensitivity increases in most markets
            if market not in ['china', 'india']:
                chars['compliance_sensitivity'] = min(0.95, chars['compliance_sensitivity'] + 0.01)
        
        # Calculate market demand conditions
        market_demand = {}
        weighted_growth = 0
        
        for market, weight in self.market_weights.items():
            market_gdp_growth = gdp_growth.get(market, 0.03)  # Default to 3% if not specified
            
            # Base demand growth is related to GDP growth
            base_demand_growth = market_gdp_growth * 1.2  # Demand grows faster than GDP
            
            # Apply demand multiplier
            effective_demand_growth = base_demand_growth * demand_multiplier
            
            # Market-specific adjustments
            if market == 'usa':
                # US retail market adjustments
                consumer_confidence_effect = np.random.normal(0, 0.01)
                effective_demand_growth += consumer_confidence_effect
            elif market == 'eu':
                # EU market adjustments
                aging_population_effect = -0.002  # Small negative effect from aging population
                effective_demand_growth += aging_population_effect
            elif market == 'japan':
                # Japan market adjustments
                aging_effect = -0.005  # Stronger negative effect from aging
                effective_demand_growth += aging_effect
            elif market == 'china' or market == 'india':
                # Emerging market adjustments
                middle_class_growth_effect = 0.01  # Additional growth from expanding middle class
                effective_demand_growth += middle_class_growth_effect
            
            # Record market demand growth
            market_demand[market] = {
                'gdp_growth': market_gdp_growth,
                'demand_growth': effective_demand_growth,
                'characteristics': self.market_characteristics[market].copy(),
            }
            
            # Calculate weighted contribution to overall growth
            weighted_growth += effective_demand_growth * weight
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'gdp_growth': gdp_growth,
            'market_demand': market_demand,
            'weighted_growth': weighted_growth,
            'market_weights': self.market_weights.copy(),
        }
        
        # Store historical data
        self.historical_markets[year_index] = results
        
        return results


class CompetitorDynamicsModel:
    """
    Model competitor dynamics in global markets
    """
    
    def __init__(self, competitor_growth_config):
        """
        Initialize competitor dynamics model
        
        Args:
            competitor_growth_config: Configuration dictionary for competitor growth rates
        """
        self.competitor_growth = competitor_growth_config
        
        # Competitor competitive factors
        self.competitor_factors = {
            'vietnam': {
                'wage_level': 1.2,  # Relative to Bangladesh (1.0)
                'productivity': 1.4,
                'quality': 1.3,
                'lead_time': 1.2,
                'infrastructure': 1.5,
                'political_stability': 1.4,
            },
            'india': {
                'wage_level': 1.1,
                'productivity': 1.3,
                'quality': 1.2,
                'lead_time': 0.9,
                'infrastructure': 1.1,
                'political_stability': 1.0,
            },
            'cambodia': {
                'wage_level': 1.0,
                'productivity': 0.9,
                'quality': 0.9,
                'lead_time': 0.8,
                'infrastructure': 0.8,
                'political_stability': 0.7,
            },
            'ethiopia': {
                'wage_level': 0.6,
                'productivity': 0.7,
                'quality': 0.7,
                'lead_time': 0.6,
                'infrastructure': 0.5,
                'political_stability': 0.5,
            },
            'myanmar': {
                'wage_level': 0.8,
                'productivity': 0.7,
                'quality': 0.7,
                'lead_time': 0.7,
                'infrastructure': 0.6,
                'political_stability': 0.3,
            },
        }
        
        # Historical data
        self.historical_competitors = {}
    
    def simulate_competitors(self,
                           year_index: int,
                           simulation_year: int,
                           gdp_growth: Dict[str, float],
                           competitor_multiplier: float = 1.0) -> Dict[str, Any]:
        """
        Simulate competitor dynamics for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            gdp_growth: GDP growth rates for key markets
            competitor_multiplier: Multiplier for competitor growth rates
            
        Returns:
            Dict with competitor dynamics simulation results
        """
        # Calculate current competitor growth rates
        effective_growth = {}
        for competitor, sectors in self.competitor_growth.items():
            effective_growth[competitor] = {}
            for sector, growth_rate in sectors.items():
                # Apply multiplier with some random variation
                random_variation = np.random.normal(0, 0.01)
                effective_rate = growth_rate * competitor_multiplier + random_variation
                effective_growth[competitor][sector] = effective_rate
        
        # Update competitor competitiveness factors
        for competitor, factors in self.competitor_factors.items():
            # Wage level increases over time (faster in more successful competitors)
            base_wage_growth = 0.03
            if competitor in effective_growth:
                avg_growth = sum(effective_growth[competitor].values()) / len(effective_growth[competitor])
                wage_growth = base_wage_growth + avg_growth * 0.3
            else:
                wage_growth = base_wage_growth
            
            factors['wage_level'] *= (1 + wage_growth)
            
            # Productivity improves over time
            productivity_growth = 0.02 + (factors['infrastructure'] - 1) * 0.01
            factors['productivity'] *= (1 + productivity_growth)
            
            # Quality improves over time
            quality_growth = 0.02 + (factors['productivity'] - 1) * 0.01
            factors['quality'] = min(2.0, factors['quality'] * (1 + quality_growth))
            
            # Infrastructure improves based on development level
            if factors['infrastructure'] < 1.0:
                infra_growth = 0.03  # Faster catch-up for less developed countries
            else:
                infra_growth = 0.01  # Slower growth for more developed countries
            
            factors['infrastructure'] = min(2.0, factors['infrastructure'] * (1 + infra_growth))
        
        # Calculate overall competitive position
        competitive_position = {}
        for competitor, factors in self.competitor_factors.items():
            # Calculate competitiveness score (higher is more competitive)
            competitiveness = (
                (1 / factors['wage_level']) * 0.3 +  # Lower wage is better
                factors['productivity'] * 0.2 +
                factors['quality'] * 0.2 +
                factors['lead_time'] * 0.1 +
                factors['infrastructure'] * 0.1 +
                factors['political_stability'] * 0.1
            )
            
            competitive_position[competitor] = {
                'competitiveness_score': competitiveness,
                'factors': factors.copy(),
            }
            
            # Add growth rates if available
            if competitor in effective_growth:
                competitive_position[competitor]['growth_rates'] = effective_growth[competitor].copy()
        
        # Calculate weighted average competitor growth
        total_weight = 0
        weighted_growth = 0
        
        for competitor, position in competitive_position.items():
            if competitor in effective_growth:
                # Weight by competitiveness score
                weight = position['competitiveness_score']
                avg_growth = sum(effective_growth[competitor].values()) / len(effective_growth[competitor])
                
                weighted_growth += avg_growth * weight
                total_weight += weight
        
        if total_weight > 0:
            weighted_growth /= total_weight
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'effective_growth': effective_growth,
            'competitive_position': competitive_position,
            'weighted_growth': weighted_growth,
        }
        
        # Store historical data
        self.historical_competitors[year_index] = results
        
        return results


class SupplyChainModel:
    """
    Model global supply chain reconfiguration
    """
    
    def __init__(self, supply_chain_config):
        """
        Initialize supply chain reconfiguration model
        
        Args:
            supply_chain_config: Configuration dictionary for supply chain parameters
        """
        self.china_plus_one = supply_chain_config.get('china_plus_one', 0.7)
        self.nearshoring_trend = supply_chain_config.get('nearshoring_trend', 0.5)
        self.resilience_premium = supply_chain_config.get('resilience_premium', 0.2)
        
        # Lead time requirements
        self.lead_time_requirements = {
            'fast_fashion': 30,  # days
            'seasonal_fashion': 60,
            'basics': 90,
            'technical_products': 75,
        }
        
        # Inventory holding patterns
        self.inventory_patterns = {
            'just_in_time': 0.4,  # Share of supply chain using JIT
            'buffer_stock': 0.4,
            'strategic_reserves': 0.2,
        }
        
        # Historical data
        self.historical_chains = {}
    
    def simulate_reconfiguration(self,
                               year_index: int,
                               simulation_year: int,
                               global_tensions: float,
                               supply_chain_multiplier: float = 1.0) -> Dict[str, Any]:
        """
        Simulate supply chain reconfiguration for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            global_tensions: Level of global geopolitical tensions (0-1)
            supply_chain_multiplier: Multiplier for supply chain effects
            
        Returns:
            Dict with supply chain simulation results
        """
        # Update china plus one trend
        china_plus_one_change = 0.02 * global_tensions * supply_chain_multiplier
        self.china_plus_one = min(0.95, self.china_plus_one + china_plus_one_change)
        
        # Update nearshoring trend
        nearshoring_change = 0.03 * global_tensions * supply_chain_multiplier
        self.nearshoring_trend = min(0.9, self.nearshoring_trend + nearshoring_change)
        
        # Update resilience premium
        resilience_change = 0.01 * global_tensions * supply_chain_multiplier
        self.resilience_premium = min(0.5, self.resilience_premium + resilience_change)
        
        # Calculate lead time evolution
        for category, days in self.lead_time_requirements.items():
            # Shorter lead times for fast categories
            if category in ['fast_fashion', 'seasonal_fashion']:
                reduction_rate = 0.02  # 2% reduction per year
            else:
                reduction_rate = 0.01  # 1% reduction per year
            
            self.lead_time_requirements[category] = max(15, days * (1 - reduction_rate))
        
        # Update inventory patterns
        if global_tensions > 0.6:
            # Shift away from JIT during high tensions
            jit_change = -0.03
            buffer_change = 0.02
            strategic_change = 0.01
        else:
            # Gradual return to JIT during low tensions
            jit_change = 0.01
            buffer_change = -0.005
            strategic_change = -0.005
        
        self.inventory_patterns['just_in_time'] = max(0.2, min(0.6, self.inventory_patterns['just_in_time'] + jit_change))
        self.inventory_patterns['buffer_stock'] = max(0.2, min(0.6, self.inventory_patterns['buffer_stock'] + buffer_change))
        self.inventory_patterns['strategic_reserves'] = max(0.1, min(0.4, self.inventory_patterns['strategic_reserves'] + strategic_change))
        
        # Normalize inventory pattern shares to sum to 1
        total_share = sum(self.inventory_patterns.values())
        for pattern, share in self.inventory_patterns.items():
            self.inventory_patterns[pattern] = share / total_share
        
        # Calculate potential benefits for Bangladesh
        # China plus one benefit depends on Bangladesh's position as an alternative
        bangladesh_attractiveness = 0.7  # Relative attractiveness as China+1 destination (0-1)
        china_plus_one_benefit = self.china_plus_one * bangladesh_attractiveness * supply_chain_multiplier
        
        # Nearshoring impact (negative for Bangladesh since it's far from major markets)
        nearshoring_impact = self.nearshoring_trend * 0.6 * supply_chain_multiplier
        
        # Resilience premium impact
        # Bangladesh gets some benefit but also has challenges
        resilience_benefit = self.resilience_premium * 0.4 * supply_chain_multiplier
        
        # Lead time impact
        weighted_lead_time = sum(self.lead_time_requirements.values()) / len(self.lead_time_requirements)
        bangladesh_lead_time = 75  # Average lead time from Bangladesh
        lead_time_impact = (weighted_lead_time - bangladesh_lead_time) / weighted_lead_time * 0.5
        
        # Inventory pattern impact
        # Higher JIT is challenging for Bangladesh due to distance
        jit_impact = -self.inventory_patterns['just_in_time'] * 0.3
        # Higher strategic reserves is generally positive
        strategic_impact = self.inventory_patterns['strategic_reserves'] * 0.2
        
        inventory_impact = jit_impact + strategic_impact
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'china_plus_one': self.china_plus_one,
            'nearshoring_trend': self.nearshoring_trend,
            'resilience_premium': self.resilience_premium,
            'lead_time_requirements': self.lead_time_requirements.copy(),
            'inventory_patterns': self.inventory_patterns.copy(),
            'china_plus_one_benefit': china_plus_one_benefit,
            'nearshoring_impact': nearshoring_impact,
            'resilience_benefit': resilience_benefit,
            'lead_time_impact': lead_time_impact,
            'inventory_impact': inventory_impact,
            'net_impact': china_plus_one_benefit - nearshoring_impact + resilience_benefit + lead_time_impact + inventory_impact,
        }
        
        # Store historical data
        self.historical_chains[year_index] = results
        
        return results
