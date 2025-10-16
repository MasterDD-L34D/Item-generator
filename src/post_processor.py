from jinja2 import Environment, FileSystemLoader
import os

# Mapping for schools of magic (EN to IT)
SCHOOL_TRANSLATION = {
    "Abjuration": "Abjurazione",
    "Conjuration": "Evocazione",
    "Divination": "Divinazione",
    "Enchantment": "Ammaliamento",
    "Evocation": "Invocazione",
    "Illusion": "Illusione",
    "Necromancy": "Necromanzia",
    "Transmutation": "Trasmutazione",
    "Universal": "Universale"
}

# Emoji mapping for item categories
CATEGORY_EMOJI = {
    "Wondrous Item": "✨",
    "Weapon": "⚔️",
    "Armor": "🛡️",
    "Ring": "💍",
    "Rod": "🪄",
    "Staff": "🌿",
    "Scroll": "📜",
    "Potion": "🧪",
    "Wand": "🪄"
}

def setup_jinja_env(template_dir):
    """Sets up the Jinja2 environment."""
    return Environment(loader=FileSystemLoader(template_dir))

def render_mic_standard(item_data: dict, env: Environment) -> str:
    """Renders the item in MIC Standard format."""
    template = env.get_template("mic_standard_template.md.j2")
    return template.render(item=item_data)

def render_tournament_format(item_data: dict, env: Environment) -> str:
    """Renders the item in Tournament Format."""
    template = env.get_template("tournament_format_template.md.j2")
    
    # Pre-process data for the template
    processed_data = item_data.copy()
    
    # Translate school of magic
    aura_parts = processed_data.get("aura", "").split()
    if len(aura_parts) > 1 and aura_parts[1] in SCHOOL_TRANSLATION:
        aura_parts[1] = SCHOOL_TRANSLATION[aura_parts[1]]
        processed_data["aura_it"] = " ".join(aura_parts)
    else:
        processed_data["aura_it"] = processed_data.get("aura", "")

    # Add category emoji
    processed_data["category_emoji"] = CATEGORY_EMOJI.get(processed_data.get("type"), "")

    return template.render(item=processed_data)


def create_template_files(template_dir):
    """Creates the Jinja2 template files if they don't exist."""
    mic_template_content = """
🧿 **{{ item.name }}**  
**Slot:** {{ item.slot }}  
**Aura:** {{ item.aura }}  
**CL:** {{ item.CL }}th  
**Prezzo:** {{ item.market_price_gp }} gp  
**Descrizione:**  
{{ item.description }}

**Costruzione:**  
Craft Wondrous Item, *{{ item.primary_spell_effect }}*; **Costo:** {{ item.crafting_cost_gp }} gp
"""

    tournament_template_content = """
### {{ item.category_emoji }} {{ item.name }}
📦 {{ item.slot }} • LI {{ item.CL }}° • Prezzo {{ item.market_price_gp }} gp • Peso — lb • Rarità: {{ item.rarity }}
**Aura/Scuola:** {{ item.aura_it }}
**Descrizione:** {{ item.description }}
**Uso/Attivazione:** {{ item.activation }} • **Durata:** {{ item.duration }}
**Effetto (1 riga):** {{ item.other_effects[0] if item.other_effects else "" }}
**Dettaglio:**
{% for effect in item.other_effects %}- {{ effect }}
{% endfor %}
**Costruzione:** Craft Wondrous Item, *{{ item.primary_spell_effect }}*; Costo: {{ item.crafting_cost_gp }} gp
**Nota Playtest:** {{ item.playtest_note }}
"""

    mic_template_path = os.path.join(template_dir, "mic_standard_template.md.j2")
    if not os.path.exists(mic_template_path):
        with open(mic_template_path, "w", encoding="utf-8") as f:
            f.write(mic_template_content)
        print(f"Created {mic_template_path}")

    tournament_template_path = os.path.join(template_dir, "tournament_format_template.md.j2")
    if not os.path.exists(tournament_template_path):
        with open(tournament_template_path, "w", encoding="utf-8") as f:
            f.write(tournament_template_content)
        print(f"Created {tournament_template_path}")


if __name__ == "__main__":
    # Example usage
    print("--- Testing Post-Processor Module ---")

    # Ensure we are in the correct directory for templates
    project_root_dir = os.path.dirname(os.path.abspath(__file__))
    create_template_files(project_root_dir)
    jinja_env = setup_jinja_env(project_root_dir)

    # Example item data (from gpt_agent.py output)
    example_item = {
        "name": "Amulet of the Valiant Flame",
        "type": "Wondrous Item",
        "slot": "Neck",
        "aura": "Moderate Evocation",
        "CL": 9,
        "market_price_gp": 12000,
        "crafting_cost_gp": 6000,
        "description": "This golden amulet glows with a faint red light. Once per day, the wearer may activate it as a swift action to deal +1d6 fire damage on all melee attacks for 1 round. Fire resistance 5 while active.",
        "primary_spell_effect": "flame blade",
        "other_effects": ["+1d6 fire damage on melee attacks for 1 round", "Fire resistance 5"],
        "activation": "swift action",
        "duration": "1 round",
        "playtest_note": "May be strong for low-level characters.",
        "rarity": "Non comune",
        "is_valid": True,
        "validation_errors": []
    }

    print("\n--- MIC Standard Format ---")
    mic_output = render_mic_standard(example_item, jinja_env)
    print(mic_output)

    print("\n--- Tournament Format ---")
    tournament_output = render_tournament_format(example_item, jinja_env)
    print(tournament_output)

