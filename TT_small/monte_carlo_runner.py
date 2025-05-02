"""
Supply Chain Resilience Monte Carlo Simulation Runner

This module implements a Monte Carlo simulation framework for supply chain resilience analysis.
The simulation explores multiple scenarios and their impact on supply chain performance by:
- Running thousands of iterations with different random seeds
- Testing various disruption scenarios
- Analyzing the effectiveness of resilience strategies
- Validating hypotheses about supply chain behavior

Key components:
- ScenarioConfig: Defines different simulation scenarios
- MonteCarloSimulation: Manages simulation execution and analysis
- Visualization functions: Generate insights from simulation results

The simulation uses TinyTroupe's agent-based modeling capabilities to represent:
- Supply chain decision makers (COO, Regional Managers)
- Supplier behavior and performance
- Complex interactions between agents and environment
"""

import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List
from datetime import datetime
from copy import deepcopy

from supply_chain_config import DEFAULT_CONFIG
from supply_chain_agents import (
    create_coo_agent,
    create_regional_manager_agent,
    create_supplier_agent
)
from supply_chain_environment import SupplyChainWorld
from supply_chain_agents import SupplyChainAgent
from tinytroupe.environment.tiny_world import TinyWorld
from tinytroupe.agent.tiny_person import TinyPerson

class ScenarioConfig:
    """
    Configuration for different simulation scenarios
    
    Each scenario represents a specific type of supply chain challenge:
    - Baseline: Normal operating conditions
    - Supplier Disruption: Increased probability of supplier failures
    - Transportation Disruption: Infrastructure and logistics challenges
    - Production Disruption: Manufacturing facility issues
    - Multi-factor: Combined disruptions testing overall resilience
    """
    
    @staticmethod
    def get_baseline_config():
        """
        Return baseline configuration representing normal business conditions
        - Standard disruption probabilities
        - Normal infrastructure quality
        - Typical production capacity
        """
        return DEFAULT_CONFIG
    
    @staticmethod
    def get_supplier_disruption_config():
        """Configuration for supplier disruption scenario"""
        config = deepcopy(DEFAULT_CONFIG)
        # Increase probability of supplier-related disruptions
        for region in config['regions'].values():
            region['disaster_probability'] *= 2
        return config
    
    @staticmethod
    def get_transportation_disruption_config():
        """Configuration for transportation disruption scenario"""
        config = deepcopy(DEFAULT_CONFIG)
        # Decrease infrastructure quality to simulate transportation issues
        for region in config['regions'].values():
            region['infrastructure_quality'] *= 0.7
        return config
    
    @staticmethod
    def get_production_disruption_config():
        """Configuration for production facility disruption scenario"""
        config = deepcopy(DEFAULT_CONFIG)
        # Decrease production capacity and increase disruption probability
        for region in config['regions'].values():
            region['production_capacity'] = region.get('production_capacity', 1.0) * 0.6
            region['disaster_probability'] *= 1.5
        return config
    
    @staticmethod
    def get_multi_factor_disruption_config():
        """Configuration for multi-factor disruption scenario"""
        config = deepcopy(DEFAULT_CONFIG)
        # Combine multiple disruption factors
        for region in config['regions'].values():
            region['disaster_probability'] *= 1.8
            region['infrastructure_quality'] *= 0.8
            region['production_capacity'] = region.get('production_capacity', 1.0) * 0.7
        return config

