"""
Supply Chain Simulation Scenario Manager

This module provides utilities for managing simulation scenarios and configurations.
It allows listing available scenarios, creating custom scenarios, and validating configurations.
"""

from typing import Dict, Any, List
from copy import deepcopy
import json

from supply_chain_config import DEFAULT_CONFIG

class ScenarioManager:
    """Manages simulation scenarios and configurations"""
    
    @staticmethod
    def get_available_scenarios() -> Dict[str, str]:
        """
        Get list of available predefined scenarios
        
        Returns:
            Dict[str, str]: Dictionary mapping scenario names to descriptions
        """
        return {
            'baseline': 'Normal operating conditions with standard parameters',
            'supplier_disruption': 'Increased probability of supplier failures',
            'transportation_disruption': 'Infrastructure and logistics challenges',
            'production_disruption': 'Manufacturing facility issues',
            'multi_factor_disruption': 'Combined disruptions testing overall resilience',
            'global_tariff_disruption': 'Impact of US-imposed tariffs on China and global trade'
        }
    
    @staticmethod
    def get_scenario_config(scenario_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific scenario
        
        Args:
            scenario_name: Name of the scenario
            
        Returns:
            Dict[str, Any]: Configuration dictionary for the scenario
        """
        config = deepcopy(DEFAULT_CONFIG)
        
        if scenario_name == 'baseline':
            return config
        
        elif scenario_name == 'supplier_disruption':
            for region in config['regions'].values():
                region['disaster_probability'] *= 2
            
        elif scenario_name == 'transportation_disruption':
            for region in config['regions'].values():
                region['infrastructure_quality'] *= 0.7
            
        elif scenario_name == 'production_disruption':
            for region in config['regions'].values():
                region['production_capacity'] = region.get('production_capacity', 1.0) * 0.6
                region['disaster_probability'] *= 1.5
            
        elif scenario_name == 'multi_factor_disruption':
            for region in config['regions'].values():
                region['disaster_probability'] *= 1.8
                region['infrastructure_quality'] *= 0.8
                region['production_capacity'] = region.get('production_capacity', 1.0) * 0.7

        elif scenario_name == 'global_tariff_disruption':
            # East Asia (China) specific impacts
            config['regions']['East_Asia']['political_stability'] *= 0.8  # Increased trade tensions
            config['regions']['East_Asia']['labor_cost'] *= 1.3  # 30% cost increase due to tariffs
            config['regions']['East_Asia']['infrastructure_quality'] *= 0.9  # Customs and border delays
            config['regions']['East_Asia']['disaster_probability'] *= 1.4  # Higher disruption risk
            
            # Global ripple effects
            for region in config['regions'].values():
                if region != config['regions']['East_Asia']:
                    region['labor_cost'] *= 1.1  # 10% global cost increase
                    region['disaster_probability'] *= 1.2  # Increased global supply chain uncertainty
                    region['infrastructure_quality'] *= 0.95  # Minor logistics slowdown
            
            # Adjust resilience strategy costs due to market complexity
            config['resilience_strategies']['supplier_diversification']['cost_impact'] *= 1.2
            config['resilience_strategies']['transportation_flexibility']['cost_impact'] *= 1.15
        
        else:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        return config
    
    @staticmethod
    def get_editable_parameters() -> Dict[str, Dict[str, Any]]:
        """
        Get list of parameters that can be edited in the UI
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of parameter metadata
        """
        return {
            'simulation': {
                'monte_carlo_iterations': {
                    'type': 'int',
                    'min': 10,
                    'max': 10000,
                    'default': 100,
                    'description': 'Number of simulation iterations'
                },
                'simulation_length_weeks': {
                    'type': 'int',
                    'min': 1,
                    'max': 520,
                    'default': 52,
                    'description': 'Length of each simulation run in weeks'
                },
                'seed': {
                    'type': 'int',
                    'min': 0,
                    'max': 999999,
                    'default': 42,
                    'description': 'Random seed for reproducibility'
                }
            },
            'regions': {
                'disaster_probability': {
                    'type': 'float',
                    'min': 0.0,
                    'max': 1.0,
                    'default': 0.1,
                    'description': 'Probability of disasters in each region'
                },
                'infrastructure_quality': {
                    'type': 'float',
                    'min': 0.0,
                    'max': 1.0,
                    'default': 0.9,
                    'description': 'Quality of infrastructure (0-1)'
                },
                'production_capacity': {
                    'type': 'float',
                    'min': 0.0,
                    'max': 1.0,
                    'default': 0.7,
                    'description': 'Production capacity utilization (0-1)'
                }
            },
            'agent': {
                'decision_making_speed': {
                    'type': 'float',
                    'min': 0.0,
                    'max': 1.0,
                    'default': 0.8,
                    'description': 'Agent decision-making speed (0-1)'
                },
                'risk_tolerance': {
                    'type': 'float',
                    'min': 0.0,
                    'max': 1.0,
                    'default': 0.6,
                    'description': 'Agent risk tolerance (0-1)'
                }
            }
        }
    
    @staticmethod
    def create_custom_config(base_scenario: str, parameter_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom configuration by modifying a base scenario
        
        Args:
            base_scenario: Name of the base scenario to modify
            parameter_updates: Dictionary of parameter updates
            
        Returns:
            Dict[str, Any]: Updated configuration dictionary
        """
        # First get the scenario-specific configuration
        config = ScenarioManager.get_scenario_config(base_scenario)
        
        # Update simulation parameters
        if 'simulation' in parameter_updates:
            config['simulation'].update(parameter_updates['simulation'])
        
        # Update regional parameters while preserving scenario-specific modifications
        if 'regions' in parameter_updates:
            # Store the scenario's modification factors
            modification_factors = {}
            if base_scenario != 'baseline':
                base_config = deepcopy(DEFAULT_CONFIG)
                for region_name, region in config['regions'].items():
                    modification_factors[region_name] = {
                        param: region[param] / base_config['regions'][region_name][param]
                        for param in region.keys()
                        if param in base_config['regions'][region_name]
                    }
            
            # Apply custom parameters while preserving scenario modifications
            for region_name, region_params in parameter_updates['regions'].items():
                if region_name in config['regions']:
                    for param, value in region_params.items():
                        if param in config['regions'][region_name]:
                            if base_scenario != 'baseline' and param in modification_factors.get(region_name, {}):
                                # Apply both the custom value and the scenario's modification factor
                                config['regions'][region_name][param] = value * modification_factors[region_name][param]
                            else:
                                config['regions'][region_name][param] = value
        
        # Update agent parameters
        if 'agent' in parameter_updates:
            for role in ['coo', 'regional_manager', 'supplier']:
                if role in config:
                    config[role].update(parameter_updates['agent'])
        
        return config
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate a configuration dictionary
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid
        """
        try:
            # Check required sections
            required_sections = ['simulation', 'regions', 'coo', 'regional_manager', 'supplier']
            for section in required_sections:
                if section not in config:
                    return False
            
            # Check simulation parameters
            sim_params = config['simulation']
            if not all(isinstance(sim_params.get(p), int) for p in ['monte_carlo_iterations', 'simulation_length_weeks', 'seed']):
                return False
            
            # Check regional parameters
            for region in config['regions'].values():
                if not all(isinstance(region.get(p), (int, float)) for p in ['disaster_probability', 'infrastructure_quality']):
                    return False
            
            return True
            
        except Exception:
            return False 