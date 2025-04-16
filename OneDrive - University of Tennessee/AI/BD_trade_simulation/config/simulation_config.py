"""
Configuration settings for the Bangladesh Trade Simulation.
"""

# Simulation time parameters
SIMULATION_CONFIG = {
    'start_year': 2025,
    'end_year': 2050,
    'time_step': 1,  # in years
}

# Export sector configurations
EXPORT_SECTORS = {
    'rmg': {  # Ready-Made Garments
        'name': 'Ready-Made Garments',
        'current_volume': 35000,  # in million USD
        'growth_trajectory': 0.08,  # annual growth rate
        'global_market_share': 0.06,
        'value_chain_position': 'low_to_mid',
        'competitiveness_factors': {
            'labor_cost': 0.8,
            'productivity': 0.6,
            'compliance': 0.7,
            'lead_time': 0.6,
            'quality': 0.7
        },
        'tariff_exposure': 0.15,
        'subsectors': [
            'knitwear', 
            'woven', 
            'technical_textiles'
        ],
    },
    'pharma': {  # Pharmaceuticals
        'name': 'Pharmaceuticals',
        'current_volume': 1500,  # in million USD
        'growth_trajectory': 0.12,
        'global_market_share': 0.01,
        'value_chain_position': 'mid',
        'competitiveness_factors': {
            'r_and_d': 0.6,
            'quality': 0.8,
            'certification': 0.7,
            'production_cost': 0.7,
            'brand_recognition': 0.5
        },
        'tariff_exposure': 0.08,
        'subsectors': [
            'generic_drugs',
            'active_ingredients',
            'vaccines'
        ],
    },
    'it_services': {  # IT Services
        'name': 'IT Services',
        'current_volume': 1200,  # in million USD
        'growth_trajectory': 0.15,
        'global_market_share': 0.005,
        'value_chain_position': 'mid',
        'competitiveness_factors': {
            'skill_level': 0.7,
            'english_proficiency': 0.8,
            'infrastructure': 0.5,
            'cost': 0.9,
            'delivery_quality': 0.7
        },
        'tariff_exposure': 0.02,
        'subsectors': [
            'software_development',
            'bpo',
            'digital_services',
            'freelancing'
        ],
    },
    'leather': {  # Leather and Footwear
        'name': 'Leather and Footwear',
        'current_volume': 1000,  # in million USD
        'growth_trajectory': 0.10,
        'global_market_share': 0.015,
        'value_chain_position': 'low_to_mid',
        'competitiveness_factors': {
            'raw_material_quality': 0.7,
            'processing_technology': 0.6,
            'design_capability': 0.5,
            'environmental_compliance': 0.5,
            'cost': 0.8
        },
        'tariff_exposure': 0.10,
        'subsectors': [
            'finished_leather',
            'footwear',
            'leather_goods'
        ],
    },
    'jute': {  # Jute and Jute Products
        'name': 'Jute and Jute Products',
        'current_volume': 800,  # in million USD
        'growth_trajectory': 0.05,
        'global_market_share': 0.40,
        'value_chain_position': 'mid',
        'competitiveness_factors': {
            'raw_material_quality': 0.9,
            'processing_technology': 0.6,
            'product_diversification': 0.5,
            'eco_friendly_appeal': 0.9,
            'cost': 0.7
        },
        'tariff_exposure': 0.05,
        'subsectors': [
            'raw_jute',
            'jute_textiles',
            'diversified_jute_products'
        ],
    },
    'agro_products': {  # Agricultural Products
        'name': 'Agricultural Products',
        'current_volume': 700,  # in million USD
        'growth_trajectory': 0.06,
        'global_market_share': 0.01,
        'value_chain_position': 'low',
        'competitiveness_factors': {
            'quality': 0.7,
            'certification': 0.5,
            'yield': 0.6,
            'processing_capability': 0.5,
            'cost': 0.8
        },
        'tariff_exposure': 0.12,
        'subsectors': [
            'frozen_food',
            'processed_food',
            'tea',
            'vegetables',
            'fruits'
        ],
    }
}

