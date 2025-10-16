import os
import json
from openai import OpenAI
from knowledge_base_creator import create_vector_knowledge_base # Assuming this can be imported or re-initialized
from calculations import calculate_market_price, calculate_crafting_cost, determine_caster_level_and_aura, validate_item

# Initialize OpenAI client
client = OpenAI()

# Global variable for the knowledge base query function
kb_query_function = None

def initialize_knowledge_base(project_root_dir: str):
    global kb_query_function
    if kb_query_function is None:
        data_files = [
            os.path.join(project_root_dir, "aonprd_magic_item_rules.json"),
            os.path.join(project_root_dir, "d20pfsrd_item_pricing.json")
        ]
        # The create_vector_knowledge_base function expects to be called from the directory
        # where the data files are, or it needs absolute paths. Let's ensure absolute paths.
        kb_query_function = create_vector_knowledge_base(data_files, output_dir=os.path.join(project_root_dir, "kb_vectors"))
    return kb_query_function

def generate_magic_item_draft(user_prompt: str, kb_query_func, project_root_dir: str) -> dict:
    """
    Generates a draft of a magic item using GPT, incorporating knowledge base context.
    """
    # Retrieve relevant information from the knowledge base based on the user prompt
    kb_results = kb_query_func(user_prompt)
    context = ""
    if kb_results:
        context = "Relevant Pathfinder 1E rules and information:\n"
        for res in kb_results:
            context += f"- Source: {res['metadata']['source']}, Section: {res['metadata']['section']}\n"
            context += f"  Content: {res['metadata'].get('text', res['metadata'].get('content'))}\n"

    system_message = f"""
You are an expert Pathfinder 1E game master and item creator. Your task is to generate a magic item based on the user's request, strictly adhering to Pathfinder 1E rules. 
First, generate the item's name, type, slot, and a brief description. Then, outline its primary magical effects. 
Do NOT include specific GP costs, CL, or Aura in this initial draft, as those will be calculated by an external module. 
Focus on creativity and adherence to Pathfinder lore and mechanics. 
{context}
Generate the item in a JSON format with the following keys: name, type, slot, description, primary_spell_effect (if any), other_effects (list of strings), rarity (use Italian terms: "Comune", "Non comune", "Raro", "Unico"), source_type (default to "Paizo PF1e"), activation, duration, playtest_note.
"""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash", # Using a suitable model
            messages=messages,
            response_format={"type": "json_object"}
        )
        raw_response_content = response.choices[0].message.content.strip()
        if raw_response_content.startswith("```json") and raw_response_content.endswith("```"):
            raw_response_content = raw_response_content[len("```json"):-len("```")].strip()
        print(f"Raw GPT response content: {raw_response_content}")
        item_draft = json.loads(raw_response_content)
        return item_draft
    except Exception as e:
        print(f"Error generating item draft with GPT: {e}")
        return None

def process_and_validate_item(item_draft: dict, project_root_dir: str, kb_query_func) -> dict:
    """
    Takes an item draft, calculates derived properties, and validates it.
    """
    processed_item = item_draft.copy()

    spell_name_for_cl_aura = None
    if processed_item.get("primary_spell_effect"):
        spell_effect_str = processed_item["primary_spell_effect"]
        import re
        if isinstance(spell_effect_str, dict):
            spell_effect_str = spell_effect_str.get("spell_name", "")

        # Improved regex to capture spell names within single or double quotes
        match = re.search(r"\'(.*?)\'", spell_effect_str) # Prioritize single quotes
        if not match:
            match = re.search(r"\"(.*?)\"", spell_effect_str) # Then double quotes
        
        if match:
            spell_name_for_cl_aura = match.group(1)
        else:
            # Fallback: try to find the word after 'incantesimo' or 'spell'
            match = re.search(r"incantesimo\s+\b(\w+)\b", spell_effect_str, re.IGNORECASE)
            if not match:
                match = re.search(r"spell\s+\b(\w+)\b", spell_effect_str, re.IGNORECASE)
            if match:
                spell_name_for_cl_aura = match.group(1)
            else:
                spell_name_for_cl_aura = spell_effect_str # Last resort fallback

    # Calculate market price and crafting cost
    # These calculations are simplified and need to be refined based on actual Pathfinder rules
    processed_item["market_price_gp"] = calculate_market_price({
        "type": item_draft.get("type"),
        "bonus": item_draft.get("bonus", 0), # Assuming 'bonus' might be in draft for weapons/armor
        "primary_spell_effect": item_draft.get("primary_spell_effect"),
        "clean_spell_name": spell_name_for_cl_aura,
        "other_effects": item_draft.get("other_effects", [])
    }, kb_query_func=kb_query_func)
    processed_item["crafting_cost_gp"] = calculate_crafting_cost(processed_item["market_price_gp"])

    # Determine Caster Level and Aura
    if spell_name_for_cl_aura:
        cl, aura = determine_caster_level_and_aura(spell_name_for_cl_aura, kb_query_func=kb_query_func)
        processed_item["CL"] = cl
        processed_item["aura"] = aura
    else:
        processed_item["CL"] = 1 # Default CL if no spell effect
        processed_item["aura"] = "Faint (None)"

    # Validate the item
    is_valid, errors = validate_item(processed_item)
    processed_item["is_valid"] = is_valid
    processed_item["validation_errors"] = errors

    return processed_item


if __name__ == "__main__":
    print("Initializing knowledge base...")
    project_root_dir = os.path.dirname(os.path.abspath(__file__))
    kb_func = initialize_knowledge_base(project_root_dir)

    if kb_func:
        user_request = "Crea un amuleto magico con tema fuoco, che dia resistenza al fuoco e un bonus ai tiri per colpire."
        print(f"\nGenerating item draft for: {user_request}")
        item_draft = generate_magic_item_draft(user_request, kb_func, project_root_dir)

        if item_draft:
            print("\nInitial GPT Draft:")
            print(json.dumps(item_draft, indent=2, ensure_ascii=False))

            print("\nProcessing and validating item...")
            final_item = process_and_validate_item(item_draft, project_root_dir, kb_func)

            print("\nFinal Processed Item:")
            print(json.dumps(final_item, indent=2, ensure_ascii=False))

            if not final_item["is_valid"]:
                print("\nValidation Errors:")
                for error in final_item["validation_errors"]:
                    print(f"- {error}")
        else:
            print("Failed to generate item draft.")
    else:
        print("Failed to initialize knowledge base. Cannot proceed.")

