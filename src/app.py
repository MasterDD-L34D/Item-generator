import streamlit as st
import json
import os
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# Configurazione della pagina
st.set_page_config(
    page_title="Pathfinder 1E Magic Items Generator",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Titolo dell'applicazione
st.title("🎲 Pathfinder 1E Magic Items Generator")
st.markdown("**Generatore ottimizzato di oggetti magici per Pathfinder 1E RPG**")

# Inizializzazione del database vettoriale e del modello di embedding
@st.cache_resource
def initialize_qdrant():
    """Inizializza il client Qdrant e il modello di embedding."""
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    qdrant_client = QdrantClient(":memory:")
    return qdrant_client, embedding_model

@st.cache_data
def load_magic_items():
    """Carica gli oggetti magici dal file JSON."""
    data_file = "parsed_data/all_magic_items.json"
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            try:
                magic_items = json.load(f)
                return magic_items
            except json.JSONDecodeError:
                st.error(f"Errore di decodifica JSON nel file: {data_file}")
                return []
    else:
        st.error(f"File di dati non trovato: {data_file}. Assicurati di aver eseguito data_parser.py.")
        return []

def populate_qdrant(qdrant_client, embedding_model, magic_items):
    """Popola il database vettoriale Qdrant con gli oggetti magici."""
    COLLECTION_NAME = "pathfinder_magic_items"
    
    # Crea la collezione se non esiste
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
    except:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        
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
        
        if points:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                wait=True,
                points=points,
            )

def search_magic_items(qdrant_client, embedding_model, query_text, top_k=10):
    """Cerca oggetti magici nel database vettoriale basandosi su una query testuale."""
    COLLECTION_NAME = "pathfinder_magic_items"
    query_embedding = embedding_model.encode(query_text, convert_to_tensor=False).tolist()

    search_result = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True,
    )

    return search_result

def optimize_magic_items(search_results, criteria):
    """Applica criteri di ottimizzazione ai risultati della ricerca."""
    # Esempio di criterio: preferire oggetti con un CL (Caster Level) più alto
    if "high_cl" in criteria:
        search_results.sort(key=lambda x: x.payload.get("cl", 0) if isinstance(x.payload.get("cl"), int) else 0, reverse=True)

    # Esempio di criterio: preferire oggetti con un costo inferiore (se disponibile e numerico)
    if "low_cost" in criteria:
        def get_numeric_cost(item):
            cost_str = item.payload.get("cost", "N/A").replace(" gp", "").replace(",", "")
            try:
                return float(cost_str)
            except (ValueError, TypeError):
                return float("inf")
        search_results.sort(key=get_numeric_cost)

    return search_results

# Carica i dati
qdrant_client, embedding_model = initialize_qdrant()
magic_items = load_magic_items()

if magic_items:
    populate_qdrant(qdrant_client, embedding_model, magic_items)
    
    # Sidebar per i filtri e le opzioni
    st.sidebar.header("Opzioni di Ricerca")
    
    # Input per la query di ricerca
    query = st.sidebar.text_input("Cerca oggetti magici:", placeholder="Es: Anello che aumenta la forza")
    
    # Numero di risultati da visualizzare
    top_k = st.sidebar.slider("Numero di risultati:", min_value=1, max_value=50, value=10)
    
    # Criteri di ottimizzazione
    st.sidebar.subheader("Criteri di Ottimizzazione")
    high_cl = st.sidebar.checkbox("Preferisci CL alto")
    low_cost = st.sidebar.checkbox("Preferisci costo basso")
    
    criteria = []
    if high_cl:
        criteria.append("high_cl")
    if low_cost:
        criteria.append("low_cost")
    
    # Pulsante di ricerca
    if st.sidebar.button("Cerca"):
        if query:
            with st.spinner("Ricerca in corso..."):
                results = search_magic_items(qdrant_client, embedding_model, query, top_k=top_k)
                
                if criteria:
                    results = optimize_magic_items(results, criteria)
                
                st.subheader(f"Risultati per: '{query}'")
                
                if results:
                    for i, item in enumerate(results):
                        with st.expander(f"{i+1}. {item.payload.get('name', 'N/A')} (CL: {item.payload.get('cl', 'N/A')}, Costo: {item.payload.get('cost', 'N/A')})"):
                            st.markdown(f"**Nome:** {item.payload.get('name', 'N/A')}")
                            st.markdown(f"**Fonte:** {item.payload.get('source', 'N/A')}")
                            st.markdown(f"**Aura:** {item.payload.get('aura', 'N/A')}")
                            st.markdown(f"**CL:** {item.payload.get('cl', 'N/A')}")
                            st.markdown(f"**Slot:** {item.payload.get('slot', 'N/A')}")
                            st.markdown(f"**Peso:** {item.payload.get('weight', 'N/A')}")
                            st.markdown(f"**Costo:** {item.payload.get('cost', 'N/A')}")
                            st.markdown(f"**Descrizione:** {item.payload.get('description', 'N/A')}")
                            st.markdown(f"**Costruzione:** {item.payload.get('construction', 'N/A')}")
                            st.markdown(f"**Requisiti:** {item.payload.get('requirements', 'N/A')}")
                            st.markdown(f"**URL:** [{item.payload.get('url', 'N/A')}]({item.payload.get('url', 'N/A')})")
                else:
                    st.warning("Nessun risultato trovato per la tua ricerca.")
        else:
            st.warning("Inserisci una query di ricerca.")
    
    # Informazioni sull'applicazione
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Questa applicazione utilizza una knowledge base RAG e algoritmi di ottimizzazione "
        "per aiutarti a trovare gli oggetti magici più adatti per il tuo personaggio di Pathfinder 1E RPG."
    )
else:
    st.error("Nessun oggetto magico disponibile. Esegui data_parser.py per popolare il database.")

