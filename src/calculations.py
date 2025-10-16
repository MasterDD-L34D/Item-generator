import json

# Placeholder for a more sophisticated knowledge base query function
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Global variables for the FAISS index and data
faiss_index = None
kb_data = []
embedding_model = None

def load_knowledge_base(output_dir: str):
    global faiss_index, kb_data, embedding_model
    if faiss_index is None or kb_data == [] or embedding_model is None:
        try:
            faiss_index = faiss.read_index(os.path.join(output_dir, "faiss_index.bin"))
            with open(os.path.join(output_dir, "kb_data.json"), "r", encoding="utf-8") as f:
                kb_data = json.load(f)
            embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("Knowledge base loaded successfully.")
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            faiss_index = None
            kb_data = []
            embedding_model = None

def query_knowledge_base_placeholder(query: str, top_k: int = 5) -> list[dict]:
    """
    Queries the FAISS index for relevant information.
    """
    global faiss_index, kb_data, embedding_model
    # The knowledge base should be loaded once during the application startup.
    # If it's not loaded, it means there was an issue during initialization.
    if faiss_index is None or kb_data == [] or embedding_model is None:
        print("Knowledge base not initialized. Cannot perform query.")
        return []

    query_embedding = embedding_model.encode([query])
    D, I = faiss_index.search(np.array(query_embedding).astype("float32"), top_k)

    results = []
    for i in I[0]:
        if i != -1:  # -1 indicates no result
            results.append(kb_data[i])
    return results

def calculate_market_price(item_properties: dict, kb_query_func=query_knowledge_base_placeholder) -> float:
    """
    Calculates the market price of a magic item based on its properties.
    This is a simplified example and needs to be expanded with actual Pathfinder rules.
    
    Args:
        item_properties (dict): A dictionary containing item properties like 'type', 'bonus', 'spell_effects'.
        kb_query_func (function): Function to query the knowledge base.
        
    Returns:
        float: The calculated market price in gp.
    """
    price = 0.0
    item_type = item_properties.get("type", "").lower()
    bonus = item_properties.get("bonus", 0)
    primary_spell_effect = item_properties.get("primary_spell_effect")
    other_effects = item_properties.get("other_effects", [])
    
    # Placeholder for a more sophisticated pricing logic based on Pathfinder rules
    # This section needs significant expansion to cover all item types and effects accurately.
    
    # Pricing for ability score bonuses
    for effect in other_effects:
        if "bonus di potenziamento +2 alla destrezza" in effect.lower() or "+2 dexterity bonus" in effect.lower():
            price += 4000  # +2 ability score item
        elif "bonus di potenziamento +4 alla destrezza" in effect.lower() or "+4 dexterity bonus" in effect.lower():
            price += 16000 # +4 ability score item
        elif "bonus di potenziamento +6 alla destrezza" in effect.lower() or "+6 dexterity bonus" in effect.lower():
            price += 36000 # +6 ability score item
        # Add more ability scores and bonuses as needed

    clean_spell_name = item_properties.get("clean_spell_name")
    spell_level = 0
    cl_for_spell = 0
    spell_school = "" # Initialize spell_school

    if clean_spell_name:
        cl_for_spell, aura_for_spell = determine_caster_level_and_aura(clean_spell_name, kb_query_func)
        
        # Infer spell_level from CL (Pathfinder 1E rule of thumb: CL = 2*Spell_Level - 1 for minimum CL)
        # This is a simplification; a more robust solution would store spell_level directly in KB.
        if cl_for_spell > 0:
            spell_level = (cl_for_spell + 1) // 2
        
        # Extract school from aura string if available
        if " " in aura_for_spell:
            spell_school = aura_for_spell.split(" ")[-1]
        
        if spell_level > 0 and cl_for_spell > 0:
            # Assuming 1/day use for now, based on the prompt example
            # Formula for 1/day spell-like ability: CL * Spell Level * 1800 / 5
            price += cl_for_spell * spell_level * 1800 / 5

    # Pricing for resistances
    for effect in other_effects:
        if "resistenza all\\\'energia (fuoco) 10" in effect.lower() or "fire resistance 10" in effect.lower():
            price += 4000 # Price for Fire Resistance 10

    return price

def calculate_crafting_cost(market_price: float) -> float:
    """
    Calculates the crafting cost, which is typically half the market price.
    """
    return market_price / 2.0

