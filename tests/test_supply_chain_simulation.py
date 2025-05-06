import unittest
import numpy as np
from supply_chain_simulation import (
    SupplyChainEnvironment,
    SupplyChainAgent,
    SupplyChainSimulation
)

class TestSupplyChainEnvironment(unittest.TestCase):
    def setUp(self):
        self.env = SupplyChainEnvironment()
        
    def test_environment_initialization(self):
        """Test if environment is properly initialized"""
        self.assertEqual(self.env.current_time, 0)
        self.assertEqual(len(self.env.disruption_events), 0)
        self.assertIn('North_America', self.env.regions)
        self.assertIn('Europe', self.env.regions)
        self.assertIn('East_Asia', self.env.regions)
        
    def test_step_advances_time(self):
        """Test if step method advances time correctly"""
        initial_time = self.env.current_time
        self.env.step()
        self.assertEqual(self.env.current_time, initial_time + 1)
        
    def test_disruption_generation(self):
        """Test if disruptions are generated with valid parameters"""
        # Run multiple steps to ensure disruptions occur
        for _ in range(100):
            self.env.step()
            
        if self.env.disruption_events:  # If any disruptions occurred
            disruption = self.env.disruption_events[0]
            self.assertIn('time', disruption)
            self.assertIn('region', disruption)
            self.assertIn('type', disruption)
            self.assertIn('severity', disruption)
            self.assertIn(disruption['type'], ['natural', 'political', 'infrastructure'])
            self.assertTrue(0 <= disruption['severity'] <= 1)

class TestSupplyChainAgent(unittest.TestCase):
    def setUp(self):
        self.env = SupplyChainEnvironment()
        self.coo = SupplyChainAgent(name="Elena", role="COO")
        self.regional_manager = SupplyChainAgent(
            name="Manager_NA",
            role="Regional_Manager",
            region="North_America"
        )
        
    def test_agent_initialization(self):
        """Test if agents are properly initialized"""
        self.assertEqual(self.coo.name, "Elena")
        self.assertEqual(self.coo.role, "COO")
        self.assertIsNone(self.coo.region)
        
        self.assertEqual(self.regional_manager.name, "Manager_NA")
        self.assertEqual(self.regional_manager.role, "Regional_Manager")
        self.assertEqual(self.regional_manager.region, "North_America")
        
    def test_coo_decision_making(self):
        """Test if COO makes valid decisions"""
        decisions = self.coo.act(self.env)
        
        self.assertIn('supplier_diversification', decisions)
        self.assertIn('inventory_adjustment', decisions)
        self.assertIn('transportation_mode_shift', decisions)
        
        for value in decisions.values():
            self.assertTrue(0 <= value <= 1)

class TestSupplyChainSimulation(unittest.TestCase):
    def setUp(self):
        self.sim = SupplyChainSimulation(num_iterations=10)  # Reduced iterations for testing
        
    def test_simulation_initialization(self):
        """Test if simulation is properly initialized"""
        self.assertEqual(self.sim.num_iterations, 10)
        self.assertEqual(len(self.sim.results), 0)
        
    def test_single_iteration(self):
        """Test if a single iteration produces valid results"""
        env = SupplyChainEnvironment()
        elena = SupplyChainAgent(name="Elena", role="COO")
        regional_managers = [
            SupplyChainAgent(name=f"Manager_{region}", role="Regional_Manager", region=region)
            for region in env.regions.keys()
        ]
        
        results = self.sim._run_iteration(env, elena, regional_managers)
        
        self.assertIn('avg_resilience', results)
        self.assertIn('avg_cost_impact', results)
        self.assertIn('avg_service_level', results)
        self.assertIn('disruption_count', results)
        
        self.assertTrue(0 <= results['avg_resilience'] <= 1)
        self.assertTrue(0 <= results['avg_cost_impact'] <= 1)
        self.assertTrue(0 <= results['avg_service_level'] <= 1)
        self.assertTrue(isinstance(results['disruption_count'], int))
        
    def test_full_simulation(self):
        """Test if full simulation runs without errors and produces valid results"""
        self.sim.run()
        results = self.sim.analyze_results()
        
        self.assertEqual(len(self.sim.results), 10)  # Check if all iterations completed
        self.assertIn('Average Resilience', results)
        self.assertIn('Average Cost Impact', results)
        self.assertIn('Average Service Level', results)
        self.assertIn('Average Disruptions', results)
        
        # Test if metrics are within valid ranges
        self.assertTrue(0 <= results['Average Resilience'] <= 1)
        self.assertTrue(0 <= results['Average Cost Impact'] <= 1)
        self.assertTrue(0 <= results['Average Service Level'] <= 1)
        self.assertTrue(results['Average Disruptions'] >= 0)

    def test_calculation_methods(self):
        """Test the metric calculation methods"""
        env = SupplyChainEnvironment()
        coo_decisions = {
            'supplier_diversification': 0.5,
            'inventory_adjustment': 0.4,
            'transportation_mode_shift': 0.3
        }
        manager_decisions = {}  # Empty for now as it's not used in current implementation
        
        resilience = self.sim._calculate_resilience(env, coo_decisions, manager_decisions)
        cost_impact = self.sim._calculate_cost_impact(coo_decisions, manager_decisions)
        service_level = self.sim._calculate_service_level(env, manager_decisions)
        
        self.assertTrue(0 <= resilience <= 1)
        self.assertTrue(0 <= cost_impact <= 1)
        self.assertTrue(0 <= service_level <= 1)

if __name__ == '__main__':
    unittest.main() 