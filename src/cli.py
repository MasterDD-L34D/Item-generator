import json
import os
import sys
from gpt_agent import initialize_knowledge_base, generate_magic_item_draft, process_and_validate_item
from post_processor import setup_jinja_env, render_mic_standard, render_tournament_format, create_template_files

def main():
    print("Benvenuto nel Generatore di Oggetti Magici per Pathfinder 1E!")
    project_root_dir = os.path.dirname(os.path.abspath(__file__))

    print("Inizializzazione della Knowledge Base...")
    kb_func = initialize_knowledge_base(project_root_dir)

    if not kb_func:
        print("Errore: Impossibile inizializzare la Knowledge Base. Uscita.")
        return

    # Ensure templates exist and setup Jinja2 environment
    create_template_files(project_root_dir)
    jinja_env = setup_jinja_env(project_root_dir)

    # If a prompt is provided as a command-line argument, process it once and exit.
    if len(sys.argv) > 1:
        user_prompt = sys.argv[1]
        process_single_request(user_prompt, kb_func, jinja_env, project_root_dir)
    else:
        # Otherwise, enter interactive mode.
        while True:
            user_prompt = input("\nDescrivi l\"oggetto magico che desideri creare (o \"esci\" per terminare): ")
            if user_prompt.lower() == 'esci':
                break
            process_single_request(user_prompt, kb_func, jinja_env, project_root_dir)

    print("Grazie per aver usato il Generatore di Oggetti Magici!")

def process_single_request(user_prompt: str, kb_func, jinja_env, project_root_dir: str):
    print(f"Generazione bozza per: {user_prompt}")
    item_draft = generate_magic_item_draft(user_prompt, kb_func, project_root_dir)

    if item_draft:
        print("Bozza generata. Elaborazione e validazione...")
        final_item = process_and_validate_item(item_draft, project_root_dir, kb_func)

        print("\n--- Oggetto Magico Generato (Formato MIC Standard) ---")
        mic_output = render_mic_standard(final_item, jinja_env)
        print(mic_output)

        print("\n--- Oggetto Magico Generato (Formato Torneo) ---")
        tournament_output = render_tournament_format(final_item, jinja_env)
        print(tournament_output)

        if not final_item["is_valid"]:
            print("\n--- Errori di Validazione ---")
            for error in final_item["validation_errors"]:
                print(f"- {error}")
        else:
            print("\nL\"oggetto è stato validato con successo.")
    else:
        print("Fallita la generazione della bozza dell\"oggetto.")

if __name__ == "__main__":
    main()
