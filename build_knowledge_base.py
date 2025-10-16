#!/usr/bin/env python3
"""
Script per costruire il knowledge base vettoriale degli oggetti magici di Pathfinder 1E.
"""

import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

def build_knowledge_base():
    # Percorsi dei file
    data_file = "parsed_data/all_magic_items.json"
    qdrant_path = "./qdrant_storage"
    
    # Carica i dati degli oggetti magici
    print(f"Caricamento dei dati da {data_file}...")
    with open(data_file, "r", encoding="utf-8") as f:
        magic_items = json.load(f)
    
    print(f"Caricati {len(magic_items)} oggetti magici dal file {data_file}.")
    
    # Inizializza il modello di embedding
    print("Inizializzazione del modello di embedding...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Inizializza il client Qdrant
    print(f"Inizializzazione del client Qdrant in {qdrant_path}...")
    client = QdrantClient(path=qdrant_path)
    
    collection_name = "pathfinder_magic_items"
    
    # Crea o ricrea la collezione
    print(f"Creazione della collezione '{collection_name}'...")
    try:
        client.delete_collection(collection_name=collection_name)
    except:
        pass
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    
    print(f"Collezione '{collection_name}' creata o ricreata.")
    
    # Genera gli embedding e carica i dati
    points = []
    for i, item in enumerate(magic_items):
        # Crea il testo per l'embedding
        text_for_embedding = f"{item.get('name', '')} {item.get('description', '')} {item.get('aura', '')} {item.get('slot', '')}"
        
        # Genera l'embedding
        embedding = model.encode(text_for_embedding).tolist()
        
        # Crea il punto per Qdrant
        point = PointStruct(
            id=i,
            vector=embedding,
            payload={
                'name': item.get('name', 'Unknown'),
                'description': item.get('description', 'N/A'),
                'aura': item.get('aura', 'N/A'),
                'cl': item.get('cl', 'N/A'),
                'slot': item.get('slot', 'N/A'),
                'cost': item.get('cost', 'N/A'),
                'weight': item.get('weight', 'N/A'),
                'requirements': item.get('requirements', 'N/A'),
                'source': item.get('source', 'N/A'),
                'url': item.get('url', '')
            }
        )
        points.append(point)
        
        if (i + 1) % 100 == 0:
            print(f"Generati {i + 1}/{len(magic_items)} embeddings...")
    
    # Carica tutti i punti nella collezione
    print(f"Caricamento di {len(points)} oggetti nella collezione...")
    client.upsert(
        collection_name=collection_name,
        points=points
    )
    
    print(f"Caricati {len(points)} oggetti con embeddings nella collezione '{collection_name}'.")
    print("Knowledge base costruito con successo!")

if __name__ == "__main__":
    build_knowledge_base()

