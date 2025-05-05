"""
Supply Chain Resilience Simulation - Streamlit Frontend

This module provides a web-based interface for running and analyzing supply chain
resilience simulations using Streamlit.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any
import json
import os
from datetime import datetime

from monte_carlo_runner import MonteCarloSimulation
from scenario_manager import ScenarioManager
from supply_chain_config import DEFAULT_CONFIG

# Ensure simulation_results directory exists
os.makedirs('simulation_results', exist_ok=True)

def main():
    st.set_page_config(page_title="Supply Chain Resilience Simulation", layout="wide")
    
    st.title("Supply Chain Resilience Simulation")
    st.markdown("""
    This application allows you to run supply chain resilience simulations with different scenarios
    and parameters. You can:
    - Select predefined scenarios or create custom ones
    - Adjust simulation parameters
    - Monitor simulation progress
    - View and analyze results
    """)
    
    # Sidebar for configuration
    st.sidebar.title("Simulation Configuration")
    
    # Scenario Selection
    available_scenarios = ScenarioManager.get_available_scenarios()
    selected_scenario = st.sidebar.selectbox(
        "Select Scenario",
        list(available_scenarios.keys()),
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    st.sidebar.markdown(f"**Description:** {available_scenarios[selected_scenario]}")
    
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
        
        config = ScenarioManager.create_custom_config(selected_scenario, parameter_updates)
    else:
        config = ScenarioManager.get_scenario_config(selected_scenario)
    
    # Run Simulation Button
    if st.sidebar.button("Run Simulation"):
        run_simulation(config, selected_scenario)

def run_simulation(config: Dict[str, Any], scenario_name: str):
    """Run simulation with progress reporting and result visualization"""
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current: int, total: int):
        """Callback for updating progress bar"""
        progress = int(100 * current / total)
        progress_bar.progress(progress)
        status_text.text(f"Running iteration {current}/{total}")
    
    # Initialize and run simulation
    simulation = MonteCarloSimulation(config, scenario_name)
    
    try:
        # Run simulation with progress reporting
        results_df = simulation.run(progress_callback=update_progress)
        
        # Get statistics and figures
        stats, figures = simulation.analyze_results()
        
        # Display results
        st.success("Simulation completed successfully!")
        
        # Statistics
        st.header("Simulation Results")
        st.subheader("Summary Statistics")
        stats_df = pd.DataFrame([stats]).T
        stats_df.columns = ['Value']
        st.dataframe(stats_df)
        
        # Figures
        st.subheader("Visualizations")
        cols = st.columns(2)
        
        # Display figures in a grid
        for i, (name, fig) in enumerate(figures.items()):
            with cols[i % 2]:
                st.markdown(f"**{name.replace('_', ' ').title()}**")
                st.pyplot(fig)
        
        # Raw Data
        with st.expander("Raw Data", expanded=False):
            st.dataframe(results_df)
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        # Save results to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_csv = f"simulation_results/{timestamp}_simulation_results.csv"
        config_json = f"simulation_results/{timestamp}_simulation_config.json"
        
        # Save files
        results_df.to_csv(results_csv, index=False)
        with open(config_json, 'w') as f:
            json.dump(config, f, indent=2)
        
        with col1:
            with open(results_csv, 'rb') as f:
                st.download_button(
                    "Download Results CSV",
                    f,
                    results_csv.split('/')[-1],
                    "text/csv"
                )
        with col2:
            with open(config_json, 'rb') as f:
                st.download_button(
                    "Download Configuration JSON",
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
        st.error(f"Error running simulation: {str(e)}")
        raise e

if __name__ == "__main__":
    main() 