class MonteCarloSimulation:
    """
    Monte Carlo simulation implementation for supply chain resilience analysis
    
    The simulation follows these steps for each iteration:
    1. Initialize environment and agents with scenario configuration
    2. Run simulation for specified time period (default: 52 weeks)
    3. Collect and analyze performance metrics
    4. Generate visualizations and statistical analysis
    
    Key metrics tracked:
    - Resilience Score: Overall system robustness
    - Cost Impact: Financial implications of disruptions and strategies
    - Service Level: Order fulfillment performance
    - Recovery Time: Speed of return to normal operations
    - Risk Exposure: Current threat level to operations
    """
    def __init__(self, config: Dict[str, Any] = None, scenario_name: str = "baseline"):
        self.config = config or DEFAULT_CONFIG
        self.results = []
        self.agents = {}
        self.scenario_name = scenario_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def initialize_agents(self):
        """Initialize supply chain agents"""
        # Create COO
        self.agents['coo'] = SupplyChainAgent(
            name="Elena Martinez",
            role="COO"
        )
        
        # Create Regional Managers
        for region in self.config['regions'].keys():
            self.agents[f'manager_{region}'] = SupplyChainAgent(
                name=f"Manager_{region}",
                role="Regional_Manager",
                region=region
            )
            
            # Create Suppliers for each region
            self.agents[f'supplier_{region}'] = SupplyChainAgent(
                name=f"Supplier_{region}",
                role="Supplier",
                region=region
            )
            
    def run(self):
        """Run Monte Carlo simulation"""
        np.random.seed(self.config['simulation']['seed'])
        
        for iteration in range(self.config['simulation']['monte_carlo_iterations']):
            # Clear environment and agent registries
            TinyWorld.all_environments.clear()
            TinyPerson.all_agents.clear()
            
            # Initialize world and agents for this iteration
            world = SupplyChainWorld(self.config)
            self.initialize_agents()
            
            # Run single iteration
            iteration_results = self._run_iteration(world)
            iteration_results['scenario'] = self.scenario_name
            self.results.append(iteration_results)
            
    def _run_iteration(self, world: SupplyChainWorld) -> Dict[str, float]:
        """Run a single iteration of the simulation"""
        simulation_length = self.config['simulation']['simulation_length_weeks']
        
        for week in range(simulation_length):
            # Update world state
            state = world.step()
            
            # COO decision making
            coo_decisions = self.agents['coo'].make_decision(world)
            
            # Regional managers and suppliers decision making
            for region in self.config['regions'].keys():
                manager = self.agents[f'manager_{region}']
                supplier = self.agents[f'supplier_{region}']
                
                manager_decisions = manager.make_decision(world)
                supplier_decisions = supplier.make_decision(world)
                
        # Return metrics summary for this iteration
        return world.get_metrics_summary()
        
    def analyze_results(self):
        """Analyze and visualize simulation results"""
        df_results = pd.DataFrame(self.results)
        
        # Calculate aggregate statistics
        stats = {
            'avg_resilience': df_results['avg_resilience'].mean(),
            'std_resilience': df_results['avg_resilience'].std(),
            'avg_cost': df_results['avg_cost_impact'].mean(),
            'std_cost': df_results['avg_cost_impact'].std(),
            'avg_service': df_results['avg_service_level'].mean(),
            'std_service': df_results['avg_service_level'].std(),
            'worst_service': df_results['min_service_level'].min(),
            'highest_cost': df_results['max_cost_impact'].max(),
            'avg_roi': df_results['avg_roi'].mean(),
            'avg_recovery_time': df_results['avg_recovery_time'].mean(),
            'avg_risk_exposure': df_results['avg_risk_exposure'].mean()
        }
        
        # Generate visualizations
        self._plot_hypothesis_validation(df_results)
        self._plot_overall_benefits(df_results)
        self._plot_domain_impact(df_results)
        self._plot_total_time_analysis(df_results)
        
        return stats
        
    def _plot_hypothesis_validation(self, df_results: pd.DataFrame):
        """Plot hypothesis validation results"""
        plt.figure(figsize=(12, 8))
        
        # Sub-hypothesis 1: Supplier Diversification
        plt.subplot(2, 2, 1)
        sns.scatterplot(data=df_results, x='avg_cost_impact', y='avg_resilience', alpha=0.6, label='Simulation Runs')
        plt.title('H1: Supplier Diversification Impact')
        plt.xlabel('Cost Impact')
        plt.ylabel('Resilience Score')
        plt.legend()
        
        # Sub-hypothesis 2: Inventory Management
        plt.subplot(2, 2, 2)
        sns.lineplot(data=df_results, x=range(len(df_results)), y='avg_service_level', label='Service Level')
        plt.title('H2: Dynamic Inventory Effectiveness')
        plt.xlabel('Simulation Run')
        plt.ylabel('Service Level')
        plt.legend()
        
        # Sub-hypothesis 3: Transportation Flexibility
        plt.subplot(2, 2, 3)
        sns.histplot(data=df_results, x='avg_recovery_time', bins=30, label='Recovery Time')
        plt.title('H3: Transportation Route Flexibility')
        plt.xlabel('Recovery Time (weeks)')
        plt.ylabel('Frequency')
        plt.legend()
        
        # Sub-hypothesis 4: Regional Production
        plt.subplot(2, 2, 4)
        metrics_map = {
            'avg_resilience': 'Resilience',
            'avg_service_level': 'Service Level',
            'avg_cost_impact': 'Cost Impact'
        }
        df_melted = pd.melt(df_results[['avg_resilience', 'avg_service_level', 'avg_cost_impact']])
        df_melted['variable'] = df_melted['variable'].map(metrics_map)
        sns.boxplot(data=df_melted, x='variable', y='value')
        plt.title('H4: Regional Production Performance')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'experimental_hypothesis_validation_{self.timestamp}.png')
        plt.close()
        
    def _plot_overall_benefits(self, df_results: pd.DataFrame):
        """Plot overall benefits analysis"""
        plt.figure(figsize=(10, 6))
        
        # ROI Distribution
        sns.histplot(data=df_results, x='avg_roi', bins=30, label='ROI Distribution')
        mean_roi = df_results['avg_roi'].mean()
        plt.axvline(x=mean_roi, color='r', linestyle='--', 
                   label=f'Mean ROI: {mean_roi:.2f}')
        
        plt.title('Distribution of Return on Resilience Investment')
        plt.xlabel('ROI')
        plt.ylabel('Frequency')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'experimental_overall_benefits_{self.timestamp}.png')
        plt.close()
        
    def _plot_domain_impact(self, df_results: pd.DataFrame):
        """Plot domain-specific impact analysis"""
        plt.figure(figsize=(15, 10))
        
        # Supplier Performance
        plt.subplot(2, 2, 1)
        supplier_data = pd.DataFrame({
            region: df_results[f'supplier_performance_{region}'].mean()
            for region in self.config['regions'].keys()
        }, index=[0]).melt()
        sns.barplot(data=supplier_data, x='variable', y='value')
        plt.title('Regional Supplier Performance')
        plt.xlabel('Region')
        plt.ylabel('Performance Score')
        plt.xticks(rotation=45)
        
        # Risk Exposure Over Time
        plt.subplot(2, 2, 2)
        sns.lineplot(data=df_results, x=range(len(df_results)), 
                    y='avg_risk_exposure', label='Risk Level')
        plt.title('Risk Exposure Trend')
        plt.xlabel('Simulation Run')
        plt.ylabel('Risk Level')
        plt.legend()
        
        # Transportation Efficiency
        plt.subplot(2, 2, 3)
        sns.histplot(data=df_results, x='transportation_efficiency', 
                    bins=30, label='Efficiency Distribution')
        plt.axvline(x=df_results['transportation_efficiency'].mean(), 
                   color='r', linestyle='--', 
                   label=f'Mean: {df_results["transportation_efficiency"].mean():.2f}')
        plt.title('Transportation Network Efficiency')
        plt.xlabel('Efficiency Score')
        plt.ylabel('Frequency')
        plt.legend()
        
        # Inventory Health
        plt.subplot(2, 2, 4)
        metrics = ['inventory_health', 'avg_service_level']
        labels = ['Inventory Health', 'Service Level']
        sns.boxplot(data=df_results[metrics], labels=labels)
        plt.title('Inventory Health vs Service Level')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'experimental_domain_impact_{self.timestamp}.png')
        plt.close()
        
    def _plot_total_time_analysis(self, df_results: pd.DataFrame):
        """Plot time-based analysis"""
        plt.figure(figsize=(15, 10))
        
        # Recovery Time Distribution
        plt.subplot(2, 2, 1)
        sns.histplot(data=df_results, x='avg_recovery_time', 
                    bins=30, label='Recovery Time')
        plt.axvline(x=df_results['avg_recovery_time'].mean(), 
                   color='r', linestyle='--', 
                   label=f'Mean: {df_results["avg_recovery_time"].mean():.1f} weeks')
        plt.title('Distribution of Recovery Times')
        plt.xlabel('Weeks')
        plt.ylabel('Frequency')
        plt.legend()
        
        # Service Level Over Time
        plt.subplot(2, 2, 2)
        mean_service = df_results['avg_service_level'].mean()
        std_service = df_results['avg_service_level'].std()
        sns.lineplot(data=df_results, x=range(len(df_results)), 
                    y='avg_service_level', label='Service Level')
        plt.fill_between(range(len(df_results)), 
                        df_results['avg_service_level'] - std_service,
                        df_results['avg_service_level'] + std_service,
                        alpha=0.3, label=f'±1 STD ({std_service:.2f})')
        plt.title(f'Service Level Stability (Mean: {mean_service:.2f})')
        plt.xlabel('Simulation Run')
        plt.ylabel('Service Level')
        plt.legend()
        
        # Cost Impact Timeline
        plt.subplot(2, 2, 3)
        sns.lineplot(data=df_results, x=range(len(df_results)), 
                    y='avg_cost_impact', label='Cost Impact')
        plt.title('Cost Impact Evolution')
        plt.xlabel('Simulation Run')
        plt.ylabel('Cost Impact')
        plt.legend()
        
        # Resilience Score Timeline
        plt.subplot(2, 2, 4)
        sns.lineplot(data=df_results, x=range(len(df_results)), 
                    y='avg_resilience', label='Resilience Score')
        plt.title('Resilience Score Evolution')
        plt.xlabel('Simulation Run')
        plt.ylabel('Resilience Score')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(f'experimental_total_time_{self.timestamp}.png')
        plt.close()
        
