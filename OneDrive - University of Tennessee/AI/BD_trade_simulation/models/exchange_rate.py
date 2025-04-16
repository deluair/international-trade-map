"""
Exchange rate model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class ExchangeRateModel:
    """
    Model exchange rate dynamics and impacts on trade
    
    This class simulates the evolution of Bangladesh's exchange rate,
    including its impacts on trade competitiveness, external balance,
    and trade finance.
    """
    
    def __init__(self, config):
        """
        Initialize exchange rate model
        
        Args:
            config: Configuration dictionary for exchange rate parameters
        """
        # Extract configuration
        self.initial_rate = config.get('initial_rate', 110.0)  # BDT to USD
        self.annual_depreciation = config.get('annual_depreciation', 0.03)
        self.volatility = config.get('volatility', 0.05)
        self.intervention_threshold = config.get('intervention_threshold', 0.08)
        self.intervention_strength = config.get('intervention_strength', 0.6)
        self.remittance_sensitivity = config.get('remittance_sensitivity', 0.4)
        self.export_elasticity = config.get('export_elasticity', 0.7)
        self.import_elasticity = config.get('import_elasticity', 0.6)
        
        # Initialize state variables
        self.current_rate = self.initial_rate
        self.real_effective_rate = 1.0  # Normalized to 1.0 at start
        self.foreign_reserves = 35000  # Initial foreign reserves in million USD
        
        # External trade variables
        self.trade_balance = 0
        self.current_account_balance = 0
        
        # Historical data
        self.historical_rates = {0: self.initial_rate}
        self.historical_impacts = {}
    
    def simulate_exchange_rate(self, 
                              year_index: int,
                              balance_of_payments: Dict[str, float],
                              central_bank_policy: Dict[str, float],
                              global_conditions: Dict[str, float]) -> Dict[str, Any]:
        """
        Simulate exchange rate dynamics for a given year
        
        Args:
            year_index: Year index from simulation start
            balance_of_payments: Dict with balance of payments components
                {
                    'exports': float,  # Export value in million USD
                    'imports': float,  # Import value in million USD
                    'remittances': float,  # Remittance inflow in million USD
                    'fdi': float,  # Foreign direct investment in million USD
                    'aid_loans': float,  # Foreign aid and loans in million USD
                    'profit_repatriation': float,  # Profit outflows in million USD
                    'other_outflows': float,  # Other capital outflows in million USD
                }
            central_bank_policy: Dict with central bank policy parameters
                {
                    'intervention_stance': float,  # 0-1, higher means more intervention
                    'reserve_threshold': float,  # Reserve threshold as months of imports
                    'interest_rate_differential': float,  # BDT interest rate - USD interest rate
                }
            global_conditions: Dict with global economic conditions
                {
                    'dollar_index': float,  # US dollar index
                    'global_risk_appetite': float,  # Global risk appetite (0-1)
                    'regional_currency_trends': float,  # Regional currency movements (-1 to 1)
                    'oil_price_change': float,  # Change in oil price
                }
                
        Returns:
            Dict with exchange rate simulation results
        """
        # Calculate balance of payments components
        exports = balance_of_payments.get('exports', 0)
        imports = balance_of_payments.get('imports', 0)
        remittances = balance_of_payments.get('remittances', 0)
        fdi = balance_of_payments.get('fdi', 0)
        aid_loans = balance_of_payments.get('aid_loans', 0)
        profit_repatriation = balance_of_payments.get('profit_repatriation', 0)
        other_outflows = balance_of_payments.get('other_outflows', 0)
        
        # Calculate trade and current account balances
        trade_balance = exports - imports
        current_account_balance = trade_balance + remittances - profit_repatriation
        capital_account_balance = fdi + aid_loans - other_outflows
        overall_balance = current_account_balance + capital_account_balance
        
        # Update foreign reserves
        previous_reserves = self.foreign_reserves
        self.foreign_reserves += overall_balance
        
        # Calculate reserve adequacy
        monthly_imports = imports / 12
        reserve_months = self.foreign_reserves / monthly_imports if monthly_imports > 0 else 12
        reserve_pressure = max(0, min(1, (3 - reserve_months) / 3)) if reserve_months < 6 else 0
        
        # Calculate base exchange rate pressure
        base_pressure = (
            -0.3 * (overall_balance / imports) +  # BoP impact
            0.2 * global_conditions.get('dollar_index', 1.0) +  # USD strength impact
            -0.1 * global_conditions.get('global_risk_appetite', 0.5) +  # Risk impact
            0.15 * global_conditions.get('regional_currency_trends', 0) +  # Regional trends
            0.25 * global_conditions.get('oil_price_change', 0) +  # Oil price impact
            0.2 * reserve_pressure  # Reserve adequacy impact
        )
        
        # Add random market volatility
        market_volatility = np.random.normal(0, self.volatility)
        total_pressure = base_pressure + market_volatility
        
        # Calculate potential depreciation rate
        potential_depreciation = self.annual_depreciation + total_pressure * 0.1
        
        # Central bank intervention
        intervention_stance = central_bank_policy.get('intervention_stance', 0.5)
        intervention_threshold = self.intervention_threshold
        
        if abs(potential_depreciation) > intervention_threshold and intervention_stance > 0.3:
            # Central bank intervenes
            intervention_effectiveness = min(self.intervention_strength * intervention_stance, 0.8)
            actual_depreciation = potential_depreciation * (1 - intervention_effectiveness)
            
            # Cost of intervention (depletion of reserves)
            intervention_cost = abs(potential_depreciation - actual_depreciation) * imports * 0.5
            self.foreign_reserves -= intervention_cost
        else:
            # No intervention
            actual_depreciation = potential_depreciation
            intervention_cost = 0
        
        # Calculate new exchange rate
        self.current_rate = self.current_rate * (1 + actual_depreciation)
        
        # Calculate real effective exchange rate (REER)
        inflation_differential = 0.02  # Bangladesh inflation - trading partner inflation
        self.real_effective_rate = self.real_effective_rate * (1 + actual_depreciation - inflation_differential)
        
        # Calculate impact on trade components
        export_impact = self.export_elasticity * actual_depreciation
        import_impact = -self.import_elasticity * actual_depreciation
        remittance_impact = self.remittance_sensitivity * actual_depreciation
        
        # Store historical data
        self.historical_rates[year_index] = self.current_rate
        
        # Compile results
        results = {
            'year_index': year_index,
            'exchange_rate': self.current_rate,
            'real_effective_rate': self.real_effective_rate,
            'depreciation_rate': actual_depreciation,
            'potential_depreciation': potential_depreciation,
            'foreign_reserves': self.foreign_reserves,
            'reserve_months': reserve_months,
            'trade_balance': trade_balance,
            'current_account_balance': current_account_balance,
            'capital_account_balance': capital_account_balance,
            'overall_balance': overall_balance,
            'intervention_cost': intervention_cost,
            'export_impact': export_impact,
            'import_impact': import_impact,
            'remittance_impact': remittance_impact,
            'market_volatility': market_volatility,
            'exchange_rate_pressure': base_pressure,
        }
        
        self.historical_impacts[year_index] = results
        
        return results


class ExternalBalanceFactors:
    """
    Model external balance factors affecting exchange rate
    """
    
    def __init__(self):
        """
        Initialize external balance factors model
        """
        # Remittance corridors
        self.remittance_corridors = {
            'middle_east': {
                'share': 0.55,
                'growth': 0.03,
                'volatility': 0.08,
            },
            'usa': {
                'share': 0.15,
                'growth': 0.05,
                'volatility': 0.07,
            },
            'uk': {
                'share': 0.10,
                'growth': 0.04,
                'volatility': 0.06,
            },
            'malaysia': {
                'share': 0.07,
                'growth': 0.06,
                'volatility': 0.09,
            },
            'other': {
                'share': 0.13,
                'growth': 0.04,
                'volatility': 0.08,
            },
        }
        
        # FDI source countries
        self.fdi_sources = {
            'china': {
                'share': 0.25,
                'growth': 0.08,
                'volatility': 0.15,
            },
            'eu': {
                'share': 0.20,
                'growth': 0.05,
                'volatility': 0.10,
            },
            'usa': {
                'share': 0.15,
                'growth': 0.06,
                'volatility': 0.12,
            },
            'japan': {
                'share': 0.12,
                'growth': 0.04,
                'volatility': 0.09,
            },
            'india': {
                'share': 0.10,
                'growth': 0.07,
                'volatility': 0.11,
            },
            'other': {
                'share': 0.18,
                'growth': 0.05,
                'volatility': 0.10,
            },
        }
        
        # Foreign aid and loans
        self.aid_loans_sources = {
            'multilateral': {
                'share': 0.50,
                'growth': 0.01,
                'volatility': 0.05,
            },
            'bilateral': {
                'share': 0.40,
                'growth': 0.00,
                'volatility': 0.08,
            },
            'other': {
                'share': 0.10,
                'growth': 0.02,
                'volatility': 0.10,
            },
        }
        
        # Capital outflow propensity
        self.capital_outflow_propensity = 0.15  # Outflow as percentage of GDP
        
        # Historical data
        self.historical_flows = {}
    
    def simulate_flows(self, 
                     year_index: int,
                     gdp: float,
                     export_earnings: float,
                     exchange_rate_yoy_change: float,
                     political_stability: float,
                     investment_climate: float) -> Dict[str, Any]:
        """
        Simulate external balance flows for a given year
        
        Args:
            year_index: Year index from simulation start
            gdp: GDP in million USD
            export_earnings: Export earnings in million USD
            exchange_rate_yoy_change: Year-over-year change in exchange rate
            political_stability: Political stability index (0-1)
            investment_climate: Investment climate index (0-1)
            
        Returns:
            Dict with flow simulation results
        """
        # Simulate remittance flows
        total_remittances = 0
        corridor_results = {}
        
        for corridor, data in self.remittance_corridors.items():
            # Base growth
            corridor_growth = data['growth']
            
            # Adjust for exchange rate
            exchange_effect = data['share'] * exchange_rate_yoy_change * 0.3
            
            # Adjust for political stability
            political_effect = (political_stability - 0.5) * 0.02
            
            # Random variation
            random_variation = np.random.normal(0, data['volatility'])
            
            # Calculate effective growth
            effective_growth = corridor_growth + exchange_effect + political_effect + random_variation
            
            # Update corridor share with constraint
            data['share'] = max(0.05, min(0.6, data['share'] * (1 + 0.1 * effective_growth)))
            
            # Normalize shares
            total_share = sum(c['share'] for c in self.remittance_corridors.values())
            for c in self.remittance_corridors.values():
                c['share'] = c['share'] / total_share
            
            # Base remittance as percentage of GDP
            base_remittance = 0.08 * gdp * data['share']
            
            # Apply growth
            corridor_remittance = base_remittance * (1 + effective_growth)
            total_remittances += corridor_remittance
            
            corridor_results[corridor] = {
                'amount': corridor_remittance,
                'share': data['share'],
                'growth': effective_growth,
            }
        
        # Simulate FDI flows
        total_fdi = 0
        fdi_results = {}
        
        for source, data in self.fdi_sources.items():
            # Base growth
            source_growth = data['growth']
            
            # Adjust for investment climate
            climate_effect = (investment_climate - 0.5) * 0.1
            
            # Adjust for political stability
            political_effect = (political_stability - 0.5) * 0.05
            
            # Random variation
            random_variation = np.random.normal(0, data['volatility'])
            
            # Calculate effective growth
            effective_growth = source_growth + climate_effect + political_effect + random_variation
            
            # Update source share with constraint
            data['share'] = max(0.05, min(0.4, data['share'] * (1 + 0.05 * effective_growth)))
            
            # Normalize shares
            total_share = sum(s['share'] for s in self.fdi_sources.values())
            for s in self.fdi_sources.values():
                s['share'] = s['share'] / total_share
            
            # Base FDI as percentage of GDP
            base_fdi = 0.02 * gdp * data['share']
            
            # Apply growth
            source_fdi = base_fdi * (1 + effective_growth)
            total_fdi += source_fdi
            
            fdi_results[source] = {
                'amount': source_fdi,
                'share': data['share'],
                'growth': effective_growth,
            }
        
        # Simulate foreign aid and loans
        total_aid_loans = 0
        aid_loans_results = {}
        
        for source, data in self.aid_loans_sources.items():
            # Base growth
            source_growth = data['growth']
            
            # Adjust for political stability
            political_effect = (political_stability - 0.5) * 0.03
            
            # Random variation
            random_variation = np.random.normal(0, data['volatility'])
            
            # Calculate effective growth
            effective_growth = source_growth + political_effect + random_variation
            
            # Base aid/loans as percentage of GDP
            base_aid_loans = 0.015 * gdp * data['share']
            
            # Apply growth
            source_aid_loans = base_aid_loans * (1 + effective_growth)
            total_aid_loans += source_aid_loans
            
            aid_loans_results[source] = {
                'amount': source_aid_loans,
                'share': data['share'],
                'growth': effective_growth,
            }
        
        # Simulate profit repatriation
        profit_repatriation = 0.6 * total_fdi  # 60% of annual FDI is repatriated as profit
        
        # Simulate other capital outflows
        base_outflow_propensity = self.capital_outflow_propensity
        
        # Adjust for exchange rate expectations
        if exchange_rate_yoy_change > 0.05:
            # Increased outflow with high depreciation
            outflow_adjustment = exchange_rate_yoy_change * 0.5
        else:
            outflow_adjustment = 0
        
        # Adjust for political stability
        stability_adjustment = (0.5 - political_stability) * 0.05
        
        effective_outflow_propensity = base_outflow_propensity + outflow_adjustment + stability_adjustment
        other_outflows = gdp * effective_outflow_propensity
        
        # Update capital outflow propensity with a stabilizing mechanism
        self.capital_outflow_propensity = 0.8 * self.capital_outflow_propensity + 0.2 * effective_outflow_propensity
        
        # Compile results
        results = {
            'year_index': year_index,
            'remittances': {
                'total': total_remittances,
                'as_percent_gdp': total_remittances / gdp if gdp > 0 else 0,
                'corridors': corridor_results,
            },
            'fdi': {
                'total': total_fdi,
                'as_percent_gdp': total_fdi / gdp if gdp > 0 else 0,
                'sources': fdi_results,
            },
            'aid_loans': {
                'total': total_aid_loans,
                'as_percent_gdp': total_aid_loans / gdp if gdp > 0 else 0,
                'sources': aid_loans_results,
            },
            'profit_repatriation': profit_repatriation,
            'other_outflows': other_outflows,
            'capital_outflow_propensity': self.capital_outflow_propensity,
            'net_capital_flow': total_fdi + total_aid_loans - profit_repatriation - other_outflows,
        }
        
        # Store historical data
        self.historical_flows[year_index] = results
        
        return results


class TradeFinanceMechanisms:
    """
    Model trade finance mechanisms and constraints
    """
    
    def __init__(self):
        """
        Initialize trade finance mechanisms model
        """
        # Letter of credit (LC) efficiency
        self.lc_efficiency = {
            'processing_time_days': 5,
            'cost_percentage': 0.015,  # 1.5% of trade value
            'rejection_rate': 0.08,  # 8% of LCs rejected
        }
        
        # Correspondent banking relationships
        self.correspondent_banking = {
            'relationship_strength': 0.7,  # 0-1 scale
            'coverage': 0.8,  # Coverage of major markets
            'cost_premium': 0.005,  # 0.5% premium
        }
        
        # Trade credit availability
        self.trade_credit = {
            'availability': 0.75,  # 0-1 scale
            'interest_premium': 0.03,  # 3% above benchmark
            'tenor_months': 4,  # Average tenor in months
        }
        
        # Foreign currency availability
        self.forex_availability = {
            'adequacy': 0.8,  # 0-1 scale
            'delay_days': 3,  # Average delay in days
            'spread_percentage': 0.01,  # 1% spread
        }
        
        # Islamic trade finance
        self.islamic_finance = {
            'market_share': 0.15,  # 15% of total trade finance
            'growth_rate': 0.08,  # 8% annual growth
            'cost_differential': -0.002,  # 0.2% cheaper
        }
        
        # Historical data
        self.historical_metrics = {}
    
    def simulate_trade_finance(self, 
                              year_index: int,
                              trade_volume: float,
                              exchange_rate_volatility: float,
                              financial_sector_development: float,
                              banking_sector_health: float,
                              foreign_reserves_adequacy: float) -> Dict[str, Any]:
        """
        Simulate trade finance mechanisms for a given year
        
        Args:
            year_index: Year index from simulation start
            trade_volume: Total trade volume in million USD
            exchange_rate_volatility: Exchange rate volatility (0-1)
            financial_sector_development: Financial sector development index (0-1)
            banking_sector_health: Banking sector health index (0-1)
            foreign_reserves_adequacy: Foreign reserves adequacy (0-1)
            
        Returns:
            Dict with trade finance simulation results
        """
        # LC efficiency evolution
        processing_improvement = 0.05 * financial_sector_development
        cost_reduction = 0.03 * financial_sector_development
        rejection_reduction = 0.04 * banking_sector_health
        
        self.lc_efficiency['processing_time_days'] = max(2, self.lc_efficiency['processing_time_days'] * (1 - processing_improvement))
        self.lc_efficiency['cost_percentage'] = max(0.005, self.lc_efficiency['cost_percentage'] * (1 - cost_reduction))
        self.lc_efficiency['rejection_rate'] = max(0.02, self.lc_efficiency['rejection_rate'] * (1 - rejection_reduction))
        
        # Correspondent banking evolution
        relationship_change = 0.02 * banking_sector_health - 0.01 * exchange_rate_volatility
        coverage_change = 0.02 * financial_sector_development
        cost_change = -0.02 * banking_sector_health + 0.03 * exchange_rate_volatility
        
        self.correspondent_banking['relationship_strength'] = max(0.3, min(0.95, self.correspondent_banking['relationship_strength'] + relationship_change))
        self.correspondent_banking['coverage'] = max(0.5, min(0.98, self.correspondent_banking['coverage'] + coverage_change))
        self.correspondent_banking['cost_premium'] = max(0.001, min(0.01, self.correspondent_banking['cost_premium'] * (1 + cost_change)))
        
        # Trade credit evolution
        availability_change = 0.03 * banking_sector_health - 0.05 * exchange_rate_volatility
        interest_change = -0.02 * financial_sector_development + 0.04 * exchange_rate_volatility
        tenor_change = 0.03 * banking_sector_health - 0.02 * exchange_rate_volatility
        
        self.trade_credit['availability'] = max(0.4, min(0.95, self.trade_credit['availability'] + availability_change))
        self.trade_credit['interest_premium'] = max(0.01, min(0.08, self.trade_credit['interest_premium'] * (1 + interest_change)))
        self.trade_credit['tenor_months'] = max(2, min(6, self.trade_credit['tenor_months'] * (1 + tenor_change)))
        
        # Foreign currency availability evolution
        adequacy_change = 0.05 * foreign_reserves_adequacy - 0.03 * exchange_rate_volatility
        delay_change = -0.04 * foreign_reserves_adequacy + 0.06 * exchange_rate_volatility
        spread_change = -0.03 * foreign_reserves_adequacy + 0.05 * exchange_rate_volatility
        
        self.forex_availability['adequacy'] = max(0.3, min(0.98, self.forex_availability['adequacy'] + adequacy_change))
        self.forex_availability['delay_days'] = max(1, min(10, self.forex_availability['delay_days'] * (1 + delay_change)))
        self.forex_availability['spread_percentage'] = max(0.003, min(0.03, self.forex_availability['spread_percentage'] * (1 + spread_change)))
        
        # Islamic trade finance evolution
        market_growth = self.islamic_finance['growth_rate'] * financial_sector_development
        self.islamic_finance['market_share'] = min(0.3, self.islamic_finance['market_share'] * (1 + market_growth))
        
        # Calculate overall trade finance efficiency
        lc_efficiency_score = (
            (1 - self.lc_efficiency['processing_time_days'] / 10) * 0.4 +
            (1 - self.lc_efficiency['cost_percentage'] / 0.03) * 0.3 +
            (1 - self.lc_efficiency['rejection_rate'] / 0.15) * 0.3
        )
        
        correspondent_banking_score = (
            self.correspondent_banking['relationship_strength'] * 0.4 +
            self.correspondent_banking['coverage'] * 0.4 +
            (1 - self.correspondent_banking['cost_premium'] / 0.01) * 0.2
        )
        
        trade_credit_score = (
            self.trade_credit['availability'] * 0.5 +
            (1 - self.trade_credit['interest_premium'] / 0.08) * 0.3 +
            (self.trade_credit['tenor_months'] / 6) * 0.2
        )
        
        forex_availability_score = (
            self.forex_availability['adequacy'] * 0.5 +
            (1 - self.forex_availability['delay_days'] / 10) * 0.3 +
            (1 - self.forex_availability['spread_percentage'] / 0.03) * 0.2
        )
        
        # Calculate weighted overall score
        overall_efficiency = (
            lc_efficiency_score * 0.3 +
            correspondent_banking_score * 0.25 +
            trade_credit_score * 0.25 +
            forex_availability_score * 0.2
        )
        
        # Calculate trade finance costs
        base_finance_cost = (
            self.lc_efficiency['cost_percentage'] +
            self.correspondent_banking['cost_premium'] +
            self.trade_credit['interest_premium'] * (self.trade_credit['tenor_months'] / 12) +
            self.forex_availability['spread_percentage']
        )
        
        # Adjust for Islamic finance (which has slightly different costs)
        effective_finance_cost = (
            base_finance_cost * (1 - self.islamic_finance['market_share']) +
            (base_finance_cost + self.islamic_finance['cost_differential']) * self.islamic_finance['market_share']
        )
        
        # Calculate trade finance constraints impact
        availability_constraint = (
            (1 - self.trade_credit['availability']) * 0.5 +
            (1 - self.forex_availability['adequacy']) * 0.5
        )
        
        # Calculate total trade finance volume
        trade_finance_volume = trade_volume * (1 - availability_constraint * 0.2)
        
        # Calculate trade financing gap
        trade_financing_gap = trade_volume - trade_finance_volume
        
        # Compile results
        results = {
            'year_index': year_index,
            'lc_efficiency': {
                'processing_time_days': self.lc_efficiency['processing_time_days'],
                'cost_percentage': self.lc_efficiency['cost_percentage'],
                'rejection_rate': self.lc_efficiency['rejection_rate'],
                'efficiency_score': lc_efficiency_score,
            },
            'correspondent_banking': {
                'relationship_strength': self.correspondent_banking['relationship_strength'],
                'coverage': self.correspondent_banking['coverage'],
                'cost_premium': self.correspondent_banking['cost_premium'],
                'efficiency_score': correspondent_banking_score,
            },
            'trade_credit': {
                'availability': self.trade_credit['availability'],
                'interest_premium': self.trade_credit['interest_premium'],
                'tenor_months': self.trade_credit['tenor_months'],
                'efficiency_score': trade_credit_score,
            },
            'forex_availability': {
                'adequacy': self.forex_availability['adequacy'],
                'delay_days': self.forex_availability['delay_days'],
                'spread_percentage': self.forex_availability['spread_percentage'],
                'efficiency_score': forex_availability_score,
            },
            'islamic_finance': {
                'market_share': self.islamic_finance['market_share'],
                'growth_rate': self.islamic_finance['growth_rate'],
                'cost_differential': self.islamic_finance['cost_differential'],
            },
            'overall_efficiency': overall_efficiency,
            'effective_finance_cost': effective_finance_cost,
            'trade_finance_volume': trade_finance_volume,
            'trade_financing_gap': trade_financing_gap,
            'financing_gap_percentage': trade_financing_gap / trade_volume if trade_volume > 0 else 0,
        }
        
        # Store historical data
        self.historical_metrics[year_index] = results
        
        return results
