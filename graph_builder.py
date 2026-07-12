from langgraph.graph import StateGraph, END
from state import AgentState
from agents.router import run_router
from agents.advisor import run_advisor
from agents.simulator import run_simulator
from agents.compliance import run_compliance_validator
from agents.handoff import run_handoff
from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def run_chitchat(state: AgentState) -> dict:
    """Handles polite greetings, goodbyes, and generic conversation."""
    print("\n--- Running Node: Chitchat ---")
    model = get_chat_model()
    messages = [
        SystemMessage(content="Eres el chatbot oficial de Caja Ica. Responde cordialmente al saludo, despedida o comentario casual del cliente, ofreciendo tu ayuda para consultas de créditos de consumo."),
        HumanMessage(content=state["messages"][-1].content)
    ]
    try:
        response = model.invoke(messages)
        new_message = AIMessage(content=response.content)
        return {
            "messages": [new_message],
            "next_action": "compliance"
        }
    except Exception as e:
        print(f"  Error in Chitchat node: {e}")
        fallback_msg = AIMessage(content="Hola, ¿en qué puedo ayudarle hoy con respecto a nuestros créditos de consumo?")
        return {
            "messages": [fallback_msg],
            "next_action": "compliance"
        }

def route_after_router(state: AgentState) -> str:
    """Decides which node to run based on Router's classification."""
    next_action = state.get("next_action")
    if next_action in ["simulation", "rag_query", "handoff", "chitchat"]:
        return next_action
    return "chitchat"  # Default fallback

def route_after_compliance(state: AgentState) -> str:
    """Routes to Handoff if compliance failed, or terminates the graph run."""
    next_action = state.get("next_action")
    if next_action == "handoff":
        return "handoff"
    return END

def build_financial_agent_graph():
    """Builds and compiles the LangGraph StateGraph representing our agent team."""
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("router", run_router)
    workflow.add_node("advisor", run_advisor)
    workflow.add_node("simulator", run_simulator)
    workflow.add_node("chitchat", run_chitchat)
    workflow.add_node("compliance", run_compliance_validator)
    workflow.add_node("handoff", run_handoff)
    
    # Set Entry Point
    workflow.set_entry_point("router")
    
    # Add Conditional Edges from Router
    workflow.add_conditional_edges(
        "router",
        route_after_router,
        {
            "simulation": "simulator",
            "rag_query": "advisor",
            "chitchat": "chitchat",
            "handoff": "handoff"
        }
    )
    
    # Connect processing nodes to Compliance Validator
    workflow.add_edge("advisor", "compliance")
    workflow.add_edge("simulator", "compliance")
    workflow.add_edge("chitchat", "compliance")
    
    # Add Conditional Edge from Compliance
    workflow.add_conditional_edges(
        "compliance",
        route_after_compliance,
        {
            "handoff": "handoff",
            END: END
        }
    )
    
    # Connect Handoff node to END
    workflow.add_edge("handoff", END)
    
    # Compile
    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app

if __name__ == "__main__":
    print("Compiling StateGraph...")
    graph = build_financial_agent_graph()
    print("Graph compiled successfully!")
