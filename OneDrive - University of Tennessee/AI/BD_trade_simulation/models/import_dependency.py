"""
Import dependency model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class ImportDependencyModel:
    """
    Model import requirements and dependencies
    
    This class simulates Bangladesh's import needs across different categories,
    including industrial inputs, consumer goods, and energy.
    """
    
    def __init__(self, 
                 category_name: str,
                 current_volume: float,
                 domestic_production_ratio: float,
                 growth_trajectory: float,
                 price_sensitivity: float,
                 substitution_elasticity: float,
                 categories: Optional[List[str]] = None):
        """
        Initialize an import dependency model
        
        Args:
            category_name: Name of the import category
            current_volume: Current import volume in million USD
            domestic_production_ratio: Ratio of domestic production to total consumption
            growth_trajectory: Base annual growth rate of imports
            price_sensitivity: Sensitivity to price changes (0-1)
            substitution_elasticity: Elasticity of substitution between imports and domestic production
            categories: List of subcategories within this import category
        """
        self.category_name = category_name
        self.current_volume = current_volume
        self.domestic_production_ratio = domestic_production_ratio
        self.base_growth_rate = growth_trajectory
        self.price_sensitivity = price_sensitivity
        self.substitution_elasticity = substitution_elasticity
        self.categories = categories or []
        
        # Initialize historical data storage
        self.historical_volumes = {0: current_volume}  # year 0 = start_year
        self.historical_domestic_ratios = {0: domestic_production_ratio}
        
        # Initialize subcategory models if applicable
        self.subcategory_models = {}
        if categories:
            # In a real implementation, we would initialize subcategory models here
            pass
    
    def simulate_import_needs(self, 
                             year_index: int,
                             domestic_production_growth: float,
                             consumption_demand_growth: float,
                             exchange_rate_impact: float,
                             tariff_changes: float,
                             global_price_changes: Dict[str, float],
                             logistics_cost: float,
                             domestic_capacity_investment: float) -> Dict[str, Any]:
        """
        Simulate import requirements for this category for one year
        
        Args:
            year_index: Year index from simulation start (0 = start_year)
            domestic_production_growth: Growth rate of domestic production
            consumption_demand_growth: Growth rate of domestic consumption demand
            exchange_rate_impact: Impact of exchange rate movements (-1 to 1 scale)
            tariff_changes: Change in import tariffs
            global_price_changes: Changes in global prices for different import categories
            logistics_cost: Import logistics cost factor
            domestic_capacity_investment: Investment in domestic production capacity
            
        Returns:
            Dict with simulation results for this year
        """
        # Get previous year's volume and domestic ratio
        prev_volume = self.historical_volumes.get(year_index - 1, self.current_volume)
        prev_domestic_ratio = self.historical_domestic_ratios.get(year_index - 1, self.domestic_production_ratio)
        
        # Calculate base import growth adjusted for consumption demand
        adjusted_growth = self.base_growth_rate * (1 + 0.7 * (consumption_demand_growth - 0.04))
        
        # Calculate total consumption (imports + domestic production)
        prev_total_consumption = prev_volume / (1 - prev_domestic_ratio)
        
        # Calculate new total consumption based on consumption demand growth
        new_total_consumption = prev_total_consumption * (1 + consumption_demand_growth)
        
        # Calculate price impact on import demand
        # Combine exchange rate, tariff, global prices, and logistics impacts
        relevant_price_change = global_price_changes.get(self.category_name, 0)
        price_impact = (
            exchange_rate_impact +  # Impact of currency depreciation/appreciation
            tariff_changes +  # Impact of tariff changes
            relevant_price_change +  # Impact of global price changes
            logistics_cost * 0.5  # Impact of logistics costs
        )
        
        # Calculate price elasticity effect
        price_elasticity_effect = -price_impact * self.price_sensitivity
        
        # Calculate domestic production ratio evolution
        # Based on domestic capacity investment and technology transfer
        domestic_ratio_change = (
            domestic_production_growth * 0.3 +  # Effect of general domestic production growth
            domestic_capacity_investment * 0.2  # Effect of targeted capacity investment
        )
        
        # Apply substitution elasticity
        if price_impact > 0:  # If imports are getting more expensive
            # Higher substitution to domestic production
            substitution_effect = price_impact * self.substitution_elasticity
            domestic_ratio_change += substitution_effect
        else:  # If imports are getting cheaper
            # Lower substitution to domestic production
            substitution_effect = price_impact * self.substitution_elasticity * 0.5
            domestic_ratio_change += substitution_effect
        
        # Calculate new domestic production ratio with constraints
        new_domestic_ratio = max(0.1, min(0.9, prev_domestic_ratio + domestic_ratio_change * 0.05))
        
        # Calculate new import volume
        new_volume = new_total_consumption * (1 - new_domestic_ratio)
        
        # Apply direct import growth effects
        new_volume = new_volume * (1 + price_elasticity_effect)
        
        # Apply some random variation (economic shocks, etc.)
        random_variation = np.random.normal(0, 0.02)  # 2% standard deviation
        new_volume = new_volume * (1 + random_variation)
        
        # Store historical data
        self.historical_volumes[year_index] = new_volume
        self.historical_domestic_ratios[year_index] = new_domestic_ratio
        
        # Calculate effective growth rate
        effective_growth_rate = (new_volume / prev_volume) - 1
        
        # Return results
        return {
            'category_name': self.category_name,
            'year_index': year_index,
            'import_volume': new_volume,
            'growth_rate': effective_growth_rate,
            'domestic_production_ratio': new_domestic_ratio,
            'total_consumption': new_total_consumption,
            'price_impact': price_impact,
            'price_elasticity_effect': price_elasticity_effect,
            'substitution_effect': substitution_effect if 'substitution_effect' in locals() else 0,
            'random_variation': random_variation
        }
    
    def simulate_subcategories(self, year_index, **kwargs):
        """
        Simulate all subcategories for this import category
        
        Args:
            year_index: Year index from simulation start
            **kwargs: Parameters to pass to subcategory simulation
            
        Returns:
            Dict of simulation results by subcategory
        """
        if not self.subcategory_models:
            return {}
        
        subcategory_results = {}
        for name, model in self.subcategory_models.items():
            subcategory_results[name] = model.simulate_import_needs(year_index, **kwargs)
        
        return subcategory_results


class IndustrialInputsModel(ImportDependencyModel):
    """
    Model for industrial inputs imports (raw materials, machinery, etc.)
    """
    
    def __init__(self, config):
        """
        Initialize industrial inputs import model with additional parameters
        
        Args:
            config: Configuration dictionary for industrial inputs
        """
        super().__init__(
            category_name=config['name'],
            current_volume=config['current_volume'],
            domestic_production_ratio=config['domestic_production_ratio'],
            growth_trajectory=config['growth_trajectory'],
            price_sensitivity=config['price_sensitivity'],
            substitution_elasticity=config['substitution_elasticity'],
            categories=config['categories']
        )
        
        # Industrial inputs specific attributes
        self.rmg_dependency = 0.7  # High dependency on RMG sector
        self.capital_machinery_share = 0.3  # Share of capital machinery in imports
        self.intermediate_goods_share = 0.5  # Share of intermediate goods
        self.local_content_development = 0.2  # Development level of local content
        self.just_in_time_ratio = 0.4  # Ratio of just-in-time inventory requirements
    
    def simulate_import_needs(self, year_index, **kwargs):
        """
        Extend the base simulation with industrial inputs specific factors
        """
        # Extract additional parameters
        rmg_growth = kwargs.get('rmg_growth', 0.05)
        industrial_policy_support = kwargs.get('industrial_policy_support', 0.5)
        tech_transfer = kwargs.get('tech_transfer', 0.3)
        inventory_policy = kwargs.get('inventory_policy', 0.5)
        
        # Get base simulation results
        results = super().simulate_import_needs(year_index, **kwargs)
        
        # Adjust for RMG sector dependency
        rmg_impact = rmg_growth * self.rmg_dependency
        
        # Simulate local content development
        local_content_improvement = 0.02 * industrial_policy_support + 0.01 * tech_transfer
        self.local_content_development = min(0.8, self.local_content_development + local_content_improvement)
        
        # Adjust just-in-time requirements based on logistics and inventory policy
        logistics_performance = kwargs.get('logistics_performance', 0.5)
        just_in_time_change = (logistics_performance - 0.5) * 0.1 + (inventory_policy - 0.5) * 0.05
        self.just_in_time_ratio = max(0.2, min(0.8, self.just_in_time_ratio + just_in_time_change))
        
        # Calculate impact of JIT requirements on import volume
        jit_impact = 0.05 * (self.just_in_time_ratio - 0.4)
        
        # Calculate impact of local content development on import volume
        local_content_impact = -0.1 * (self.local_content_development - 0.2)
        
        # Apply industrial inputs specific impacts
        results['import_volume'] *= (1 + rmg_impact + jit_impact + local_content_impact)
        
        # Add sector-specific metrics to results
        results['rmg_dependency'] = self.rmg_dependency
        results['local_content_development'] = self.local_content_development
        results['just_in_time_ratio'] = self.just_in_time_ratio
        results['rmg_impact'] = rmg_impact
        results['jit_impact'] = jit_impact
        results['local_content_impact'] = local_content_impact
        
        return results


class ConsumerGoodsModel(ImportDependencyModel):
    """
    Model for consumer goods imports
    """
    
    def __init__(self, config):
        """
        Initialize consumer goods import model with additional parameters
        
        Args:
            config: Configuration dictionary for consumer goods
        """
        super().__init__(
            category_name=config['name'],
            current_volume=config['current_volume'],
            domestic_production_ratio=config['domestic_production_ratio'],
            growth_trajectory=config['growth_trajectory'],
            price_sensitivity=config['price_sensitivity'],
            substitution_elasticity=config['substitution_elasticity'],
            categories=config['categories']
        )
        
        # Consumer goods specific attributes
        self.essential_goods_share = 0.6  # Share of essential goods in imports
        self.luxury_goods_share = 0.2  # Share of luxury goods
        self.electronics_share = 0.3  # Share of electronics
        self.food_imports_share = 0.25  # Share of food imports
        self.import_competing_production = 0.3  # Domestic production competing with imports
        self.consumer_preference_imports = 0.6  # Consumer preference for imports (0-1)
    
    def simulate_import_needs(self, year_index, **kwargs):
        """
        Extend the base simulation with consumer goods specific factors
        """
        # Extract additional parameters
        gdp_per_capita_growth = kwargs.get('gdp_per_capita_growth', 0.04)
        urbanization_rate = kwargs.get('urbanization_rate', 0.5)
        middle_class_growth = kwargs.get('middle_class_growth', 0.06)
        domestic_quality_improvement = kwargs.get('domestic_quality_improvement', 0.03)
        
        # Get base simulation results
        results = super().simulate_import_needs(year_index, **kwargs)
        
        # Calculate income effect on luxury goods imports
        luxury_growth = gdp_per_capita_growth * 2 * middle_class_growth * 1.5
        luxury_impact = luxury_growth * self.luxury_goods_share
        
        # Calculate impact on essential goods imports
        essential_impact = gdp_per_capita_growth * 0.5 * self.essential_goods_share
        
        # Calculate electronics imports growth
        electronics_growth = gdp_per_capita_growth * 1.8 + urbanization_rate * 0.2
        electronics_impact = electronics_growth * self.electronics_share
        
        # Calculate food imports impact
        food_self_sufficiency_improvement = kwargs.get('agricultural_productivity', 0.02)
        food_import_impact = (gdp_per_capita_growth * 0.3 - food_self_sufficiency_improvement) * self.food_imports_share
        
        # Update consumer preference for imports
        preference_change = middle_class_growth * 0.1 - domestic_quality_improvement * 0.2
        self.consumer_preference_imports = max(0.3, min(0.9, self.consumer_preference_imports + preference_change))
        
        # Calculate impact of consumer preference
        preference_impact = 0.1 * (self.consumer_preference_imports - 0.6)
        
        # Calculate impact of import-competing production
        import_competing_change = domestic_quality_improvement * 0.3
        self.import_competing_production = min(0.8, self.import_competing_production + import_competing_change)
        competing_impact = -0.15 * (self.import_competing_production - 0.3)
        
        # Apply consumer goods specific impacts
        total_impact = luxury_impact + essential_impact + electronics_impact + food_import_impact + preference_impact + competing_impact
        results['import_volume'] *= (1 + total_impact)
        
        # Update category shares based on growth differentials
        total_share = self.luxury_goods_share + self.essential_goods_share + self.electronics_share + self.food_imports_share
        luxury_share_change = (luxury_growth - gdp_per_capita_growth) * 0.02
        electronics_share_change = (electronics_growth - gdp_per_capita_growth) * 0.02
        food_share_change = (food_import_impact / self.food_imports_share - gdp_per_capita_growth) * 0.01
        
        self.luxury_goods_share = max(0.1, min(0.4, self.luxury_goods_share + luxury_share_change))
        self.electronics_share = max(0.2, min(0.5, self.electronics_share + electronics_share_change))
        self.food_imports_share = max(0.1, min(0.4, self.food_imports_share + food_share_change))
        
        # Adjust essential goods share to maintain total
        new_total = self.luxury_goods_share + self.electronics_share + self.food_imports_share
        self.essential_goods_share = max(0.3, 1 - new_total)
        
        # Add sector-specific metrics to results
        results['luxury_goods_share'] = self.luxury_goods_share
        results['essential_goods_share'] = self.essential_goods_share
        results['electronics_share'] = self.electronics_share
        results['food_imports_share'] = self.food_imports_share
        results['consumer_preference_imports'] = self.consumer_preference_imports
        results['import_competing_production'] = self.import_competing_production
        results['luxury_impact'] = luxury_impact
        results['electronics_impact'] = electronics_impact
        results['food_import_impact'] = food_import_impact
        results['preference_impact'] = preference_impact
        results['competing_impact'] = competing_impact
        
        return results


class EnergyImportsModel(ImportDependencyModel):
    """
    Model for energy imports (fossil fuels, LNG, etc.)
    """
    
    def __init__(self, config):
        """
        Initialize energy imports model with additional parameters
        
        Args:
            config: Configuration dictionary for energy imports
        """
        super().__init__(
            category_name=config['name'],
            current_volume=config['current_volume'],
            domestic_production_ratio=config['domestic_production_ratio'],
            growth_trajectory=config['growth_trajectory'],
            price_sensitivity=config['price_sensitivity'],
            substitution_elasticity=config['substitution_elasticity'],
            categories=config['categories']
        )
        
        # Energy imports specific attributes
        self.fossil_fuel_dependency = 0.85  # Dependency on fossil fuels
        self.renewable_transition_level = 0.1  # Transition to renewable energy
        self.domestic_gas_depletion = 0.03  # Annual depletion rate of domestic gas reserves
        self.energy_efficiency = 0.4  # Energy efficiency level
        self.strategic_reserve_months = 1.5  # Strategic reserves in months of consumption
    
    def simulate_import_needs(self, year_index, **kwargs):
        """
        Extend the base simulation with energy imports specific factors
        """
        # Extract additional parameters
        economic_growth = kwargs.get('economic_growth', 0.06)
        industrialization_rate = kwargs.get('industrialization_rate', 0.04)
        global_energy_price_change = kwargs.get('global_energy_price_change', 0)
        renewable_investment = kwargs.get('renewable_investment', 0.4)
        energy_policy_strength = kwargs.get('energy_policy_strength', 0.5)
        
        # Get base simulation results
        results = super().simulate_import_needs(year_index, **kwargs)
        
        # Calculate base energy demand growth
        energy_demand_growth = economic_growth * 1.2 + industrialization_rate * 0.5
        
        # Simulate renewable energy transition
        renewable_growth = 0.03 * renewable_investment + 0.01 * energy_policy_strength
        self.renewable_transition_level = min(0.6, self.renewable_transition_level + renewable_growth)
        
        # Calculate impact of renewable transition
        renewable_impact = -0.2 * (self.renewable_transition_level - 0.1)
        
        # Calculate impact of energy efficiency improvements
        efficiency_improvement = 0.02 * energy_policy_strength
        self.energy_efficiency = min(0.8, self.energy_efficiency + efficiency_improvement)
        efficiency_impact = -0.15 * (self.energy_efficiency - 0.4)
        
        # Calculate impact of domestic gas depletion
        if self.domestic_production_ratio > 0.1:
            # Only deplete if there's still domestic production
            self.domestic_gas_depletion = min(0.1, self.domestic_gas_depletion + 0.002)
            depletion_impact = self.domestic_gas_depletion * (self.domestic_production_ratio / 0.2)
        else:
            depletion_impact = 0
        
        # Update fossil fuel dependency
        fossil_reduction = self.renewable_transition_level * 0.1
        self.fossil_fuel_dependency = max(0.4, self.fossil_fuel_dependency - fossil_reduction)
        
        # Calculate price volatility impact
        price_volatility_impact = global_energy_price_change * 2 * self.price_sensitivity
        
        # Calculate strategic reserves adjustment
        if global_energy_price_change < -0.1:  # If prices are falling significantly
            # Increase strategic reserves
            reserve_change = min(0.5, -global_energy_price_change)
            self.strategic_reserve_months += reserve_change
            strategic_impact = reserve_change * 0.1
        elif global_energy_price_change > 0.1:  # If prices are rising significantly
            # Possibility to use strategic reserves
            reserve_use_probability = min(0.7, global_energy_price_change)
            if np.random.random() < reserve_use_probability and self.strategic_reserve_months > 1:
                reserve_change = -min(0.5, self.strategic_reserve_months - 1)
                self.strategic_reserve_months += reserve_change
                strategic_impact = reserve_change * 0.1
            else:
                strategic_impact = 0
        else:
            strategic_impact = 0
        
        # Apply energy imports specific impacts
        total_impact = energy_demand_growth + renewable_impact + efficiency_impact + depletion_impact + price_volatility_impact + strategic_impact
        results['import_volume'] *= (1 + total_impact)
        
        # Add sector-specific metrics to results
        results['fossil_fuel_dependency'] = self.fossil_fuel_dependency
        results['renewable_transition_level'] = self.renewable_transition_level
        results['energy_efficiency'] = self.energy_efficiency
        results['strategic_reserve_months'] = self.strategic_reserve_months
        results['energy_demand_growth'] = energy_demand_growth
        results['renewable_impact'] = renewable_impact
        results['efficiency_impact'] = efficiency_impact
        results['depletion_impact'] = depletion_impact
        results['price_volatility_impact'] = price_volatility_impact
        results['strategic_impact'] = strategic_impact
        
        return results
