import { readFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';

// Ottieni il percorso del file corrente in modo compatibile con ESM
const getCurrentDir = () => {
  try {
    return new URL('.', import.meta.url).pathname;
  } catch {
    // Fallback per ambienti che non supportano import.meta.url
    return __dirname;
  }
};

export interface MagicItem {
  name: string;
  description: string;
  type?: string;
  rarity?: string;
  price?: string;
  [key: string]: any;
}

let cachedItems: MagicItem[] | null = null;

/**
 * Carica gli oggetti magici dal file JSON.
 * Il file viene letto una sola volta e poi messo in cache.
 */
export function loadMagicItems(): MagicItem[] {
  if (cachedItems) {
    return cachedItems;
  }

  try {
    // Usa un percorso assoluto basato sulla root del progetto
    const dataPath = join(process.cwd(), 'server', 'data', 'all_magic_items.json');
    const fileContent = readFileSync(dataPath, 'utf-8');
    cachedItems = JSON.parse(fileContent);
    console.log(`[MagicItems] Loaded ${cachedItems?.length || 0} magic items from ${dataPath}`);
    return cachedItems || [];
  } catch (error) {
    console.error('[MagicItems] Error loading magic items:', error);
    throw new Error(`Failed to load magic items: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Restituisce statistiche sugli oggetti magici caricati.
 */
export function getMagicItemsStats() {
  const items = loadMagicItems();
  
  return {
    totalCount: items.length,
    sampleItem: items[0] || null,
    types: Array.from(new Set(items.map(item => item.type).filter(Boolean))).slice(0, 10),
  };
}

