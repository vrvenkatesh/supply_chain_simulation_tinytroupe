import numpy as np
import pandas as pd
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

class Environment:
    """Base environment class"""
    def __init__(self):
        pass

    @abstractmethod
    def step(self):
        pass

class Agent:
    """Base agent class"""
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def act(self, env) -> Dict[str, Any]:
        pass

class SupplyChainEnvironment(Environment):
    def __init__(self):
        super().__init__()
        # Geographic regions with their parameters
        self.regions = {
            'North_America': {
                'political_stability': 8,
                'disaster_probability': 0.1,
                'labor_cost': 1.0,
                'infrastructure_quality': 0.9
            },
            'Europe': {
                'political_stability': 7,
                'disaster_probability': 0.08,
                'labor_cost': 1.1,
                'infrastructure_quality': 0.95
            },
            'East_Asia': {
                'political_stability': 6,
                'disaster_probability': 0.15,
                'labor_cost': 0.7,
                'infrastructure_quality': 0.85
            }
        }
        
        self.current_time = 0
        self.disruption_events = []
        
    def step(self):
        """Advance simulation time and generate random events"""
        self.current_time += 1
        self._generate_disruptions()
        
    def _generate_disruptions(self):
        """Generate random disruption events based on regional probabilities"""
        for region, params in self.regions.items():
            if np.random.random() < params['disaster_probability']:
                self.disruption_events.append({
                    'time': self.current_time,
                    'region': region,
                    'type': np.random.choice(['natural', 'political', 'infrastructure']),
                    'severity': np.random.uniform(0.1, 1.0)
                })

class SupplyChainAgent(Agent):
    def __init__(self, name: str, role: str, region: str = None):
        super().__init__(name)
        self.role = role
        self.region = region
        self.performance_metrics = {
            'cost': 0,
            'resilience': 0,
            'service_level': 0
        }
        
    def act(self, env: SupplyChainEnvironment) -> Dict[str, Any]:
        """Make decisions based on current environment state"""
        if self.role == 'COO':
            return self._coo_decision_making(env)
        elif self.role == 'Regional_Manager':
            return self._regional_manager_decision_making(env)
        elif self.role == 'Supplier':
            return self._supplier_decision_making(env)
        return {}
        
    def _coo_decision_making(self, env: SupplyChainEnvironment) -> Dict[str, Any]:
        """Strategic decision making for COO role"""
        current_disruptions = [d for d in env.disruption_events if d['time'] == env.current_time]
        
        decisions = {
            'supplier_diversification': 0.0,
            'inventory_adjustment': 0.0,
            'transportation_mode_shift': 0.0
        }
        
        if current_disruptions:
            # Increase resilience measures during disruptions
            decisions['supplier_diversification'] = np.random.uniform(0.6, 0.9)
            decisions['inventory_adjustment'] = np.random.uniform(0.4, 0.7)
            decisions['transportation_mode_shift'] = np.random.uniform(0.5, 0.8)
        else:
            # Balance cost and resilience during normal operations
            decisions['supplier_diversification'] = np.random.uniform(0.3, 0.5)
            decisions['inventory_adjustment'] = np.random.uniform(0.2, 0.4)
            decisions['transportation_mode_shift'] = np.random.uniform(0.2, 0.4)
            
        return decisions
    
    def _regional_manager_decision_making(self, env: SupplyChainEnvironment) -> Dict[str, Any]:
        """Regional manager decision making"""
        return {}  # Implement if needed
        
    def _supplier_decision_making(self, env: SupplyChainEnvironment) -> Dict[str, Any]:
        """Supplier decision making"""
        return {}  # Implement if needed

