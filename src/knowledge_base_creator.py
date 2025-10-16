import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def create_vector_knowledge_base(data_files, model_name="all-MiniLM-L6-v2", output_dir="kb_vectors"):
    """
    Creates a FAISS vector knowledge base from JSON data files.
    """
    model = SentenceTransformer(model_name)
    all_texts = []
    metadata = []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path in data_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if isinstance(data, list): # Handle aonprd_spells.json which is a list of spells
            for spell in data:
                spell_text = f"Spell: {spell.get('name')}. Level: {spell.get('level')}. School: {spell.get('school')}. Description: {spell.get('description')}"
                if spell_text:
                    all_texts.append(spell_text)
                    metadata.append({"source": spell.get("source_url", "unknown"), "section": "Spells", "type": "spell", "name": spell.get("name"), "level": spell.get("level"), "school": spell.get("school"), "text": spell_text})
        else: # Handle other JSON files with 'sections'
            source_url = data.get("source_url", "unknown")
            
            for section in data.get("sections", []):
                section_heading = section.get("heading", "N/A")
                
                # Process paragraphs
                for content_item in section.get("content", []):
                    if content_item.get("type") == "paragraph":
                        text = content_item.get("text")
                        if text:
                            all_texts.append(text)
                            metadata.append({"source": source_url, "section": section_heading, "type": "paragraph", "text": text})
                
                # Process tables
                for table in section.get("tables", []):
                    table_str = json.dumps(table) # Convert table to string for embedding
                    if table_str:
                        all_texts.append(table_str)
                        metadata.append({"source": source_url, "section": section_heading, "type": "table", "content": table})

    if not all_texts:
        print("No text found to create embeddings.")
        return

    print(f"Generating embeddings for {len(all_texts)} text chunks...")
    embeddings = model.encode(all_texts, show_progress_bar=True)
    
    # FAISS index creation
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension) # Using L2 distance for similarity search
    index.add(embeddings)

    # Save index and metadata
    faiss.write_index(index, os.path.join(output_dir, "faiss_index.bin"))
    with open(os.path.join(output_dir, "kb_data.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    
    print(f"FAISS index and metadata saved to {output_dir}")

    # Create a simple query function for testing
    def query_knowledge_base(query_text, k=5):
        query_embedding = model.encode([query_text])
        distances, indices = index.search(query_embedding, k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1: # Ensure valid index
                results.append({
                    "score": 1 - distances[0][i], # Convert distance to similarity score
                    "metadata": metadata[idx]
                })
        return results
    
    return query_knowledge_base # Return the query function for immediate use or testing

if __name__ == "__main__":
    project_root_dir = os.path.dirname(os.path.abspath(__file__))
    data_files = [
        os.path.join(project_root_dir, "aonprd_magic_item_rules.json"),
        os.path.join(project_root_dir, "d20pfsrd_item_pricing.json"),
        os.path.join(project_root_dir, "aonprd_spells.json")
    ]
    
    # Ensure we are in the correct directory for data files
    # This part is now handled by passing full paths to create_vector_knowledge_base
    # os.chdir(project_root_dir) # No longer needed here
    
    # Ensure we are in the correct directory for data files


    query_func = create_vector_knowledge_base(data_files)

    if query_func:
        print("\nTesting knowledge base with a query:")
        results = query_func("How much does a +1 weapon cost?")
        for res in results:
            print(f"Score: {res['score']:.4f}")
            print(f"Source: {res['metadata']['source']}")
            print(f"Section: {res['metadata']['section']}")
            text_content = res['metadata'].get('text', res['metadata'].get('content'))
            print(f"Text: {text_content}\n")