def run_all_scenarios():
    """Run simulations for all scenarios and generate comparative analysis"""
    scenarios = {
        'baseline': ScenarioConfig.get_baseline_config(),
        'supplier_disruption': ScenarioConfig.get_supplier_disruption_config(),
        'transportation_disruption': ScenarioConfig.get_transportation_disruption_config(),
        'production_disruption': ScenarioConfig.get_production_disruption_config(),
        'multi_factor_disruption': ScenarioConfig.get_multi_factor_disruption_config()
    }
    
    all_results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Run simulations for each scenario
    for scenario_name, config in scenarios.items():
        print(f"\nRunning scenario: {scenario_name}")
        simulation = MonteCarloSimulation(config, scenario_name)
        simulation.run()
        all_results.extend(simulation.results)
    
    # Convert results to DataFrame
    df_results = pd.DataFrame(all_results)
    
    # Generate comparative visualizations
    plot_scenario_comparisons(df_results, timestamp)
    plot_strategy_effectiveness(df_results, timestamp)
    plot_disruption_impact_analysis(df_results, timestamp)
    
    # Print summary statistics
    print_scenario_summaries(df_results)

def plot_scenario_comparisons(df_results: pd.DataFrame, timestamp: str):
    """Generate comparative visualizations for different scenarios"""
    plt.figure(figsize=(15, 10))
    
    # Core metrics comparison
    plt.subplot(2, 2, 1)
    metrics = ['avg_resilience', 'avg_service_level', 'avg_cost_impact']
    metric_labels = {'avg_resilience': 'Resilience', 
                    'avg_service_level': 'Service Level', 
                    'avg_cost_impact': 'Cost Impact'}
    df_melted = pd.melt(df_results, id_vars=['scenario'], value_vars=metrics)
    df_melted['variable'] = df_melted['variable'].map(metric_labels)
    sns.boxplot(data=df_melted, x='variable', y='value', hue='scenario')
    plt.title('Core Metrics by Scenario')
    plt.xticks(rotation=45)
    plt.legend(title='Scenario', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Recovery time comparison
    plt.subplot(2, 2, 2)
    sns.boxplot(data=df_results, x='scenario', y='avg_recovery_time')
    plt.title('Recovery Time by Scenario')
    plt.xlabel('Scenario')
    plt.ylabel('Recovery Time (weeks)')
    plt.xticks(rotation=45)
    
    # Risk exposure comparison
    plt.subplot(2, 2, 3)
    sns.boxplot(data=df_results, x='scenario', y='avg_risk_exposure')
    plt.title('Risk Exposure by Scenario')
    plt.xlabel('Scenario')
    plt.ylabel('Risk Level')
    plt.xticks(rotation=45)
    
    # ROI comparison
    plt.subplot(2, 2, 4)
    sns.boxplot(data=df_results, x='scenario', y='avg_roi')
    plt.title('ROI by Scenario')
    plt.xlabel('Scenario')
    plt.ylabel('Return on Investment')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'test_results/scenario_comparison_{timestamp}.png', bbox_inches='tight')
    plt.close()

