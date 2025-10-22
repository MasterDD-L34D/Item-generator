/**
 * Modulo per la generazione e ricerca di oggetti magici usando l'API LLM di Manus.
 * Conforme alle regole di Pathfinder 1E e al Formato Torneo.
 */

import { invokeLLM } from './_core/llm';
import { loadMagicItems, MagicItem } from './magicItems';

/**
 * Schema completo per un oggetto magico in Formato Torneo.
 */
export interface TournamentMagicItem {
  // Metadati
  name: string;
  slot: string;
  casterLevel: number; // LI (Livello Incantatore)
  price: number; // in gp
  weight: string; // es. "1 lb" o "—"
  rarity: 'Comune' | 'Non comune' | 'Raro' | 'Unico';
  category: string; // Tipo (Wondrous Item, Weapon, Armor, Ring, etc.)
  
  // Aura e Scuola
  auraIntensity: 'Debole' | 'Moderata' | 'Forte';
  school: string; // Scuola in italiano
  
  // Descrizione (solo flavour, 2-4 frasi)
  description: string;
  
  // Uso/Attivazione
  activationAction: string; // es. "Veloce", "Standard", "Movimento"
  usesPerDay: string; // es. "1/giorno", "3/giorno", "illimitato"
  duration: string;
  savingThrow: string; // es. "—", "Volontà CD 15"
  spellResistance: string; // "Sì" o "No"
  referencedSpell?: string; // es. "flame blade, LI 9°"
  
  // Effetto
  effect: string; // 1 riga, sintesi secca
  
  // Dettaglio (max 3 bullet)
  details: string[];
  
  // Interazioni
  bonusType?: string; // es. "competenza", "circostanziale", "schivare"
  stacking: string; // es. "Non cumula con altri bonus di competenza"
  rawTag: 'RAW' | 'RAI' | 'HR';
  
  // Costruzione
  craftingRequirements: string; // es. "Craft Wondrous Item, flame blade, resist energy"
  craftingCost: number; // Prezzo / 2
  
  // Note
  playtestNote: string; // 1 riga obbligatoria su rischi/abusi
  narrativeHook?: string; // Opzionale, 1 riga
}

/**
 * Genera un nuovo oggetto magico basato su una descrizione dell'utente.
 * Conforme al Formato Torneo e alle regole Pathfinder 1E.
 */
export async function generateMagicItem(userPrompt: string): Promise<TournamentMagicItem> {
  const systemPrompt = `Sei un esperto Game Master di Pathfinder 1E specializzato nella creazione di oggetti magici bilanciati e conformi alle regole ufficiali Paizo.

REGOLE OBBLIGATORIE:
1. Solo contenuto Paizo PF1e ufficiale (nessun 3PP)
2. Prezzi secondo tabelle ufficiali Core Rulebook
3. Costo crafting = Prezzo / 2 (arrotondato per difetto)
4. Aura e LI derivano dall'incantesimo principale
5. Terminologia italiana: LI (Livello Incantatore), scuole in italiano
6. Descrizione: solo flavour (2-4 frasi), SENZA regole
7. Dettaglio: massimo 3 bullet atomici e specifici
8. Nota Playtest obbligatoria (1 riga su rischi/abusi)

FORMULE DI CALCOLO:
- Incantesimo 1/giorno: livello incantesimo × LI × 1.800 gp
- Incantesimo 3/giorno: livello incantesimo × LI × 5.400 gp
- Incantesimo illimitato: livello incantesimo × LI × 2.000 gp × 4
- Bonus fisso +X: bonus² × 1.000 gp (competenza) o bonus² × 2.000 gp (altri)
- CD Tiro Salvezza: 10 + livello incantesimo + modificatore attributo (min +3)
- LI minimo: livello incantesimo × 2 - 1 (es: fireball LI 5° → LI 5)

AURA (basata su LI):
- Debole: LI 1-5
- Moderata: LI 6-11  
- Forte: LI 12+

SCUOLE (traduci sempre in italiano):
- Abjuration → Abjurazione
- Conjuration → Evocazione
- Divination → Divinazione
- Enchantment → Ammaliamento
- Evocation → Invocazione
- Illusion → Illusione
- Necromancy → Necromanzia
- Transmutation → Trasmutazione

TIPI DI BONUS (specifica sempre):
competenza, circostanziale, schivare, intuizione, potenziamento, fortuna, sacro/profano, morale, resistenza, deviazione

RARITÀ:
- Comune: diffuso, impatto basso-medio, prezzo < 10.000 gp
- Non comune: tematico/regionale, utility marcata, 10.000-50.000 gp
- Raro: condizioni/rituali specifici, possibili combo, 50.000-200.000 gp
- Unico: pezzo narrativo, spesso HR/vincoli, > 200.000 gp

ESEMPI DI RIFERIMENTO:
- Ring of Protection +1: 2.000 gp, LI 5°, Abjurazione, bonus deviazione
- Ring of Feather Falling: 2.200 gp, LI 1°, Trasmutazione, illimitato
- Cloak of Resistance +1: 1.000 gp, LI 5°, Abjurazione, bonus resistenza
- Wand of Fireball (CL 5): 11.250 gp, 50 cariche, LI 5°

BILANCIAMENTO:
- Evita effetti "sempre attivo" troppo potenti
- Limita usi/giorno per effetti forti
- Considera azione di attivazione (Standard = più bilanciato)
- TS e SR devono essere coerenti con l'incantesimo base
- Dettagli devono specificare limitazioni e interazioni`;

  const userMessage = `Crea un oggetto magico Pathfinder 1E basato su: "${userPrompt}"

Fornisci l'oggetto in formato JSON con TUTTI i seguenti campi:

{
  "name": "Nome fantasioso in italiano",
  "slot": "Slot PF ufficiale (ring, head, neck, etc.) o —",
  "casterLevel": numero intero (LI),
  "price": numero intero (prezzo in gp),
  "weight": "peso in lb o —",
  "rarity": "Comune" | "Non comune" | "Raro" | "Unico",
  "category": "Ring, Wondrous Item, Weapon, Armor, etc.",
  "auraIntensity": "Debole" | "Moderata" | "Forte",
  "school": "Scuola di magia in italiano",
  "description": "2-4 frasi evocative, SOLO flavour text",
  "activationAction": "Veloce, Standard, Movimento, o Reazione",
  "usesPerDay": "1/giorno, 3/giorno, illimitato, etc.",
  "duration": "Durata dell'effetto",
  "savingThrow": "TS richiesto (es: Volontà CD 15) o —",
  "spellResistance": "Sì" | "No",
  "referencedSpell": "Incantesimo di riferimento con LI (es: fireball, LI 7°)",
  "effect": "1 riga, sintesi secca dell'effetto meccanico",
  "details": ["bullet 1", "bullet 2", "bullet 3"] (max 3 bullet atomici),
  "bonusType": "Tipo di bonus (competenza, circostanziale, etc.) o stringa vuota",
  "stacking": "Regole di cumulabilità",
  "rawTag": "RAW" | "RAI" | "HR",
  "craftingRequirements": "Talenti e incantesimi richiesti",
  "craftingCost": numero intero (= price / 2),
  "playtestNote": "1 riga su rischi/abusi/attenzioni",
  "narrativeHook": "1 riga su dove/come è trovato (opzionale, può essere stringa vuota)"
}

Rispondi SOLO con il JSON, senza altro testo.`;

  const response = await invokeLLM({
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userMessage },
    ],
    response_format: {
      type: 'json_object',
    },
  });

  const content = response.choices[0].message.content;
  if (!content || typeof content !== 'string') {
    throw new Error('No valid content in LLM response');
  }

  const item = JSON.parse(content) as TournamentMagicItem;
  
  // Validazione post-generazione
  if (item.craftingCost !== Math.floor(item.price / 2)) {
    item.craftingCost = Math.floor(item.price / 2);
  }
  
  if (item.details.length > 3) {
    item.details = item.details.slice(0, 3);
  }

  return item;
}