# Import dependency configuration
IMPORT_DEPENDENCIES = {
    'industrial_inputs': {
        'name': 'Industrial Inputs',
        'current_volume': 25000,  # in million USD
        'domestic_production_ratio': 0.3,
        'growth_trajectory': 0.08,
        'price_sensitivity': 0.7,
        'substitution_elasticity': 0.4,
        'categories': [
            'cotton',
            'yarn',
            'fabric',
            'machinery',
            'chemicals',
            'metals',
            'plastics'
        ]
    },
    'consumer_goods': {
        'name': 'Consumer Goods',
        'current_volume': 15000,  # in million USD
        'domestic_production_ratio': 0.5,
        'growth_trajectory': 0.10,
        'price_sensitivity': 0.8,
        'substitution_elasticity': 0.6,
        'categories': [
            'food',
            'electronics',
            'vehicles',
            'luxury_goods',
            'household_items'
        ]
    },
    'energy': {
        'name': 'Energy',
        'current_volume': 5000,  # in million USD
        'domestic_production_ratio': 0.2,
        'growth_trajectory': 0.07,
        'price_sensitivity': 0.9,
        'substitution_elasticity': 0.3,
        'categories': [
            'crude_oil',
            'lng',
            'coal',
            'petroleum_products'
        ]
    }
}

# Trade policy configuration
TRADE_POLICY = {
    'ldc_graduation': {
        'year': 2026,
        'eu_tariff_increase': 0.09,
        'us_tariff_increase': 0.15,
        'canada_tariff_increase': 0.12,
        'japan_tariff_increase': 0.10,
        'australia_tariff_increase': 0.08,
    },
    'fta_implementation': {
        'safta': {
            'implementation_level': 0.6,
            'tariff_reduction': 0.7,
            'sensitive_list_coverage': 0.3,
        },
        'bimstec': {
            'implementation_level': 0.3,
            'tariff_reduction': 0.5,
            'sensitive_list_coverage': 0.4,
        },
        'proposed_ftas': {
            'japan': {'year': 2029, 'probability': 0.6},
            'malaysia': {'year': 2027, 'probability': 0.7},
            'indonesia': {'year': 2030, 'probability': 0.5},
            'thailand': {'year': 2028, 'probability': 0.6},
        },
        'rcep_accession': {'year': 2032, 'probability': 0.4},
    },
    'domestic_policy': {
        'import_tariff_rationalization': 0.05,  # annual reduction rate
        'export_incentives': {
            'cash_incentive_level': 0.05,  # percentage of export value
            'covered_sectors': ['rmg', 'pharma', 'it_services', 'agro_products', 'leather'],
        },
        'economic_zones': {
            'number_planned': 100,
            'annual_implementation_rate': 0.06,
            'effectiveness': 0.7,
        }
    }
}

# Logistics and facilitation configuration
LOGISTICS = {
    'ports': {
        'chittagong': {
            'current_capacity': 3000000,  # TEUs per year
            'utilization_rate': 0.95,
            'expansion_timeline': {
                2028: 4000000,
                2035: 5000000,
                2042: 6500000,
            },
            'efficiency_improvement': 0.03,  # annual improvement rate
            'waiting_time': 3,  # days
        },
        'matarbari': {
            'start_year': 2027,
            'initial_capacity': 1500000,  # TEUs per year
            'expansion_timeline': {
                2032: 2500000,
                2040: 4000000,
            },
            'efficiency': 0.8,
            'waiting_time': 1,  # days
        },
        'payra': {
            'start_year': 2026,
            'initial_capacity': 500000,  # TEUs per year
            'expansion_timeline': {
                2030: 1000000,
                2038: 1800000,
            },
            'efficiency': 0.7,
            'waiting_time': 2,  # days
        }
    },
    'transport': {
        'road_network': {
            'current_quality': 0.6,
            'improvement_rate': 0.02,
            'capacity_increase_rate': 0.04,
        },
        'rail_freight': {
            'current_share': 0.15,
            'target_share': 0.30,
            'annual_increase': 0.01,
        },
        'inland_waterways': {
            'current_share': 0.25,
            'target_share': 0.35,
            'annual_increase': 0.005,
        }
    },
    'trade_facilitation': {
        'customs_modernization': {
            'current_level': 0.5,
            'target_level': 0.9,
            'annual_improvement': 0.02,
        },
        'single_window': {
            'implementation_year': 2026,
            'adoption_rate': 0.1,  # annual adoption rate
            'efficiency_gain': 0.3,  # time reduction
        },
        'paperless_trade': {
            'current_level': 0.3,
            'target_level': 0.8,
            'annual_improvement': 0.03,
        }
    }
}

