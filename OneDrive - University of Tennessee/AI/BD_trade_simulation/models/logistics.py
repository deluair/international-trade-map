"""
Logistics model for Bangladesh trade simulation.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional


class LogisticsModel:
    """
    Model trade logistics infrastructure and processes
    
    This class simulates the evolution of Bangladesh's logistics infrastructure,
    including ports, transport connectivity, and trade facilitation.
    """
    
    def __init__(self, config):
        """
        Initialize logistics model
        
        Args:
            config: Configuration dictionary for logistics parameters
        """
        self.ports_config = config.get('ports', {})
        self.transport_config = config.get('transport', {})
        self.trade_facilitation_config = config.get('trade_facilitation', {})
        
        # Initialize port infrastructure
        self.ports = {}
        for port_name, port_data in self.ports_config.items():
            self.ports[port_name] = PortInfrastructure(port_name, port_data)
        
        # Initialize transport connectivity
        self.transport = TransportConnectivity(self.transport_config)
        
        # Initialize trade facilitation
        self.facilitation = TradeFacilitation(self.trade_facilitation_config)
        
        # Historical data
        self.historical_performance = {}
    
    def simulate_logistics_performance(self, 
                                     year_index: int, 
                                     simulation_year: int,
                                     trade_volume: float,
                                     infrastructure_investment: float,
                                     policy_effectiveness: float,
                                     external_disruptions: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Simulate logistics performance for a given year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            trade_volume: Total trade volume (exports + imports) in million USD
            infrastructure_investment: Level of investment in infrastructure (0-1)
            policy_effectiveness: Effectiveness of logistics policies (0-1)
            external_disruptions: Optional dict of external disruptions (e.g., weather, labor unrest)
            
        Returns:
            Dict with logistics performance simulation results
        """
        # Default external disruptions if none provided
        if external_disruptions is None:
            external_disruptions = {
                'weather_events': 0.1,
                'labor_unrest': 0.1,
                'global_shipping_disruption': 0.1,
            }
        
        # Calculate container volume from trade volume (rough approximation)
        container_volume = trade_volume * 0.01  # Approximate TEUs per million USD of trade
        
        # Simulate port performance
        port_results = {}
        aggregate_port_capacity = 0
        aggregate_port_utilization = 0
        aggregate_port_efficiency = 0
        
        for port_name, port in self.ports.items():
            port_result = port.simulate_year(
                year_index=year_index,
                simulation_year=simulation_year,
                container_volume=container_volume * port.get_market_share(),
                infrastructure_investment=infrastructure_investment,
                policy_effectiveness=policy_effectiveness,
                external_disruptions=external_disruptions
            )
            port_results[port_name] = port_result
            
            # Accumulate for aggregate metrics
            aggregate_port_capacity += port_result['capacity']
            aggregate_port_utilization += port_result['utilized_capacity']
            aggregate_port_efficiency += port_result['efficiency'] * port_result['market_share']
        
        # Simulate transport connectivity
        transport_result = self.transport.simulate_year(
            year_index=year_index,
            simulation_year=simulation_year,
            trade_volume=trade_volume,
            infrastructure_investment=infrastructure_investment,
            policy_effectiveness=policy_effectiveness,
            external_disruptions=external_disruptions
        )
        
        # Simulate trade facilitation
        facilitation_result = self.facilitation.simulate_year(
            year_index=year_index,
            simulation_year=simulation_year,
            trade_volume=trade_volume,
            infrastructure_investment=infrastructure_investment,
            policy_effectiveness=policy_effectiveness
        )
        
        # Calculate overall logistics performance
        # Add safety check for zero capacity before calculating port score
        if aggregate_port_capacity > 0:
            port_performance_score = aggregate_port_efficiency * (1 - min(1, aggregate_port_utilization / aggregate_port_capacity))
        else:
            port_performance_score = 0.0 # Assign a default score if no capacity
            
        transport_performance_score = transport_result['performance_score']
        facilitation_performance_score = facilitation_result['performance_score']
        
        # Weights for overall logistics performance
        weights = {
            'port': 0.4,
            'transport': 0.35,
            'facilitation': 0.25
        }
        
        overall_performance = (
            weights['port'] * port_performance_score +
            weights['transport'] * transport_performance_score +
            weights['facilitation'] * facilitation_performance_score
        )
        
        # Calculate logistics costs as percentage of trade value
        base_logistics_cost = 0.15  # 15% of trade value as baseline
        cost_reduction_factor = (overall_performance - 0.5) * 0.1
        logistics_cost = max(0.05, base_logistics_cost - cost_reduction_factor)
        
        # Calculate time delays in days
        base_time_delay = 10  # 10 days as baseline
        time_reduction_factor = (overall_performance - 0.5) * 5
        time_delay = max(2, base_time_delay - time_reduction_factor)
        
        # Calculate reliability (on-time delivery percentage)
        base_reliability = 0.7  # 70% on-time delivery as baseline
        reliability_improvement_factor = (overall_performance - 0.5) * 0.2
        reliability = min(0.98, base_reliability + reliability_improvement_factor)
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'overall_performance': overall_performance,
            'port_performance': port_performance_score,
            'transport_performance': transport_performance_score,
            'facilitation_performance': facilitation_performance_score,
            'logistics_cost': logistics_cost,
            'time_delay': time_delay,
            'reliability': reliability,
            'port_results': port_results,
            'transport_result': transport_result,
            'facilitation_result': facilitation_result,
            'container_volume': container_volume,
            'aggregate_port_capacity': aggregate_port_capacity,
            'capacity_utilization': aggregate_port_utilization / aggregate_port_capacity if aggregate_port_capacity > 0 else 1,
        }
        
        # Store historical performance
        self.historical_performance[year_index] = results
        
        return results


