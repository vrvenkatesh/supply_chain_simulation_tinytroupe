import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import json
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any, Union

from monte_carlo_runner import (
    MonteCarloSimulation,
    plot_scenario_comparisons,
    plot_strategy_effectiveness,
    plot_disruption_impact_analysis,
    create_styled_stats_df
)
from scenario_manager import ScenarioManager

def run_multiple_scenarios(scenarios: List[str], use_custom_scenario: bool, parameter_updates: Dict = None):
    """Run multiple scenarios concurrently and compare results"""
    
    # Initialize progress tracking
    progress_container = st.empty()
    progress_text = st.empty()
    scenario_progress = {scenario: 0 for scenario in scenarios}
    total_scenarios = len(scenarios)
    
    def update_progress(scenario: str, current: int, total: int):
        """Update progress for a specific scenario"""
        scenario_progress[scenario] = current / total
        total_progress = sum(scenario_progress.values()) / total_scenarios
        progress_container.progress(total_progress)
        progress_text.text(f"Running {scenario}: {current}/{total} iterations")
    
    try:
        all_results = []
        all_stats = {}
        all_figures = {}
        
        # Run each scenario
        for scenario in scenarios:
            st.markdown(f"**Running {scenario.replace('_', ' ').title()} Scenario**")
            
            # Get the appropriate configuration
            if scenario == 'custom':
                if not parameter_updates:
                    st.error("Custom scenario selected but no parameters provided")
                    return
                config = ScenarioManager.create_custom_config('baseline', parameter_updates)  # Use baseline as the base scenario
                st.info("Using custom parameters for simulation")
            else:
                config = ScenarioManager.get_scenario_config(scenario)
            
            # Initialize and run simulation
            simulation = MonteCarloSimulation(config, scenario)
            results_df = simulation.run(
                progress_callback=lambda current, total: update_progress(scenario, current, total)
            )
            
            # Get statistics and figures
            stats, figures = simulation.analyze_results()
            
            all_results.append(results_df)
            all_stats[scenario] = stats
            all_figures[scenario] = figures
        
        # Combine results for comparison
        combined_results = pd.concat(all_results, ignore_index=True)
        
        # Display comparative results
        st.success("All simulations completed successfully!")
        
        # Comparative Statistics
        st.header("Comparative Results")
        
        # Create and display styled statistics table
        st.subheader("Summary Statistics by Scenario")
        st.markdown("*Note: Values are shown first, followed by percentage changes from baseline.*")
        
        values_df, pct_change_df = create_styled_stats_df(all_stats)
        
        # Display values
        st.markdown("**Actual Values:**")
        st.dataframe(
            values_df,
            use_container_width=True,
            hide_index=False
        )
        
        # Display percentage changes
        if not pct_change_df.empty:
            st.markdown("**Percentage Changes from Baseline:**")
            st.dataframe(
                pct_change_df.round(1).applymap(lambda x: f"{x:+.1f}%" if x != 0 else "0.0%"),
                use_container_width=True,
                hide_index=False
            )
        
        # Comparative Visualizations
        st.subheader("Scenario Comparisons")
        
        # Generate timestamp for saving files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create comparative plots
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Core Metrics Comparison**")
            fig_metrics = plt.figure(figsize=(10, 6))
            metrics = ['avg_resilience', 'avg_service_level', 'avg_cost_impact']
            df_melted = pd.melt(combined_results, id_vars=['scenario'], value_vars=metrics)
            sns.boxplot(data=df_melted, x='variable', y='value', hue='scenario')
            plt.title('Core Metrics by Scenario')
            plt.xticks(rotation=45)
            st.pyplot(fig_metrics)
            plt.close()
            
            st.markdown("**Risk and Recovery Analysis**")
            fig_risk = plt.figure(figsize=(10, 6))
            metrics = ['avg_risk_exposure', 'avg_recovery_time']
            df_melted = pd.melt(combined_results, id_vars=['scenario'], value_vars=metrics)
            sns.boxplot(data=df_melted, x='variable', y='value', hue='scenario')
            plt.title('Risk and Recovery by Scenario')
            plt.xticks(rotation=45)
            st.pyplot(fig_risk)
            plt.close()
        
        with col2:
            st.markdown("**Performance Metrics**")
            fig_perf = plt.figure(figsize=(10, 6))
            metrics = ['transportation_efficiency', 'inventory_health']
            df_melted = pd.melt(combined_results, id_vars=['scenario'], value_vars=metrics)
            sns.boxplot(data=df_melted, x='variable', y='value', hue='scenario')
            plt.title('Performance Metrics by Scenario')
            plt.xticks(rotation=45)
            st.pyplot(fig_perf)
            plt.close()
            
            st.markdown("**Cost vs. Resilience Trade-off**")
            fig_trade = plt.figure(figsize=(10, 6))
            for scenario in scenarios:
                scenario_data = combined_results[combined_results['scenario'] == scenario]
                plt.scatter(scenario_data['avg_cost_impact'], 
                          scenario_data['avg_resilience'],
                          label=scenario, alpha=0.6)
            plt.title('Cost vs. Resilience Trade-off')
            plt.xlabel('Cost Impact')
            plt.ylabel('Resilience Score')
            plt.legend()
            st.pyplot(fig_trade)
            plt.close()
        
        # Save comparative plots
        plt.figure(figsize=(15, 10))
        plot_scenario_comparisons(combined_results, timestamp)
        plot_strategy_effectiveness(combined_results, timestamp)
        plot_disruption_impact_analysis(combined_results, timestamp)
        
        # Raw Results (expandable sections for each scenario)
        st.header("Detailed Results")
        for scenario in scenarios:
            scenario_data = combined_results[combined_results['scenario'] == scenario]
            with st.expander(f"Raw Data - {scenario.replace('_', ' ').title()}", expanded=False):
                st.dataframe(scenario_data)
        
        # Download buttons
        st.header("Download Results")
        col1, col2, col3 = st.columns(3)
        
        # Save results to files
        results_csv = f"simulation_results/{timestamp}_comparative_results.csv"
        config_json = f"simulation_results/{timestamp}_simulation_configs.json"
        
        # Save files
        combined_results.to_csv(results_csv, index=False)
        
        # Save all configurations
        configs = {
            scenario: (ScenarioManager.create_custom_config('baseline', parameter_updates)
                     if scenario == 'custom' 
                     else ScenarioManager.get_scenario_config(scenario))
            for scenario in scenarios
        }
        with open(config_json, 'w') as f:
            json.dump(configs, f, indent=2)
        
        with col1:
            with open(results_csv, 'rb') as f:
                st.download_button(
                    "Download Combined Results CSV",
                    f,
                    results_csv.split('/')[-1],
                    "text/csv"
                )
        with col2:
            with open(config_json, 'rb') as f:
                st.download_button(
                    "Download All Configurations JSON",
                    f,
                    config_json.split('/')[-1],
                    "application/json"
                )
        with col3:
            st.markdown("""
            **Results Location**  
            All simulation results are saved in the `simulation_results` directory
            """)
    
    except Exception as e:
        st.error(f"Error running simulations: {str(e)}")
        raise e

