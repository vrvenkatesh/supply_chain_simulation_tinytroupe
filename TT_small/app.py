"""
Supply Chain Resilience Simulation - Streamlit Frontend

This module provides a web-based interface for running and analyzing supply chain
resilience simulations using Streamlit.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Tuple
import json
import os
from datetime import datetime
import seaborn as sns

from monte_carlo_runner import MonteCarloSimulation, plot_scenario_comparisons, plot_strategy_effectiveness, plot_disruption_impact_analysis
from scenario_manager import ScenarioManager
from supply_chain_config import DEFAULT_CONFIG

# Ensure simulation_results directory exists
os.makedirs('simulation_results', exist_ok=True)

def create_styled_stats_df(all_stats: Dict[str, Dict[str, float]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create two DataFrames - one for values and one for percentage changes"""
    # Convert stats to DataFrame and round to 3 decimal places
    df = pd.DataFrame(all_stats).T.round(3)
    
    if 'baseline' in df.index:
        baseline_values = df.loc['baseline']
        
        # Calculate percentage changes
        pct_change = df.copy()
        for col in df.columns:
            pct_change[col] = ((df[col] - baseline_values[col]) / baseline_values[col] * 100).round(1)
        
        # Keep only non-baseline rows for percentage changes
        pct_change = pct_change.drop('baseline')
        
        return df, pct_change
    
    return df, pd.DataFrame()

def main():
    st.set_page_config(page_title="Supply Chain Resilience Simulation", layout="wide")
    
    st.title("Supply Chain Resilience Simulation")
    st.markdown("""
    This application allows you to run supply chain resilience simulations with different scenarios
    and parameters. You can:
    - Select multiple scenarios to compare with baseline
    - Adjust simulation parameters
    - Monitor simulation progress
    - View comparative analysis and results
    """)
    
    # Sidebar for configuration
    st.sidebar.title("Simulation Configuration")
    
    # Scenario Selection
    available_scenarios = ScenarioManager.get_available_scenarios()
    disruption_scenarios = {k: v for k, v in available_scenarios.items() if k != 'baseline'}
    
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
    
    # Always include baseline
    selected_scenarios = ['baseline'] + selected_disruptions
    
    # Parameter Configuration
    st.sidebar.subheader("Parameters")
    use_custom_params = st.sidebar.checkbox("Customize Parameters")
    
    if use_custom_params:
        parameter_updates = {}
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
        for param, meta in editable_params['regions'].items():
            value = st.sidebar.number_input(
                meta['description'],
                min_value=float(meta['min']),
                max_value=float(meta['max']),
                value=float(meta['default']),
                key=f"region_{param}"
            )
            parameter_updates['regions'][param] = value
        
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
    
    # Run Simulation Button
    if st.sidebar.button("Run Selected Scenarios"):
        run_multiple_scenarios(selected_scenarios, use_custom_params, parameter_updates if use_custom_params else None)

def run_multiple_scenarios(scenarios: List[str], use_custom_params: bool, parameter_updates: Dict = None):
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
            if use_custom_params:
                config = ScenarioManager.create_custom_config(scenario, parameter_updates)
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
        st.markdown("""
        *Note: Values are shown first, followed by percentage changes from baseline.  
        For percentage changes: Green indicates improvement, Red indicates degradation.  
        For cost and risk metrics, lower values are better.*
        """)
        
        values_df, pct_change_df = create_styled_stats_df(all_stats)
        
        # Display values
        st.markdown("**Actual Values:**")
        st.dataframe(
            values_df,
            use_container_width=True,
            hide_index=False
        )
        
        # Display percentage changes with styling
        if not pct_change_df.empty:
            st.markdown("**Percentage Changes from Baseline:**")
            
            # Create the styling
            def style_pct_changes(val, col_name):
                is_cost_or_risk = 'cost' in col_name.lower() or 'risk' in col_name.lower()
                color = ''
                if is_cost_or_risk:
                    color = 'green' if val < 0 else 'red' if val > 0 else 'black'
                else:
                    color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                return f"{val:+.1f}%" if val != 0 else "0.0%"
            
            # Format the percentage changes
            formatted_pct = pd.DataFrame(index=pct_change_df.index, columns=pct_change_df.columns)
            for col in pct_change_df.columns:
                formatted_pct[col] = pct_change_df[col].apply(lambda x: style_pct_changes(x, col))
            
            st.dataframe(
                formatted_pct,
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
            scenario: ScenarioManager.get_scenario_config(scenario)
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

if __name__ == "__main__":
    main() 