import os
from dotenv import load_dotenv
from graph_builder import build_financial_agent_graph
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def run_single_trace():
    print("Inicializando el Grafo de Agentes con LangGraph...")
    app = build_financial_agent_graph()
    
    # Executing a single test query to create a trace in LangSmith
    config = {"configurable": {"thread_id": "langsmith-test-session-001"}}
    query = "Hola, me gustaría saber si tienen requisitos de edad mínima para préstamos."
    
    print(f"\n👤 [Usuario]: '{query}'")
    print("Enviando al grafo y subiendo traza a LangSmith...")
    
    inputs = {"messages": [HumanMessage(content=query)]}
    
    last_message = None
    try:
        # Stream updates to see the nodes executing
        for event in app.stream(inputs, config, stream_mode="updates"):
            for node_name, node_output in event.items():
                print(f"   ↳ ⚙️ [Nodo: {node_name.upper()}]")
                if "messages" in node_output and len(node_output["messages"]) > 0:
                    last_message = node_output["messages"][-1]
                    
        if last_message:
            print(f"\n🤖 [Chatbot]:\n{last_message.content}")
        print("\n✅ Consulta completada. ¡Revisa tu panel de LangSmith para ver la traza gráfica!")
        
    except Exception as e:
        print(f"\n❌ Error al ejecutar el agente: {e}")
        print("Esto podría deberse a la cuota diaria del plan gratuito de Gemini. El código de tracing de LangSmith está correctamente configurado.")

if __name__ == "__main__":
    run_single_trace()
