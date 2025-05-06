# Supply Chain Resilience Simulation

This simulation uses Monte Carlo methods to analyze and optimize supply chain resilience for Tekron Industries, a global manufacturer of industrial automation equipment.

## Features

- Multi-agent simulation with COO and Regional Manager agents
- Geographic-specific disruption modeling
- Cost-resilience trade-off analysis
- Service level impact assessment
- Visualization of key metrics
- Comprehensive test suite

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the simulation:
```bash
python supply_chain_simulation.py
```

The simulation will:
1. Run 1000 iterations of the supply chain scenario
2. Generate visualizations in `supply_chain_simulation_results.png`
3. Print summary metrics including:
   - Average Resilience Score
   - Average Cost Impact
   - Average Service Level
   - Average Number of Disruptions

## Running Tests

Run the test suite:
```bash
python -m unittest tests/test_supply_chain_simulation.py
```

The test suite covers:
- Environment initialization and behavior
- Agent creation and decision-making
- Simulation execution and metrics calculation
- Edge cases and validation checks

## Simulation Parameters

The simulation includes:
- 52-week simulation period
- 3 geographic regions (North America, Europe, East Asia)
- Multiple disruption types (natural, political, infrastructure)
- Configurable agent decision-making strategies

## Output Interpretation

The visualization includes:
1. Resilience vs Cost Trade-off scatter plot
2. Service Level distribution
3. Disruption count distribution

These visualizations help validate the hypotheses about supply chain resilience and cost efficiency trade-offs.

## Core Metric Calculations

The simulation tracks several key performance indicators (KPIs) that measure supply chain resilience and performance. Below are the detailed calculations for each core metric:

### 1. Resilience Score (0-1 scale)
The overall resilience score combines three components:
```
Resilience Score = 0.4 * Recovery_Capability + 0.3 * Risk_Mitigation + 0.3 * Operational_Stability

Where:
- Recovery_Capability = 1 - (Avg_Recovery_Time / Max_Recovery_Time)
- Risk_Mitigation = 1 - Risk_Exposure
- Operational_Stability = Mean(Service_Level, Transportation_Efficiency, Inventory_Health)
```

### 2. Service Level (0-1 scale)
Measures order fulfillment performance:
```
Service_Level = Base_Service_Level * (1 - Disruption_Impact) * Regional_Performance * Inventory_Health

Where:
- Base_Service_Level = 0.98 (industry standard target)
- Disruption_Impact = Sum(Disruption_Severities) / 20
- Regional_Performance = Average performance across all regions
- Inventory_Health = Current inventory level relative to target
```

### 3. Cost Impact (Normalized to baseline)
Quantifies financial implications:
```
Cost_Impact = Strategy_Cost + Disruption_Cost

Where:
Strategy_Cost = Sum(
    Supplier_Diversification * 0.5 +
    Inventory_Management * 0.3 +
    Transportation_Flexibility * 0.2
)

Disruption_Cost = Sum(Disruption_Severities * 0.5)
```

### 4. Recovery Time (Weeks)
Estimates time to return to normal operations:
```
Recovery_Time = max(1, Base_Recovery * (1 - Strategy_Effectiveness))

Where:
- Base_Recovery = Max_Disruption_Severity * 10
- Strategy_Effectiveness = Sum(
    Supplier_Diversification * 0.3 +
    Inventory_Management * 0.4 +
    Transportation_Flexibility * 0.3
)
```

### 5. Risk Exposure (0-1 scale)
Assesses current threat level:
```
Risk_Exposure = min(1.0, Base_Risk + Current_Disruption_Impact + Economic_Risk)

Where:
- Base_Risk = Average(Region_Disaster_Probability * (1 - Infrastructure_Quality))
- Current_Disruption_Impact = Sum(Active_Disruption_Severities) / 10
- Economic_Risk = Average(abs(GDP_Growth_Rate)) across regions
```

### 6. Return on Investment (ROI)
Measures effectiveness of resilience investments:
```
ROI = (Resilience_Benefit - Investment_Cost) / Investment_Cost

Where:
- Resilience_Benefit = Potential_Loss - Actual_Loss
- Potential_Loss = Sum(Disruption_Severities)
- Actual_Loss = Potential_Loss * (1 - Resilience_Score)
```

### 7. Transportation Efficiency (0-1 scale)
Evaluates logistics network performance:
```
Transportation_Efficiency = max(0, min(1, Base_Efficiency - (Disruption_Impact * (1 - Flexibility_Factor))))

Where:
- Base_Efficiency = Average(Infrastructure_Quality) across regions
- Disruption_Impact = Sum(Disruption_Severities) / Number_of_Regions
- Flexibility_Factor = Transportation_Strategy_Effectiveness
```

### 8. Inventory Health (0-1 scale)
Assesses inventory management effectiveness:
```
Inventory_Health = 0.4 * Stock_Score + 0.3 * Holding_Cost_Score + 0.3 * Matching_Score

Where:
- Stock_Score = Current_Service_Level / Target_Service_Level
- Holding_Cost_Score = 1 - (Cost_Impact * 0.3)
- Matching_Score = 1 - Demand_Volatility
```

### Regional Performance (0-1 scale)
Evaluates region-specific effectiveness:
```
Regional_Performance = 0.4 * Supplier_Score + 0.3 * Infrastructure_Score + 0.3 * Stability_Score

Where:
- Supplier_Score = Base_Performance - Disruption_Impact + Economic_Impact
- Infrastructure_Score = Region's infrastructure quality
- Stability_Score = Region's political stability
```

These metrics are calculated and updated at each simulation step (weekly) and aggregated across all Monte Carlo iterations to provide robust statistical insights into supply chain resilience.

## Interpretation Guidelines

The simulation results should be interpreted considering:

1. **Metric Correlations**: High resilience scores often correlate with higher costs, representing the fundamental trade-off in supply chain management.

2. **Regional Variations**: Performance metrics vary by region due to different:
   - Infrastructure quality
   - Political stability
   - Labor costs
   - Market sizes

3. **Time Dynamics**: Metrics evolve over the simulation period, reflecting:
   - Learning and adaptation
   - Cumulative impact of disruptions
   - Effectiveness of resilience strategies

4. **Statistical Significance**: Results are based on 1000 Monte Carlo iterations, providing:
   - 95% confidence level
   - 3% margin of error
   - Robust statistical distributions 