def determine_caster_level_and_aura(spell_name: str, kb_query_func=query_knowledge_base_placeholder) -> tuple[int, str]:
    """
    Determines the Caster Level (CL) and Aura based on the primary spell effect.
    This is a simplified example.
    
    Args:
        spell_name (str): The name of the primary spell effect.
        kb_query_func (function): Function to query the knowledge base.
        
    Returns:
        tuple[int, str]: A tuple containing (caster_level, aura_description).
    """
    # In a real scenario, this would query the KB for spell details
    # For now, we'll use a very basic mapping
    spell_name_lower = spell_name.lower()
    
    caster_level = 1 # Default
    aura = "Minore (Nessuna)"

    # Clean spell name for querying
    # Handle spell_name being a dictionary (if passed directly from GPT response)
    if isinstance(spell_name, dict):
        spell_name_from_dict = spell_name.get("spell_name", "")
        clean_spell_name = spell_name_from_dict.replace("\"", "").replace("**", "").replace("*", "").strip()
    else:
        clean_spell_name = spell_name.replace("\"", "").replace("**", "").replace("*", "").strip()
    if "(" in clean_spell_name:
        clean_spell_name = clean_spell_name.split("(")[0].strip()

    # Query KB for spell details
    kb_results = kb_query_func(f"Pathfinder 1E spell {clean_spell_name} details")
    spell_level = 0
    spell_school = ""

    # Extract spell level
    for i in range(1, 10): # Check for spell levels 1-9
            if f"level {i}" in text_content or f"{i}th-level" in text_content or f"{i}º livello" in text_content: spell_level = max(spell_level, i)


        # Extract spell school and determine aura strength
    if "abjuration" in text_content: spell_school = "Abjuration"
    elif "conjuration" in text_content: spell_school = "Conjuration"
    elif "divination" in text_content: spell_school = "Divination"
    elif "enchantment" in text_content: spell_school = "Incantamento"
    elif "evocation" in text_content: spell_school = "Invocazione"
    elif "illusion" in text_content: spell_school = "Illusione"
    elif "necromancy" in text_content: spell_school = "Necromanzia"
    elif "transmutation" in text_content: spell_school = "Trasmutazione"

    # Determine Caster Level based on spell level (minimum CL for spell level)
    if spell_level == 1: caster_level = 1
    elif spell_level == 2: caster_level = 3
    elif spell_level == 3: caster_level = 5
    elif spell_level == 4: caster_level = 7
    elif spell_level == 5: caster_level = 9
    elif spell_level == 6: caster_level = 11
    elif spell_level == 7: caster_level = 13
    elif spell_level == 8: caster_level = 15
    elif spell_level == 9: caster_level = 17

    # Determine Aura strength based on CL
    if spell_school:
        if caster_level >= 11: aura = f"Forte {spell_school}"
        elif caster_level >= 7: aura = f"Moderata {spell_school}"
        elif caster_level >= 4: aura = f"Debole {spell_school}"
        elif caster_level >= 1: aura = f"Minore {spell_school}"
    

    return caster_level, aura


