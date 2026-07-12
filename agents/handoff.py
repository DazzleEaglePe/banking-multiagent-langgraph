from langchain_core.messages import AIMessage
from state import AgentState

def run_handoff(state: AgentState) -> dict:
    """Handles human agent handoffs, formatting a polite explanation to the customer."""
    print("\n--- Running Node: Handoff (Escalación a Humano) ---")
    
    reason = state.get("escalation_reason")
    intent = state.get("current_intent")
    
    # Draft handoff explanation
    if intent == "handoff":
        explanation = "debido a que su consulta involucra operaciones transaccionales críticas, soporte de fraude o solicitudes de información confidencial."
    elif reason:
        explanation = f"debido a la siguiente política de seguridad: {reason}."
    else:
        explanation = "para brindarle una atención personalizada sobre su consulta."
        
    handoff_text = f"""⚠️ **Transferencia de Atención (Handoff a Asesor Humano)**
    
Estimado cliente, de acuerdo con las políticas de seguridad y secreto bancario de **Caja Ica**, procederemos a transferir esta conversación de inmediato con un **asesor humano** en nuestros canales de atención oficiales.

*   **Motivo de derivación:** {explanation}
*   **Canales alternativos oficiales de contacto:**
    *   📞 Call Center Nacional: **(056) 581 430**
    *   🏢 O visite cualquiera de nuestras agencias a nivel nacional.

Un asesor de nuestro equipo continuará con su atención en unos instantes. ¡Muchas gracias por su paciencia!"""

    new_message = AIMessage(content=handoff_text)
    return {
        "messages": [new_message],
        "next_action": "end"
    }
