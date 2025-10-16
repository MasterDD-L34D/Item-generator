from flask import Blueprint, request, jsonify
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import os
import json
from openai import OpenAI

generator_bp = Blueprint('generator', __name__)

# Inizializza i componenti necessari
qdrant_client = QdrantClient(path="./qdrant_storage")
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
openai_client = OpenAI()

COLLECTION_NAME = "pathfinder_magic_items"

@generator_bp.route('/generate', methods=['POST'])
def generate_item():
    """
    Genera un nuovo oggetto magico basato sulla descrizione fornita dall'utente.
    """
    try:
        data = request.get_json()
        user_description = data.get('description', '')
        
        if not user_description:
            return jsonify({'error': 'La descrizione è richiesta'}), 400
        
        # Genera l'embedding per la descrizione dell'utente
        query_embedding = embedding_model.encode(user_description).tolist()
        
        # Cerca gli oggetti simili nel database vettoriale
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=5
        )
        
        # Estrai i dettagli degli oggetti simili
        similar_items = []
        for result in search_results:
            similar_items.append({
                'name': result.payload.get('name'),
                'description': result.payload.get('description'),
                'aura': result.payload.get('aura'),
                'cl': result.payload.get('cl'),
                'slot': result.payload.get('slot'),
                'cost': result.payload.get('cost'),
                'weight': result.payload.get('weight'),
                'requirements': result.payload.get('requirements'),
                'source': result.payload.get('source')
            })
        
        # Costruisci il prompt per l'LLM
        context = "Ecco alcuni oggetti magici di Pathfinder 1E simili alla richiesta:\n\n"
        for i, item in enumerate(similar_items, 1):
            context += f"{i}. {item['name']}\n"
            context += f"   Descrizione: {item['description']}\n"
            context += f"   Aura: {item['aura']}, CL: {item['cl']}\n"
            context += f"   Slot: {item['slot']}, Prezzo: {item['cost']}\n\n"
        
        prompt = f"""Sei un esperto game designer di Pathfinder 1E. Crea un nuovo oggetto magico basato sulla seguente richiesta dell'utente:

"{user_description}"

{context}

Crea un oggetto magico completamente nuovo e originale che si ispiri agli esempi forniti ma che sia unico. L'oggetto deve essere bilanciato per Pathfinder 1E e includere:
- Nome dell'oggetto
- Aura (scuola di magia e intensità)
- Caster Level (CL)
- Slot (dove si indossa/usa l'oggetto)
- Prezzo in gp
- Peso
- Descrizione dettagliata delle capacità e degli effetti
- Requisiti di costruzione
- Costo di costruzione

Formatta la risposta in modo chiaro e strutturato, seguendo lo stile degli oggetti magici di Pathfinder 1E."""

        # Genera l'oggetto magico usando l'LLM
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Sei un esperto game designer di Pathfinder 1E specializzato nella creazione di oggetti magici bilanciati e interessanti."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1500
        )
        
        generated_item = response.choices[0].message.content
        
        return jsonify({
            'generated_item': generated_item,
            'similar_items': similar_items
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generator_bp.route('/search', methods=['POST'])
def search_items():
    """
    Cerca oggetti magici esistenti nel database basandosi su una query.
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'La query è richiesta'}), 400
        
        # Genera l'embedding per la query
        query_embedding = embedding_model.encode(query).tolist()
        
        # Cerca gli oggetti simili nel database vettoriale
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=10
        )
        
        # Estrai i dettagli degli oggetti trovati
        items = []
        for result in search_results:
            items.append({
                'name': result.payload.get('name'),
                'description': result.payload.get('description'),
                'aura': result.payload.get('aura'),
                'cl': result.payload.get('cl'),
                'slot': result.payload.get('slot'),
                'cost': result.payload.get('cost'),
                'weight': result.payload.get('weight'),
                'requirements': result.payload.get('requirements'),
                'source': result.payload.get('source'),
                'url': result.payload.get('url'),
                'score': result.score
            })
        
        return jsonify({'items': items})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@generator_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Restituisce statistiche sul database degli oggetti magici.
    """
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        
        return jsonify({
            'total_items': collection_info.points_count,
            'collection_name': COLLECTION_NAME
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

