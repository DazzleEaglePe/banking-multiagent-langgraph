from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import query_rag_tool
from state import AgentState

ADVISOR_PROMPT = """
Eres el Asesor Especialista en Créditos y Políticas de Caja Ica.
Tu objetivo es responder de manera clara, amable y profesional las preguntas informativas del cliente utilizando el Contexto oficial del banco proporcionado abajo.

Reglas del Juego:
1. Responde basándote ÚNICAMENTE en el Contexto de Caja Ica proporcionado.
2. Si la respuesta no está en el Contexto, sé honesto y responde con cortesía diciendo que no tienes esa información oficial disponible en tu base de conocimientos actual.
3. Nunca alucines datos, porcentajes o plazos que no figuren textualmente en el Contexto.
4. Mantén siempre el tono institucional de Caja Ica (formal, empático y servicial).
"""

def run_advisor(state: AgentState) -> dict:
    """Responde consultas sobre políticas de Caja Ica usando el motor RAG."""
    print("\n--- Running Node: Advisor (RAG) ---")
    
    # Extract last user message
    last_user_msg = state["messages"][-1].content
    
    # Query RAG tool
    print(f"  Retrieving context for query: '{last_user_msg[:40]}...'")
    context = query_rag_tool(last_user_msg)
    
    # Compile prompt
    model = get_chat_model()
    messages = [
        SystemMessage(content=ADVISOR_PROMPT),
        HumanMessage(content=f"Contexto Oficial de Caja Ica:\n{context}\n\nConsulta del Cliente: {last_user_msg}")
    ]
    
    try:
        response = model.invoke(messages)
        # Create an AIMessage to append to history
        new_message = AIMessage(content=response.content)
        return {
            "messages": [new_message],
            "next_action": "compliance"
        }
    except Exception as e:
        print(f"  Error in Advisor node: {e}")
        fallback_msg = AIMessage(content="Disculpe, he tenido un inconveniente al consultar nuestras políticas. Por favor, vuelva a intentarlo o consulte con un asesor.")
        return {
            "messages": [fallback_msg],
            "next_action": "compliance"
        }