def plot_strategy_effectiveness(df_results: pd.DataFrame, timestamp: str):
    """Analyze effectiveness of different strategies"""
    plt.figure(figsize=(15, 10))
    
    # Strategy effectiveness in different scenarios
    plt.subplot(2, 2, 1)
    strategy_metrics = ['transportation_efficiency', 'inventory_health']
    df_melted = pd.melt(df_results, id_vars=['scenario'], value_vars=strategy_metrics)
    sns.boxplot(data=df_melted, x='scenario', y='value', hue='variable')
    plt.title('Strategy Effectiveness by Scenario')
    plt.xticks(rotation=45)
    
    # Regional performance comparison
    plt.subplot(2, 2, 2)
    regional_cols = [col for col in df_results.columns if 'supplier_performance_' in col]
    df_melted = pd.melt(df_results, id_vars=['scenario'], value_vars=regional_cols)
    sns.boxplot(data=df_melted, x='scenario', y='value', hue='variable')
    plt.title('Regional Performance by Scenario')
    plt.xticks(rotation=45)
    
    # Cost vs. Resilience trade-off
    plt.subplot(2, 2, 3)
    for scenario in df_results['scenario'].unique():
        scenario_data = df_results[df_results['scenario'] == scenario]
        plt.scatter(scenario_data['avg_cost_impact'], scenario_data['avg_resilience'], 
                   label=scenario, alpha=0.6)
    plt.title('Cost vs. Resilience Trade-off')
    plt.xlabel('Cost Impact')
    plt.ylabel('Resilience Score')
    plt.legend()
    
    # Service level stability
    plt.subplot(2, 2, 4)
    sns.boxplot(data=df_results, x='scenario', y='avg_service_level')
    plt.title('Service Level Stability')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'test_results/strategy_effectiveness_{timestamp}.png')
    plt.close()

