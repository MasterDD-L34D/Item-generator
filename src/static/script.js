// Carica le statistiche al caricamento della pagina
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
});

// Funzione per caricare le statistiche
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('stats').textContent = 'Statistiche non disponibili';
        } else {
            document.getElementById('stats').textContent = 
                `Database: ${data.total_items} oggetti magici`;
        }
    } catch (error) {
        console.error('Errore nel caricamento delle statistiche:', error);
        document.getElementById('stats').textContent = 'Statistiche non disponibili';
    }
}

// Funzione per cambiare tab
function switchTab(tabName) {
    // Nascondi tutte le tab
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Rimuovi la classe active da tutti i bottoni
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    
    // Mostra la tab selezionata
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Aggiungi la classe active al bottone selezionato
    event.target.classList.add('active');
}

// Funzione per generare un oggetto magico
async function generateItem() {
    const description = document.getElementById('description').value.trim();
    
    if (!description) {
        alert('Per favore, inserisci una descrizione dell\'oggetto magico.');
        return;
    }
    
    // Mostra il loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(`Errore: ${data.error}`);
            return;
        }
        
        // Mostra i risultati
        displayGeneratedItem(data.generated_item);
        displaySimilarItems(data.similar_items);
        
        // Nascondi il loading e mostra i risultati
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');
        
        // Scroll ai risultati
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Errore nella generazione:', error);
        alert('Si è verificato un errore durante la generazione dell\'oggetto magico.');
        document.getElementById('loading').classList.add('hidden');
    }
}

// Funzione per visualizzare l'oggetto generato
function displayGeneratedItem(itemText) {
    const container = document.getElementById('generated-item');
    container.textContent = itemText;
}

// Funzione per visualizzare gli oggetti simili
function displaySimilarItems(items) {
    const container = document.getElementById('similar-items');
    container.innerHTML = '';
    
    items.forEach((item, index) => {
        const itemCard = document.createElement('div');
        itemCard.className = 'item-card';
        
        itemCard.innerHTML = `
            <h4>${index + 1}. ${item.name}</h4>
            <div class="item-details">
                <div class="item-detail"><strong>Aura:</strong> ${item.aura}</div>
                <div class="item-detail"><strong>CL:</strong> ${item.cl}</div>
                <div class="item-detail"><strong>Slot:</strong> ${item.slot}</div>
                <div class="item-detail"><strong>Prezzo:</strong> ${item.cost}</div>
                <div class="item-detail"><strong>Peso:</strong> ${item.weight}</div>
            </div>
            <div class="item-description">
                <strong>Descrizione:</strong> ${item.description}
            </div>
            ${item.requirements !== 'N/A' ? `
                <div class="item-description">
                    <strong>Requisiti:</strong> ${item.requirements}
                </div>
            ` : ''}
        `;
        
        container.appendChild(itemCard);
    });
}

// Funzione per cercare oggetti magici
async function searchItems() {
    const query = document.getElementById('search-query').value.trim();
    
    if (!query) {
        alert('Per favore, inserisci una query di ricerca.');
        return;
    }
    
    // Mostra il loading
    document.getElementById('search-loading').classList.remove('hidden');
    document.getElementById('search-results').classList.add('hidden');
    
    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(`Errore: ${data.error}`);
            return;
        }
        
        // Mostra i risultati
        displaySearchResults(data.items);
        
        // Nascondi il loading e mostra i risultati
        document.getElementById('search-loading').classList.add('hidden');
        document.getElementById('search-results').classList.remove('hidden');
        
        // Scroll ai risultati
        document.getElementById('search-results').scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Errore nella ricerca:', error);
        alert('Si è verificato un errore durante la ricerca.');
        document.getElementById('search-loading').classList.add('hidden');
    }
}

// Funzione per visualizzare i risultati della ricerca
function displaySearchResults(items) {
    const container = document.getElementById('search-results');
    container.innerHTML = '';
    
    if (items.length === 0) {
        container.innerHTML = '<p>Nessun oggetto trovato.</p>';
        return;
    }
    
    const resultsTitle = document.createElement('h2');
    resultsTitle.textContent = `🔍 Trovati ${items.length} oggetti`;
    resultsTitle.style.color = '#667eea';
    resultsTitle.style.marginBottom = '20px';
    container.appendChild(resultsTitle);
    
    items.forEach((item, index) => {
        const itemCard = document.createElement('div');
        itemCard.className = 'item-card';
        
        itemCard.innerHTML = `
            <h4>${index + 1}. ${item.name}</h4>
            <div class="item-details">
                <div class="item-detail"><strong>Aura:</strong> ${item.aura}</div>
                <div class="item-detail"><strong>CL:</strong> ${item.cl}</div>
                <div class="item-detail"><strong>Slot:</strong> ${item.slot}</div>
                <div class="item-detail"><strong>Prezzo:</strong> ${item.cost}</div>
                <div class="item-detail"><strong>Peso:</strong> ${item.weight}</div>
                <div class="item-detail"><strong>Rilevanza:</strong> ${(item.score * 100).toFixed(1)}%</div>
            </div>
            <div class="item-description">
                <strong>Descrizione:</strong> ${item.description}
            </div>
            ${item.requirements !== 'N/A' ? `
                <div class="item-description">
                    <strong>Requisiti:</strong> ${item.requirements}
                </div>
            ` : ''}
            ${item.source !== 'N/A' ? `
                <div class="item-description">
                    <strong>Fonte:</strong> ${item.source}
                </div>
            ` : ''}
            ${item.url ? `
                <div class="item-url">
                    <a href="${item.url}" target="_blank">Vedi su Archives of Nethys →</a>
                </div>
            ` : ''}
        `;
        
        container.appendChild(itemCard);
    });
}

// Gestione dell'invio con Enter nella textarea
document.getElementById('description').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        generateItem();
    }
});

// Gestione dell'invio con Enter nell'input di ricerca
document.getElementById('search-query').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        searchItems();
    }
});

