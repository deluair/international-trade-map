"""
Compliance model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class ComplianceModel:
    """
    Model evolution of standards, certification, and compliance
    
    This class simulates how labor standards, environmental compliance,
    and product standards affect Bangladesh's trade competitiveness.
    """
    
    def __init__(self, config):
        """
        Initialize compliance model
        
        Args:
            config: Configuration dictionary for compliance parameters
        """
        # Extract configuration
        self.labor_standards = config.get('labor_standards', {})
        self.environmental_standards = config.get('environmental_standards', {})
        self.product_standards = config.get('product_standards', {})
        
        # Initialize submodels
        self.labor = LaborStandardsModel(self.labor_standards)
        self.environmental = EnvironmentalComplianceModel(self.environmental_standards)
        self.product = ProductStandardsModel(self.product_standards)
        
        # Historical data
        self.historical_compliance = {}
    
    def simulate_compliance_environment(self, 
                                      year_index: int,
                                      simulation_year: int,
                                      regulatory_developments: float,
                                      buyer_requirements: float) -> Dict[str, Any]:
        """
        Simulate compliance environment for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            regulatory_developments: Strength of regulatory developments (0-1)
            buyer_requirements: Stringency of buyer requirements (0-1)
            
        Returns:
            Dict with compliance simulation results
        """
        # Simulate labor standards
        labor_result = self.labor.simulate_standards(
            year_index=year_index,
            simulation_year=simulation_year,
            regulatory_pressure=regulatory_developments,
            buyer_requirements=buyer_requirements
        )
        
        # Simulate environmental compliance
        environmental_result = self.environmental.simulate_compliance(
            year_index=year_index,
            simulation_year=simulation_year,
            regulatory_pressure=regulatory_developments,
            buyer_requirements=buyer_requirements
        )
        
        # Simulate product standards
        product_result = self.product.simulate_standards(
            year_index=year_index,
            simulation_year=simulation_year,
            regulatory_pressure=regulatory_developments,
            buyer_requirements=buyer_requirements
        )
        
        # Calculate compliance costs
        labor_compliance_cost = labor_result['compliance_cost']
        environmental_compliance_cost = environmental_result['compliance_cost']
        product_compliance_cost = product_result['compliance_cost']
        
        total_compliance_cost = (
            labor_compliance_cost * 0.4 +
            environmental_compliance_cost * 0.3 +
            product_compliance_cost * 0.3
        )
        
        # Calculate market access premium
        labor_premium = labor_result['market_premium']
        environmental_premium = environmental_result['market_premium']
        product_premium = product_result['market_premium']
        
        total_market_premium = (
            labor_premium * 0.3 +
            environmental_premium * 0.4 +
            product_premium * 0.3
        )
        
        # Calculate net impact (premium minus cost)
        net_compliance_impact = total_market_premium - total_compliance_cost
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'labor_standards': labor_result,
            'environmental_compliance': environmental_result,
            'product_standards': product_result,
            'total_compliance_cost': total_compliance_cost,
            'total_market_premium': total_market_premium,
            'net_compliance_impact': net_compliance_impact,
        }
        
        # Store historical data
        self.historical_compliance[year_index] = results
        
        return results


class LaborStandardsModel:
    """
    Model labor standards evolution and impacts
    """
    
    def __init__(self, config):
        """
        Initialize labor standards model
        
        Args:
            config: Configuration dictionary for labor standards
        """
        # Minimum wage parameters
        self.minimum_wage = 75  # USD per month
        self.wage_growth = config.get('minimum_wage_growth', 0.08)
        
        # Compliance parameters
        self.compliance_cost = config.get('compliance_cost', 0.03)
        self.buyer_requirements_increase = config.get('buyer_requirements_increase', 0.05)
        
        # Current standards implementation
        self.standards = {
            'wage_compliance': 0.7,  # Compliance level (0-1)
            'safety_compliance': 0.8,
            'working_hours_compliance': 0.6,
            'child_labor_compliance': 0.9,
            'union_rights_compliance': 0.5,
        }
        
        # Labor unrest risk
        self.unrest_risk = 0.3  # Probability of significant labor unrest
        
        # Living wage gap
        self.living_wage = 150  # USD per month
        self.living_wage_growth = 0.04  # Annual growth
        
        # Historical data
        self.historical_standards = {}
    
    def simulate_standards(self,
                         year_index: int,
                         simulation_year: int,
                         regulatory_pressure: float,
                         buyer_requirements: float) -> Dict[str, Any]:
        """
        Simulate labor standards for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            regulatory_pressure: Strength of regulatory developments (0-1)
            buyer_requirements: Stringency of buyer requirements (0-1)
            
        Returns:
            Dict with labor standards simulation results
        """
        # Update minimum wage
        effective_wage_growth = self.wage_growth * (0.8 + 0.4 * regulatory_pressure)
        self.minimum_wage *= (1 + effective_wage_growth)
        
        # Update living wage
        self.living_wage *= (1 + self.living_wage_growth)
        
        # Calculate living wage gap
        living_wage_gap = max(0, (self.living_wage - self.minimum_wage) / self.living_wage)
        
        # Update standards compliance
        for standard, level in self.standards.items():
            # Base improvement from regulations and buyer pressure
            base_improvement = 0.02 * regulatory_pressure + 0.03 * buyer_requirements
            
            # Random variation
            variation = np.random.normal(0, 0.01)
            
            # Apply improvement with diminishing returns
            improvement = base_improvement * (1 - level * 0.5) + variation
            self.standards[standard] = min(0.98, max(level + improvement, level))
        
        # Calculate compliance costs
        # Base cost from compliance levels
        avg_compliance = sum(self.standards.values()) / len(self.standards)
        base_cost = self.compliance_cost * avg_compliance
        
        # Additional cost from wage growth
        wage_cost = effective_wage_growth * 0.5
        
        total_compliance_cost = base_cost + wage_cost
        
        # Calculate market premium
        # Premium increases with compliance and buyer requirements
        base_premium = avg_compliance * 0.02
        buyer_premium = buyer_requirements * 0.04
        
        market_premium = base_premium + buyer_premium
        
        # Update labor unrest risk
        # Risk decreases with higher wages and better standards, increases with living wage gap
        risk_change = (
            -0.02 * effective_wage_growth  # Wage growth reduces risk
            -0.01 * (avg_compliance - 0.7)  # Better standards reduce risk
            +0.02 * living_wage_gap  # Living wage gap increases risk
        )
        
        self.unrest_risk = max(0.05, min(0.8, self.unrest_risk + risk_change))
        
        # Calculate unrest probability for this year
        unrest_probability = self.unrest_risk * (1 - regulatory_pressure * 0.3)
        
        # Determine if unrest occurs
        unrest_occurs = np.random.random() < unrest_probability
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'minimum_wage': self.minimum_wage,
            'minimum_wage_growth': effective_wage_growth,
            'living_wage': self.living_wage,
            'living_wage_gap': living_wage_gap,
            'standards_compliance': self.standards.copy(),
            'average_compliance': avg_compliance,
            'compliance_cost': total_compliance_cost,
            'market_premium': market_premium,
            'unrest_risk': self.unrest_risk,
            'unrest_occurs': unrest_occurs,
        }
        
        # Store historical data
        self.historical_standards[year_index] = results
        
        return results


class EnvironmentalComplianceModel:
    """
    Model environmental compliance evolution and impacts
    """
    
    def __init__(self, config):
        """
        Initialize environmental compliance model
        
        Args:
            config: Configuration dictionary for environmental standards
        """
        # Carbon border tax
        self.carbon_border_tax = config.get('carbon_border_tax', {})
        
        # Green certification
        self.green_certification = {
            'certification_premium': config.get('green_certification_premium', 0.05),
            'adoption_rate': config.get('certification_adoption_rate', 0.1),
            'current_adoption': 0.2,  # Share of exporters with certification
        }
        
        # Environmental compliance areas
        self.compliance_areas = {
            'water_treatment': 0.6,  # Compliance level (0-1)
            'air_emissions': 0.5,
            'chemical_management': 0.7,
            'waste_management': 0.6,
            'energy_efficiency': 0.4,
        }
        
        # Carbon intensity
        self.carbon_intensity = 0.8  # Relative to global average (1.0)
        
        # Historical data
        self.historical_compliance = {}
    
    def simulate_compliance(self,
                          year_index: int,
                          simulation_year: int,
                          regulatory_pressure: float,
                          buyer_requirements: float) -> Dict[str, Any]:
        """
        Simulate environmental compliance for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            regulatory_pressure: Strength of regulatory developments (0-1)
            buyer_requirements: Stringency of buyer requirements (0-1)
            
        Returns:
            Dict with environmental compliance simulation results
        """
        # Check carbon border tax implementation
        carbon_tax_implemented = False
        carbon_tax_rate = 0
        
        if 'implementation_year' in self.carbon_border_tax:
            if simulation_year >= self.carbon_border_tax['implementation_year']:
                carbon_tax_implemented = True
                base_rate = self.carbon_border_tax.get('initial_level', 0.02)
                years_active = simulation_year - self.carbon_border_tax['implementation_year']
                annual_increase = self.carbon_border_tax.get('annual_increase', 0.005)
                
                carbon_tax_rate = base_rate + years_active * annual_increase
        
        # Update green certification adoption
        base_adoption_increase = self.green_certification['adoption_rate']
        adjusted_increase = base_adoption_increase * (0.8 + 0.4 * buyer_requirements)
        
        # Carbon tax accelerates green certification
        if carbon_tax_implemented:
            adjusted_increase *= (1 + carbon_tax_rate * 5)
        
        self.green_certification['current_adoption'] = min(0.9, self.green_certification['current_adoption'] + adjusted_increase)
        
        # Update compliance areas
        for area, level in self.compliance_areas.items():
            # Base improvement from regulations and buyer pressure
            base_improvement = 0.02 * regulatory_pressure + 0.02 * buyer_requirements
            
            # Carbon tax adds additional pressure
            if carbon_tax_implemented and area in ['air_emissions', 'energy_efficiency']:
                base_improvement += carbon_tax_rate * 0.5
            
            # Random variation
            variation = np.random.normal(0, 0.01)
            
            # Apply improvement with diminishing returns
            improvement = base_improvement * (1 - level * 0.5) + variation
            self.compliance_areas[area] = min(0.95, max(level + improvement, level))
        
        # Update carbon intensity
        carbon_reduction = (
            0.01 * (self.compliance_areas['energy_efficiency'] - 0.4) * 2 +
            0.005 * (self.compliance_areas['air_emissions'] - 0.5) * 2
        )
        
        if carbon_tax_implemented:
            carbon_reduction += carbon_tax_rate * 0.3
        
        self.carbon_intensity = max(0.4, self.carbon_intensity - carbon_reduction)
        
        # Calculate compliance costs
        avg_compliance = sum(self.compliance_areas.values()) / len(self.compliance_areas)
        
        # Base compliance cost
        base_cost = 0.02 * avg_compliance
        
        # Additional cost from carbon tax
        carbon_tax_cost = 0
        if carbon_tax_implemented:
            carbon_tax_cost = carbon_tax_rate * self.carbon_intensity
        
        # Green certification cost
        cert_adoption_cost = self.green_certification['current_adoption'] * 0.01
        
        total_compliance_cost = base_cost + carbon_tax_cost + cert_adoption_cost
        
        # Calculate market premium
        # Premium from green certification
        cert_premium = self.green_certification['current_adoption'] * self.green_certification['certification_premium']
        
        # Premium from general environmental performance
        environmental_premium = avg_compliance * 0.03 * buyer_requirements
        
        market_premium = cert_premium + environmental_premium
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'carbon_tax_implemented': carbon_tax_implemented,
            'carbon_tax_rate': carbon_tax_rate,
            'green_certification_adoption': self.green_certification['current_adoption'],
            'compliance_areas': self.compliance_areas.copy(),
            'average_compliance': avg_compliance,
            'carbon_intensity': self.carbon_intensity,
            'compliance_cost': total_compliance_cost,
            'market_premium': market_premium,
        }
        
        # Store historical data
        self.historical_compliance[year_index] = results
        
        return results


class ProductStandardsModel:
    """
    Model product standards evolution and impacts
    """
    
    def __init__(self, config):
        """
        Initialize product standards model
        
        Args:
            config: Configuration dictionary for product standards
        """
        # Technical barriers growth
        self.technical_barriers_growth = config.get('technical_barriers_growth', 0.06)
        
        # Testing capacity
        self.testing_capacity = 0.5  # 0-1 scale
        self.testing_improvement = config.get('testing_capacity_improvement', 0.08)
        
        # Compliance capability
        self.compliance_capability = 0.6  # 0-1 scale
        self.capability_improvement = config.get('compliance_capability_improvement', 0.07)
        
        # Standards by sector
        self.sector_standards = {
            'rmg': {
                'current_requirements': 0.6,  # Complexity of requirements (0-1)
                'current_compliance': 0.7,  # Compliance level (0-1)
                'growth_rate': 0.04,  # Annual growth in requirements
            },
            'pharma': {
                'current_requirements': 0.8,
                'current_compliance': 0.8,
                'growth_rate': 0.05,
            },
            'food': {
                'current_requirements': 0.7,
                'current_compliance': 0.6,
                'growth_rate': 0.06,
            },
            'electronics': {
                'current_requirements': 0.75,
                'current_compliance': 0.55,
                'growth_rate': 0.05,
            },
            'other': {
                'current_requirements': 0.6,
                'current_compliance': 0.6,
                'growth_rate': 0.04,
            },
        }
        
        # Certification adoption
        self.certifications = {
            'iso9001': 0.4,  # Adoption rate (0-1)
            'iso14001': 0.3,
            'halal': 0.5,
            'gmp': 0.6,
            'other': 0.3,
        }
        
        # Historical data
        self.historical_standards = {}
    
    def simulate_standards(self,
                         year_index: int,
                         simulation_year: int,
                         regulatory_pressure: float,
                         buyer_requirements: float) -> Dict[str, Any]:
        """
        Simulate product standards for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            regulatory_pressure: Strength of regulatory developments (0-1)
            buyer_requirements: Stringency of buyer requirements (0-1)
            
        Returns:
            Dict with product standards simulation results
        """
        # Update testing capacity
        capacity_increase = self.testing_improvement * (0.8 + 0.4 * regulatory_pressure)
        self.testing_capacity = min(0.95, self.testing_capacity + capacity_increase * (1 - self.testing_capacity * 0.5))
        
        # Update compliance capability
        capability_increase = self.capability_improvement * (0.8 + 0.4 * buyer_requirements)
        self.compliance_capability = min(0.95, self.compliance_capability + capability_increase * (1 - self.compliance_capability * 0.5))
        
        # Update sector standards
        sector_results = {}
        
        for sector, standards in self.sector_standards.items():
            # Update requirements complexity
            effective_growth = standards['growth_rate'] * (0.8 + 0.4 * buyer_requirements)
            new_requirements = min(0.95, standards['current_requirements'] + effective_growth * standards['current_requirements'])
            
            # Update compliance level
            compliance_gap = new_requirements - standards['current_compliance']
            compliance_improvement = (
                0.03 * self.testing_capacity +
                0.04 * self.compliance_capability +
                0.02 * regulatory_pressure -
                0.05 * compliance_gap
            )
            
            new_compliance = min(0.95, max(0.3, standards['current_compliance'] + compliance_improvement))
            
            # Calculate compliance gap
            new_gap = new_requirements - new_compliance
            
            # Update standards
            standards['current_requirements'] = new_requirements
            standards['current_compliance'] = new_compliance
            
            # Store in results
            sector_results[sector] = {
                'requirements': new_requirements,
                'compliance': new_compliance,
                'gap': new_gap,
            }
        
        # Update certification adoption
        certification_results = {}
        
        for cert, adoption in self.certifications.items():
            # Base adoption increase
            base_increase = 0.03
            
            # Adjusted by buyer requirements and capability
            adjusted_increase = base_increase * (0.8 + 0.4 * buyer_requirements) * (0.8 + 0.4 * self.compliance_capability)
            
            # Apply increase with diminishing returns
            new_adoption = min(0.9, adoption + adjusted_increase * (1 - adoption * 0.7))
            self.certifications[cert] = new_adoption
            
            certification_results[cert] = new_adoption
        
        # Calculate average standards compliance
        avg_requirements = sum(s['requirements'] for s in sector_results.values()) / len(sector_results)
        avg_compliance = sum(s['compliance'] for s in sector_results.values()) / len(sector_results)
        avg_gap = avg_requirements - avg_compliance
        
        # Calculate compliance costs
        
        # Base cost from requirements
        base_cost = 0.02 * avg_requirements
        
        # Additional cost from compliance gap
        gap_cost = 0.03 * avg_gap
        
        # Certification cost
        cert_cost = 0.01 * sum(self.certifications.values()) / len(self.certifications)
        
        total_compliance_cost = base_cost + gap_cost + cert_cost
        
        # Calculate market premium
        
        # Premium from certification
        cert_premium = 0.03 * sum(self.certifications.values()) / len(self.certifications)
        
        # Premium from compliance level
        compliance_premium = 0.04 * avg_compliance * buyer_requirements
        
        market_premium = cert_premium + compliance_premium
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'testing_capacity': self.testing_capacity,
            'compliance_capability': self.compliance_capability,
            'sector_standards': sector_results,
            'certifications': certification_results,
            'average_requirements': avg_requirements,
            'average_compliance': avg_compliance,
            'average_gap': avg_gap,
            'compliance_cost': total_compliance_cost,
            'market_premium': market_premium,
        }
        
        # Store historical data
        self.historical_standards[year_index] = results
        
        return results
