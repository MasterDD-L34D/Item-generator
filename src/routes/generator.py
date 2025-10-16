from flask import Blueprint, request, jsonify
from qdrant_client import QdrantClient
import os
import json
from openai import OpenAI

generator_bp = Blueprint('generator', __name__)

# Inizializza i componenti necessari una sola volta all'avvio dell'applicazione
# Il percorso di qdrant_storage sarà relativo alla root del progetto Flask
QDRANT_STORAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qdrant_storage")
qdrant_client = QdrantClient(path=QDRANT_STORAGE_PATH)
openai_client = OpenAI()

COLLECTION_NAME = "pathfinder_magic_items"

def get_embedding_from_openai(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002", 
        input=text
    )
    return response.data[0].embedding

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
        
        # Genera l'embedding per la descrizione dell'utente usando l'API di OpenAI
        query_embedding = get_embedding_from_openai(user_description)
        
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
        
        prompt = f"""Sei un esperto game designer di Pathfinder 1E. Crea un nuovo oggetto magico basato sulla seguente richiesta dell'utente:\n\n\"{user_description}\"\n\n{context}\n\nCrea un oggetto magico completamente nuovo e originale che si ispiri agli esempi forniti ma che sia unico. L'oggetto deve essere bilanciato per Pathfinder 1E e includere:\n- Nome dell'oggetto\n- Aura (scuola di magia e intensità)\n- Caster Level (CL)\n- Slot (dove si indossa/usa l'oggetto)\n- Prezzo in gp\n- Peso\n- Descrizione dettagliata delle capacità e degli effetti\n- Requisiti di costruzione\n- Costo di costruzione\n\nFormatta la risposta in modo chiaro e strutturato, seguendo lo stile degli oggetti magici di Pathfinder 1E."""

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
        
        # Genera l'embedding per la query usando l'API di OpenAI
        query_embedding = get_embedding_from_openai(query)
        
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

