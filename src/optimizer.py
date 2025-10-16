import json
import os
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "pathfinder_magic_items"
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
qdrant_client = QdrantClient(":memory:") # Inizializza il client Qdrant in memoria

def search_magic_items(query_text, top_k=5):
    """
    Cerca oggetti magici nel database vettoriale basandosi su una query testuale.
    """
    query_embedding = embedding_model.encode(query_text, convert_to_tensor=False).tolist()

    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True, # Restituisce il payload completo degli oggetti
    )

    return search_result

def optimize_magic_items(search_results, criteria):
    """
    Applica criteri di ottimizzazione ai risultati della ricerca.
    Questa è una logica di esempio e può essere estesa.
    """
    optimized_results = []

    # Esempio di criterio: preferire oggetti con un CL (Caster Level) più alto
    if "high_cl" in criteria:
        search_results.sort(key=lambda x: x.payload.get("cl", 0) if isinstance(x.payload.get("cl"), int) else 0, reverse=True)

    # Esempio di criterio: preferire oggetti con un costo inferiore (se disponibile e numerico)
    if "low_cost" in criteria:
        # Converti il costo in un valore numerico per il confronto
        def get_numeric_cost(item):
            cost_str = item.payload.get("cost", "N/A").replace(" gp", "").replace(",", "")
            try:
                return float(cost_str)
            except (ValueError, TypeError):
                return float("inf") # Oggetti senza costo numerico vanno alla fine
        search_results.sort(key=get_numeric_cost)

    # Qui si possono aggiungere altri criteri di ottimizzazione più complessi
    # ad esempio, sinergie tra oggetti, slot disponibili, ecc.

    optimized_results = search_results # Per ora, restituisce i risultati ordinati

    return optimized_results

if __name__ == "__main__":
    # Carica gli oggetti magici
    data_file = "parsed_data/all_magic_items.json"
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            try:
                magic_items = json.load(f)
            except json.JSONDecodeError:
                print(f"Errore di decodifica JSON nel file: {data_file}")
                magic_items = []
    else:
        print(f"File di dati non trovato: {data_file}. Assicurati di aver eseguito data_parser.py.")
        magic_items = []

    if magic_items:
        # Re-crea la collezione e carica gli elementi
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        print(f"Collezione '{COLLECTION_NAME}' creata o ricreata.")

        points = []
        for i, item in enumerate(magic_items):
            text_to_embed = (
                f"Nome: {item.get('name', 'N/A')}. "
                f"Aura: {item.get('aura', 'N/A')}. "
                f"CL: {item.get('cl', 'N/A')}. "
                f"Slot: {item.get('slot', 'N/A')}. "
                f"Peso: {item.get('weight', 'N/A')}. "
                f"Descrizione: {item.get('description', 'N/A')}. "
                f"Costruzione: {item.get('construction', 'N/A')}. "
                f"Requisiti: {item.get('requirements', 'N/A')}. "
                f"Costo: {item.get('cost', 'N/A')}. "
                f"URL: {item.get('url', 'N/A')}."
            )
            
            embedding = embedding_model.encode(text_to_embed, convert_to_tensor=False).tolist()
            points.append(
                models.PointStruct(
                    id=i,
                    vector=embedding,
                    payload=item,
                )
            )
            if (i + 1) % 100 == 0:
                print(f"Generati {i + 1}/{len(magic_items)} embeddings...")

        if points:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                wait=True,
                points=points,
            )
            print(f"Caricati {len(points)} oggetti con embeddings nella collezione '{COLLECTION_NAME}'.")

        print("\n--- Test di Ricerca e Ottimizzazione ---")
        query = "Anello che aumenta la forza e la resistenza"
        print(f"Ricerca per: '{query}'")
        
        results = search_magic_items(query, top_k=10)
        print("\nRisultati della ricerca (non ottimizzati):")
        for i, item in enumerate(results):
            print(f"  {i+1}. {item.payload.get('name', 'N/A')} (CL: {item.payload.get('cl', 'N/A')}, Costo: {item.payload.get('cost', 'N/A')})")

        print("\nRisultati ottimizzati (preferendo CL alto e costo basso):")
        optimized_results = optimize_magic_items(results, ["high_cl", "low_cost"])
        for i, item in enumerate(optimized_results):
            print(f"  {i+1}. {item.payload.get('name', 'N/A')} (CL: {item.payload.get('cl', 'N/A')}, Costo: {item.payload.get('cost', 'N/A')})")
    else:
        print("Nessun oggetto magico disponibile per la ricerca e l'ottimizzazione.")

