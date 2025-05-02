"""
Supply Chain Resilience Simulation - Agent Definitions

This module implements intelligent agents that represent key decision makers in the supply chain:
- Chief Operating Officer (COO): Global strategic decisions
- Regional Managers: Tactical regional operations
- Suppliers: Local operational decisions

Agent Architecture:
1. Mental Faculties:
   - Decision Making: Strategic choice evaluation
   - Risk Assessment: Threat evaluation and mitigation
   - Strategic Planning: Long-term strategy development

2. Memory Systems:
   - Semantic Memory: Domain knowledge and best practices
   - Episodic Memory: Learning from past experiences

The agents use TinyTroupe's cognitive architecture to:
- Process environmental information
- Make context-aware decisions
- Learn from experience
- Adapt to changing conditions
"""

from tinytroupe.agent.tiny_person import TinyPerson
from tinytroupe.agent.memory import SemanticMemory, EpisodicMemory, TinyMemory
from tinytroupe.agent.mental_faculty import TinyMentalFaculty
from typing import Dict, Any, List
import numpy as np

class SupplyChainMentalFaculty(TinyMentalFaculty):
    """
    Base class for supply chain mental faculties
    
    Mental faculties represent cognitive capabilities that agents use to:
    - Process information from the environment
    - Evaluate options and make decisions
    - Assess risks and opportunities
    - Plan strategic responses
    
    Each faculty produces a score between 0 and 1, representing:
    0.0: Completely negative/unfavorable assessment
    0.5: Neutral/uncertain assessment
    1.0: Completely positive/favorable assessment
    """
    def process(self, input_data: Any) -> float:
        """Process input data and return a score between 0 and 1"""
        return 0.5  # Default implementation

class DecisionMakingFaculty(SupplyChainMentalFaculty):
    """
    Mental faculty for strategic decision making
    
    This faculty evaluates potential decisions based on:
    - Current environmental conditions
    - Past experiences (via episodic memory)
    - Domain knowledge (via semantic memory)
    - Risk assessments
    - Strategic objectives
    """
    def process(self, input_data: Any) -> float:
        # Simple implementation - return a random score
        return np.random.random()

class RiskAssessmentFaculty(SupplyChainMentalFaculty):
    """Mental faculty for risk assessment"""
    def process(self, disruptions: List[Dict[str, Any]]) -> float:
        if not disruptions:
            return 0.0
        return sum(d['severity'] for d in disruptions) / len(disruptions)

class StrategicPlanningFaculty(SupplyChainMentalFaculty):
    """Mental faculty for strategic planning"""
    def process(self, input_data: Any) -> float:
        # Simple implementation - return a random score
        return np.random.random()

class SupplyChainSemanticMemory(TinyMemory):
    """
    Custom semantic memory for supply chain knowledge
    
    Stores and manages:
    1. Domain Knowledge:
       - Supply chain principles
       - Best practices
       - Industry standards
    
    2. Role-specific Knowledge:
       - Strategic objectives
       - Decision-making authority
       - Operational scope
    
    3. Environmental Knowledge:
       - Market conditions
       - Regional characteristics
       - Risk factors
    """
    def __init__(self):
        super().__init__("Supply Chain Memory")
        self.memories = []
    
    def _store(self, value: Any) -> None:
        """Store a value in memory"""
        self.memories.append(value)
    
    def retrieve_relevant(self, relevance_target: str, top_k: int = 20) -> list:
        """Retrieve relevant memories"""
        # Simple implementation - return all memories
        return self.memories

