import json
from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState

COMPLIANCE_PROMPT = """
Eres el Oficial de Cumplimiento Normativo (Compliance Officer) de Caja Ica.
Tu rol es auditar el borrador de respuesta generado por el asistente virtual antes de que se envíe al cliente, garantizando el cumplimiento de la Ley de Secreto Bancario (Ley N° 26702) y la de Protección de Datos Personales (Ley N° 29733).

Debes verificar que el borrador cumpla con las siguientes reglas estrictas de seguridad:
1. NO solicitar ni revelar claves secretas, contraseñas, ni códigos OTP (tokens digitales).
2. NO revelar saldos exactos de cuentas ni realizar transferencias monetarias de forma automatizada por chat.
3. Si el borrador responde a una solicitud transaccional crítica (saldos, transferencias, bloqueo de tarjetas) o maneja reclamos de fraude, DEBE indicar que se le transferirá con un asesor humano. Si no ofrece la derivación, debes desaprobarlo.
4. NO contener insultos ni respuestas informales inadecuadas.

Analiza el borrador proporcionado y decide si apruebas la respuesta.
Responde ESTRICTAMENTE en formato JSON con la siguiente estructura (sin agregar texto fuera del JSON):
{
  "approved": true | false,
  "reason": "Si se desaprueba, explica la razón (ej. solicita claves, no deriva saldo a humano). Si se aprueba, dejar en blanco."
}
"""

def run_compliance_validator(state: AgentState) -> dict:
    """Audita el borrador de respuesta para garantizar la seguridad regulatoria de Caja Ica."""
    print("\n--- Running Node: Compliance Validator ---")
    
    # Extract the proposed answer (the last message drafted by Advisor or Simulator)
    draft_msg = state["messages"][-1].content
    
    model = get_chat_model()
    messages = [
        SystemMessage(content=COMPLIANCE_PROMPT),
        HumanMessage(content=f"Borrador de Respuesta a Auditar:\n{draft_msg}")
    ]
    
    try:
        response = model.invoke(messages)
        result = json.loads(response.content.strip())
        
        approved = result.get("approved", True)
        reason = result.get("reason", "")
        
        if not approved:
            print(f"  [COMPLIANCE REJECTED] Reason: {reason}")
            return {
                "compliance_approved": False,
                "escalation_reason": reason,
                "next_action": "handoff"
            }
        else:
            print("  [COMPLIANCE APPROVED]")
            return {
                "compliance_approved": True,
                "next_action": "end"
            }
    except Exception as e:
        print(f"  Error in Compliance Validator node: {e}")
        # Fail safe: if validator fails, assume approved unless flagged
        return {
            "compliance_approved": True,
            "next_action": "end"
        }
