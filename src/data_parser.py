
import requests
from bs4 import BeautifulSoup
import json
import os
import re

BASE_URL = "http://www.aonprd.com/"

def get_category_links(url):
    """
    Recupera e analizza la pagina principale degli oggetti magici per estrarre i link delle categorie.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero dell\"URL {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    main_content = soup.find('div', {'id': 'main'})
    if not main_content:
        print("Impossibile trovare il contenuto principale per le categorie di oggetti magici.")
        return []

    links = []
    # I link delle categorie sono in un h2 che contiene il testo delle categorie
    category_h2 = main_content.find('h2', string=lambda text: text and 'Armor | Artifacts | Cursed Items' in text)
    if category_h2:
        for a in category_h2.find_all('a', href=True):
            href = a.get('href')
            if href:
                if not href.startswith('http'):
                    full_href = f"{BASE_URL}{href}"
                else:
                    full_href = href
                links.append(full_href)
    else:
        print("Impossibile trovare l'intestazione H2 con i link delle categorie. Tentativo di estrazione alternativa.")
        # Fallback se l'h2 specifico non viene trovato, cerca tutti i link nel main_content
        for a in main_content.find_all('a', href=True):
            href = a.get('href')
            # Filtra solo i link che sembrano essere categorie di oggetti magici
            if any(cat in href for cat in ['MagicArmor.aspx', 'MagicArtifacts.aspx', 'MagicCursed.aspx',
                                         'MagicIntelligent.aspx', 'MagicPotions.aspx', 'MagicRings.aspx',
                                         'MagicRods.aspx', 'MagicStaves.aspx', 'MagicWeapons.aspx',
                                         'MagicWondrous.aspx', 'MagicOther.aspx']):
                if not href.startswith('http'):
                    full_href = f"{BASE_URL}{href}"
                else:
                    full_href = href
                links.append(full_href)
    
    return list(set(links))

def get_links_from_page(page_url):
    """
    Recupera una pagina e separa i link agli oggetti magici dai link alle sottocategorie.
    """
    try:
        response = requests.get(page_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero dell\"URL della pagina {page_url}: {e}")
        return [], []

    soup = BeautifulSoup(response.text, 'html.parser')
    item_links = []
    sub_category_links = []

    main_content_div = soup.find('div', {'id': 'main'})
    if main_content_div:
        for a_tag in main_content_div.find_all('a', href=True):
            href = a_tag['href']
            if not href.startswith('http'):
                full_href = f"{BASE_URL}{href}"
            else:
                full_href = href

            if href.startswith('#') or href.startswith('javascript'):
                continue

            # Filtra i link che puntano a pagine di oggetti specifici
            if (
                ('Display.aspx' in href or 'ItemName=' in href or 'FinalName=' in href) and
                not any(exclude_pattern in href for exclude_pattern in [
                    'SpellDisplay.aspx', 'ClassDisplay.aspx', 'FeatDisplay.aspx', 'MonsterDisplay.aspx',
                    'TraitDisplay.aspx', 'SkillDisplay.aspx', 'MythicDisplay.aspx', 'DeityDisplay.aspx',
                    'Rules.aspx', 'FAQ.aspx', 'Equipment.aspx', 'MagicItems.aspx'
                ])
            ):
                item_links.append(full_href)
            # Filtra i link che puntano a sottocategorie (pagine .aspx che non sono pagine di oggetti specifici)
            elif (
                href.endswith('aspx') and
                not any(cat_page in href for cat_page in [
                    'MagicItems.aspx', 'MagicArmor.aspx', 'MagicArtifacts.aspx', 'MagicCursed.aspx',
                    'MagicIntelligent.aspx', 'MagicPotions.aspx', 'MagicRings.aspx', 'MagicRods.aspx',
                    'MagicStaves.aspx', 'MagicWeapons.aspx', 'MagicWondrous.aspx', 'MagicOther.aspx'
                ]) and
                not any(item_link_pattern in href for item_link_pattern in ['Display.aspx', 'ItemName=', 'FinalName='])
            ):
                sub_category_links.append(full_href)
    
    return list(set(item_links)), list(set(sub_category_links))

def parse_item_details(item_url):
    """
    Analizza i dettagli di un singolo oggetto magico dalla sua pagina.
    """
    try:
        response = requests.get(item_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero dell\"URL dell\"oggetto {item_url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    item_data = {'url': item_url}

    main_content = soup.find('div', {'id': 'main'})
    if not main_content:
        item_data['name'] = "Unknown Item"
        return item_data

    # Estrazione del nome dell'oggetto
    # Il nome dell'oggetto è spesso nel primo h1 all'interno del main_content
    item_name_h1 = main_content.find('h1')
    if item_name_h1:
        item_data['name'] = item_name_h1.get_text(strip=True)
    else:
        item_data['name'] = "Unknown Item"

    # Inizializzazione dei campi
    item_data['source'] = "N/A"
    item_data['aura'] = "N/A"
    item_data['cl'] = "N/A"
    item_data['slot'] = "N/A"
    item_data['weight'] = "N/A"
    item_data['description'] = "N/A"
    item_data['construction'] = "N/A"
    item_data['requirements'] = "N/A"
    item_data['cost'] = "N/A"

    # Estrazione dei dettagli principali (Source, Aura, CL, Slot, Weight, Price)
    details_text = ''
    # Cerca i dettagli nel testo che segue l'h1 o in un paragrafo subito dopo
    if item_name_h1:
        # Prova a prendere il testo dai paragrafi successivi all'h1 fino alla descrizione
        for sibling in item_name_h1.find_next_siblings():
            if sibling.name == 'h3' and sibling.get_text(strip=True) == 'Description':
                break
            if sibling.name == 'p':
                details_text += sibling.get_text(strip=True) + ' '
    
    # Fallback se non si trovano dettagli dopo l'h1, cerca nel main_content
    if not details_text:
        details_p = main_content.find('p', string=re.compile(r'Source|Aura|CL|Slot|Weight|Price'))
        if details_p:
            details_text = details_p.get_text()

    source_match = re.search(r'Source\s*(.*?)(?=\s*Aura|\s*CL|\s*Slot|\s*Price|\s*Weight|$)\s*', details_text)
    if source_match:
        item_data['source'] = source_match.group(1).strip()

    aura_match = re.search(r'Aura\s*(.*?)(?=\s*CL|\s*Slot|\s*Price|\s*Weight|$)\s*', details_text)
    if aura_match:
        item_data['aura'] = aura_match.group(1).strip()

    cl_match = re.search(r'CL\s*(\d+)(?:st|nd|rd|th)?', details_text)
    if cl_match:
        item_data['cl'] = int(cl_match.group(1))

    slot_match = re.search(r'Slot\s*(.*?)(?=\s*Price|\s*Weight|$)\s*', details_text)
    if slot_match:
        item_data['slot'] = slot_match.group(1).strip()

    price_match = re.search(r'Price\s*([\d,]+\s*gp)', details_text)
    if price_match:
        item_data['cost'] = price_match.group(1).strip()

    weight_match = re.search(r'Weight\s*(.*?)(?=\s*$)', details_text)
    if weight_match:
        item_data['weight'] = weight_match.group(1).strip()

    # Estrazione della Descrizione
    description_heading = soup.find('h3', string='Description')
    if description_heading:
        description_text = []
        for sibling in description_heading.find_next_siblings():
            if sibling.name == 'h3' and sibling.get_text(strip=True) == 'Construction':
                break
            if sibling.name == 'p': # Assicurati di prendere solo i paragrafi per la descrizione
                description_text.append(sibling.get_text(strip=True))
        item_data['description'] = "\n".join(description_text)

    # Estrazione della Costruzione e Requisiti/Costo
    construction_heading = soup.find('h3', string='Construction')
    if construction_heading:
        construction_text = []
        for sibling in construction_heading.find_next_siblings():
            if sibling.name == 'p':
                construction_text.append(sibling.get_text(strip=True))
            elif sibling.name == 'div' and 'clear' in sibling.get('class', []):
                break
        item_data['construction'] = "\n".join(construction_text)
        
        req_match = re.search(r'Requirements\s*(.*?)(?:;\s*Cost\s*([\d,]+\s*gp))?$', item_data['construction'])
        if req_match:
            item_data['requirements'] = req_match.group(1).strip()
            if req_match.group(2):
                item_data['cost'] = req_match.group(2).strip()

    return item_data


if __name__ == "__main__":
    magic_items_url = f"{BASE_URL}MagicItems.aspx"
    
    all_item_urls = []

    category_links = get_category_links(magic_items_url)
    
    if category_links:
        print("Elaborazione delle categorie di oggetti magici...")
        for link in category_links:
            full_category_url = link # get_category_links ora restituisce URL completi
            print(f"\nRecupero dei link degli oggetti e sottocategorie dalla categoria: {full_category_url}")
            
            item_links_from_page, sub_category_links = get_links_from_page(full_category_url)
            all_item_urls.extend(item_links_from_page)

            for sub_link in sub_category_links:
                print(f"Recupero degli oggetti dalla sottocategoria: {sub_link}")
                item_links_from_sub, _ = get_links_from_page(sub_link)
                all_item_urls.extend(item_links_from_sub)

            if not item_links_from_page and not sub_category_links:
                print(f"DEBUG: Nessun link di oggetto o sottocategoria trovato per {full_category_url}.")
            else:
                print(f"Trovati {len(item_links_from_page)} link di oggetti e {len(sub_category_links)} link di sottocategorie in {full_category_url}.")

    else:
        print("Nessun link di categoria trovato. Uscita.")

    if all_item_urls:
        unique_item_urls = list(set(all_item_urls))
        print(f"\nTotale link di oggetti unici trovati in tutte le categorie e sottocategorie: {len(unique_item_urls)}")
        
        output_dir = "parsed_data"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "all_magic_items.json")

        parsed_items = []
        parsed_urls = set()
        if os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    parsed_items = json.load(f)
                parsed_urls = {item["url"] for item in parsed_items}
                print(f"Caricati {len(parsed_items)} oggetti già parsati da {output_file}.")
            except json.JSONDecodeError:
                print(f"Avviso: Il file {output_file} è corrotto o vuoto. Inizio un nuovo parsing.")
                parsed_items = []
                parsed_urls = set()

        for i, item_url in enumerate(unique_item_urls):
            if item_url in parsed_urls:
                continue

            print(f"\nAnalisi dell\"oggetto {len(parsed_items) + 1}/{len(unique_item_urls)}: {item_url}")
            item_details = parse_item_details(item_url)
            if item_details and item_details.get('name') != "Unknown Item":
                parsed_items.append(item_details)
                # Salva incrementalmente ogni 10 oggetti
                if len(parsed_items) % 10 == 0:
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(parsed_items, f, indent=4, ensure_ascii=False)
                    print(f"Salvato lo stato attuale ({len(parsed_items)} oggetti) in {output_file}.")
        
        # Salvataggio finale
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(parsed_items, f, indent=4, ensure_ascii=False)
        print(f"\nOggetti analizzati salvati in {output_file}")

    else:
        print("Nessun URL di oggetto magico raccolto.")

    if os.path.exists("example_parsed_content.html"):
        os.remove("example_parsed_content.html")
        print("Pulizia di example_parsed_content.html eseguita.")

