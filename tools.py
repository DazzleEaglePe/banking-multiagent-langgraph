import os
import chromadb
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext
)
from llama_index.vector_stores.chroma import ChromaVectorStore

# Global variable to cache the index
_cached_index = None

def get_rag_index():
    """Initializes and returns the persistent ChromaDB index, self-healing if missing."""
    global _cached_index
    if _cached_index is not None:
        return _cached_index
        
    db_path = "./.chromadb"
    db = chromadb.PersistentClient(path=db_path)
    chroma_collection = db.get_or_create_collection("cajaica_policies")
    
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # If the collection is empty, read data and ingest it
    if chroma_collection.count() == 0:
        print("ChromaDB collection empty. Ingesting policies from './data'...")
        if not os.path.exists("./data"):
            raise FileNotFoundError("Policies folder './data' not found. Please place policy files in './data'")
        documents = SimpleDirectoryReader("./data").load_data()
        _cached_index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        print("Ingestion complete.")
    else:
        # Load from store
        _cached_index = VectorStoreIndex.from_vector_store(
            vector_store, storage_context=storage_context
        )
    return _cached_index

def query_rag_tool(query_text: str) -> str:
    """
    Queries the Caja Ica internal policy knowledge base (credit requirements, security rules, etc.).
    Useful for questions about interest rates, age limits, Infocorp status, and documents.
    """
    try:
        index = get_rag_index()
        query_engine = index.as_query_engine(similarity_top_k=2)
        response = query_engine.query(query_text)
        return str(response)
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"

def simulate_loan_tool(monto: float, cuotas: int, tipo_credito: str) -> dict:
    """
    Simulates a credit loan quota for Caja Ica using French amortization formulas.
    
    Args:
        monto: Loan amount in Soles (S/.)
        cuotas: Loan duration in months
        tipo_credito: One of 'facilito', 'crediahorro', 'personal'
        
    Returns:
        A dictionary with quota simulation breakdown (TEA, TEM, monthly quota, desgravamen, total to pay).
    """
    tipo_credito = tipo_credito.strip().lower()
    
    # Establish TEA based on credit type
    if "facilito" in tipo_credito:
        tea = 0.350  # 35.0%
        label = "Crédito Facilito Consumo"
    elif "crediahorro" in tipo_credito or "ahorro" in tipo_credito:
        tea = 0.185  # 18.5% (garantía de plazo fijo)
        label = "Crédito CrediAhorro Consumo (Garantía Líquida)"
    else:
        tea = 0.480  # 48.0% (Crédito Personal Directo / independientes)
        label = "Crédito Personal Directo"
        
    # Validation
    if monto <= 0:
        return {"error": "El monto del préstamo debe ser mayor a 0."}
    if cuotas <= 0 or cuotas > 60:
        return {"error": "El plazo debe ser de 1 a 60 meses."}
        
    # 1. Convert TEA to TEM (Tasa Efectiva Mensual)
    tem = (1 + tea) ** (1 / 12) - 1
    
    # 2. Base Monthly Quota (amortización francesa)
    # Formula: P * [TEM * (1+TEM)^n] / [(1+TEM)^n - 1]
    cuota_base = monto * (tem * (1 + tem) ** cuotas) / ((1 + tem) ** cuotas - 1)
    
    # 3. Monthly desgravamen (Flat 0.085% of initial principal for simplified estimate)
    seguro_desgravamen = monto * 0.00085
    
    # 4. Total Monthly Quota
    cuota_total = cuota_base + seguro_desgravamen
    
    # 5. Totals
    total_a_pagar = cuota_total * cuotas
    intereses_totales = total_a_pagar - monto
    
    return {
        "tipo_credito": label,
        "monto_prestado": f"S/. {monto:,.2f}",
        "cuotas": cuotas,
        "tea_anual": f"{tea*100:.2f}%",
        "tem_mensual": f"{tem*100:.4f}%",
        "cuota_mensual_base": f"S/. {cuota_base:.2f}",
        "seguro_desgravamen_mensual": f"S/. {seguro_desgravamen:.2f}",
        "cuota_mensual_total_estimada": f"S/. {cuota_total:.2f}",
        "intereses_totales_estimados": f"S/. {intereses_totales:.2f}",
        "total_a_pagar_estimado": f"S/. {total_a_pagar:.2f}"
    }

if __name__ == "__main__":
    # Quick tool validation run
    print("Testing simulation tool:")
    sim = simulate_loan_tool(5000, 12, "facilito")
    for k, v in sim.items():
        print(f"  {k}: {v}")