class SupplyChainAgent(TinyPerson):
    def __init__(self, name: str, role: str, region: str = None):
        super().__init__(name)
        self.role = role
        self.region = region
        
        # Initialize semantic memory with role-specific knowledge
        self.semantic_memory = SupplyChainSemanticMemory()
        self._initialize_semantic_memory()
        
        # Initialize episodic memory for experience-based learning
        self.episodic_memory = EpisodicMemory()
        
        # Initialize mental faculties
        self.decision_making = DecisionMakingFaculty("decision_making")
        self.risk_assessment = RiskAssessmentFaculty("risk_assessment")
        self.strategic_planning = StrategicPlanningFaculty("strategic_planning")
        
    def _initialize_semantic_memory(self):
        """Initialize role-specific knowledge in semantic memory"""
        base_knowledge = {
            "type": "stimulus",
            "simulation_timestamp": 0,
            "content": {
                "supply_chain_principles": [
                    "risk mitigation",
                    "cost optimization",
                    "service level maintenance"
                ],
                "disruption_types": [
                    "natural disasters",
                    "political events",
                    "infrastructure failures"
                ]
            }
        }
        
        role_specific_knowledge = {
            "COO": {
                "type": "stimulus",
                "simulation_timestamp": 0,
                "content": {
                    "strategic_objectives": [
                        "global network optimization",
                        "resilience enhancement",
                        "cost control"
                    ],
                    "decision_scope": "global",
                    "authority_level": "executive"
                }
            },
            "Regional_Manager": {
                "type": "stimulus",
                "simulation_timestamp": 0,
                "content": {
                    "strategic_objectives": [
                        "regional performance",
                        "supplier management",
                        "local risk mitigation"
                    ],
                    "decision_scope": "regional",
                    "authority_level": "middle_management"
                }
            },
            "Supplier": {
                "type": "stimulus",
                "simulation_timestamp": 0,
                "content": {
                    "strategic_objectives": [
                        "production efficiency",
                        "quality control",
                        "delivery reliability"
                    ],
                    "decision_scope": "local",
                    "authority_level": "operational"
                }
            }
        }
        
        # Store base knowledge
        self.semantic_memory.store(base_knowledge)
            
        # Store role-specific knowledge
        if self.role in role_specific_knowledge:
            self.semantic_memory.store(role_specific_knowledge[self.role])
                
    def perceive_environment(self, env) -> Dict[str, Any]:
        """Process environmental information and store in episodic memory"""
        perception = {
            'type': 'stimulus',
            'simulation_timestamp': env.current_time,
            'content': {
                'time': env.current_time,
                'disruptions': [d for d in env.disruption_events if d['time'] == env.current_time],
                'region_status': env.regions[self.region] if self.region else env.regions
            }
        }
        
        # Store experience in episodic memory
        self.episodic_memory.store(perception)
        return perception
        
    def make_decision(self, env) -> Dict[str, Any]:
        """Make decisions based on current perception and memories"""
        perception = self.perceive_environment(env)
        
        if self.role == "COO":
            return self._make_coo_decision(perception)
        elif self.role == "Regional_Manager":
            return self._make_regional_manager_decision(perception)
        elif self.role == "Supplier":
            return self._make_supplier_decision(perception)
        return {}
        
    def _make_coo_decision(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Strategic decision making for COO role"""
        # Use mental faculties for decision making
        risk_level = self.risk_assessment.process(perception['content']['disruptions'])
        strategic_importance = self.strategic_planning.process(perception['content']['region_status'])
        
        decisions = {
            'supplier_diversification': self.decision_making.process(risk_level) * 0.8,
            'inventory_adjustment': self.decision_making.process(strategic_importance) * 0.6,
            'transportation_mode_shift': self.decision_making.process(risk_level + strategic_importance) * 0.7
        }
        
        # Store decision in episodic memory
        self.episodic_memory.store({
            'type': 'action',
            'simulation_timestamp': perception['simulation_timestamp'],
            'content': {
                'decision': decisions,
                'context': perception['content']
            }
        })
        
        return decisions
        
    def _make_regional_manager_decision(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Regional manager decision making"""
        if not self.region:
            return {}
            
        region_status = perception['content']['region_status']
        risk_level = self.risk_assessment.process([
            d for d in perception['content']['disruptions'] 
            if d['region'] == self.region
        ])
        
        decisions = {
            'local_inventory_level': self.decision_making.process(risk_level) * 0.7,
            'supplier_coordination': self.decision_making.process(region_status['infrastructure_quality']) * 0.8,
            'contingency_activation': 1.0 if risk_level > 0.7 else 0.0
        }
        
        self.episodic_memory.store({
            'type': 'action',
            'simulation_timestamp': perception['simulation_timestamp'],
            'content': {
                'decision': decisions,
                'context': perception['content']
            }
        })
        
        return decisions
        
    def _make_supplier_decision(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Supplier decision making"""
        if not self.region:
            return {}
            
        region_status = perception['content']['region_status']
        local_disruptions = [
            d for d in perception['content']['disruptions']
            if d['region'] == self.region
        ]
        
        decisions = {
            'production_rate': self.decision_making.process(region_status['infrastructure_quality']) * 0.9,
            'quality_control': 0.8,  # Maintain high quality standards
            'delivery_schedule': self.decision_making.process(local_disruptions) * 0.7
        }
        
        self.episodic_memory.store({
            'type': 'action',
            'simulation_timestamp': perception['simulation_timestamp'],
            'content': {
                'decision': decisions,
                'context': perception['content']
            }
        })
        
        return decisions

def create_coo_agent(name: str, config: Dict[str, Any], simulation_id: str) -> TinyPerson:
    """Create a COO agent with appropriate mental faculties"""
    coo = TinyPerson(name=name)
    
    # Add semantic memory with COO-specific knowledge
    semantic_memory = SemanticMemory()
    semantic_memory.store("role", "Chief Operating Officer responsible for global supply chain operations")
    semantic_memory.store("objectives", [
        "Maintain supply chain resilience",
        "Optimize operational costs",
        "Ensure service level targets",
        "Manage regional operations"
    ])
    semantic_memory.store("capabilities", {
        "decision_making_speed": config['decision_making_speed'],
        "risk_tolerance": config['risk_tolerance'],
        "strategic_vision": config['strategic_vision'],
        "leadership_effectiveness": config['leadership_effectiveness']
    })
    coo.semantic_memory = semantic_memory
    
    # Add episodic memory for tracking decisions and outcomes
    coo.episodic_memory = EpisodicMemory()
    
    # Add supply chain mental faculty
    coo.add_faculty(SupplyChainMentalFaculty(config))
    
    return coo

def create_regional_manager_agent(name: str, region: str, config: Dict[str, Any], simulation_id: str) -> TinyPerson:
    """Create a Regional Manager agent"""
    manager = TinyPerson(name=name)
    
    # Add semantic memory with region-specific knowledge
    semantic_memory = SemanticMemory()
    semantic_memory.store("role", f"Regional Manager for {region}")
    semantic_memory.store("region", region)
    semantic_memory.store("objectives", [
        "Implement regional supply chain strategies",
        "Manage local supplier relationships",
        "Optimize regional operations",
        "Respond to local disruptions"
    ])
    semantic_memory.store("capabilities", {
        "local_market_knowledge": config['local_market_knowledge'],
        "operational_efficiency": config['operational_efficiency'],
        "team_management": config['team_management'],
        "risk_assessment": config['risk_assessment']
    })
    manager.semantic_memory = semantic_memory
    
    # Add episodic memory for tracking regional events
    manager.episodic_memory = EpisodicMemory()
    
    # Add supply chain mental faculty
    manager.add_faculty(SupplyChainMentalFaculty(config))
    
    return manager

def create_supplier_agent(name: str, region: str, config: Dict[str, Any], simulation_id: str) -> TinyPerson:
    """Create a Supplier agent"""
    supplier = TinyPerson(name=name)
    
    # Add semantic memory with supplier-specific knowledge
    semantic_memory = SemanticMemory()
    semantic_memory.store("role", f"Supplier based in {region}")
    semantic_memory.store("region", region)
    semantic_memory.store("objectives", [
        "Maintain production quality",
        "Meet delivery schedules",
        "Optimize production costs",
        "Innovate processes and products"
    ])
    semantic_memory.store("capabilities", {
        "production_capacity": config['production_capacity'],
        "quality_consistency": config['quality_consistency'],
        "delivery_reliability": config['delivery_reliability'],
        "innovation_capability": config['innovation_capability']
    })
    supplier.semantic_memory = semantic_memory
    
    # Add episodic memory for tracking production and delivery events
    supplier.episodic_memory = EpisodicMemory()
    
    # Add supply chain mental faculty
    supplier.add_faculty(SupplyChainMentalFaculty(config))
    
    return supplier 