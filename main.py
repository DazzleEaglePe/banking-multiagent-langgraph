import sys
from config import get_chat_model
from langchain_core.messages import HumanMessage
from graph_builder import build_financial_agent_graph

def run_chat_loop():
    print("=================================================================")
    print(" 🏦 ASISTENTE MULTI-AGENTE FINANCIERO - CAJA ICA")
    print("=================================================================")
    print("  Orquestado con LangGraph & Google Gemini (Gratuito)")
    print("  Desarrollado como entregable del Módulo 1.2")
    print("  Escribe 'salir' para terminar la conversación.")
    print("=================================================================\n")
    
    # Compile the agent StateGraph with MemorySaver checkpointer
    print("Inicializando el grafo de agentes...")
    app = build_financial_agent_graph()
    print("Grafo inicializado y listo.\n")
    
    # Establish conversational thread session config
    config = {"configurable": {"thread_id": "cajaica-user-session-001"}}
    
    while True:
        try:
            user_input = input("👤 [Tú]: ")
            if not user_input.strip():
                continue
                
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("\nGracias por consultarnos. ¡Hasta pronto! 🏦")
                break
                
            print("\nProcesando con la red de agentes...")
            
            # Stream graph node updates to show the multi-agent trajectory
            last_message = None
            inputs = {"messages": [HumanMessage(content=user_input)]}
            
            # Execute and stream node triggers
            for event in app.stream(inputs, config, stream_mode="updates"):
                for node_name, node_output in event.items():
                    print(f"   ↳ ⚙️ [Nodo Ejecutado: {node_name.upper()}]")
                    if "messages" in node_output and len(node_output["messages"]) > 0:
                        last_message = node_output["messages"][-1]
            
            # Print the final response approved by the compliance validator
            if last_message:
                print(f"\n🤖 [Bot]: {last_message.content}\n")
                print("-" * 65 + "\n")
            else:
                print("\n🤖 [Bot]: Disculpe, no se pudo generar una respuesta. Intente nuevamente.\n")
                
        except KeyboardInterrupt:
            print("\n\nSesión cancelada. ¡Hasta luego! 🏦")
            break
        except Exception as e:
            print(f"\n❌ Error durante la conversación: {e}\n")

if __name__ == "__main__":
    run_chat_loop()