class SupplyChainSimulation:
    def __init__(self, num_iterations: int = 1000):
        self.num_iterations = num_iterations
        self.results = []
        
    def run(self):
        """Run Monte Carlo simulation"""
        for i in range(self.num_iterations):
            # Initialize environment and agents
            env = SupplyChainEnvironment()
            
            elena = SupplyChainAgent(name="Elena Martinez", role="COO")
            regional_managers = [
                SupplyChainAgent(name=f"Manager_{region}", role="Regional_Manager", region=region)
                for region in env.regions.keys()
            ]
            
            # Run single iteration
            iteration_results = self._run_iteration(env, elena, regional_managers)
            self.results.append(iteration_results)
            
    def _run_iteration(self, env: SupplyChainEnvironment, 
                      coo: SupplyChainAgent, 
                      regional_managers: List[SupplyChainAgent]) -> Dict[str, float]:
        """Run a single iteration of the simulation"""
        simulation_length = 52  # weeks
        
        resilience_scores = []
        cost_impacts = []
        service_levels = []
        
        for week in range(simulation_length):
            env.step()
            
            # COO decisions
            coo_decisions = coo.act(env)
            
            # Regional manager responses
            for manager in regional_managers:
                manager_decisions = manager.act(env)
                
                # Calculate metrics
                resilience_score = self._calculate_resilience(env, coo_decisions, manager_decisions)
                cost_impact = self._calculate_cost_impact(coo_decisions, manager_decisions)
                service_level = self._calculate_service_level(env, manager_decisions)
                
                resilience_scores.append(resilience_score)
                cost_impacts.append(cost_impact)
                service_levels.append(service_level)
        
        return {
            'avg_resilience': np.mean(resilience_scores),
            'avg_cost_impact': np.mean(cost_impacts),
            'avg_service_level': np.mean(service_levels),
            'disruption_count': len(env.disruption_events)
        }
    
    def _calculate_resilience(self, env: SupplyChainEnvironment, 
                            coo_decisions: Dict[str, float],
                            manager_decisions: Dict[str, float]) -> float:
        """Calculate resilience score based on decisions and environment state"""
        base_resilience = (
            coo_decisions.get('supplier_diversification', 0) * 0.4 +
            coo_decisions.get('inventory_adjustment', 0) * 0.3 +
            coo_decisions.get('transportation_mode_shift', 0) * 0.3
        )
        
        # Adjust for current disruptions
        current_disruptions = [d for d in env.disruption_events if d['time'] == env.current_time]
        disruption_impact = sum(d['severity'] for d in current_disruptions) if current_disruptions else 0
        
        return max(0, min(1, base_resilience - disruption_impact * 0.5))
    
    def _calculate_cost_impact(self, coo_decisions: Dict[str, float],
                             manager_decisions: Dict[str, float]) -> float:
        """Calculate cost impact of resilience decisions"""
        # Higher resilience measures increase costs
        return (
            coo_decisions.get('supplier_diversification', 0) * 0.5 +
            coo_decisions.get('inventory_adjustment', 0) * 0.3 +
            coo_decisions.get('transportation_mode_shift', 0) * 0.2
        )
    
    def _calculate_service_level(self, env: SupplyChainEnvironment,
                               manager_decisions: Dict[str, float]) -> float:
        """Calculate service level achievement"""
        base_service_level = 0.95  # Target service level
        
        # Impact of current disruptions
        current_disruptions = [d for d in env.disruption_events if d['time'] == env.current_time]
        disruption_impact = sum(d['severity'] for d in current_disruptions) if current_disruptions else 0
        
        return max(0, min(1, base_service_level - disruption_impact * 0.3))
    
    def analyze_results(self):
        """Analyze and visualize simulation results"""
        df_results = pd.DataFrame(self.results)
        
        # Calculate key metrics
        metrics = {
            'Average Resilience': df_results['avg_resilience'].mean(),
            'Average Cost Impact': df_results['avg_cost_impact'].mean(),
            'Average Service Level': df_results['avg_service_level'].mean(),
            'Average Disruptions': df_results['disruption_count'].mean()
        }
        
        # Create visualizations
        plt.figure(figsize=(15, 10))
        
        # Resilience vs Cost Impact scatter plot
        plt.subplot(2, 2, 1)
        plt.scatter(df_results['avg_cost_impact'], df_results['avg_resilience'], alpha=0.5)
        plt.xlabel('Cost Impact')
        plt.ylabel('Resilience Score')
        plt.title('Resilience vs Cost Trade-off')
        
        # Service Level distribution
        plt.subplot(2, 2, 2)
        plt.hist(df_results['avg_service_level'], bins=30)
        plt.xlabel('Service Level')
        plt.ylabel('Frequency')
        plt.title('Service Level Distribution')
        
        # Disruption count distribution
        plt.subplot(2, 2, 3)
        plt.hist(df_results['disruption_count'], bins=30)
        plt.xlabel('Number of Disruptions')
        plt.ylabel('Frequency')
        plt.title('Disruption Distribution')
        
        plt.tight_layout()
        plt.savefig('simulation_results/supply_chain_simulation_results.png')
        
        return metrics

if __name__ == "__main__":
    # Run simulation
    sim = SupplyChainSimulation(num_iterations=1000)
    sim.run()
    
    # Analyze results
    results = sim.analyze_results()
    print("\nSimulation Results:")
    for metric, value in results.items():
        print(f"{metric}: {value:.4f}") 