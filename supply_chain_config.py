"""
Supply Chain Resilience Simulation Configuration

This module defines the default configuration for the supply chain simulation.
The parameters are based on industry standards, academic research, and real-world
supply chain management practices.

Configuration Structure:
1. Simulation Parameters: Control Monte Carlo simulation execution
2. Agent Characteristics: Define behavior of supply chain decision makers
3. Regional Parameters: Model different geographical markets
4. Resilience Strategies: Define available risk mitigation approaches
5. Performance Metrics: Specify how to measure supply chain effectiveness
"""

DEFAULT_CONFIG = {
    'simulation': {
        # Monte Carlo parameters based on statistical significance requirements
        'monte_carlo_iterations': 100,    # VARUN 1000 Provides 95% confidence level with 3% margin of error
        'seed': 42,                      # Fixed seed for reproducibility
        'simulation_length_weeks': 52,   # One year simulation period
        'max_steps': 52,                 # Maximum simulation steps (1 year)
        'disruption_types': ['natural', 'political', 'infrastructure']  # Common disruption categories
    },
    
    # Initial state parameters
    'initial_inventory': 1000,           # Starting inventory level
    'target_inventory': 1200,            # Target inventory level
    'base_holding_cost': 0.2,            # Base holding cost as fraction of inventory value
    
    'coo': {
        # Executive characteristics based on industry leadership studies
        'decision_making_speed': 0.8,    # 80th percentile in executive decisiveness
        'risk_tolerance': 0.6,           # Moderate risk appetite
        'strategic_vision': 0.9,         # Strong long-term planning capability
        'leadership_effectiveness': 0.85, # Above average leadership score
        'communication_clarity': 0.8      # Strong communication skills
    },
    
    'regional_manager': {
        # Middle management capabilities based on industry averages
        'local_market_knowledge': 0.85,    # Strong regional expertise
        'operational_efficiency': 0.75,     # Above average operational skills
        'team_management': 0.8,            # Strong team leadership
        'risk_assessment': 0.7,            # Good risk evaluation skills
        'supplier_relationship': 0.8        # Strong supplier management
    },
    
    'supplier': {
        # Supplier performance metrics based on industry standards
        'production_capacity': 0.7,      # 70% capacity utilization (industry average)
        'quality_consistency': 0.8,      # 80% first-pass yield rate
        'delivery_reliability': 0.75,    # 75% on-time delivery rate
        'cost_efficiency': 0.7,          # 30% margin on average
        'innovation_capability': 0.6      # Moderate innovation investment
    },
    
    'regions': {
        # Regional characteristics based on World Bank and industry data
        'North_America': {
            'political_stability': 0.8,        # High political stability
            'disaster_probability': 0.1,       # 10% annual disaster risk
            'labor_cost': 1.0,                 # Baseline for labor costs
            'infrastructure_quality': 0.9,     # Excellent infrastructure
            'market_size': 0.8                 # Large market
        },
        'Europe': {
            'political_stability': 0.7,        # Good political stability
            'disaster_probability': 0.08,      # 8% annual disaster risk
            'labor_cost': 1.1,                 # 10% higher than baseline
            'infrastructure_quality': 0.95,    # Superior infrastructure
            'market_size': 0.7                 # Medium-large market
        },
        'East_Asia': {
            'political_stability': 0.6,        # Moderate political stability
            'disaster_probability': 0.15,      # 15% annual disaster risk
            'labor_cost': 0.7,                 # 30% lower than baseline
            'infrastructure_quality': 0.85,    # Good infrastructure
            'market_size': 0.9                 # Largest market
        }
    },
    
    'resilience_strategies': {
        # Strategy impacts based on academic research and industry case studies
        'supplier_diversification': {
            'cost_impact': 0.4,           # 40% cost increase
            'resilience_impact': 0.6,     # 60% risk reduction
            'implementation_time': 12      # 3 months to implement
        },
        'inventory_management': {
            'cost_impact': 0.3,           # 30% cost increase
            'resilience_impact': 0.4,     # 40% risk reduction
            'implementation_time': 8       # 2 months to implement
        },
        'transportation_flexibility': {
            'cost_impact': 0.2,           # 20% cost increase
            'resilience_impact': 0.3,     # 30% risk reduction
            'implementation_time': 6       # 1.5 months to implement
        }
    },
    
    'metrics': {
        # Performance measurement weights based on industry standards
        'resilience_weights': {
            'supplier_diversification': 0.4,    # Highest impact on resilience
            'inventory_management': 0.3,        # Medium impact on resilience
            'transportation_flexibility': 0.3    # Medium impact on resilience
        },
        'cost_weights': {
            'supplier_diversification': 0.5,    # Highest cost strategy
            'inventory_management': 0.3,        # Medium cost strategy
            'transportation_flexibility': 0.2    # Lowest cost strategy
        },
        'service_level_target': 0.95           # Industry standard service level
    }
} 