# Exchange rate dynamics configuration
EXCHANGE_RATE = {
    'initial_rate': 110.0,  # BDT to USD
    'annual_depreciation': 0.03,
    'volatility': 0.05,
    'intervention_threshold': 0.08,  # central bank intervenes at this depreciation rate
    'intervention_strength': 0.6,  # effectiveness of central bank intervention
    'remittance_sensitivity': 0.4,  # remittance response to exchange rate changes
    'export_elasticity': 0.7,  # export response to exchange rate changes
    'import_elasticity': 0.6,  # import response to exchange rate changes
}

# Global market conditions configuration
GLOBAL_MARKETS = {
    'gdp_growth': {
        'usa': 0.025,
        'eu': 0.015,
        'china': 0.05,
        'india': 0.06,
        'japan': 0.01,
        'asean': 0.04,
    },
    'market_demand_growth': {
        'rmg': 0.03,
        'pharma': 0.06,
        'it_services': 0.08,
        'leather': 0.04,
        'jute': 0.02,
        'agro_products': 0.03,
    },
    'competitor_growth': {
        'vietnam': {
            'rmg': 0.07,
            'electronics': 0.10,
            'footwear': 0.06,
        },
        'india': {
            'it_services': 0.12,
            'pharma': 0.09,
            'textiles': 0.05,
        },
        'cambodia': {
            'rmg': 0.09,
        },
        'ethiopia': {
            'textiles': 0.12,
            'leather': 0.10,
        }
    },
    'supply_chain_reconfiguration': {
        'china_plus_one': 0.7,  # probability of firms diversifying from China
        'nearshoring_trend': 0.5,  # strength of nearshoring trend
        'resilience_premium': 0.2,  # additional cost firms willing to pay for resilience
    }
}

# Geopolitical factors configuration
GEOPOLITICS = {
    'regional_integration': {
        'bbin': {
            'implementation_level': 0.3,
            'annual_improvement': 0.03,
        },
        'bay_of_bengal': {
            'cooperation_level': 0.4,
            'annual_improvement': 0.02,
        },
        'saarc': {
            'revival_probability': 0.3,
        }
    },
    'global_tensions': {
        'us_china': {
            'initial_level': 0.7,  # high tension
            'annual_change': -0.01,  # slight reduction over time
        },
        'india_china': {
            'initial_level': 0.6,
            'annual_change': -0.01,
        }
    },
    'trade_war_probability': {
        'initial': 0.3,
        'annual_change': -0.01,
    },
    'belt_and_road_initiative': {
        'bangladesh_participation': 0.7,
        'project_implementation_rate': 0.1,
    }
}

# Compliance and standards configuration
COMPLIANCE = {
    'labor_standards': {
        'minimum_wage_growth': 0.08,  # annual increase
        'compliance_cost': 0.03,  # as percentage of production cost
        'buyer_requirements_increase': 0.05,  # annual increase in stringency
    },
    'environmental_standards': {
        'carbon_border_tax': {
            'implementation_year': 2027,
            'initial_level': 0.02,  # as percentage of export value
            'annual_increase': 0.005,
        },
        'green_certification_premium': 0.05,  # price premium for green certification
        'certification_adoption_rate': 0.1,  # annual adoption rate
    },
    'product_standards': {
        'technical_barriers_growth': 0.06,  # annual increase
        'testing_capacity_improvement': 0.08,  # annual improvement
        'compliance_capability_improvement': 0.07,  # annual improvement
    }
}

# Structural transformation configuration
STRUCTURAL_TRANSFORMATION = {
    'export_diversification': {
        'current_concentration_index': 0.75,  # high concentration (RMG)
        'target_concentration_index': 0.5,
        'annual_improvement': 0.01,
    },
    'value_chain_positioning': {
        'current_position': 0.3,  # low in value chain
        'target_position': 0.6,
        'annual_improvement': 0.01,
    },
    'industrial_policy': {
        'effectiveness': 0.5,
        'target_sectors': ['pharma', 'it_services', 'leather', 'electronics', 'light_engineering'],
        'policy_coordination_level': 0.6,
    }
}

