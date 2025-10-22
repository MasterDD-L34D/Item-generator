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
 * Invalida la cache degli oggetti magici (utile per reload)
 */
export function invalidateCache() {
  cachedItems = null;
}

/**
 * Carica gli oggetti magici dal file JSON.
 * Il file viene letto una sola volta e poi messo in cache.
 */
/**
 * Estrae il nome dell'oggetto dall'URL quando il campo name è generico
 */
function extractNameFromUrl(url: string): string {
  try {
    const match = url.match(/ItemName=([^&]+)/);
    if (match && match[1]) {
      return decodeURIComponent(match[1].replace(/\+/g, ' '));
    }
  } catch {
    // Ignora errori
  }
  return '';
}

/**
 * Normalizza un oggetto magico per migliorare la visualizzazione
 */
function normalizeItem(item: any): MagicItem {
  const urlName = extractNameFromUrl(item.url || '');
  
  return {
    ...item,
    name: (item.name && item.name !== 'Magic Sets' && item.name !== 'N/A') 
      ? item.name 
      : urlName || 'Oggetto Magico',
    description: (item.description && item.description !== 'N/A')
      ? item.description
      : `${item.slot || 'Slot sconosciuto'} • ${item.aura || 'Aura sconosciuta'} • CL ${item.cl || '?'}`,
  };
}

export function loadMagicItems(): MagicItem[] {
  if (cachedItems) {
    return cachedItems;
  }

  try {
    // Usa un percorso assoluto basato sulla root del progetto
    const dataPath = join(process.cwd(), 'server', 'data', 'all_magic_items.json');
    const fileContent = readFileSync(dataPath, 'utf-8');
    const rawItems = JSON.parse(fileContent);
    
    // Normalizza tutti gli oggetti
    cachedItems = rawItems.map(normalizeItem);
    
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