# Set up the Streamlit page
st.set_page_config(page_title="Supply Chain Resilience Simulation", layout="wide")

st.title("Supply Chain Resilience Simulation")
st.markdown("""
This application allows you to run supply chain resilience simulations with different scenarios
and parameters. You can:
- Select multiple scenarios to compare with baseline
- Create a custom scenario with your own parameters
- Monitor simulation progress
- View comparative analysis and results
""")

# Sidebar for configuration
st.sidebar.title("Simulation Configuration")

# Scenario Selection
available_scenarios = ScenarioManager.get_available_scenarios()
disruption_scenarios = {k: v for k, v in available_scenarios.items() if k not in ['baseline', 'custom']}

st.sidebar.markdown("### Scenario Selection")
st.sidebar.markdown("**Baseline scenario is always included**")

# Store selected scenarios in session state
if 'selected_scenarios' not in st.session_state:
    st.session_state.selected_scenarios = []

# Checkboxes for disruption scenarios
selected_disruptions = []
for scenario in disruption_scenarios.keys():
    if st.sidebar.checkbox(
        scenario.replace('_', ' ').title(),
        help=disruption_scenarios[scenario],
        key=f"scenario_{scenario}"
    ):
        selected_disruptions.append(scenario)

# Custom Scenario Configuration
st.sidebar.markdown("### Custom Scenario")
use_custom_scenario = st.sidebar.checkbox("Add Custom Scenario", help="Create a scenario with custom parameters")

parameter_updates = {}
if use_custom_scenario:
    editable_params = ScenarioManager.get_editable_parameters()
    
    # Simulation Parameters
    st.sidebar.markdown("**Simulation Parameters**")
    parameter_updates['simulation'] = {}
    for param, meta in editable_params['simulation'].items():
        value = st.sidebar.number_input(
            meta['description'],
            min_value=meta['min'],
            max_value=meta['max'],
            value=meta['default'],
            key=f"sim_{param}"
        )
        parameter_updates['simulation'][param] = value
    
    # Regional Parameters
    st.sidebar.markdown("**Regional Parameters**")
    parameter_updates['regions'] = {}
    
    # Create tabs for each region
    regions = ['North_America', 'Europe', 'East_Asia']
    region_tabs = st.sidebar.tabs([region.replace('_', ' ') for region in regions])
    
    for region, tab in zip(regions, region_tabs):
        with tab:
            parameter_updates['regions'][region] = {}
            for param, meta in editable_params['regions'].items():
                value = st.number_input(
                    f"{meta['description']} ({region.replace('_', ' ')})",
                    min_value=float(meta['min']),
                    max_value=float(meta['max']),
                    value=float(meta['default']),
                    key=f"region_{region}_{param}"
                )
                parameter_updates['regions'][region][param] = value
    
    # Agent Parameters
    st.sidebar.markdown("**Agent Parameters**")
    parameter_updates['agent'] = {}
    for param, meta in editable_params['agent'].items():
        value = st.sidebar.number_input(
            meta['description'],
            min_value=float(meta['min']),
            max_value=float(meta['max']),
            value=float(meta['default']),
            key=f"agent_{param}"
        )
        parameter_updates['agent'][param] = value

# Always include baseline
selected_scenarios = ['baseline'] + selected_disruptions
if use_custom_scenario:
    selected_scenarios.append('custom')

# Run Simulation Button
if st.sidebar.button("Run Selected Scenarios"):
    run_multiple_scenarios(selected_scenarios, use_custom_scenario, parameter_updates if use_custom_scenario else None) 