# Digital trade configuration
DIGITAL_TRADE = {
    'e_commerce': {
        'current_share': 0.05,  # as percentage of total trade
        'growth_rate': 0.15,  # annual growth
        'cross_border_barriers': 0.7,  # high barriers
        'barrier_reduction_rate': 0.05,  # annual reduction
    },
    'digital_services': {
        'current_volume': 1000,  # million USD
        'growth_rate': 0.2,  # annual growth
        'skill_development_rate': 0.1,  # annual improvement
    },
    'digital_policy': {
        'regulatory_quality': 0.4,
        'improvement_rate': 0.05,  # annual improvement
    }
}

# Services trade configuration
SERVICES_TRADE = {
    'labor_services': {
        'current_volume': 18000,  # million USD (remittances)
        'growth_rate': 0.06,  # annual growth
        'skill_composition_improvement': 0.03,  # annual improvement towards skilled workers
    },
    'tourism': {
        'current_volume': 500,  # million USD
        'growth_rate': 0.12,  # annual growth
        'infrastructure_improvement': 0.08,  # annual improvement
    },
    'business_services': {
        'current_volume': 800,  # million USD
        'growth_rate': 0.15,  # annual growth
        'quality_improvement': 0.07,  # annual improvement
    }
}

# Investment configuration
INVESTMENT = {
    'fdi': {
        'current_volume': 2500,  # million USD
        'growth_rate': 0.10,  # annual growth
        'sector_distribution': {
            'rmg': 0.3,
            'energy': 0.2,
            'telecom': 0.15,
            'infrastructure': 0.1,
            'banking': 0.05,
            'other': 0.2,
        }
    },
    'domestic_investment': {
        'current_volume': 15000,  # million USD
        'growth_rate': 0.08,  # annual growth
        'export_oriented_share': 0.4,
    },
    'special_economic_zones': {
        'planned': 100,
        'current_operational': 15,
        'annual_new_operational': 5,
        'investment_per_zone': 300,  # million USD
        'export_percentage': 0.7,
    }
}

# Simulation scenario configurations
SCENARIOS = {
    'baseline': {
        'name': 'Baseline Scenario',
        'description': 'Current trends continue with gradual improvements',
        'modifiers': {}  # No modifications to default parameters
    },
    'accelerated_growth': {
        'name': 'Accelerated Growth',
        'description': 'Rapid economic development with strong export growth',
        'modifiers': {
            'export_growth_multiplier': 1.3,
            'fdi_growth_multiplier': 1.5,
            'productivity_improvement_multiplier': 1.4,
            'infrastructure_development_multiplier': 1.5,
            'skill_development_multiplier': 1.3,
        }
    },
    'global_slowdown': {
        'name': 'Global Economic Slowdown',
        'description': 'Reduced global demand affecting Bangladesh exports',
        'modifiers': {
            'global_demand_multiplier': 0.7,
            'export_growth_multiplier': 0.6,
            'fdi_growth_multiplier': 0.5,
            'remittance_growth_multiplier': 0.8,
        }
    },
    'digital_transformation': {
        'name': 'Digital Transformation',
        'description': 'Accelerated digital adoption in trade and economy',
        'modifiers': {
            'digital_trade_multiplier': 2.0,
            'e_commerce_growth_multiplier': 2.5,
            'service_exports_multiplier': 1.8,
            'trade_facilitation_multiplier': 1.5,
        }
    },
    'sustainability_focus': {
        'name': 'Sustainability Focus',
        'description': 'Stronger environmental regulations and green growth',
        'modifiers': {
            'environmental_compliance_cost_multiplier': 1.7,
            'green_certification_adoption_multiplier': 2.0,
            'carbon_border_tax_multiplier': 1.5,
            'clean_energy_transition_multiplier': 1.8,
        }
    },
    'geopolitical_tensions': {
        'name': 'Heightened Geopolitical Tensions',
        'description': 'Increased trade barriers and regional instability',
        'modifiers': {
            'trade_barrier_multiplier': 1.8,
            'regional_cooperation_multiplier': 0.6,
            'supply_chain_disruption_multiplier': 1.7,
            'fdi_growth_multiplier': 0.7,
        }
    }
}
