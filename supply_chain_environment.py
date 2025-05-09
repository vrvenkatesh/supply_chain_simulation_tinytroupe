"""
Supply Chain Resilience Simulation - Environment

This simulation models a complex supply chain network across multiple regions, incorporating:
- Market dynamics and economic indicators
- Regional supplier performance and disruptions
- Transportation and inventory management
- Risk assessment and mitigation strategies

The metrics and calculations are based on real-world supply chain management principles
and academic research in supply chain resilience.
"""

from tinytroupe.environment.tiny_world import TinyWorld
from typing import Dict, Any, List, Tuple
import numpy as np
from supply_chain_config import DEFAULT_CONFIG

class SupplyChainWorld(TinyWorld):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="Supply Chain World")
        self.config = config or DEFAULT_CONFIG
        self.current_time = 0
        self.disruption_events = []
        self.regions = self.config['regions']
        
        # Market dynamics
        # These variables model real-world market conditions and their volatility
        self.market_conditions = {
            'demand_volatility': 0.2,  # Based on typical consumer goods demand variation (20%)
            'price_trends': {},        # Region-specific price evolution
            'competitor_actions': [],   # Strategic moves by market competitors
            'economic_indicators': {    # Key economic factors affecting supply chain
                'gdp_growth': {},      # Annual GDP growth rate by region
                'inflation_rate': {},   # Annual inflation rate by region
                'exchange_rates': {}    # Currency exchange rate fluctuations
            }
        }
        
        # Initialize state
        self.state = {
            'time': self.current_time,
            'regions': self.regions,
            'disruptions': [],
            'current_inventory': self.config['initial_inventory'],
            'target_inventory': self.config['target_inventory'],
            'holding_cost': self.config['base_holding_cost'],
            'demand_volatility': self.market_conditions['demand_volatility'],
            'metrics': {}
        }
        
        # Enhanced metrics tracking
        # Each metric is carefully chosen to represent key supply chain performance indicators
        self.metrics = {
            'resilience_score': [],    # Measures overall ability to withstand and recover from disruptions (0-1)
            'cost_impact': [],         # Tracks financial impact of disruptions and mitigation strategies ($)
            'service_level': [],       # Measures ability to meet customer demand (typically targeting 95-99%)
            'roi': [],                 # Return on investment for resilience strategies (%)
            'recovery_time': [],       # Time to return to normal operations after disruptions (weeks)
            'risk_exposure': [],       # Aggregate measure of current risk levels (0-1)
            'supplier_performance': {}, # Region-specific supplier reliability and quality metrics (0-1)
            'regional_performance': {}, # Overall regional operational effectiveness (0-1)
            'transportation_efficiency': [], # Logistics network performance (0-1)
            'inventory_health': []     # Balance between stockouts and holding costs (0-1)
        }
        
        # Initialize regional performance tracking
        for region in self.regions:
            self.metrics['supplier_performance'][region] = []
            self.metrics['regional_performance'][region] = []
        
    def step(self, action: Dict[str, Any] = None) -> Tuple[Dict[str, Any], float, bool]:
        """Advance simulation time and update world state"""
        self.current_time += 1
        
        # Update state with current time
        self.state['time'] = self.current_time
        
        # Update market and economic conditions
        self._update_market_dynamics()
        self._update_economic_indicators()
        self._generate_disruptions()
        
        # Update disruptions in state
        self.state['disruptions'] = [d for d in self.disruption_events if d['time'] == self.current_time]
        
        # Calculate metrics in correct order to avoid circular dependencies
        inventory_health = self._calculate_inventory_health(self.state)
        self.state['inventory_health'] = inventory_health
        self.metrics['inventory_health'].append(inventory_health)
        
        service_level = self._calculate_service_level(self.state)
        self.state['service_level'] = service_level
        self.metrics['service_level'].append(service_level)
        
        # Update all other metrics
        self._update_metrics(self.state)
        
        # Calculate reward and check if simulation is done
        reward = self._calculate_reward(self.state)
        done = self._is_done(self.state)
        
        return self.state, reward, done
        
    def _update_market_dynamics(self):
        """
        Update market conditions and competitor behavior
        
        Real-world basis:
        - Price trends: Follow normal distribution with 20% volatility, matching typical market behavior
        - Competitor actions: 10% monthly probability of strategic moves, based on industry averages
        - Action magnitude: 10-50% impact, reflecting typical market share shifts
        """
        for region in self.regions:
            # Update price trends using normal distribution to model real market behavior
            self.market_conditions['price_trends'][region] = np.random.normal(1.0, self.market_conditions['demand_volatility'])
            
            # Model competitor actions (10% probability reflects monthly strategic changes)
            if np.random.random() < 0.1:
                self.market_conditions['competitor_actions'].append({
                    'time': self.current_time,
                    'region': region,
                    'type': np.random.choice(['price_cut', 'capacity_increase', 'new_supplier']),
                    'magnitude': np.random.uniform(0.1, 0.5)  # 10-50% impact magnitude
                })
                
    def _update_economic_indicators(self):
        """
        Update economic indicators for each region
        
        Real-world basis:
        - GDP growth: Bounded between -5% and +10% annually, with 1% monthly variation
        - Inflation: 0-15% range with 0.5% monthly variation, based on global economics
        - Exchange rates: Log-normal distribution with 2% monthly volatility
        """
        for region in self.regions:
            # GDP growth rate changes (monthly variations around annual targets)
            current_gdp = self.market_conditions['economic_indicators']['gdp_growth'].get(region, 0.02)
            self.market_conditions['economic_indicators']['gdp_growth'][region] = max(-0.05, min(0.1, current_gdp + np.random.normal(0, 0.01)))
            
            # Inflation rate changes (based on typical central bank targets)
            current_inflation = self.market_conditions['economic_indicators']['inflation_rate'].get(region, 0.02)
            self.market_conditions['economic_indicators']['inflation_rate'][region] = max(0, min(0.15, current_inflation + np.random.normal(0, 0.005)))
            
            # Exchange rate fluctuations (log-normal to prevent negative rates)
            current_rate = self.market_conditions['economic_indicators']['exchange_rates'].get(region, 1.0)
            self.market_conditions['economic_indicators']['exchange_rates'][region] = max(0.5, min(2.0, current_rate * np.exp(np.random.normal(0, 0.02))))
            
    def _update_metrics(self, state: Dict[str, Any]):
        """Update all performance metrics"""
        # Core metrics
        self.metrics['resilience_score'].append(self._calculate_resilience_score(state))
        self.metrics['cost_impact'].append(self._calculate_cost_impact(state))
        self.metrics['service_level'].append(self._calculate_service_level(state))
        
        # ROI calculation
        investment_cost = sum(self._calculate_strategy_costs(state))
        benefit = self._calculate_resilience_benefits(state)
        self.metrics['roi'].append((benefit - investment_cost) / investment_cost if investment_cost > 0 else 0)
        
        # Recovery time (if there are disruptions)
        if state['disruptions']:
            self.metrics['recovery_time'].append(self._calculate_recovery_time(state))
        
        # Risk exposure
        self.metrics['risk_exposure'].append(self._calculate_risk_exposure(state))
        
        # Regional metrics
        for region in self.regions:
            self.metrics['supplier_performance'][region].append(self._calculate_supplier_performance(region, state))
            self.metrics['regional_performance'][region].append(self._calculate_regional_performance(region, state))
            
        # Operational metrics
        self.metrics['transportation_efficiency'].append(self._calculate_transportation_efficiency(state))
        self.metrics['inventory_health'].append(self._calculate_inventory_health(state))

    def _calculate_strategy_costs(self, state: Dict[str, Any]) -> List[float]:
        """Calculate costs of resilience strategies"""
        weights = self.config['metrics']['cost_weights']
        return [
            weights['supplier_diversification'] * 0.4,
            weights['inventory_management'] * 0.3,
            weights['transportation_flexibility'] * 0.2
        ]
        
    def _calculate_resilience_benefits(self, state: Dict[str, Any]) -> float:
        """Calculate benefits from resilience strategies"""
        if not state['disruptions']:
            return 0.0
            
        potential_loss = sum(d['severity'] for d in state['disruptions'])
        actual_loss = potential_loss * (1 - self._calculate_resilience_score(state))
        return potential_loss - actual_loss
        
    def _calculate_recovery_time(self, state: Dict[str, Any]) -> float:
        """
        Estimate recovery time from disruptions
        
        Real-world basis:
        - Base recovery: 10 weeks per severity unit, derived from industry recovery patterns
        - Strategy effectiveness: Weighted impact of different resilience strategies
        - Minimum time: 1 week, reflecting practical constraints of any recovery process
        
        The formula approximates real-world recovery patterns where:
        - Minor disruptions (severity 0.1): 1-2 weeks recovery
        - Moderate disruptions (severity 0.5): 3-5 weeks recovery
        - Major disruptions (severity 0.9): 7-9 weeks recovery
        """
        if not state['disruptions']:
            return 0.0
            
        max_severity = max(d['severity'] for d in state['disruptions'])
        base_recovery = max_severity * 10  # Base recovery time in weeks
        
        # Strategy effectiveness combines multiple approaches:
        # - Supplier diversification (30%): Alternative sourcing speed
        # - Inventory management (40%): Buffer against disruptions
        # - Transportation flexibility (30%): Routing adaptability
        strategy_effectiveness = (
            self.config['metrics']['resilience_weights']['supplier_diversification'] * 0.3 +
            self.config['metrics']['resilience_weights']['inventory_management'] * 0.4 +
            self.config['metrics']['resilience_weights']['transportation_flexibility'] * 0.3
        )
        
        return max(1, base_recovery * (1 - strategy_effectiveness))
        
    def _calculate_risk_exposure(self, state: Dict[str, Any]) -> float:
        """
        Calculate current risk exposure level
        
        Real-world basis:
        - Base risk: Combines regional disaster probability and infrastructure quality
        - Disruption impact: Normalized by factor of 10 to match industry risk scales
        - Economic risk: Based on GDP volatility as key risk indicator
        
        Output scale 0-1 maps to industry risk categories:
        - 0.0-0.3: Low risk
        - 0.3-0.6: Medium risk
        - 0.6-0.8: High risk
        - 0.8-1.0: Critical risk
        """
        # Base risk calculation considers infrastructure quality and disaster probability
        base_risk = sum(
            region_data['disaster_probability'] * (1 - region_data['infrastructure_quality'])
            for region_data in self.regions.values()
        ) / len(self.regions)
        
        # Current disruptions impact (normalized by 10 to match risk scale)
        current_disruption_impact = sum(d['severity'] for d in state['disruptions']) / 10 if state['disruptions'] else 0
        
        # Economic risk based on GDP volatility
        economic_risk = np.mean([
            abs(self.market_conditions['economic_indicators']['gdp_growth'].get(r, 0))
            for r in self.regions
        ])
        
        return min(1.0, base_risk + current_disruption_impact + economic_risk)
        
    def _calculate_supplier_performance(self, region: str, state: Dict[str, Any]) -> float:
        """
        Calculate supplier performance score for a region
        
        Real-world basis:
        - Base performance: Infrastructure quality as foundation (roads, ports, technology)
        - Disruption impact: Halved severity impact reflects supplier resilience capabilities
        - Economic impact: GDP growth minus inflation represents economic health
        
        Output scale 0-1 maps to supplier reliability levels:
        - 0.9-1.0: Excellent (Six Sigma level)
        - 0.8-0.9: Good (Industry standard)
        - 0.6-0.8: Fair (Needs improvement)
        - <0.6: Poor (Requires intervention)
        """
        region_data = self.regions[region]
        base_performance = region_data['infrastructure_quality']
        
        # Disruption impact (severity halved to model supplier resilience)
        region_disruptions = [d for d in state['disruptions'] if d['region'] == region]
        disruption_impact = sum(d['severity'] for d in region_disruptions) / 2 if region_disruptions else 0
        
        # Economic health impact on supplier performance
        economic_impact = (
            self.market_conditions['economic_indicators']['gdp_growth'].get(region, 0) -
            self.market_conditions['economic_indicators']['inflation_rate'].get(region, 0)
        )
        
        return max(0.0, min(1.0, base_performance - disruption_impact + economic_impact))
        
    def _calculate_regional_performance(self, region: str, state: Dict[str, Any]) -> float:
        """
        Calculate overall regional performance
        
        Real-world basis:
        - Supplier score (40%): Most critical factor in regional performance
        - Infrastructure (30%): Physical and technological capabilities
        - Political stability (30%): Business environment reliability
        
        The weights reflect typical supply chain risk assessments where:
        - Supplier issues account for ~40% of disruptions
        - Infrastructure problems cause ~30% of delays
        - Political/regulatory changes impact ~30% of operations
        """
        supplier_score = self._calculate_supplier_performance(region, state)
        infrastructure_score = self.regions[region]['infrastructure_quality']
        stability_score = self.regions[region]['political_stability']
        
        weights = {
            'supplier': 0.4,      # Primary factor in regional success
            'infrastructure': 0.3, # Physical and tech capabilities
            'stability': 0.3      # Business environment reliability
        }
        
        return (
            weights['supplier'] * supplier_score +
            weights['infrastructure'] * infrastructure_score +
            weights['stability'] * stability_score
        )
        
    def _calculate_transportation_efficiency(self, state: Dict[str, Any]) -> float:
        """
        Calculate transportation network efficiency
        
        Real-world basis:
        - Infrastructure quality: Physical network capability
        - Disruption impact: Reduced by transportation flexibility
        - Route optimization: Based on available alternatives
        
        Output interpretation:
        - >0.95: Optimal performance (JIT delivery possible)
        - 0.85-0.95: Good performance (Minor delays)
        - 0.70-0.85: Fair performance (Regular delays)
        - <0.70: Poor performance (Significant delays)
        """
        # Base efficiency from infrastructure
        base_efficiency = np.mean([
            region_data['infrastructure_quality']
            for region_data in self.regions.values()
        ])
        
        # Impact of current disruptions
        disruption_impact = sum(d['severity'] for d in state['disruptions']) / len(self.regions) if state['disruptions'] else 0
        
        # Adjust for transportation flexibility strategy
        flexibility_factor = self.config['resilience_strategies']['transportation_flexibility']['resilience_impact']
        
        return max(0.0, min(1.0, base_efficiency - (disruption_impact * (1 - flexibility_factor))))
        
    def _calculate_inventory_health(self, state: Dict[str, Any]) -> float:
        """
        Calculate inventory health based on service level, cost impact, and resilience
        
        The metric is now dynamically derived from other core metrics:
        - Stock score: Based on service level (indicates stock adequacy)
        - Holding cost score: Derived from cost impact (reflects cost efficiency)
        - Matching score: Combination of resilience and risk exposure (indicates demand matching capability)
        
        Returns:
            float: Inventory health score (0-1)
        """
        # Stock score based on service level
        # Service level directly reflects our ability to meet demand with current stock
        stock_score = state.get('service_level', 0.9)
        
        # Holding cost score derived from cost impact
        # Lower cost impact means better holding cost management
        holding_cost_score = 1 - min(1.0, self._calculate_cost_impact(state))
        
        # Matching score based on resilience and risk
        # Higher resilience and lower risk exposure indicate better demand matching
        matching_score = (
            self._calculate_resilience_score(state) * 0.6 +  # Resilience has higher weight
            (1 - self._calculate_risk_exposure(state)) * 0.4  # Risk exposure has lower weight
        )
        
        # Weighted combination of all components
        inventory_health = (
            0.4 * stock_score +          # Stock adequacy is most important
            0.3 * holding_cost_score +   # Cost efficiency
            0.3 * matching_score         # Demand matching capability
        )
        
        return max(0.0, min(1.0, inventory_health))

    def _calculate_resilience_score(self, state: Dict[str, Any]) -> float:
        """
        Calculate overall supply chain resilience score
        
        Real-world basis:
        - Recovery capability (40%): Speed of disruption recovery
        - Risk mitigation (30%): Effectiveness of preventive measures
        - Operational stability (30%): Day-to-day performance consistency
        
        Score interpretation:
        - >0.9: World-class resilience
        - 0.8-0.9: Strong resilience
        - 0.6-0.8: Moderate resilience
        - <0.6: Needs improvement
        """
        # Recovery capability
        recovery_score = 1.0 - (self._calculate_recovery_time(state) / (10 * len(self.regions)))
        
        # Risk mitigation effectiveness
        risk_score = 1.0 - self._calculate_risk_exposure(state)
        
        # Operational stability
        stability_score = np.mean([
            state.get('service_level', 1.0),
            self._calculate_transportation_efficiency(state),
            state.get('inventory_health', 1.0)
        ])
        
        # Weighted combination
        resilience_score = (
            0.4 * recovery_score +
            0.3 * risk_score +
            0.3 * stability_score
        )
        
        return max(0.0, min(1.0, resilience_score))

    def _calculate_service_level(self, state: Dict[str, Any]) -> float:
        """
        Calculate service level based on order fulfillment performance
        
        Args:
            state: Current simulation state
            
        Returns:
            float: Service level score (0-1)
        """
        base_service_level = 0.98  # Industry standard target
        
        # Calculate impacts
        disruption_impact = sum(d['severity'] for d in state['disruptions']) / 20.0
        regional_impact = np.mean([
            self._calculate_regional_performance(region, state)
            for region in self.regions
        ])
        
        # Get inventory health directly from state if available, otherwise use base value
        inventory_impact = state.get('inventory_health', 0.9)  # Use stored value or default
        
        # Calculate final service level
        service_level = (
            base_service_level *
            (1 - disruption_impact) *
            regional_impact *
            inventory_impact
        )
        
        return max(0.0, min(1.0, service_level))
        
    def _calculate_reward(self, state: Dict[str, Any]) -> float:
        """Calculate reward based on service level and cost impact"""
        service_level = state.get('service_level', 0)
        cost_impact = self._calculate_cost_impact(state)
        return service_level - (cost_impact * 0.5)  # Reward high service level while penalizing high costs
        
    def _is_done(self, state: Dict[str, Any]) -> bool:
        """Check if simulation should end"""
        return self.current_time >= self.config['simulation']['max_steps']

    def get_state(self) -> Dict[str, Any]:
        """Return current world state"""
        return {
            'time': self.current_time,
            'regions': self.regions,
            'disruptions': [d for d in self.disruption_events if d['time'] == self.current_time],
            'metrics': {
                'resilience_score': self.metrics['resilience_score'][-1] if self.metrics['resilience_score'] else 1.0,
                'cost_impact': self.metrics['cost_impact'][-1] if self.metrics['cost_impact'] else 0.0,
                'service_level': self.metrics['service_level'][-1] if self.metrics['service_level'] else 1.0
            }
        }
        
    def _generate_disruptions(self):
        """Generate random disruption events based on regional probabilities"""
        for region_name, region_data in self.regions.items():
            if np.random.random() < region_data['disaster_probability']:
                disruption_type = np.random.choice(self.config['simulation']['disruption_types'])
                severity = self._calculate_disruption_severity(region_name, disruption_type)
                
                self.disruption_events.append({
                    'time': self.current_time,
                    'region': region_name,
                    'type': disruption_type,
                    'severity': severity
                })
                
    def _calculate_disruption_severity(self, region: str, disruption_type: str) -> float:
        """Calculate disruption severity based on region and type"""
        base_severity = np.random.uniform(0.1, 1.0)
        region_data = self.regions[region]
        
        # Adjust severity based on region characteristics
        if disruption_type == 'natural':
            severity = base_severity * (1 - region_data['infrastructure_quality'])
        elif disruption_type == 'political':
            severity = base_severity * (1 - region_data['political_stability'])
        else:  # infrastructure
            severity = base_severity * (1 - region_data['infrastructure_quality'])
            
        return max(0.1, min(1.0, severity))
        
    def _calculate_cost_impact(self, state: Dict[str, Any]) -> float:
        """Calculate cost impact of current state"""
        weights = self.config['metrics']['cost_weights']
        disruption_cost = sum(d['severity'] * 0.5 for d in state['disruptions'])
        
        strategy_cost = (
            weights['supplier_diversification'] * 0.4 +
            weights['inventory_management'] * 0.3 +
            weights['transportation_flexibility'] * 0.2
        )
        
        return strategy_cost + disruption_cost
        
    def get_metrics_summary(self) -> Dict[str, float]:
        """Return summary statistics of simulation metrics"""
        return {
            'avg_resilience': np.mean(self.metrics['resilience_score']),
            'avg_cost_impact': np.mean(self.metrics['cost_impact']),
            'avg_service_level': np.mean(self.metrics['service_level']),
            'min_service_level': min(self.metrics['service_level']),
            'max_cost_impact': max(self.metrics['cost_impact']),
            'avg_roi': np.mean(self.metrics['roi']) if self.metrics['roi'] else 0.0,
            'avg_recovery_time': np.mean(self.metrics['recovery_time']) if self.metrics['recovery_time'] else 0.0,
            'avg_risk_exposure': np.mean(self.metrics['risk_exposure']),
            'transportation_efficiency': np.mean(self.metrics['transportation_efficiency']),
            'inventory_health': np.mean(self.metrics['inventory_health']),
            **{
                f'supplier_performance_{region}': np.mean(perf)
                for region, perf in self.metrics['supplier_performance'].items()
            }
        } 