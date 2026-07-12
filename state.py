from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages

class SimulationParams(TypedDict, total=False):
    monto: Optional[float]
    cuotas: Optional[int]
    tipo_credito: Optional[str]

class AgentState(TypedDict):
    # messages list is annotated with add_messages, which appends new messages automatically
    messages: Annotated[List[Any], add_messages]
    
    # Intention categorized by the Router
    current_intent: Optional[str]
    
    # Extracted loan parameters for simulation
    simulation_params: SimulationParams
    
    # Safety and compliance validation flags
    compliance_approved: Optional[bool]
    
    # Reason for escalations or failures
    escalation_reason: Optional[str]
    
    # Target node for transition (routing control)
    next_action: Optional[str]
