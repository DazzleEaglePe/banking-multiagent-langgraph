import os
# Configure a dummy key for initialization tests to avoid ValueError
os.environ["GEMINI_API_KEY"] = "AIzaSyDummyKeyForTestingPurposesOnly"

from unittest.mock import MagicMock
import google.generativeai as genai
# Prevent LlamaIndex from making a real network check for model configuration metadata
mock_meta = MagicMock()
mock_meta.supported_generation_methods = ["generateContent"]
genai.get_model = MagicMock(return_value=mock_meta)

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_endpoint():
    print("\n[CI Test] Probando el endpoint de salud /health...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "banking-multiagent-langgraph"
    assert data["agent_graph_loaded"] is True
    print("✅ Endpoint /health verificado con éxito (Grafo de agentes compilado).")

if __name__ == "__main__":
    test_health_endpoint()
