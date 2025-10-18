/**
 * Script di test per l'API LLM di Manus.
 * Verifica che possiamo usare l'LLM per generare descrizioni e analizzare oggetti magici.
 */

import { invokeLLM } from './_core/llm';

async function testManusLLM() {
  console.log('=== Test Manus LLM API ===\n');

  try {
    // Test 1: Generazione semplice
    console.log('1. Test di generazione semplice...');
    const response1 = await invokeLLM({
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: 'Say "Hello from Manus LLM!"' },
      ],
    });
    console.log('✓ Risposta:', response1.choices[0].message.content);

    // Test 2: Analisi di un oggetto magico
    console.log('\n2. Test di analisi di un oggetto magico...');
    const magicItem = {
      name: 'Flaming Sword +1',
      description: 'A longsword that deals an extra 1d6 fire damage on hit.',
    };
    
    const response2 = await invokeLLM({
      messages: [
        { 
          role: 'system', 
          content: 'You are an expert in Pathfinder 1E magic items. Analyze items and extract key features.' 
        },
        { 
          role: 'user', 
          content: `Analyze this magic item and list its key features:\n\nName: ${magicItem.name}\nDescription: ${magicItem.description}\n\nProvide: type, primary effect, damage type, and power level.` 
        },
      ],
    });
    console.log('✓ Analisi:', response2.choices[0].message.content);

    // Test 3: Generazione strutturata (JSON)
    console.log('\n3. Test di generazione strutturata (JSON)...');
    const response3 = await invokeLLM({
      messages: [
        { 
          role: 'system', 
          content: 'You are a helpful assistant designed to output JSON.' 
        },
        { 
          role: 'user', 
          content: 'Extract the weapon type and damage type from this item: "Flaming Sword +1 - deals 1d6 fire damage"' 
        },
      ],
      response_format: {
        type: 'json_schema',
        json_schema: {
          name: 'item_analysis',
          strict: true,
          schema: {
            type: 'object',
            properties: {
              weapon_type: { type: 'string', description: 'Type of weapon' },
              damage_type: { type: 'string', description: 'Type of damage dealt' },
              enhancement_bonus: { type: 'integer', description: 'Enhancement bonus' },
            },
            required: ['weapon_type', 'damage_type', 'enhancement_bonus'],
            additionalProperties: false,
          },
        },
      },
    });
    console.log('✓ JSON strutturato:', response3.choices[0].message.content);

    console.log('\n=== ✓ Tutti i test completati con successo! ===\n');
    console.log('L\'API LLM di Manus funziona perfettamente e può essere usata per:');
    console.log('  - Analizzare oggetti magici');
    console.log('  - Generare descrizioni');
    console.log('  - Estrarre features strutturate');
    console.log('  - Implementare ricerca semantica basata su LLM\n');
    
    return true;

  } catch (error: any) {
    console.error('\n❌ ERRORE durante il test:');
    console.error('   Tipo:', error.constructor.name);
    console.error('   Messaggio:', error.message);
    
    if (error.stack) {
      console.error('   Stack:', error.stack.split('\n').slice(0, 3).join('\n'));
    }

    console.log('\n');
    return false;
  }
}

// Esegui il test
testManusLLM()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('Errore inaspettato:', error);
    process.exit(1);
  });