def plot_disruption_impact_analysis(df_results: pd.DataFrame, timestamp: str):
    """Analyze impact of different types of disruptions"""
    plt.figure(figsize=(15, 10))
    
    # Recovery time vs. disruption type
    plt.subplot(2, 2, 1)
    sns.boxplot(data=df_results, x='scenario', y='avg_recovery_time')
    plt.title('Recovery Time by Disruption Type')
    plt.xticks(rotation=45)
    
    # Cost impact vs. disruption type
    plt.subplot(2, 2, 2)
    sns.boxplot(data=df_results, x='scenario', y='avg_cost_impact')
    plt.title('Cost Impact by Disruption Type')
    plt.xticks(rotation=45)
    
    # Service level impact
    plt.subplot(2, 2, 3)
    sns.boxplot(data=df_results, x='scenario', y='avg_service_level')
    plt.title('Service Level Impact')
    plt.xticks(rotation=45)
    
    # Risk exposure comparison
    plt.subplot(2, 2, 4)
    sns.boxplot(data=df_results, x='scenario', y='avg_risk_exposure')
    plt.title('Risk Exposure by Disruption Type')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'test_results/disruption_impact_{timestamp}.png')
    plt.close()

def print_scenario_summaries(df_results: pd.DataFrame):
    """Print summary statistics for each scenario"""
    print("\nScenario Analysis Summary:")
    for scenario in df_results['scenario'].unique():
        scenario_data = df_results[df_results['scenario'] == scenario]
        print(f"\n{scenario.upper()}:")
        print(f"Resilience Score: {scenario_data['avg_resilience'].mean():.3f} (±{scenario_data['avg_resilience'].std():.3f})")
        print(f"Service Level: {scenario_data['avg_service_level'].mean():.3f} (±{scenario_data['avg_service_level'].std():.3f})")
        print(f"Cost Impact: {scenario_data['avg_cost_impact'].mean():.3f} (±{scenario_data['avg_cost_impact'].std():.3f})")
        print(f"Recovery Time: {scenario_data['avg_recovery_time'].mean():.1f} weeks")
        print(f"Risk Exposure: {scenario_data['avg_risk_exposure'].mean():.3f}")
        print(f"ROI: {scenario_data['avg_roi'].mean():.3f}")

def main():
    # Run all scenarios and generate comparative analysis
    run_all_scenarios()

if __name__ == "__main__":
    main() 