class PortInfrastructure:
    """
    Model for port infrastructure and operations
    """
    
    def __init__(self, port_name, config):
        """
        Initialize port infrastructure model
        
        Args:
            port_name: Name of the port
            config: Configuration dictionary for the port
        """
        self.port_name = port_name
        self.config = config
        
        # Extract configuration
        self.current_capacity = config.get('current_capacity', 0)
        self.utilization_rate = config.get('utilization_rate', 0.8)
        self.expansion_timeline = config.get('expansion_timeline', {})
        self.efficiency_improvement = config.get('efficiency_improvement', 0.03)
        self.waiting_time = config.get('waiting_time', 3)
        self.start_year = config.get('start_year', 2025)
        
        # For new ports
        self.initial_capacity = config.get('initial_capacity', 0)
        self.efficiency = config.get('efficiency', 0.7)
        
        # Market share and operational status
        self.market_share = 0.0
        self.operational = port_name == 'chittagong'  # Chittagong is operational at start
        
        # If already operational, set initial values
        if self.operational:
            self.capacity = self.current_capacity
        else:
            self.capacity = 0
        
        # Historical data
        self.historical_performance = {}
    
    def get_market_share(self):
        """
        Get current market share of this port
        
        Returns:
            float: Current market share (0-1)
        """
        return self.market_share
    
    def simulate_year(self, 
                     year_index: int, 
                     simulation_year: int,
                     container_volume: float,
                     infrastructure_investment: float,
                     policy_effectiveness: float,
                     external_disruptions: Dict[str, float]) -> Dict[str, Any]:
        """
        Simulate port performance for one year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            container_volume: Expected container volume for this port in TEUs
            infrastructure_investment: Level of investment in infrastructure (0-1)
            policy_effectiveness: Effectiveness of port policies (0-1)
            external_disruptions: Dict of external disruptions
            
        Returns:
            Dict with port performance simulation results
        """
        # Check if port becomes operational this year
        if not self.operational and simulation_year >= self.start_year:
            self.operational = True
            self.capacity = self.initial_capacity
            self.efficiency = self.config.get('efficiency', 0.7)
        
        # No simulation needed if port is not operational
        if not self.operational:
            # Return empty results for non-operational port
            results = {
                'year_index': year_index,
                'simulation_year': simulation_year,
                'operational': False,
                'capacity': 0,
                'utilized_capacity': 0,
                'efficiency': 0,
                'waiting_time': 0,
                'market_share': 0,
                'congestion_level': 0,
            }
            self.historical_performance[year_index] = results
            return results
        
        # Check for capacity expansions
        if simulation_year in self.expansion_timeline:
            self.capacity = self.expansion_timeline[simulation_year]
        
        # Calculate efficiency improvement
        base_improvement = self.efficiency_improvement * infrastructure_investment * policy_effectiveness
        efficiency_improvement = base_improvement * (1 - min(0.5, self.efficiency))  # Diminishing returns
        self.efficiency = min(0.95, self.efficiency + efficiency_improvement)
        
        # Calculate utilized capacity
        utilized_capacity = min(container_volume, self.capacity)
        utilization_rate = utilized_capacity / self.capacity if self.capacity > 0 else 1
        
        # Calculate congestion effect
        congestion_threshold = 0.8  # Congestion starts at 80% utilization
        if utilization_rate > congestion_threshold:
            congestion_level = (utilization_rate - congestion_threshold) / (1 - congestion_threshold)
        else:
            congestion_level = 0
        
        # Calculate waiting time based on congestion and external disruptions
        disruption_factor = 0.5 * external_disruptions.get('weather_events', 0) + 0.3 * external_disruptions.get('labor_unrest', 0) + 0.2 * external_disruptions.get('global_shipping_disruption', 0)
        base_waiting_time = self.waiting_time * (1 + congestion_level * 2)  # Congestion doubles waiting time at most
        adjusted_waiting_time = base_waiting_time * (1 + disruption_factor)
        
        # Reduce waiting time based on efficiency improvements
        waiting_time = adjusted_waiting_time * (1 - self.efficiency * 0.3)
        
        # Calculate market share based on capacity and efficiency
        # This will be normalized across all ports in the main LogisticsModel
        raw_market_share = self.capacity * self.efficiency * (1 - congestion_level * 0.5)
        self.market_share = raw_market_share  # Will be normalized later
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'operational': self.operational,
            'capacity': self.capacity,
            'utilized_capacity': utilized_capacity,
            'utilization_rate': utilization_rate,
            'efficiency': self.efficiency,
            'waiting_time': waiting_time,
            'congestion_level': congestion_level,
            'market_share': raw_market_share,  # Raw share, will be normalized
            'disruption_factor': disruption_factor,
        }
        
        # Store historical performance
        self.historical_performance[year_index] = results
        
        return results


