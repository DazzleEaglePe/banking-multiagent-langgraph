import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph_builder import build_financial_agent_graph

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Caja Ica - Agente Financiero Multi-Agente API",
    version="1.0.0",
    description="REST API para interactuar con la red de agentes inteligentes de Caja Ica utilizando LangGraph."
)

# Initialize the LangGraph agent system globally
print("[Inicialización] Cargando Grafo de Agentes de LangGraph...")
try:
    agent_graph = build_financial_agent_graph()
    print("   ↳ Grafo cargado e inicializado con éxito.")
except Exception as e:
    print(f"❌ Error al inicializar el grafo de agentes: {e}")
    agent_graph = None

# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    message: str = Field(
        ..., 
        description="Mensaje enviado por el usuario al chatbot", 
        example="Hola, quiero simular un crédito de 5000 soles a 12 meses."
    )
    thread_id: str = Field(
        "default-thread-001",
        description="Identificador único de la sesión o hilo conversacional para mantener la memoria",
        example="sesion-cliente-12345"
    )

class ChatResponse(BaseModel):
    response: str = Field(..., description="Respuesta final auditada y devuelta por el agente")

# --- API Endpoints ---
@app.get("/health", summary="Verificar Salud de la API")
def health_check():
    return {
        "status": "ok",
        "project": "banking-multiagent-langgraph",
        "agent_graph_loaded": agent_graph is not None
    }

@app.post("/chat", response_model=ChatResponse, summary="Enviar Mensaje al Agente")
def chat_with_agent(req: ChatRequest):
    if not agent_graph:
        raise HTTPException(status_code=500, detail="El grafo de agentes no está disponible en este momento.")
    
    try:
        # 1. Config session thread ID for LangGraph MemorySaver checkpointer
        config = {"configurable": {"thread_id": req.thread_id}}
        
        # 2. Package request into HumanMessage
        inputs = {"messages": [HumanMessage(content=req.message)]}
        
        # 3. Invoke the graph synchronously
        result = agent_graph.invoke(inputs, config)
        
        # 4. Extract the last AI Message content (Compliance Officer audited response)
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            return ChatResponse(response=last_message.content)
        else:
            raise HTTPException(status_code=500, detail="El agente no devolvió ningún mensaje de respuesta.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el procesamiento conversacional: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