/**
 * Cerca oggetti magici simili a una descrizione dell'utente usando l'LLM.
 */
export async function searchMagicItems(query: string, limit: number = 5): Promise<MagicItem[]> {
  const allItems = loadMagicItems();
  
  // Usa l'LLM per analizzare la query e identificare caratteristiche chiave
  const analysisResponse = await invokeLLM({
    messages: [
      {
        role: 'system',
        content: 'Sei un esperto di Pathfinder 1E. Analizza query di ricerca ed estrai caratteristiche chiave per trovare oggetti magici.',
      },
      {
        role: 'user',
        content: `Analizza questa ricerca e estrai caratteristiche: "${query}"

Fornisci un JSON con:
- keywords: array di parole chiave importanti
- item_types: array di tipi di oggetto probabili (weapon, armor, ring, wondrous, etc.)
- effects: array di effetti o proprietà desiderati

Esempio: {"keywords": ["fuoco", "danno"], "item_types": ["ring", "weapon"], "effects": ["fireball", "fire damage"]}

Rispondi SOLO con il JSON.`,
      },
    ],
    response_format: {
      type: 'json_object',
    },
  });

  const analysisContent = analysisResponse.choices[0].message.content;
  if (!analysisContent || typeof analysisContent !== 'string') {
    throw new Error('No valid content in analysis response');
  }

  const analysis = JSON.parse(analysisContent) as {
    keywords: string[];
    item_types: string[];
    effects: string[];
  };

  // Filtra gli oggetti basandosi sull'analisi
  const scoredItems = allItems.map(item => {
    let score = 0;
    const itemText = `${item.name} ${item.description}`.toLowerCase();

    // Punteggio per keywords
    analysis.keywords.forEach(keyword => {
      if (itemText.includes(keyword.toLowerCase())) {
        score += 3;
      }
    });

    // Punteggio per tipo
    analysis.item_types.forEach(type => {
      if (item.type && item.type.toLowerCase().includes(type.toLowerCase())) {
        score += 5;
      }
    });

    // Punteggio per effetti
    analysis.effects.forEach(effect => {
      if (itemText.includes(effect.toLowerCase())) {
        score += 4;
      }
    });

    return { item, score };
  });

  // Ordina per punteggio e prendi i top risultati
  const topItems = scoredItems
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(({ item }) => item);

  return topItems;
}

/**
 * Ottiene suggerimenti di oggetti casuali per ispirazione.
 */
export function getRandomItems(count: number = 3): MagicItem[] {
  const allItems = loadMagicItems();
  const shuffled = [...allItems].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

