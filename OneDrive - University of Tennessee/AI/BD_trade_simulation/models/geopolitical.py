"""
Geopolitical model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class GeopoliticalModel:
    """
    Model geopolitical factors affecting trade
    
    This class simulates geopolitical factors, including regional integration,
    global power shifts, and trade war impacts.
    """
    
    def __init__(self, config):
        """
        Initialize geopolitical model
        
        Args:
            config: Configuration dictionary for geopolitical parameters
        """
        # Extract configuration
        self.regional_integration = config.get('regional_integration', {})
        self.global_tensions = config.get('global_tensions', {})
        self.trade_war_probability = config.get('trade_war_probability', {})
        self.belt_and_road = config.get('belt_and_road_initiative', {})
        
        # Initialize regional integration model
        self.regional = RegionalIntegrationModel(self.regional_integration)
        
        # Initialize global power shifts model
        self.global_powers = GlobalPowerShiftsModel(self.global_tensions)
        
        # Initialize trade war impacts model
        self.trade_wars = TradeWarImpactsModel(self.trade_war_probability)
        
        # Historical data
        self.historical_environment = {}
    
    def simulate_geopolitical_environment(self, 
                                       year_index: int,
                                       simulation_year: int,
                                       regional_dynamics: float = 0.5,
                                       global_tensions: float = 0.5) -> Dict[str, Any]:
        """
        Simulate geopolitical environment for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            regional_dynamics: Level of regional cooperation (0-1)
            global_tensions: Level of global geopolitical tensions (0-1)
            
        Returns:
            Dict with geopolitical simulation results
        """
        # Simulate regional integration
        regional_result = self.regional.simulate_integration(
            year_index=year_index,
            simulation_year=simulation_year,
            cooperation_level=regional_dynamics
        )
        
        # Simulate global power shifts
        global_result = self.global_powers.simulate_power_shifts(
            year_index=year_index,
            simulation_year=simulation_year,
            tension_level=global_tensions
        )
        
        # Simulate trade war impacts
        trade_war_result = self.trade_wars.simulate_trade_wars(
            year_index=year_index,
            simulation_year=simulation_year,
            tension_level=global_tensions,
            regional_cooperation=regional_dynamics
        )
        
        # Calculate Belt and Road Initiative impacts
        bri_participation = self.belt_and_road.get('bangladesh_participation', 0.7)
        bri_implementation = self.belt_and_road.get('project_implementation_rate', 0.1)
        
        bri_impact = bri_participation * bri_implementation * (1 - 0.3 * global_tensions)
        
        # Calculate overall geopolitical impact on trade
        trade_benefit = (
            regional_result['trade_facilitation_score'] * 0.4 +
            global_result['favorable_relations_score'] * 0.3 +
            trade_war_result['opportunity_score'] * 0.2 +
            bri_impact * 0.1
        )
        
        trade_risk = (
            (1 - regional_result['stability_score']) * 0.3 +
            global_result['tension_level'] * 0.4 +
            trade_war_result['vulnerability_score'] * 0.3
        )
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'regional_integration': regional_result,
            'global_power_shifts': global_result,
            'trade_war_impacts': trade_war_result,
            'bri_impact': bri_impact,
            'trade_benefit': trade_benefit,
            'trade_risk': trade_risk,
            'net_geopolitical_impact': trade_benefit - trade_risk,
        }
        
        # Store historical data
        self.historical_environment[year_index] = results
        
        return results


class RegionalIntegrationModel:
    """
    Model regional integration dynamics
    """
    
    def __init__(self, config):
        """
        Initialize regional integration model
        
        Args:
            config: Configuration dictionary for regional integration
        """
        self.bbin = config.get('bbin', {})
        self.bay_of_bengal = config.get('bay_of_bengal', {})
        self.saarc = config.get('saarc', {})
        
        # Bilateral relations with key neighbors
        self.bilateral_relations = {
            'india': {
                'political_level': 0.6,  # 0-1 scale, higher is better
                'economic_level': 0.7,
                'security_level': 0.5,
                'volatility': 0.1,
            },
            'china': {
                'political_level': 0.7,
                'economic_level': 0.8,
                'security_level': 0.6,
                'volatility': 0.1,
            },
            'myanmar': {
                'political_level': 0.4,
                'economic_level': 0.5,
                'security_level': 0.3,
                'volatility': 0.2,
            },
        }
        
        # Rohingya crisis impact
        self.rohingya_crisis = {
            'severity': 0.7,  # 0-1 scale
            'annual_change': -0.02,  # Gradual improvement
            'economic_impact': 0.3,  # Impact on regional economic cooperation
        }
        
        # Historical data
        self.historical_integration = {}
    
    def simulate_integration(self, 
                           year_index: int,
                           simulation_year: int,
                           cooperation_level: float) -> Dict[str, Any]:
        """
        Simulate regional integration for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            cooperation_level: Level of regional cooperation (0-1)
            
        Returns:
            Dict with regional integration simulation results
        """
        # Update BBIN implementation
        bbin_implementation = self.bbin.get('implementation_level', 0.3)
        bbin_improvement = self.bbin.get('annual_improvement', 0.03) * cooperation_level
        
        new_bbin_level = min(1.0, bbin_implementation + bbin_improvement)
        self.bbin['implementation_level'] = new_bbin_level
        
        # Update Bay of Bengal cooperation
        bob_cooperation = self.bay_of_bengal.get('cooperation_level', 0.4)
        bob_improvement = self.bay_of_bengal.get('annual_improvement', 0.02) * cooperation_level
        
        new_bob_level = min(1.0, bob_cooperation + bob_improvement)
        self.bay_of_bengal['cooperation_level'] = new_bob_level
        
        # Update SAARC revival probability
        saarc_revival_prob = self.saarc.get('revival_probability', 0.3)
        
        # Adjust based on India-Pakistan relations (simplified)
        india_pakistan_relations = 0.3 + 0.1 * np.random.random()  # Random between 0.3-0.4
        saarc_revival_prob = 0.7 * saarc_revival_prob + 0.3 * india_pakistan_relations
        
        self.saarc['revival_probability'] = saarc_revival_prob
        
        # Simulate actual SAARC revival
        saarc_revival = np.random.random() < saarc_revival_prob and cooperation_level > 0.6
        
        # Update bilateral relations
        bilateral_results = {}
        for country, relations in self.bilateral_relations.items():
            # Random variation based on volatility
            variation = np.random.normal(0, relations['volatility'])
            
            # Base change depends on cooperation level
            base_change = (cooperation_level - 0.5) * 0.05
            
            # Update political relations
            political_change = base_change + variation
            relations['political_level'] = max(0.1, min(0.9, relations['political_level'] + political_change))
            
            # Update economic relations (more stable than political)
            economic_change = base_change * 0.7 + variation * 0.5
            relations['economic_level'] = max(0.2, min(0.95, relations['economic_level'] + economic_change))
            
            # Update security relations
            security_change = base_change * 0.5 + variation
            relations['security_level'] = max(0.1, min(0.9, relations['security_level'] + security_change))
            
            # Overall relationship score
            relationship_score = (
                relations['political_level'] * 0.4 +
                relations['economic_level'] * 0.4 +
                relations['security_level'] * 0.2
            )
            
            bilateral_results[country] = {
                'political_level': relations['political_level'],
                'economic_level': relations['economic_level'],
                'security_level': relations['security_level'],
                'relationship_score': relationship_score,
            }
        
        # Update Rohingya crisis
        self.rohingya_crisis['severity'] = max(0.1, self.rohingya_crisis['severity'] + self.rohingya_crisis['annual_change'])
        
        # Calculate implications for trade
        
        # Trade facilitation from regional initiatives
        trade_facilitation = (
            self.bbin['implementation_level'] * 0.4 +
            self.bay_of_bengal['cooperation_level'] * 0.3 +
            (0.3 if saarc_revival else 0.1) * 0.3
        )
        
        # Stability score (higher is more stable)
        stability_score = (
            (1 - self.rohingya_crisis['severity']) * 0.3 +
            bilateral_results['india']['relationship_score'] * 0.3 +
            bilateral_results['china']['relationship_score'] * 0.2 +
            bilateral_results['myanmar']['relationship_score'] * 0.2
        )
        
        # Calculate market access impact
        india_market_access = bilateral_results['india']['economic_level'] * 0.6 + self.bbin['implementation_level'] * 0.4
        china_market_access = bilateral_results['china']['economic_level'] * 0.7 + self.bay_of_bengal['cooperation_level'] * 0.3
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'bbin_implementation': self.bbin['implementation_level'],
            'bay_of_bengal_cooperation': self.bay_of_bengal['cooperation_level'],
            'saarc_revival_probability': self.saarc['revival_probability'],
            'saarc_revival_occurred': saarc_revival,
            'bilateral_relations': bilateral_results,
            'rohingya_crisis_severity': self.rohingya_crisis['severity'],
            'trade_facilitation_score': trade_facilitation,
            'stability_score': stability_score,
            'market_access': {
                'india': india_market_access,
                'china': china_market_access,
            },
        }
        
        # Store historical data
        self.historical_integration[year_index] = results
        
        return results


class GlobalPowerShiftsModel:
    """
    Model global power shifts and impacts
    """
    
    def __init__(self, config):
        """
        Initialize global power shifts model
        
        Args:
            config: Configuration dictionary for global tensions
        """
        self.us_china = config.get('us_china', {})
        self.india_china = config.get('india_china', {})
        
        # Bangladesh's alignment with major powers
        self.alignment = {
            'us': 0.5,  # 0-1 scale, higher means more aligned
            'china': 0.7,
            'india': 0.6,
            'eu': 0.6,
            'russia': 0.4,
            'japan': 0.5,
        }
        
        # Development finance competition
        self.dev_finance = {
            'western': {
                'volume': 1000,  # Million USD
                'conditionality': 0.7,  # 0-1 scale, higher means more conditions
                'interest_rate': 0.02,
                'growth_rate': 0.02,
            },
            'asian': {
                'volume': 1500,
                'conditionality': 0.4,
                'interest_rate': 0.03,
                'growth_rate': 0.05,
            },
        }
        
        # Indo-Pacific strategy relevance
        self.indo_pacific = {
            'engagement_level': 0.4,  # Bangladesh's engagement
            'strategic_importance': 0.6,  # Bangladesh's importance in the strategy
        }
        
        # Historical data
        self.historical_shifts = {}
    
    def simulate_power_shifts(self, 
                            year_index: int,
                            simulation_year: int,
                            tension_level: float) -> Dict[str, Any]:
        """
        Simulate global power shifts for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            tension_level: Level of global geopolitical tensions (0-1)
            
        Returns:
            Dict with global power shifts simulation results
        """
        # Update US-China tensions
        us_china_level = self.us_china.get('initial_level', 0.7)
        annual_change = self.us_china.get('annual_change', -0.01)
        
        # Adjust annual change based on current tension level
        adjusted_change = annual_change * (1 + (tension_level - 0.5) * 2)
        
        new_us_china_level = max(0.3, min(0.9, us_china_level + adjusted_change))
        self.us_china['initial_level'] = new_us_china_level
        
        # Update India-China tensions (correlated with US-China but not identical)
        india_china_level = self.india_china.get('initial_level', 0.6)
        india_china_annual = self.india_china.get('annual_change', -0.01)
        
        # India-China tensions are influenced by US-China tensions
        india_china_adjusted = india_china_annual * (1 + (tension_level - 0.5) * 1.5)
        
        new_india_china_level = max(0.3, min(0.9, india_china_level + india_china_adjusted))
        self.india_china['initial_level'] = new_india_china_level
        
        # Update Bangladesh's alignment with major powers
        alignment_results = {}
        
        # Alignment shifts are complex and depend on many factors
        # Simplification: tension increases need to choose sides, influences alignment shifts
        
        # Update US alignment
        us_shift = np.random.normal(0, 0.05) + (tension_level - 0.5) * 0.03
        self.alignment['us'] = max(0.2, min(0.8, self.alignment['us'] + us_shift))
        
        # Update China alignment (somewhat inversely related to US alignment)
        china_shift = np.random.normal(0, 0.05) - us_shift * 0.7
        self.alignment['china'] = max(0.3, min(0.9, self.alignment['china'] + china_shift))
        
        # Update India alignment (somewhat correlated with US, complex with China)
        india_shift = np.random.normal(0, 0.03) + us_shift * 0.3 - china_shift * 0.3
        self.alignment['india'] = max(0.3, min(0.8, self.alignment['india'] + india_shift))
        
        # Update other alignments
        for power in ['eu', 'russia', 'japan']:
            # Random shift with less volatility
            power_shift = np.random.normal(0, 0.02)
            self.alignment[power] = max(0.2, min(0.8, self.alignment[power] + power_shift))
        
        alignment_results = self.alignment.copy()
        
        # Update development finance competition
        western_growth = self.dev_finance['western']['growth_rate'] * (1 + (self.alignment['us'] - 0.5) * 0.5)
        asian_growth = self.dev_finance['asian']['growth_rate'] * (1 + (self.alignment['china'] - 0.5) * 0.5)
        
        self.dev_finance['western']['volume'] *= (1 + western_growth)
        self.dev_finance['asian']['volume'] *= (1 + asian_growth)
        
        # Conditionality changes based on competition
        competition_intensity = tension_level * 0.5
        conditionality_change = -0.01 * competition_intensity  # Competition reduces conditionality
        
        self.dev_finance['western']['conditionality'] = max(0.4, min(0.9, self.dev_finance['western']['conditionality'] + conditionality_change))
        self.dev_finance['asian']['conditionality'] = max(0.2, min(0.7, self.dev_finance['asian']['conditionality'] + conditionality_change * 0.5))
        
        # Update Indo-Pacific strategy
        ip_engagement_change = (self.alignment['us'] - 0.5) * 0.05 + (self.alignment['japan'] - 0.5) * 0.03
        ip_importance_change = tension_level * 0.02
        
        self.indo_pacific['engagement_level'] = max(0.2, min(0.8, self.indo_pacific['engagement_level'] + ip_engagement_change))
        self.indo_pacific['strategic_importance'] = max(0.3, min(0.9, self.indo_pacific['strategic_importance'] + ip_importance_change))
        
        # Calculate implications for trade
        
        # Favorable relations score (weighted by economic importance)
        favorable_relations = (
            self.alignment['china'] * 0.3 +
            self.alignment['india'] * 0.3 +
            self.alignment['us'] * 0.2 +
            self.alignment['eu'] * 0.1 +
            self.alignment['japan'] * 0.05 +
            self.alignment['russia'] * 0.05
        )
        
        # Calculate tension impact on trade
        tension_impact = (
            new_us_china_level * 0.5 +
            new_india_china_level * 0.3 +
            tension_level * 0.2
        )
        
        # Development finance availability
        dev_finance_availability = (
            self.dev_finance['western']['volume'] +
            self.dev_finance['asian']['volume']
        ) / 2500  # Normalize to 0-1 scale
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'us_china_tension': new_us_china_level,
            'india_china_tension': new_india_china_level,
            'power_alignment': alignment_results,
            'development_finance': {
                'western': {
                    'volume': self.dev_finance['western']['volume'],
                    'conditionality': self.dev_finance['western']['conditionality'],
                },
                'asian': {
                    'volume': self.dev_finance['asian']['volume'],
                    'conditionality': self.dev_finance['asian']['conditionality'],
                },
                'availability': dev_finance_availability,
            },
            'indo_pacific': {
                'engagement_level': self.indo_pacific['engagement_level'],
                'strategic_importance': self.indo_pacific['strategic_importance'],
            },
            'favorable_relations_score': favorable_relations,
            'tension_level': tension_impact,
        }
        
        # Store historical data
        self.historical_shifts[year_index] = results
        
        return results


class TradeWarImpactsModel:
    """
    Model trade war impacts on Bangladesh
    """
    
    def __init__(self, config):
        """
        Initialize trade war impacts model
        
        Args:
            config: Configuration dictionary for trade war parameters
        """
        self.initial_probability = config.get('initial', 0.3)
        self.annual_change = config.get('annual_change', -0.01)
        
        # Current trade war status
        self.current_probability = self.initial_probability
        self.active_trade_wars = {}
        
        # Order diversion potential
        self.order_diversion = {
            'rmg': 0.6,  # Potential to capture diverted orders
            'footwear': 0.5,
            'light_manufacturing': 0.4,
            'electronics': 0.3,
            'other': 0.2,
        }
        
        # Export market diversification
        self.market_diversification = 0.4  # 0-1 scale, higher means more diversified
        
        # Secondary sanction exposure
        self.secondary_sanction_exposure = 0.3  # 0-1 scale
        
        # Historical data
        self.historical_impacts = {}
    
    def simulate_trade_wars(self,
                          year_index: int,
                          simulation_year: int,
                          tension_level: float,
                          regional_cooperation: float) -> Dict[str, Any]:
        """
        Simulate trade war impacts for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            tension_level: Level of global geopolitical tensions (0-1)
            regional_cooperation: Level of regional cooperation (0-1)
            
        Returns:
            Dict with trade war impacts simulation results
        """
        # Update trade war probability
        base_change = self.annual_change
        tension_effect = (tension_level - 0.5) * 0.1
        
        probability_change = base_change + tension_effect
        self.current_probability = max(0.05, min(0.8, self.current_probability + probability_change))
        
        # Determine if new trade wars start
        new_trade_wars = {}
        potential_conflicts = [
            ('us', 'china', 0.7),  # Country A, Country B, intensity if occurs
            ('us', 'eu', 0.5),
            ('china', 'india', 0.6),
            ('china', 'vietnam', 0.4),
        ]
        
        for country_a, country_b, intensity in potential_conflicts:
            conflict_id = f"{country_a}_{country_b}"
            reverse_id = f"{country_b}_{country_a}"
            
            # Skip if this conflict or its reverse is already active
            if conflict_id in self.active_trade_wars or reverse_id in self.active_trade_wars:
                continue
            
            # Adjust probability based on the countries involved
            adjusted_probability = self.current_probability
            if country_a == 'us' and country_b == 'china':
                adjusted_probability *= 1.5  # Higher probability for US-China
            
            # Determine if trade war starts
            if np.random.random() < adjusted_probability:
                # New trade war
                actual_intensity = intensity * (0.8 + 0.4 * np.random.random())  # Some variation in intensity
                
                self.active_trade_wars[conflict_id] = {
                    'started_year': simulation_year,
                    'intensity': actual_intensity,
                    'duration_years': int(2 + 3 * np.random.random()),  # 2-5 years duration
                }
                
                new_trade_wars[conflict_id] = self.active_trade_wars[conflict_id].copy()
        
        # Update existing trade wars
        ended_trade_wars = []
        for conflict_id, details in self.active_trade_wars.items():
            # Check if trade war should end
            years_active = simulation_year - details['started_year']
            
            if years_active >= details['duration_years']:
                # Trade war ends
                ended_trade_wars.append(conflict_id)
            else:
                # Intensity can change over time
                intensity_change = np.random.normal(0, 0.1)
                details['intensity'] = max(0.1, min(0.9, details['intensity'] + intensity_change))
        
        # Remove ended trade wars
        for conflict_id in ended_trade_wars:
            del self.active_trade_wars[conflict_id]
        
        # Update order diversion potential
        for sector in self.order_diversion:
            # Order diversion potential improves with experience and capacity development
            improvement = 0.02 * np.random.random()
            self.order_diversion[sector] = min(0.9, self.order_diversion[sector] + improvement)
        
        # Update market diversification
        diversification_change = 0.02 * regional_cooperation - 0.01 * tension_level
        self.market_diversification = max(0.3, min(0.9, self.market_diversification + diversification_change))
        
        # Update secondary sanction exposure
        sanction_exposure_change = 0.01 * tension_level - 0.02 * self.market_diversification
        self.secondary_sanction_exposure = max(0.1, min(0.7, self.secondary_sanction_exposure + sanction_exposure_change))
        
        # Calculate trade war impacts
        
        # Tariff escalation
        active_wars_intensity = sum(war['intensity'] for war in self.active_trade_wars.values())
        tariff_escalation = 0.1 * active_wars_intensity if self.active_trade_wars else 0
        
        # Order diversion opportunity
        # More active trade wars mean more diverted orders potential
        order_diversion_opportunities = {}
        for sector, potential in self.order_diversion.items():
            opportunity = potential * active_wars_intensity * 0.5
            order_diversion_opportunities[sector] = opportunity
        
        # Calculate weighted order diversion opportunity
        weighted_opportunity = sum(opportunities for opportunities in order_diversion_opportunities.values()) / len(order_diversion_opportunities)
        
        # Secondary sanction risk
        sanction_risk = self.secondary_sanction_exposure * active_wars_intensity * 0.3
        
        # Calculate overall opportunity score
        opportunity_score = weighted_opportunity * 0.7 - sanction_risk * 0.3
        
        # Calculate vulnerability score
        vulnerability_score = (
            (1 - self.market_diversification) * 0.5 +
            self.secondary_sanction_exposure * 0.3 +
            tariff_escalation * 0.2
        )
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'trade_war_probability': self.current_probability,
            'active_trade_wars': self.active_trade_wars.copy(),
            'new_trade_wars': new_trade_wars,
            'ended_trade_wars': ended_trade_wars,
            'order_diversion_potential': self.order_diversion.copy(),
            'market_diversification': self.market_diversification,
            'secondary_sanction_exposure': self.secondary_sanction_exposure,
            'tariff_escalation': tariff_escalation,
            'order_diversion_opportunities': order_diversion_opportunities,
            'sanction_risk': sanction_risk,
            'opportunity_score': opportunity_score,
            'vulnerability_score': vulnerability_score,
        }
        
        # Store historical data
        self.historical_impacts[year_index] = results
        
        return results