class TransportConnectivity:
    """
    Model for transport connectivity and network
    """
    
    def __init__(self, config):
        """
        Initialize transport connectivity model
        
        Args:
            config: Configuration dictionary for transport connectivity
        """
        self.config = config
        
        # Road network
        self.road_network = {
            'quality': config.get('road_network', {}).get('current_quality', 0.6),
            'improvement_rate': config.get('road_network', {}).get('improvement_rate', 0.02),
            'capacity_increase_rate': config.get('road_network', {}).get('capacity_increase_rate', 0.04),
            'capacity': 1.0,  # Normalized capacity
        }
        
        # Rail freight
        self.rail_freight = {
            'current_share': config.get('rail_freight', {}).get('current_share', 0.15),
            'target_share': config.get('rail_freight', {}).get('target_share', 0.30),
            'annual_increase': config.get('rail_freight', {}).get('annual_increase', 0.01),
            'quality': 0.5,  # Initial quality
        }
        
        # Inland waterways
        self.inland_waterways = {
            'current_share': config.get('inland_waterways', {}).get('current_share', 0.25),
            'target_share': config.get('inland_waterways', {}).get('target_share', 0.35),
            'annual_increase': config.get('inland_waterways', {}).get('annual_increase', 0.005),
            'quality': 0.6,  # Initial quality
        }
        
        # Modal shares
        self.modal_shares = {
            'road': 1 - self.rail_freight['current_share'] - self.inland_waterways['current_share'],
            'rail': self.rail_freight['current_share'],
            'waterway': self.inland_waterways['current_share'],
        }
        
        # Historical data
        self.historical_performance = {}
    
    def simulate_year(self, 
                     year_index: int, 
                     simulation_year: int,
                     trade_volume: float,
                     infrastructure_investment: float,
                     policy_effectiveness: float,
                     external_disruptions: Dict[str, float]) -> Dict[str, Any]:
        """
        Simulate transport connectivity for one year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            trade_volume: Total trade volume in million USD
            infrastructure_investment: Level of investment in infrastructure (0-1)
            policy_effectiveness: Effectiveness of transport policies (0-1)
            external_disruptions: Dict of external disruptions
            
        Returns:
            Dict with transport performance simulation results
        """
        # Road network improvement
        quality_improvement = self.road_network['improvement_rate'] * infrastructure_investment * policy_effectiveness
        capacity_increase = self.road_network['capacity_increase_rate'] * infrastructure_investment
        
        self.road_network['quality'] = min(0.95, self.road_network['quality'] + quality_improvement)
        self.road_network['capacity'] = self.road_network['capacity'] * (1 + capacity_increase)
        
        # Rail freight development
        rail_share_increase = min(
            self.rail_freight['target_share'] - self.rail_freight['current_share'],
            self.rail_freight['annual_increase'] * infrastructure_investment * policy_effectiveness
        )
        self.rail_freight['current_share'] = self.rail_freight['current_share'] + rail_share_increase
        
        # Rail quality improvement
        rail_quality_improvement = 0.03 * infrastructure_investment * policy_effectiveness
        self.rail_freight['quality'] = min(0.9, self.rail_freight['quality'] + rail_quality_improvement)
        
        # Inland waterways development
        waterway_share_increase = min(
            self.inland_waterways['target_share'] - self.inland_waterways['current_share'],
            self.inland_waterways['annual_increase'] * infrastructure_investment * policy_effectiveness
        )
        self.inland_waterways['current_share'] = self.inland_waterways['current_share'] + waterway_share_increase
        
        # Waterway quality improvement
        waterway_quality_improvement = 0.02 * infrastructure_investment * policy_effectiveness
        self.inland_waterways['quality'] = min(0.85, self.inland_waterways['quality'] + waterway_quality_improvement)
        
        # Recalculate modal shares
        self.modal_shares = {
            'road': max(0.3, 1 - self.rail_freight['current_share'] - self.inland_waterways['current_share']),
            'rail': self.rail_freight['current_share'],
            'waterway': self.inland_waterways['current_share'],
        }
        
        # Calculate disruption impact
        road_disruption = 0.7 * external_disruptions.get('weather_events', 0) + 0.3 * external_disruptions.get('labor_unrest', 0)
        rail_disruption = 0.5 * external_disruptions.get('weather_events', 0) + 0.5 * external_disruptions.get('labor_unrest', 0)
        waterway_disruption = 0.9 * external_disruptions.get('weather_events', 0) + 0.1 * external_disruptions.get('labor_unrest', 0)
        
        # Calculate modal performance
        road_performance = self.road_network['quality'] * (1 - road_disruption) * min(1, self.road_network['capacity'] / self.modal_shares['road'])
        rail_performance = self.rail_freight['quality'] * (1 - rail_disruption)
        waterway_performance = self.inland_waterways['quality'] * (1 - waterway_disruption)
        
        # Calculate overall transport performance
        performance_score = (
            self.modal_shares['road'] * road_performance +
            self.modal_shares['rail'] * rail_performance +
            self.modal_shares['waterway'] * waterway_performance
        )
        
        # Calculate transport costs
        modal_costs = {
            'road': 1.0,  # Normalized cost
            'rail': 0.7,  # 30% cheaper than road
            'waterway': 0.6,  # 40% cheaper than road
        }
        
        weighted_transport_cost = (
            self.modal_shares['road'] * modal_costs['road'] / road_performance +
            self.modal_shares['rail'] * modal_costs['rail'] / rail_performance +
            self.modal_shares['waterway'] * modal_costs['waterway'] / waterway_performance
        )
        
        # Normalize to a 0-1 scale
        transport_cost = max(0.4, min(1.0, weighted_transport_cost / 1.0))
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'modal_shares': self.modal_shares,
            'road_quality': self.road_network['quality'],
            'road_capacity': self.road_network['capacity'],
            'rail_share': self.rail_freight['current_share'],
            'rail_quality': self.rail_freight['quality'],
            'waterway_share': self.inland_waterways['current_share'],
            'waterway_quality': self.inland_waterways['quality'],
            'road_performance': road_performance,
            'rail_performance': rail_performance,
            'waterway_performance': waterway_performance,
            'performance_score': performance_score,
            'transport_cost': transport_cost,
            'disruption_impact': {
                'road': road_disruption,
                'rail': rail_disruption,
                'waterway': waterway_disruption,
            },
        }
        
        # Store historical performance
        self.historical_performance[year_index] = results
        
        return results


