import json
from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState

ROUTER_PROMPT = """
Eres el Agente Clasificador (Router) del asistente virtual de Caja Ica.
Tu tarea es analizar el último mensaje del usuario y clasificar su intención en una de las siguientes categorías:

1. 'simulation': El usuario quiere simular un crédito, cotizar cuotas, saber cuánto pagará por un préstamo, o continuar aportando datos de una simulación en curso (como montos, cuotas o tipo de crédito).
2. 'rag_query': El usuario hace preguntas generales o informativas sobre políticas de crédito (edad mínima, tasas, requisitos, Infocorp, garantías, etc.).
3. 'handoff': El usuario intenta consultar información confidencial transaccional (ej: saldos exactos de cuenta, transferencias de dinero), reporta un fraude o bloqueo, proporciona claves/OTP, o usa insultos/lenguaje ofensivo de manera persistente.
4. 'chitchat': El usuario saluda, se despide, agradece o conversa de manera informal.

Adicionalmente, si la intención es 'simulation', debes intentar extraer los siguientes parámetros si están presentes en la conversación:
- 'monto': El monto en Soles (ej: 5000, 3000.5). Debe ser solo un número.
- 'cuotas': El plazo en meses (ej: 12, 24). Debe ser solo un número entero.
- 'tipo_credito': El tipo de crédito que busca. Debe ser uno de: 'facilito', 'crediahorro' o 'personal'.

Responde ESTRICTAMENTE en formato JSON con la siguiente estructura (sin agregar texto fuera del JSON):
{
  "intent": "simulation" | "rag_query" | "handoff" | "chitchat",
  "extracted_params": {
    "monto": float | null,
    "cuotas": int | null,
    "tipo_credito": "facilito" | "crediahorro" | "personal" | null
  },
  "reason": "Explicación breve de la clasificación"
}
"""

def run_router(state: AgentState) -> dict:
    """Clasifica el mensaje del usuario y extrae parámetros iniciales de simulación."""
    print("\n--- Running Node: Router ---")
    model = get_chat_model()
    
    # Get conversational history and compile it
    conversation_history = []
    for msg in state["messages"]:
        role = "User" if msg.type == "human" else "Assistant"
        conversation_history.append(f"{role}: {msg.content}")
        
    conversation_str = "\n".join(conversation_history)
    
    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=f"Historial de conversación:\n{conversation_str}\n\nAnaliza el último mensaje del usuario.")
    ]
    
    try:
        response = model.invoke(messages)
        # Parse the JSON response
        result = json.loads(response.content.strip())
        
        # Merge extracted params with existing params in state
        existing_params = state.get("simulation_params", {})
        new_params = result.get("extracted_params", {})
        
        merged_params = {
            "monto": new_params.get("monto") if new_params.get("monto") is not None else existing_params.get("monto"),
            "cuotas": new_params.get("cuotas") if new_params.get("cuotas") is not None else existing_params.get("cuotas"),
            "tipo_credito": new_params.get("tipo_credito") if new_params.get("tipo_credito") is not None else existing_params.get("tipo_credito")
        }
        
        print(f"  Classification: {result['intent'].upper()}")
        print(f"  Merged Params: {merged_params}")
        
        return {
            "current_intent": result["intent"],
            "simulation_params": merged_params,
            "next_action": result["intent"]
        }
    except Exception as e:
        print(f"  Error in Router node: {e}")
        # Default fallback
        return {
            "current_intent": "chitchat",
            "next_action": "chitchat"
        }