def validate_item(item_data: dict) -> tuple[bool, list[str]]:
    """
    Validates an item against Pathfinder 1E rules and the provided checklist.
    This is a placeholder and needs to be fully implemented.
    
    Args:
        item_data (dict): The item data in JSON format.
        
    Returns:
        tuple[bool, list[str]]: A tuple where the first element is True if valid, False otherwise,
                                and the second element is a list of error messages.
    """
    errors = []
    is_valid = True

    # 1. Solo Paizo PF1e (niente 3PP); se PFS ON, verifica legalità specifica del modulo.
    # (Requires KB lookup or specific flags in item_data)
    if item_data.get("source_type") == "3PP": # Example check
        errors.append("Item uses 3rd-party content, which is not allowed.")
        is_valid = False

    # 2. Slot valido e unico; evita conflitti con Big Six se richiesto dal format torneo.
    valid_slots = ["Collo", "Testa", "Cintura", "Corpo", "Torso", "Piedi", "Mani", "Fascia", "Occhi", "Spalle", "Polso", "Anello", "Arma", "Armatura", "Scudo", "Neck", "Head", "Belt", "Body", "Chest", "Feet", "Hands", "Headband", "Eyes", "Shoulders", "Wrist", "Ring", "Weapon", "Armor", "Shield"]
    if item_data.get("slot") and item_data["slot"] not in valid_slots:
        errors.append(f"Invalid slot: {item_data['slot']!r}.")
        is_valid = False

    # 3. LI coerente con effetti e incantesimi; Aura/Scuola tradotta correttamente.
    # This would require comparing item_data["CL"] with derived CL from spells
    # For now, a basic check:
    if not isinstance(item_data.get("CL"), int) or item_data["CL"] < 1:
        errors.append("Caster Level (CL) is missing or invalid.")
        is_valid = False
    
    # 4. Prezzo e Costo calcolati correttamente (Costo = Prezzo/2).
    market_price = item_data.get("market_price_gp")
    craft_cost = item_data.get("crafting_cost_gp")
    if market_price and craft_cost and abs(craft_cost - (market_price / 2.0)) > 0.01:
        errors.append(f"Crafting cost ({craft_cost}) is not half of market price ({market_price}).")
        is_valid = False

    # 5. Uso/Attivazione chiaro, con azione esplicita e durata; TS/SR se replica incantesimo.
    if not item_data.get("activation") or not item_data.get("duration"):
        errors.append("Activation or duration is missing.")
        is_valid = False

    # 6. Interazioni/Stacking specifica il tipo di bonus e la non-cumulabilità dove previsto.
    # (Requires more complex logic, possibly KB lookup for bonus types)

    # 7. Nota Playtest obbligatoria (1 riga) per rischi/abusi.
    if not item_data.get("playtest_note"):
        errors.append("Playtest note is missing.")
        is_valid = False

    # 8. Rarità definita secondo legenda; marca [HR] se necessario.
    valid_rarities = ["Comune", "Non comune", "Raro", "Unico"]
    if item_data.get("rarity") and item_data["rarity"] not in valid_rarities:
        errors.append(f"Invalid rarity: {item_data['rarity']}.")
        is_valid = False

    # 9. Terminologia: PF, LI, scuole IT; incantesimi *in corsivo*, condizioni **in grassetto**.
    # (This is mostly a post-processing concern, but can be checked for keywords)

    # 10. Navigazione: titolo con emoji + ancora HTML coerente.
    # (Post-processing concern)

    return is_valid, errors


if __name__ == "__main__":
    # Example usage
    print("--- Testing Calculations Module ---")

    # Test calculate_market_price
    item_props_weapon = {"type": "weapon", "bonus": 1}
    price_weapon = calculate_market_price(item_props_weapon)
    print(f"Market price for +1 weapon: {price_weapon} gp")
    print(f"Crafting cost for +1 weapon: {calculate_crafting_cost(price_weapon)} gp\n")

    item_props_armor = {"type": "armor", "bonus": 1}
    price_armor = calculate_market_price(item_props_armor)
    print(f"Market price for +1 armor: {price_armor} gp")
    print(f"Crafting cost for +1 armor: {calculate_crafting_cost(price_armor)} gp\n")

    # Test determine_caster_level_and_aura
    cl_flame, aura_flame = determine_caster_level_and_aura("flame blade")
    print(f"Flame Blade - CL: {cl_flame}, Aura: {aura_flame}")

    cl_resist, aura_resist = determine_caster_level_and_aura("resist energy")
    print(f"Resist Energy - CL: {cl_resist}, Aura: {aura_resist}\n")

    # Test validate_item
    valid_item_example = {
        "name": "Amulet of the Valiant Flame",
        "type": "Wondrous Item",
        "slot": "Neck",
        "aura": "Moderate Evocation",
        "CL": 9,
        "market_price_gp": 12000,
        "crafting_cost_gp": 6000,
        "description": "This golden amulet glows...",
        "activation": "swift action",
        "duration": "1 round",
        "playtest_note": "May be strong for low-level characters.",
        "rarity": "Non comune",
        "source_type": "Paizo PF1e"
    }
    is_valid, errors = validate_item(valid_item_example)
    print(f"Valid item example validation: {is_valid}")
    if errors:
        print("Errors:", errors)

    invalid_item_example = {
        "name": "Broken Amulet",
        "type": "Wondrous Item",
        "slot": "Invalid Slot",
        "CL": 0,
        "market_price_gp": 100,
        "crafting_cost_gp": 10,
        "description": "",
        "playtest_note": "",
        "rarity": "Legendary",
        "source_type": "3PP"
    }
    is_valid, errors = validate_item(invalid_item_example)
    print(f"Invalid item example validation: {is_valid}")
    if errors:
        print("Errors:", errors)

