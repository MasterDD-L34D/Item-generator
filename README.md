# Pathfinder 1E Magic Item Generator

Generatore di oggetti magici per Pathfinder 1E conforme al Formato Torneo, con integrazione LLM per la generazione automatica.

## Caratteristiche

- ✨ **Generazione AI**: Crea oggetti magici personalizzati usando l'AI di Manus
- 🔍 **Ricerca**: Cerca tra 588+ oggetti magici del database ufficiale
- 🎲 **Casuale**: Genera oggetti casuali per ispirazione
- 📋 **Formato Torneo**: Output conforme alle regole RAW di Pathfinder 1E
- 🎨 **UI Moderna**: Interfaccia elegante con tema viola/magenta

## Tecnologie

- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Backend**: Node.js + Express + TypeScript
- **AI**: Manus LLM API (Gemini 2.5 Flash)
- **Database**: JSON statico con 588 oggetti magici

## Installazione

```bash
# Installa le dipendenze
pnpm install

# Configura le variabili d'ambiente
# Aggiungi OPENAI_API_KEY nel file .env

# Avvia il server di sviluppo
pnpm dev
```

## Uso

1. **Genera**: Descrivi l'oggetto magico che vuoi creare
2. **Cerca**: Cerca oggetti esistenti nel database
3. **Casuale**: Ottieni ispirazione da oggetti casuali

## Formato Output

Gli oggetti generati seguono il Formato Torneo con:
- Nome e metadati (tipo, LI, prezzo, peso, rarità)
- Aura e scuola di magia
- Descrizione flavour
- Meccaniche complete (azione, usi, durata, TS, SR)
- Dettagli tecnici
- Requisiti di costruzione
- Note playtest
- Hook narrativo

## Deployment

L'applicazione è configurata per il deployment su piattaforme Node.js come Render, Railway, o Heroku.

### Variabili d'Ambiente Richieste

- `OPENAI_API_KEY`: API key di Manus per la generazione LLM
- `OPENAI_API_BASE`: (Opzionale) Base URL dell'API, default: https://api.manus.im/v1

## Licenza

MIT

