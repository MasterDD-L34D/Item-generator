import json
import os
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# Inizializza il client Qdrant
qdrant_client = QdrantClient(":memory:") # O con un URL se si usa un server Qdrant

COLLECTION_NAME = "pathfinder_magic_items"

# Carica il modello di embedding locale
# Utilizziamo un modello comune e leggero come 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def load_magic_items(file_path):
    """
    Carica gli oggetti magici da un file JSON.
    """
    if not os.path.exists(file_path):
        print(f"Errore: Il file {file_path} non esiste.")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_embedding(text):
    """
    Genera un embedding per il testo dato usando SentenceTransformer.
    """
    try:
        # SentenceTransformer gestisce automaticamente la pulizia del testo per l'embedding
        embedding = embedding_model.encode(text, convert_to_tensor=False).tolist()
        return embedding
    except Exception as e:
        print(f"Errore nella generazione dell'embedding: {e}")
        return None

def create_qdrant_collection():
    """
    Crea la collezione Qdrant se non esiste.
    """
    # La dimensione del vettore deve corrispondere alla dimensione dell'output del modello di embedding
    # 'all-MiniLM-L6-v2' produce vettori di dimensione 384
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
    )
    print(f"Collezione '{COLLECTION_NAME}' creata o ricreata.")

def upload_items_to_qdrant(magic_items):
    """
    Genera embeddings e carica gli oggetti magici in Qdrant.
    """
    points = []
    for i, item in enumerate(magic_items):
        # Combina i campi rilevanti per creare un testo da embeddare
        text_to_embed = f"Nome: {item.get('name', 'N/A')}. " \
                        f"Aura: {item.get('aura', 'N/A')}. " \
                        f"CL: {item.get('cl', 'N/A')}. " \
                        f"Slot: {item.get('slot', 'N/A')}. " \
                        f"Peso: {item.get('weight', 'N/A')}. " \
                        f"Descrizione: {item.get('description', 'N/A')}. " \
                        f"Costruzione: {item.get('construction', 'N/A')}. " \
                        f"Requisiti: {item.get('requirements', 'N/A')}. " \
                        f"Costo: {item.get('cost', 'N/A')}. " \
                        f"URL: {item.get('url', 'N/A')}."
        
        embedding = generate_embedding(text_to_embed)
        if embedding:
            points.append(
                models.PointStruct(
                    id=i,
                    vector=embedding,
                    payload=item, # Salva tutti i dettagli dell'oggetto come payload
                )
            )
        if i % 100 == 0:
            print(f"Generati {i}/{len(magic_items)} embeddings...")

    if points:
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            wait=True,
            points=points,
        )
        print(f"Caricati {len(points)} oggetti con embeddings nella collezione '{COLLECTION_NAME}'.")
    else:
        print("Nessun oggetto con embedding generato per il caricamento.")

if __name__ == "__main__":
    data_file = "parsed_data/all_magic_items.json"
    magic_items = load_magic_items(data_file)

    if magic_items:
        print(f"Caricati {len(magic_items)} oggetti magici dal file {data_file}.")
        create_qdrant_collection()
        upload_items_to_qdrant(magic_items)
    else:
        print("Nessun oggetto magico caricato. Impossibile costruire la knowledge base.")

