/**
 * Script di test indipendente per validare l'accesso all'API di embedding di OpenAI.
 * Questo script può essere eseguito separatamente per debuggare problemi di connettività,
 * autenticazione o accesso ai modelli prima di integrare nell'applicazione.
 */

import OpenAI from 'openai';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

async function testOpenAIEmbedding() {
  console.log('=== Test OpenAI Embedding API ===\n');

  // Verifica che la chiave API sia presente
  if (!OPENAI_API_KEY) {
    console.error('❌ ERRORE: OPENAI_API_KEY non è impostata nelle variabili d\'ambiente');
    console.log('   Imposta la chiave con: export OPENAI_API_KEY="your-key-here"');
    process.exit(1);
  }

  console.log('✓ Chiave API trovata:', OPENAI_API_KEY.substring(0, 20) + '...');

  try {
    // Inizializza il client OpenAI
    console.log('\n1. Inizializzazione del client OpenAI...');
    const client = new OpenAI({
      apiKey: OPENAI_API_KEY,
    });
    console.log('✓ Client inizializzato con successo');

    // Test con un testo semplice
    const testText = 'A magical sword that glows in the dark';
    const modelsToTest = ['text-embedding-3-small', 'text-embedding-ada-002', 'text-embedding-3-large'];
    
    let workingModel: string | null = null;
    let workingResponse: any = null;

    console.log(`\n2. Test di embedding con vari modelli...`);
    for (const model of modelsToTest) {
      try {
        console.log(`   Tentativo con ${model}...`);
        const startTime = Date.now();
        const response = await client.embeddings.create({
          model: model,
          input: testText,
        });
        const endTime = Date.now();
        
        workingModel = model;
        workingResponse = response;
        console.log(`   ✓ ${model} funziona! (${endTime - startTime}ms)`);
        console.log(`     Dimensione del vettore: ${response.data[0].embedding.length}`);
        console.log(`     Primi 5 valori: [${response.data[0].embedding.slice(0, 5).map((v: number) => v.toFixed(4)).join(', ')}...]`);
        break;
      } catch (error: any) {
        console.log(`   ✗ ${model} non disponibile: ${error.message}`);
      }
    }

    if (!workingModel) {
      console.log('\n⚠ Nessun modello di embedding funziona. Provo con un modello di chat per verificare la chiave API...');
      try {
        const chatResponse = await client.chat.completions.create({
          model: 'gpt-3.5-turbo',
          messages: [{ role: 'user', content: 'Say "test"' }],
          max_tokens: 5,
        });
        console.log('✓ La chiave API funziona con i modelli di chat!');
        console.log('  Risposta:', chatResponse.choices[0].message.content);
        console.log('\n❌ Problema: I modelli di embedding non sono disponibili per questo account.');
        console.log('   Contatta il supporto OpenAI o verifica le limitazioni del tuo piano.');
        return false;
      } catch (chatError: any) {
        console.log('✗ Anche i modelli di chat falliscono:', chatError.message);
        throw new Error('La chiave API non funziona con nessun modello OpenAI');
      }
    }

    console.log('\n=== ✓ Tutti i test completati con successo! ===\n');
    return true;

  } catch (error: any) {
    console.error('\n❌ ERRORE durante il test:');
    console.error('   Tipo:', error.constructor.name);
    console.error('   Messaggio:', error.message);
    
    if (error.status) {
      console.error('   Status Code:', error.status);
    }
    
    if (error.code) {
      console.error('   Error Code:', error.code);
    }

    if (error.status === 401) {
      console.log('\n💡 Suggerimento: La chiave API non è valida o è scaduta.');
      console.log('   Verifica la chiave su https://platform.openai.com/account/api-keys');
    } else if (error.status === 429) {
      console.log('\n💡 Suggerimento: Hai superato la quota o il rate limit.');
      console.log('   Verifica il tuo piano su https://platform.openai.com/account/billing');
    } else if (error.status === 404) {
      console.log('\n💡 Suggerimento: Il modello richiesto non è disponibile per il tuo account.');
      console.log('   Verifica i modelli disponibili su https://platform.openai.com/docs/models');
    }

    console.log('\n');
    return false;
  }
}

// Esegui il test
testOpenAIEmbedding()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('Errore inaspettato:', error);
    process.exit(1);
  });

