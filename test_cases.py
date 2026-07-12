import time
from langchain_core.messages import HumanMessage
from graph_builder import build_financial_agent_graph

def run_test_journey(title, messages_list, app, config):
    print(f"\n========================================================")
    print(f" 🧪 EJECUTANDO: {title}")
    print(f"========================================================")
    
    for user_input in messages_list:
        print(f"\n👤 [Usuario]: '{user_input}'")
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        last_message = None
        for event in app.stream(inputs, config, stream_mode="updates"):
            for node_name, node_output in event.items():
                print(f"   ↳ ⚙️ [Nodo: {node_name.upper()}]")
                if "messages" in node_output and len(node_output["messages"]) > 0:
                    last_message = node_output["messages"][-1]
                    
        if last_message:
            print(f"\n🤖 [Chatbot]:\n{last_message.content}")
        print("-" * 56)
        time.sleep(2)  # Pause to avoid rate limits

def run_all_tests():
    print("Inicializando el Grafo de Agentes con LangGraph...")
    app = build_financial_agent_graph()
    
    # ----------------------------------------------------
    # Caso 1: Asesoría General (RAG)
    # ----------------------------------------------------
    config_1 = {"configurable": {"thread_id": "test-session-1"}}
    run_test_journey(
        "CASO 1: Consulta Informativa de Políticas (RAG)",
        ["Hola, ¿si tengo una calificación de CPP en Infocorp puedo pedir crédito de consumo?"],
        app,
        config_1
    )
    
    # ----------------------------------------------------
    # Caso 2: Simulación Directa Completa
    # ----------------------------------------------------
    config_2 = {"configurable": {"thread_id": "test-session-2"}}
    run_test_journey(
        "CASO 2: Simulación Directa Completa",
        ["Quiero simular un préstamo de S/. 5,000 a 12 meses de tipo Facilito."],
        app,
        config_2
    )
    
    # ----------------------------------------------------
    # Caso 3: Simulación Interactiva (Paso a Paso)
    # ----------------------------------------------------
    config_3 = {"configurable": {"thread_id": "test-session-3"}}
    run_test_journey(
        "CASO 3: Simulación Interactiva de Crédito",
        [
            "Hola, me gustaría simular un préstamo por favor.",
            "Quiero S/. 8,000",
            "A un plazo de 24 meses",
            "Elijo el tipo CrediAhorro"
        ],
        app,
        config_3
    )
    
    # ----------------------------------------------------
    # Caso 4: Violación de Seguridad y Derivación a Humano
    # ----------------------------------------------------
    config_4 = {"configurable": {"thread_id": "test-session-4"}}
    run_test_journey(
        "CASO 4: Interceptación por Seguridad / Secreto Bancario",
        ["Hola, quiero hacer un pago de mi préstamo y ver mi saldo, mi DNI es 10203040 y mi clave de tarjeta es 9876."],
        app,
        config_4
    )

if __name__ == "__main__":
    run_all_tests()
