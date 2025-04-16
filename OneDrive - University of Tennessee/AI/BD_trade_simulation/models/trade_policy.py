"""
Trade policy model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class TradePolicyModel:
    """
    Model trade policy frameworks and evolution
    
    This class simulates the effects of various trade policies, including
    preferential market access, free trade agreements, and domestic trade policies.
    """
    
    def __init__(self, config):
        """
        Initialize trade policy model
        
        Args:
            config: Configuration dictionary for trade policy parameters
        """
        self.ldc_graduation = config.get('ldc_graduation', {})
        self.fta_implementation = config.get('fta_implementation', {})
        self.domestic_policy = config.get('domestic_policy', {})
        
        # Track policy implementation status
        self.policies = {
            'ldc_graduation_implemented': False,
            'active_ftas': {},
            'tariff_rates': {},
            'economic_zones_operational': 0,
        }
        
        # Initialize historical data
        self.historical_policy_impacts = {}
    
    def implement_policy_change(self, 
                               year_index: int,
                               simulation_year: int,
                               policy_type: str,
                               implementation_timeline: Dict[str, Any],
                               enforcement_quality: float) -> Dict[str, Any]:
        """
        Calculate impacts of trade policy changes
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year of simulation
            policy_type: Type of policy change
            implementation_timeline: Timeline parameters for implementation
            enforcement_quality: Quality of policy enforcement (0-1)
            
        Returns:
            Dict with policy implementation results
        """
        policy_impact = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'policy_type': policy_type,
            'implemented': False,
            'implementation_level': 0.0,
            'tariff_changes': {},
            'market_access_impact': 0.0,
            'trade_creation': 0.0,
            'trade_diversion': 0.0,
            'domestic_industry_impact': 0.0,
            'enforcement_quality': enforcement_quality,
        }
        
        # LDC Graduation Implementation
        if policy_type == 'ldc_graduation' and simulation_year >= self.ldc_graduation.get('year', 2026):
            if not self.policies['ldc_graduation_implemented']:
                # Implement LDC graduation
                self.policies['ldc_graduation_implemented'] = True
                
                # Calculate tariff changes due to LDC graduation
                tariff_changes = {
                    'eu': self.ldc_graduation.get('eu_tariff_increase', 0.09),
                    'us': self.ldc_graduation.get('us_tariff_increase', 0.15),
                    'canada': self.ldc_graduation.get('canada_tariff_increase', 0.12),
                    'japan': self.ldc_graduation.get('japan_tariff_increase', 0.10),
                    'australia': self.ldc_graduation.get('australia_tariff_increase', 0.08),
                }
                
                # Store tariff changes
                self.policies['tariff_rates'].update(tariff_changes)
                
                # Calculate market access impact
                # Higher enforcement quality means more accurate implementation
                market_access_impact = -sum(tariff_changes.values()) / len(tariff_changes) * enforcement_quality
                
                # Update policy impact
                policy_impact.update({
                    'implemented': True,
                    'implementation_level': enforcement_quality,
                    'tariff_changes': tariff_changes,
                    'market_access_impact': market_access_impact,
                    'domestic_industry_impact': market_access_impact * 0.7,  # Domestic impact somewhat less than market access impact
                })
        
        # FTA Implementation
        elif policy_type.startswith('fta_') and policy_type[4:] in self.fta_implementation:
            fta_name = policy_type[4:]
            fta_config = self.fta_implementation.get(fta_name, {})
            
            # Check if this is a proposed FTA
            if fta_name == 'proposed_ftas':
                for country, proposal in fta_config.items():
                    if simulation_year >= proposal.get('year', 2030):
                        # Probabilistic implementation based on stated probability
                        implementation_probability = proposal.get('probability', 0.5) * enforcement_quality
                        if np.random.random() < implementation_probability and country not in self.policies['active_ftas']:
                            # Implement new FTA
                            self.policies['active_ftas'][country] = {
                                'implementation_level': 0.3,  # Initial implementation level
                                'year_implemented': simulation_year,
                            }
                            
                            # Calculate initial impact
                            tariff_reduction = 0.3  # Initial tariff reduction
                            market_access_impact = tariff_reduction * 0.5
                            
                            # Update policy impact
                            policy_impact.update({
                                'implemented': True,
                                'implementation_level': 0.3,
                                'fta_partner': country,
                                'tariff_changes': {country: -tariff_reduction},
                                'market_access_impact': market_access_impact,
                                'trade_creation': market_access_impact * 1.2,
                                'trade_diversion': market_access_impact * 0.3,
                            })
            
            # Existing FTA implementation progress
            elif fta_name in ['safta', 'bimstec', 'rcep_accession']:
                current_level = self.policies['active_ftas'].get(fta_name, {}).get('implementation_level', 0)
                target_level = fta_config.get('implementation_level', 0.7)
                
                if current_level < target_level:
                    # Gradual implementation improvement
                    new_level = min(target_level, current_level + 0.05 * enforcement_quality)
                    
                    # Store updated implementation level
                    if fta_name not in self.policies['active_ftas']:
                        self.policies['active_ftas'][fta_name] = {
                            'implementation_level': new_level,
                            'year_implemented': simulation_year,
                        }
                    else:
                        self.policies['active_ftas'][fta_name]['implementation_level'] = new_level
                    
                    # Calculate implementation impact
                    tariff_reduction = fta_config.get('tariff_reduction', 0.5) * (new_level - current_level)
                    sensitive_list_coverage = fta_config.get('sensitive_list_coverage', 0.3)
                    effective_tariff_reduction = tariff_reduction * (1 - sensitive_list_coverage)
                    
                    # Calculate market impacts
                    market_access_impact = effective_tariff_reduction * 0.7
                    
                    # Update policy impact
                    policy_impact.update({
                        'implemented': True,
                        'implementation_level': new_level,
                        'fta_name': fta_name,
                        'tariff_changes': {fta_name: -effective_tariff_reduction},
                        'market_access_impact': market_access_impact,
                        'trade_creation': market_access_impact * 1.5,
                        'trade_diversion': market_access_impact * 0.4,
                        'sensitive_list_coverage': sensitive_list_coverage,
                    })
        
        # Domestic Trade Policy Implementation
        elif policy_type == 'domestic_policy':
            # Import tariff rationalization
            tariff_rationalization_rate = self.domestic_policy.get('import_tariff_rationalization', 0.05)
            tariff_reduction = tariff_rationalization_rate * enforcement_quality
            
            # Export incentives
            export_incentives = self.domestic_policy.get('export_incentives', {})
            incentive_level = export_incentives.get('cash_incentive_level', 0.05)
            covered_sectors = export_incentives.get('covered_sectors', [])
            
            # Economic zones development
            ez_config = self.domestic_policy.get('economic_zones', {})
            planned_zones = ez_config.get('number_planned', 100)
            annual_implementation_rate = ez_config.get('annual_implementation_rate', 0.06)
            effectiveness = ez_config.get('effectiveness', 0.7)
            
            # Calculate new economic zones
            new_zones = max(0, min(
                planned_zones - self.policies['economic_zones_operational'],
                int(planned_zones * annual_implementation_rate * enforcement_quality)
            ))
            self.policies['economic_zones_operational'] += new_zones
            
            # Calculate policy impacts
            tariff_rationalization_impact = -tariff_reduction * 0.6  # Negative impact on domestic protected industries
            export_incentive_impact = incentive_level * len(covered_sectors) / 10 * enforcement_quality
            economic_zone_impact = new_zones / planned_zones * effectiveness * 2
            
            net_impact = tariff_rationalization_impact + export_incentive_impact + economic_zone_impact
            
            # Update policy impact
            policy_impact.update({
                'implemented': True,
                'implementation_level': enforcement_quality,
                'tariff_changes': {'domestic': -tariff_reduction},
                'market_access_impact': 0,  # Domestic policies don't directly affect market access
                'domestic_industry_impact': net_impact,
                'export_incentive_impact': export_incentive_impact,
                'economic_zone_impact': economic_zone_impact,
                'tariff_rationalization_impact': tariff_rationalization_impact,
                'economic_zones_operational': self.policies['economic_zones_operational'],
            })
        
        # Store historical policy impact
        self.historical_policy_impacts[year_index] = policy_impact
        
        return policy_impact
    
    def get_overall_policy_environment(self, year_index, simulation_year):
        """
        Calculate the overall trade policy environment for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            
        Returns:
            Dict with overall policy environment metrics
        """
        # Collect all policy impacts for this year and previous years
        relevant_impacts = {y: impact for y, impact in self.historical_policy_impacts.items() if y <= year_index}
        
        # Calculate aggregate metrics
        tariff_rates = {}
        market_access_score = 0
        domestic_policy_score = 0
        fta_coverage = len(self.policies['active_ftas']) / 10  # Normalize by assuming 10 potential FTAs
        
        # Base values for new simulation
        if not relevant_impacts:
            return {
                'year_index': year_index,
                'simulation_year': simulation_year,
                'tariff_rates': self.policies['tariff_rates'],
                'market_access_score': 0.7,  # Starting with good market access as LDC
                'domestic_policy_score': 0.5,  # Moderate domestic policy environment
                'fta_coverage': fta_coverage,
                'economic_zones_operational': self.policies['economic_zones_operational'],
                'ldc_benefits_active': not self.policies['ldc_graduation_implemented'],
            }
        
        # Calculate cumulative impacts
        cumulative_market_access = 0
        cumulative_domestic_impact = 0
        
        for y, impact in relevant_impacts.items():
            # Accumulate tariff changes
            for market, rate in impact.get('tariff_changes', {}).items():
                if market in tariff_rates:
                    tariff_rates[market] += rate
                else:
                    tariff_rates[market] = rate
            
            # Accumulate other impacts with recency weighting
            recency_weight = 1 / (1 + 0.2 * (year_index - y))  # More recent changes have higher weight
            cumulative_market_access += impact.get('market_access_impact', 0) * recency_weight
            cumulative_domestic_impact += impact.get('domestic_industry_impact', 0) * recency_weight
        
        # Calculate overall scores
        market_access_score = max(0.1, min(1.0, 0.7 + cumulative_market_access))  # Start from 0.7 baseline (as LDC)
        domestic_policy_score = max(0.1, min(1.0, 0.5 + cumulative_domestic_impact))  # Start from 0.5 baseline
        
        # Return overall environment
        return {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'tariff_rates': tariff_rates,
            'market_access_score': market_access_score,
            'domestic_policy_score': domestic_policy_score,
            'fta_coverage': fta_coverage,
            'economic_zones_operational': self.policies['economic_zones_operational'],
            'ldc_benefits_active': not self.policies['ldc_graduation_implemented'],
            'active_ftas': list(self.policies['active_ftas'].keys()),
        }


class PreferentialAccessModel:
    """
    Model for preferential market access and LDC graduation impacts
    """
    
    def __init__(self, config):
        """
        Initialize preferential market access model
        
        Args:
            config: Configuration dictionary with preferential access parameters
        """
        self.ldc_graduation_year = config.get('ldc_graduation', {}).get('year', 2026)
        self.tariff_increases = {
            'eu': config.get('ldc_graduation', {}).get('eu_tariff_increase', 0.09),
            'us': config.get('ldc_graduation', {}).get('us_tariff_increase', 0.15),
            'canada': config.get('ldc_graduation', {}).get('canada_tariff_increase', 0.12),
            'japan': config.get('ldc_graduation', {}).get('japan_tariff_increase', 0.10),
            'australia': config.get('ldc_graduation', {}).get('australia_tariff_increase', 0.08),
        }
        
        # GSP+ qualification probability
        self.gsp_plus_qualification = {
            'base_probability': 0.6,
            'implementation_year': self.ldc_graduation_year + 1,
            'requirements_met': {
                'governance': 0.7,
                'human_rights': 0.6,
                'labor_standards': 0.7,
                'environmental_conventions': 0.5,
            }
        }
        
        # Rules of origin compliance
        self.rules_of_origin_compliance = {
            'rmg': 0.7,
            'pharma': 0.8,
            'leather': 0.6,
            'jute': 0.9,
            'agro_products': 0.8,
        }
        
        # Historical data
        self.market_access_history = {}
    
    def simulate_market_access(self, year_index, simulation_year, sector, country_policies):
        """
        Simulate preferential market access for a sector in a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            sector: Export sector to simulate access for
            country_policies: Dict of country-specific policy parameters
            
        Returns:
            Dict with market access simulation results
        """
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'sector': sector,
            'ldc_benefits_active': simulation_year < self.ldc_graduation_year,
            'gsp_plus_active': False,
            'tariff_rates': {},
            'preference_utilization': {},
            'rules_of_origin_compliance': self.rules_of_origin_compliance.get(sector, 0.6),
        }
        
        # LDC benefits phase-out
        if simulation_year >= self.ldc_graduation_year:
            # LDC graduation has occurred
            results['ldc_benefits_active'] = False
            
            # Calculate base tariffs by destination
            for country, increase in self.tariff_increases.items():
                results['tariff_rates'][country] = increase
            
            # Check for GSP+ qualification
            if simulation_year >= self.gsp_plus_qualification['implementation_year']:
                # Calculate probability of qualification
                qualification_score = sum(self.gsp_plus_qualification['requirements_met'].values()) / len(self.gsp_plus_qualification['requirements_met'])
                gsp_probability = self.gsp_plus_qualification['base_probability'] * qualification_score
                
                # Determine if GSP+ is active
                results['gsp_plus_active'] = np.random.random() < gsp_probability
                
                if results['gsp_plus_active']:
                    # Adjust EU tariffs under GSP+
                    results['tariff_rates']['eu'] *= 0.3  # 70% reduction in tariffs under GSP+
        else:
            # LDC benefits still active
            for country in self.tariff_increases.keys():
                results['tariff_rates'][country] = 0  # Duty-free access
        
        # Calculate preference utilization based on rules of origin compliance
        for country, tariff in results['tariff_rates'].items():
            if tariff > 0:
                utilization = max(0, min(1, self.rules_of_origin_compliance.get(sector, 0.6) - 0.1 * tariff))
                results['preference_utilization'][country] = utilization
                
                # Adjust effective tariff rate based on preference utilization
                results['tariff_rates'][country] *= (1 - utilization * 0.7)
        
        # Store historical data
        if sector not in self.market_access_history:
            self.market_access_history[sector] = {}
        self.market_access_history[sector][year_index] = results
        
        return results


class FreeTradeAgreementModel:
    """
    Model for Free Trade Agreement implementation and impacts
    """
    
    def __init__(self, config):
        """
        Initialize FTA model
        
        Args:
            config: Configuration dictionary with FTA parameters
        """
        self.fta_config = config.get('fta_implementation', {})
        
        # Active agreements
        self.active_agreements = {
            'safta': {
                'implementation_level': self.fta_config.get('safta', {}).get('implementation_level', 0.6),
                'sensitive_list_coverage': self.fta_config.get('safta', {}).get('sensitive_list_coverage', 0.3),
            },
            'bimstec': {
                'implementation_level': self.fta_config.get('bimstec', {}).get('implementation_level', 0.3),
                'sensitive_list_coverage': self.fta_config.get('bimstec', {}).get('sensitive_list_coverage', 0.4),
            },
        }
        
        # Proposed agreements
        self.proposed_agreements = self.fta_config.get('proposed_ftas', {})
        
        # RCEP accession
        self.rcep_accession = self.fta_config.get('rcep_accession', {})
        
        # Historical data
        self.fta_history = {}
    
    def simulate_fta_evolution(self, year_index, simulation_year, enforcement_quality):
        """
        Simulate FTA evolution for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            enforcement_quality: Quality of policy enforcement (0-1)
            
        Returns:
            Dict with FTA simulation results
        """
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'active_agreements': {},
            'new_agreements': [],
            'overall_fta_coverage': 0,
            'trade_creation': 0,
            'trade_diversion': 0,
        }
        
        # Update existing agreement implementation levels
        for agreement, details in self.active_agreements.items():
            # Gradual implementation progress
            implementation_increase = 0.05 * enforcement_quality
            new_level = min(1.0, details['implementation_level'] + implementation_increase)
            self.active_agreements[agreement]['implementation_level'] = new_level
            
            # Calculate trade creation and diversion
            implementation_change = new_level - details['implementation_level']
            if implementation_change > 0:
                effective_change = implementation_change * (1 - details['sensitive_list_coverage'])
                trade_creation = effective_change * 0.15  # 15% of effective change translates to trade creation
                trade_diversion = effective_change * 0.05  # 5% of effective change is trade diversion
                
                results['trade_creation'] += trade_creation
                results['trade_diversion'] += trade_diversion
            
            # Add to results
            results['active_agreements'][agreement] = {
                'implementation_level': new_level,
                'sensitive_list_coverage': details['sensitive_list_coverage'],
            }
        
        # Check for new agreement implementation
        for country, proposal in self.proposed_agreements.items():
            if simulation_year >= proposal.get('year', 2030) and country not in self.active_agreements:
                # Probability of implementation
                implementation_probability = proposal.get('probability', 0.5) * enforcement_quality
                
                if np.random.random() < implementation_probability:
                    # New agreement activated
                    self.active_agreements[country] = {
                        'implementation_level': 0.2,  # Initial implementation
                        'sensitive_list_coverage': 0.4,  # Initial sensitive list is conservative
                    }
                    
                    results['new_agreements'].append(country)
                    results['active_agreements'][country] = self.active_agreements[country]
                    
                    # Initial trade creation and diversion
                    results['trade_creation'] += 0.02  # 2% trade creation from new agreement
                    results['trade_diversion'] += 0.01  # 1% trade diversion from new agreement
        
        # Check for RCEP accession
        if simulation_year >= self.rcep_accession.get('year', 2032) and 'rcep' not in self.active_agreements:
            accession_probability = self.rcep_accession.get('probability', 0.4) * enforcement_quality
            
            if np.random.random() < accession_probability:
                # RCEP accession successful
                self.active_agreements['rcep'] = {
                    'implementation_level': 0.1,  # Initial implementation
                    'sensitive_list_coverage': 0.5,  # High sensitive list initially
                }
                
                results['new_agreements'].append('rcep')
                results['active_agreements']['rcep'] = self.active_agreements['rcep']
                
                # Major trade impact from RCEP
                results['trade_creation'] += 0.04  # 4% trade creation
                results['trade_diversion'] += 0.02  # 2% trade diversion
        
        # Calculate overall FTA coverage
        potential_agreements = len(self.proposed_agreements) + 3  # SAFTA, BIMSTEC, RCEP + proposed
        results['overall_fta_coverage'] = len(self.active_agreements) / potential_agreements
        
        # Store historical data
        self.fta_history[year_index] = results
        
        return results


class DomesticTradePolicy:
    """
    Model for domestic trade policy evolution
    """
    
    def __init__(self, config):
        """
        Initialize domestic trade policy model
        
        Args:
            config: Configuration dictionary with domestic policy parameters
        """
        self.policy_config = config.get('domestic_policy', {})
        
        # Import tariff structure
        self.import_tariffs = {
            'consumer_goods': 0.25,
            'intermediate_goods': 0.15,
            'capital_machinery': 0.05,
            'raw_materials': 0.10,
        }
        
        # Export incentives
        self.export_incentives = self.policy_config.get('export_incentives', {})
        
        # Economic zones
        self.economic_zones = {
            'planned': self.policy_config.get('economic_zones', {}).get('number_planned', 100),
            'operational': 10,  # Starting number
            'implementation_rate': self.policy_config.get('economic_zones', {}).get('annual_implementation_rate', 0.06),
            'effectiveness': self.policy_config.get('economic_zones', {}).get('effectiveness', 0.7),
        }
        
        # Historical data
        self.policy_history = {}
    
    def simulate_policy_evolution(self, year_index, simulation_year, policy_coordination, external_pressure):
        """
        Simulate domestic trade policy evolution for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            policy_coordination: Level of policy coordination (0-1)
            external_pressure: Level of external pressure for liberalization (0-1)
            
        Returns:
            Dict with domestic policy simulation results
        """
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'import_tariffs': {},
            'export_incentives': {},
            'economic_zones': {},
            'policy_rationalization_score': 0,
            'export_promotion_score': 0,
            'investment_environment_score': 0,
        }
        
        # Tariff rationalization
        rationalization_rate = self.policy_config.get('import_tariff_rationalization', 0.05)
        rationalization_pressure = 0.5 * policy_coordination + 0.5 * external_pressure
        effective_rationalization = rationalization_rate * rationalization_pressure
        
        # Update tariffs
        for category, rate in self.import_tariffs.items():
            new_rate = max(0.01, rate * (1 - effective_rationalization))
            self.import_tariffs[category] = new_rate
            results['import_tariffs'][category] = new_rate
        
        # Calculate policy rationalization score
        avg_tariff = sum(self.import_tariffs.values()) / len(self.import_tariffs)
        results['policy_rationalization_score'] = 1 - (avg_tariff / 0.15)  # Normalize against initial average
        
        # Export incentives
        incentive_level = self.export_incentives.get('cash_incentive_level', 0.05)
        covered_sectors = self.export_incentives.get('covered_sectors', [])
        
        # Gradual reduction in cash incentives, offset by more targeted support
        if policy_coordination > 0.6:  # Higher coordination leads to more sophisticated incentives
            incentive_level *= (1 - 0.02 * policy_coordination)
            self.export_incentives['cash_incentive_level'] = incentive_level
        
        results['export_incentives'] = {
            'cash_incentive_level': incentive_level,
            'covered_sectors': covered_sectors,
            'effectiveness': 0.5 + 0.3 * policy_coordination,  # Better coordination improves effectiveness
        }
        
        # Economic zones development
        new_zones = min(
            self.economic_zones['planned'] - self.economic_zones['operational'],
            int(self.economic_zones['planned'] * self.economic_zones['implementation_rate'] * policy_coordination)
        )
        
        self.economic_zones['operational'] += new_zones
        zone_effectiveness = self.economic_zones['effectiveness'] + 0.02 * policy_coordination  # Improving over time
        self.economic_zones['effectiveness'] = min(0.95, zone_effectiveness)
        
        results['economic_zones'] = {
            'operational': self.economic_zones['operational'],
            'planned': self.economic_zones['planned'],
            'implementation_rate': self.economic_zones['implementation_rate'],
            'effectiveness': self.economic_zones['effectiveness'],
            'new_zones': new_zones,
        }
        
        # Calculate scores
        results['export_promotion_score'] = incentive_level * len(covered_sectors) / 5 * results['export_incentives']['effectiveness']
        results['investment_environment_score'] = (self.economic_zones['operational'] / self.economic_zones['planned']) * self.economic_zones['effectiveness']
        
        # Store historical data
        self.policy_history[year_index] = results
        
        return results