class TradeFacilitation:
    """
    Model for trade facilitation improvements
    """
    
    def __init__(self, config):
        """
        Initialize trade facilitation model
        
        Args:
            config: Configuration dictionary for trade facilitation
        """
        self.config = config
        
        # Customs modernization
        self.customs = {
            'current_level': config.get('customs_modernization', {}).get('current_level', 0.5),
            'target_level': config.get('customs_modernization', {}).get('target_level', 0.9),
            'annual_improvement': config.get('customs_modernization', {}).get('annual_improvement', 0.02),
        }
        
        # Single window implementation
        self.single_window = {
            'implementation_year': config.get('single_window', {}).get('implementation_year', 2026),
            'adoption_rate': config.get('single_window', {}).get('adoption_rate', 0.1),
            'efficiency_gain': config.get('single_window', {}).get('efficiency_gain', 0.3),
            'current_adoption': 0.0,
        }
        
        # Paperless trade
        self.paperless_trade = {
            'current_level': config.get('paperless_trade', {}).get('current_level', 0.3),
            'target_level': config.get('paperless_trade', {}).get('target_level', 0.8),
            'annual_improvement': config.get('paperless_trade', {}).get('annual_improvement', 0.03),
        }
        
        # Documentary compliance metrics
        self.documentary_compliance = {
            'time_days': 3.0,  # Initial time in days
            'cost_usd': 200.0,  # Initial cost in USD
        }
        
        # Border compliance metrics
        self.border_compliance = {
            'time_days': 5.0,  # Initial time in days
            'cost_usd': 400.0,  # Initial cost in USD
        }
        
        # Corruption/informal payment incidence
        self.corruption_incidence = 0.4  # Initial corruption level (0-1)
        
        # Historical data
        self.historical_performance = {}
    
    def simulate_year(self, 
                     year_index: int, 
                     simulation_year: int,
                     trade_volume: float,
                     infrastructure_investment: float,
                     policy_effectiveness: float) -> Dict[str, Any]:
        """
        Simulate trade facilitation for one year
        
        Args:
            year_index: Year index from simulation start
            simulation_year: Actual calendar year
            trade_volume: Total trade volume in million USD
            infrastructure_investment: Level of investment in infrastructure (0-1)
            policy_effectiveness: Effectiveness of facilitation policies (0-1)
            
        Returns:
            Dict with trade facilitation performance simulation results
        """
        # Customs modernization progress
        customs_improvement = min(
            self.customs['target_level'] - self.customs['current_level'],
            self.customs['annual_improvement'] * policy_effectiveness
        )
        self.customs['current_level'] = self.customs['current_level'] + customs_improvement
        
        # Single window implementation
        if simulation_year >= self.single_window['implementation_year']:
            adoption_increase = min(
                1.0 - self.single_window['current_adoption'],
                self.single_window['adoption_rate'] * policy_effectiveness
            )
            self.single_window['current_adoption'] = self.single_window['current_adoption'] + adoption_increase
        
        # Paperless trade progress
        paperless_improvement = min(
            self.paperless_trade['target_level'] - self.paperless_trade['current_level'],
            self.paperless_trade['annual_improvement'] * policy_effectiveness
        )
        self.paperless_trade['current_level'] = self.paperless_trade['current_level'] + paperless_improvement
        
        # Calculate documentary compliance improvements
        documentary_time_reduction = (
            0.4 * customs_improvement +
            0.3 * self.single_window['current_adoption'] * self.single_window['efficiency_gain'] +
            0.3 * paperless_improvement
        ) * 0.5  # 50% of improvements translate to time reduction
        
        documentary_cost_reduction = (
            0.3 * customs_improvement +
            0.4 * self.single_window['current_adoption'] * self.single_window['efficiency_gain'] +
            0.3 * paperless_improvement
        ) * 0.3  # 30% of improvements translate to cost reduction
        
        self.documentary_compliance['time_days'] = max(1.0, self.documentary_compliance['time_days'] * (1 - documentary_time_reduction))
        self.documentary_compliance['cost_usd'] = max(50.0, self.documentary_compliance['cost_usd'] * (1 - documentary_cost_reduction))
        
        # Calculate border compliance improvements
        border_time_reduction = (
            0.5 * customs_improvement +
            0.2 * self.single_window['current_adoption'] * self.single_window['efficiency_gain'] +
            0.3 * paperless_improvement
        ) * 0.4  # 40% of improvements translate to time reduction
        
        border_cost_reduction = (
            0.4 * customs_improvement +
            0.3 * self.single_window['current_adoption'] * self.single_window['efficiency_gain'] +
            0.3 * paperless_improvement
        ) * 0.25  # 25% of improvements translate to cost reduction
        
        self.border_compliance['time_days'] = max(2.0, self.border_compliance['time_days'] * (1 - border_time_reduction))
        self.border_compliance['cost_usd'] = max(100.0, self.border_compliance['cost_usd'] * (1 - border_cost_reduction))
        
        # Calculate corruption/informal payment reduction
        corruption_reduction = (
            0.4 * customs_improvement +
            0.3 * self.single_window['current_adoption'] * self.single_window['efficiency_gain'] +
            0.3 * paperless_improvement +
            0.2 * policy_effectiveness
        ) * 0.2  # 20% of improvements translate to corruption reduction
        
        self.corruption_incidence = max(0.05, self.corruption_incidence * (1 - corruption_reduction))
        
        # Calculate overall performance score
        # Normalize each component to 0-1 scale
        customs_score = self.customs['current_level']
        single_window_score = self.single_window['current_adoption'] * self.single_window['efficiency_gain']
        paperless_score = self.paperless_trade['current_level']
        
        # Documentary compliance score (inversely related to time and cost)
        doc_time_score = 1 - min(1, self.documentary_compliance['time_days'] / 5)  # 5 days as baseline
        doc_cost_score = 1 - min(1, self.documentary_compliance['cost_usd'] / 300)  # $300 as baseline
        
        # Border compliance score (inversely related to time and cost)
        border_time_score = 1 - min(1, self.border_compliance['time_days'] / 7)  # 7 days as baseline
        border_cost_score = 1 - min(1, self.border_compliance['cost_usd'] / 500)  # $500 as baseline
        
        # Corruption score (inversely related to incidence)
        corruption_score = 1 - self.corruption_incidence
        
        # Weights for overall score
        weights = {
            'customs': 0.2,
            'single_window': 0.15,
            'paperless': 0.15,
            'doc_time': 0.1,
            'doc_cost': 0.1,
            'border_time': 0.1,
            'border_cost': 0.1,
            'corruption': 0.1,
        }
        
        performance_score = (
            weights['customs'] * customs_score +
            weights['single_window'] * single_window_score +
            weights['paperless'] * paperless_score +
            weights['doc_time'] * doc_time_score +
            weights['doc_cost'] * doc_cost_score +
            weights['border_time'] * border_time_score +
            weights['border_cost'] * border_cost_score +
            weights['corruption'] * corruption_score
        )
        
        # Compile results
        results = {
            'year_index': year_index,
            'simulation_year': simulation_year,
            'customs_level': self.customs['current_level'],
            'single_window_adoption': self.single_window['current_adoption'],
            'paperless_trade_level': self.paperless_trade['current_level'],
            'documentary_compliance': {
                'time_days': self.documentary_compliance['time_days'],
                'cost_usd': self.documentary_compliance['cost_usd'],
            },
            'border_compliance': {
                'time_days': self.border_compliance['time_days'],
                'cost_usd': self.border_compliance['cost_usd'],
            },
            'corruption_incidence': self.corruption_incidence,
            'performance_score': performance_score,
        }
        
        # Store historical performance
        self.historical_performance[year_index] = results
        
        return results
