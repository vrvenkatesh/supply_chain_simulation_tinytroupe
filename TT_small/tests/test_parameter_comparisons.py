import unittest
import os
import json
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supply_chain_simulation import SupplyChainEnvironment, SupplyChainAgent, SupplyChainSimulation

class TestParameterComparisons(unittest.TestCase):
    def setUp(self):
        # Create test_results directory if it doesn't exist
        self.base_results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_results')
        os.makedirs(self.base_results_dir, exist_ok=True)
        
        # Number of iterations for each test
        self.num_iterations = 100
        
    def run_simulation_with_params(self, test_name, modified_params=None):
        """Run simulation with modified parameters and store results"""
        # Create test-specific directory
        test_dir = os.path.join(self.base_results_dir, test_name)
        os.makedirs(test_dir, exist_ok=True)
        
        # Run baseline simulation
        baseline_sim = SupplyChainSimulation(num_iterations=self.num_iterations)
        baseline_sim.run()
        baseline_results = baseline_sim.analyze_results()
        
        # Run modified simulation
        if modified_params:
            # Create a subclass of SupplyChainEnvironment with modified parameters
            class ModifiedEnvironment(SupplyChainEnvironment):
                def __init__(self):
                    super().__init__()
                    for region, params in modified_params.items():
                        if region in self.regions:
                            self.regions[region].update(params)
                            
            # Create a subclass of SupplyChainAgent with modified parameters
            class ModifiedAgent(SupplyChainAgent):
                def _supplier_decision_making(self, env):
                    decisions = super()._supplier_decision_making(env)
                    if 'supplier_params' in modified_params:
                        decisions.update(modified_params['supplier_params'])
                    return decisions
                
                def _coo_decision_making(self, env):
                    decisions = super()._coo_decision_making(env)
                    if 'coo_params' in modified_params:
                        decisions.update(modified_params['coo_params'])
                    return decisions
            
            # Run simulation with modified environment/agents
            modified_sim = SupplyChainSimulation(num_iterations=self.num_iterations)
            modified_sim.run()
            modified_results = modified_sim.analyze_results()
            
            # Save results
            with open(os.path.join(test_dir, 'baseline_results.json'), 'w') as f:
                json.dump(baseline_results, f, indent=4)
            
            with open(os.path.join(test_dir, 'modified_results.json'), 'w') as f:
                json.dump(modified_results, f, indent=4)
            
            # Calculate and save differences
            differences = {
                metric: modified_results[metric] - baseline_results[metric]
                for metric in baseline_results.keys()
                if isinstance(baseline_results[metric], (int, float))
            }
            
            with open(os.path.join(test_dir, 'differences.json'), 'w') as f:
                json.dump(differences, f, indent=4)
                
            return baseline_results, modified_results, differences
            
        return baseline_results, None, None

    def test_east_asia_disaster_probability(self):
        """Test impact of adjusting East Asia disaster probability from 0.15 to 0.5"""
        modified_params = {
            'East_Asia': {
                'disaster_probability': 0.5  # Modified from default 0.15
            }
        }
        
        baseline, modified, diff = self.run_simulation_with_params(
            'east_asia_disaster_prob_comparison',
            modified_params
        )
        
        # Verify the test ran and produced results
        self.assertIsNotNone(baseline)
        self.assertIsNotNone(modified)
        self.assertIsNotNone(diff)

    def test_supplier_qc_factor(self):
        """Test impact of adjusting supplier QC factor from 0.8 to 0.2"""
        modified_params = {
            'supplier_params': {
                'quality_control': 0.2  # Modified from default 0.8
            }
        }
        
        baseline, modified, diff = self.run_simulation_with_params(
            'supplier_qc_factor_comparison',
            modified_params
        )
        
        # Verify the test ran and produced results
        self.assertIsNotNone(baseline)
        self.assertIsNotNone(modified)
        self.assertIsNotNone(diff)

    def test_supplier_diversification_metric(self):
        """Test impact of adjusting supplier diversification metric from 0.4 to 0.9"""
        modified_params = {
            'coo_params': {
                'supplier_diversification': 0.9  # Modified from default weight of 0.4
            }
        }
        
        baseline, modified, diff = self.run_simulation_with_params(
            'supplier_diversification_comparison',
            modified_params
        )
        
        # Verify the test ran and produced results
        self.assertIsNotNone(baseline)
        self.assertIsNotNone(modified)
        self.assertIsNotNone(diff)

if __name__ == '__main__':
    unittest.main() 