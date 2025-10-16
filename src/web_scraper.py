import requests
from bs4 import BeautifulSoup
import json

def scrape_aonprd_magic_item_creation_rules(url="https://aonprd.com/Rules.aspx?ID=401"):
    """
    Scrapes magic item creation rules from Aonprd.com.
    Focuses on tables and general rules for pricing and crafting.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {
        "source_url": url,
        "title": soup.find('h1').get_text(strip=True) if soup.find('h1') else 'N/A',
        "sections": []
    }

    # Find the main content area, usually within a div or article tag
    content_div = soup.find('div', class_='main') or soup.find('article')
    if not content_div:
        content_div = soup # Fallback to entire soup if specific content div not found

    current_section = None
    for element in content_div.find_all(['h2', 'h3', 'p', 'table']):
        if element.name == 'h2':
            if current_section:
                data["sections"].append(current_section)
            current_section = {"heading": element.get_text(strip=True), "content": [], "tables": []}
        elif element.name == 'h3':
            if current_section:
                current_section["content"].append({"type": "subheading", "text": element.get_text(strip=True)})
        elif element.name == 'p':
            if current_section:
                current_section["content"].append({"type": "paragraph", "text": element.get_text(strip=True)})
        elif element.name == 'table':
            if current_section:
                table_data = []
                headers = [th.get_text(strip=True) for th in element.find_all('th')]
                for row in element.find_all('tr'):
                    cols = [td.get_text(strip=True) for td in row.find_all('td')]
                    if cols:
                        table_data.append(dict(zip(headers, cols)) if headers else cols)
                current_section["tables"].append(table_data)

    if current_section:
        data["sections"].append(current_section)

    return data

def scrape_aonprd_spells(url_list_page="https://aonprd.com/Spells.aspx?Class=All"):
    """
    Scrapes spell data from Aonprd.com, extracting name, level, school, and description.
    """
    all_spells_data = []
    try:
        response = requests.get(url_list_page)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching spell list from {url_list_page}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Aonprd lists spells in tables, often with links to individual spell pages
    # We need to find the links to individual spell pages and then scrape each one.
    # This is a simplified approach, a more robust one would involve iterating through pages or using a search.
    
    # Find all links that point to spell display pages
    spell_links = soup.find_all('a', href=lambda href: href and 'SpellDisplay.aspx' in href)
    
    # Limit the number of spells to scrape for testing purposes to avoid long execution times
    # In a full implementation, this limit would be removed.
    max_spells_to_scrape = 50 # Adjust as needed for testing
    scraped_count = 0

    for link in spell_links:
        if scraped_count >= max_spells_to_scrape:
            break

        spell_url = "https://aonprd.com/" + link['href']
        spell_name = link.get_text(strip=True)
        
        if not spell_name: # Skip empty links
            continue

        print(f"Scraping spell: {spell_name} from {spell_url}")
        spell_data = scrape_single_spell_page(spell_url, spell_name)
        if spell_data:
            all_spells_data.append(spell_data)
            scraped_count += 1

    return all_spells_data

def scrape_single_spell_page(url: str, spell_name: str) -> dict:
    """
    Scrapes a single spell page for detailed information.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching spell page {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    spell_info = {
        "name": spell_name,
        "source_url": url,
        "level": "",
        "school": "",
        "description": ""
    }

    # Extract spell level and school
    # The relevant information is typically found within a <div class="heading">.
    details_div = soup.find("div", class_="heading")
    if details_div:
        details_text = details_div.get_text(separator="; ", strip=True)
        
        # Extract School
        school_match = re.search(r"School\s*([\w\s]+?)(?:;|$)", details_text, re.IGNORECASE)
        if school_match: spell_info["school"] = school_match.group(1).strip()

        # Extract Level (the lowest level across all classes is usually the most relevant for item creation)
        level_matches = re.findall(r"(\w+)\s*(\d+)", details_text)
        if level_matches:
            min_level = 99 # Initialize with a high value
            for class_name, level_str in level_matches:
                try:
                    level = int(level_str)
                    if level < min_level: min_level = level
                except ValueError:
                    pass
            if min_level != 99: spell_info["level"] = str(min_level)

    # Extract description (usually in a paragraph after the details)
    description_p = soup.find("h2", string="Description")
    if description_p:
        description_content = []
        for sibling in description_p.find_next_siblings():
            if sibling.name == 'h2': # Stop at next heading
                break
            if sibling.name == 'p':
                description_content.append(sibling.get_text(strip=True))
        spell_info['description'] = " ".join(description_content)

    return spell_info

import re

def scrape_d20pfsrd_item_pricing(url="https://www.d20pfsrd.com/magic-items/magic-item-creation/"):
    """
    Scrapes magic item pricing guidelines from d20PFSRD.com.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {
        "source_url": url,
        "title": soup.find('h1').get_text(strip=True) if soup.find('h1') else 'N/A',
        "sections": []
    }

    # d20PFSRD often uses specific div structures for content
    content_div = soup.find('div', class_='post-content') or soup.find('article')
    if not content_div:
        content_div = soup # Fallback

    current_section = None
    for element in content_div.find_all(['h2', 'h3', 'p', 'table']):
        if element.name == 'h2':
            if current_section:
                data["sections"].append(current_section)
            current_section = {"heading": element.get_text(strip=True), "content": [], "tables": []}
        elif element.name == 'h3':
            if current_section:
                current_section["content"].append({"type": "subheading", "text": element.get_text(strip=True)})
        elif element.name == 'p':
            if current_section:
                current_section["content"].append({"type": "paragraph", "text": element.get_text(strip=True)})
        elif element.name == 'table':
            if current_section:
                table_data = []
                headers = [th.get_text(strip=True) for th in element.find_all('th')]
                for row in element.find_all('tr'):
                    cols = [td.get_text(strip=True) for td in row.find_all('td')]
                    if cols:
                        table_data.append(dict(zip(headers, cols)) if headers else cols)
                current_section["tables"].append(table_data)

    if current_section:
        data["sections"].append(current_section)

    return data


if __name__ == "__main__":
    print("Scraping Aonprd Magic Item Creation Rules...")
    aonprd_rules = scrape_aonprd_magic_item_creation_rules()
    if aonprd_rules:
        with open("aonprd_magic_item_rules.json", "w", encoding="utf-8") as f:
            json.dump(aonprd_rules, f, indent=4, ensure_ascii=False)
        print("Aonprd magic item rules scraped and saved to aonprd_magic_item_rules.json")

    print("\nScraping d20PFSRD Item Pricing Guidelines...")
    d20pfsrd_pricing = scrape_d20pfsrd_item_pricing()
    if d20pfsrd_pricing:
        with open("d20pfsrd_item_pricing.json", "w", encoding="utf-8") as f:
            json.dump(d20pfsrd_pricing, f, indent=4, ensure_ascii=False)
        print("d20PFSRD item pricing guidelines scraped and saved to d20pfsrd_item_pricing.json")

    print("\nScraping Aonprd Spells...")
    all_spells_data = scrape_aonprd_spells()
    if all_spells_data:
        with open("aonprd_spells.json", "w", encoding="utf-8") as f:
            json.dump(all_spells_data, f, indent=4, ensure_ascii=False)
        print("Aonprd spell data scraped and saved to aonprd_spells.json")
