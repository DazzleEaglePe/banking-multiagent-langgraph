from config import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from tools import simulate_loan_tool
from state import AgentState

SIMULATOR_PROMPT = """
Eres el Agente de Simulación de Créditos de Caja Ica.
Tu rol es presentar de manera sumamente clara, profesional y comercial los resultados de la simulación de crédito calculada por nuestro sistema.

Abajo recibirás el desglose del cálculo exacto realizado por la herramienta interna.
Tu objetivo es redactar un mensaje amigable al cliente que resuma esta cotización y le presente la información en un formato legible (puedes usar listas o tablas en Markdown). 
Asegúrate de destacar:
- El tipo de crédito y monto.
- La cuota mensual estimada final (que incluye el seguro de desgravamen).
- El plazo elegido (cuotas).
- El total final a pagar y las tasas aplicadas (TEA y TEM).

Mantén un tono de bienvenida, formal y transparente. No modifiques las cifras calculadas por la herramienta bajo ninguna circunstancia.
"""

def run_simulator(state: AgentState) -> dict:
    """Gestiona el flujo interactivo de simulación y calcula la cotización final."""
    print("\n--- Running Node: Simulator ---")
    params = state.get("simulation_params", {})
    
    monto = params.get("monto")
    cuotas = params.get("cuotas")
    tipo_credito = params.get("tipo_credito")
    
    # Check for missing parameters and ask for them interactively
    if monto is None:
        msg = AIMessage(content="Para poder realizar su simulación de crédito en Caja Ica, ¿cuál es el **monto en Soles** que desearía solicitar? (Ejemplo: S/. 5,000)")
        return {
            "messages": [msg],
            "next_action": "compliance"
        }
        
    if cuotas is None:
        msg = AIMessage(content="Entendido. ¿En **cuántas cuotas mensuales** (plazo en meses) desearía cancelar el préstamo? (Ejemplo: 12 o 24 meses)")
        return {
            "messages": [msg],
            "next_action": "compliance"
        }
        
    if tipo_credito is None:
        msg = AIMessage(content="Perfecto. Por favor, indíqueme cuál de nuestras modalidades de crédito de consumo prefiere:\n\n1. 🔹 **Facilito** (Proceso ágil, sin necesidad de vivienda propia o aval).\n2. 🔹 **CrediAhorro** (Tasa preferencial especial respaldada por sus depósitos a plazo fijo).\n3. 🔹 **Personal** (Crédito de libre disponibilidad tradicional).")
        return {
            "messages": [msg],
            "next_action": "compliance"
        }
        
    # All parameters are present, execute simulation tool!
    print(f"  All parameters gathered. Simulating loan: Monto={monto}, Cuotas={cuotas}, Tipo={tipo_credito}")
    sim_data = simulate_loan_tool(float(monto), int(cuotas), tipo_credito)
    
    if "error" in sim_data:
        msg = AIMessage(content=f"Lo siento, no he podido procesar la simulación debido al siguiente error: {sim_data['error']}. Por favor, verifique los datos proporcionados.")
        return {
            "messages": [msg],
            "next_action": "compliance"
        }
        
    # Use LLM to format the simulation results beautifully
    model = get_chat_model()
    messages = [
        SystemMessage(content=SIMULATOR_PROMPT),
        HumanMessage(content=f"Resultado de la simulación de la herramienta:\n{sim_data}")
    ]
    
    try:
        response = model.invoke(messages)
        new_message = AIMessage(content=response.content)
        return {
            "messages": [new_message],
            "next_action": "compliance"
        }
    except Exception as e:
        print(f"  Error formatting simulation: {e}")
        # Fallback raw markdown presentation
        raw_md = f"""### 📊 Simulación de Crédito - Caja Ica
*   **Modalidad:** {sim_data['tipo_credito']}
*   **Monto Solicitado:** {sim_data['monto_prestado']}
*   **Plazo:** {sim_data['cuotas']} meses
*   **TEA / TEM:** {sim_data['tea_anual']} / {sim_data['tem_mensual']}
*   **Cuota Base:** {sim_data['cuota_mensual_base']}
*   **Seguro de Desgravamen:** {sim_data['seguro_desgravamen_mensual']}
*   **Cuota Mensual Total Estimada:** **{sim_data['cuota_mensual_total_estimada']}**
*   **Total a Pagar:** {sim_data['total_a_pagar_estimado']}
"""
        new_message = AIMessage(content=raw_md)
        return {
            "messages": [new_message],
            "next_action": "compliance"
        }
