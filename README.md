# Laboratory Logbook - Guida Utente

## Descrizione
Laboratory Logbook è un'applicazione desktop per tracciare esperimenti di laboratorio con gestione automatica delle cartelle dati e sistema di archiviazione flessibile basato su file.

## Requisiti
- Python 3.6 o superiore
- Tkinter (incluso nella maggior parte delle installazioni Python)

## Installazione e Avvio

### Windows
1. Apri il Prompt dei comandi o PowerShell
2. Naviga nella cartella dove hai salvato il file
3. Esegui: `python lab_logbook.py`

### macOS/Linux
1. Apri il Terminale
2. Naviga nella cartella dove hai salvato il file
3. Esegui: `python3 lab_logbook.py`

## Concetto Fondamentale: Archiviazione Basata su Cartelle

A differenza dei logbook tradizionali che usano un database centralizzato, questa applicazione usa un approccio **basato su file system**:

- Ogni esperimento è una **cartella** che contiene i dati
- Ogni cartella di esperimento contiene un file **`data_description.json`** con i metadati
- Puoi organizzare le cartelle come preferisci (per progetto, per data, per tipo, ecc.)
- L'applicazione **scansiona automaticamente** tutte le sottocartelle per trovare gli esperimenti

### Vantaggi di questo Approccio
✅ **Flessibilità**: Organizza le cartelle come vuoi, senza vincoli
✅ **Portabilità**: Copia/sposta le cartelle liberamente
✅ **Backup semplice**: Basta copiare le cartelle
✅ **Leggibilità**: I file JSON sono leggibili anche senza l'applicazione
✅ **Integrazione**: Funziona bene con sistemi di versioning (Git), cloud storage (Dropbox), ecc.

## Funzionalità Principali

### 1. Creare una Nuova Entrata
- Clicca sul pulsante **"+ Nuova Entrata"**
- Compila i campi:
  - **Campione**: Nome del campione utilizzato (obbligatorio)
  - **Categoria**: Tipo di esperimento (Sintesi, Caratterizzazione, ecc.)
  - **Descrizione**: Descrizione dettagliata dell'esperimento
- Usa i pulsanti **B** (grassetto) e **R** (rosso) per formattare parti del testo
  - Seleziona il testo che vuoi formattare
  - Clicca sul pulsante corrispondente
  - Puoi applicare entrambe le formattazioni (grassetto E rosso)
- Clicca **"Salva"** per salvare l'entrata
- L'applicazione creerà automaticamente una cartella con nome: `YYYYMMDD_HHMMSS_Campione_Categoria`

### 2. Visualizzare le Entrate
- Tutte le entrate sono elencate nel pannello sinistro
- Clicca su un'entrata per visualizzarne i dettagli nel pannello destro
- Le entrate sono **sempre ordinate cronologicamente** (più recenti prima)

### 3. Filtrare le Entrate
Nel pannello "Filtri" puoi cercare entrate specifiche:

- **Campione**: Filtra per nome campione (ricerca parziale)
- **Ricerca testo**: Cerca parole nella descrizione
- **Categoria**: Filtra per tipo di esperimento

Clicca **"Applica Filtri"** per vedere i risultati, **"Reset"** per rimuovere tutti i filtri.

### 4. Aprire la Cartella Dati
- Visualizza un'entrata
- Clicca sul pulsante **"Apri"** accanto al campo "Cartella dati"
- Si aprirà la cartella dove puoi salvare i tuoi file di risultati

### 5. Eliminare un'Entrata
- Visualizza l'entrata che vuoi eliminare
- Clicca **"Elimina"**
- Conferma l'operazione
- **Nota**: Viene eliminato solo il file `data_description.json`, la cartella e tutti i dati rimarranno intatti

### 6. Ricaricare le Entrate
Menu **File → Ricarica Entrate**:
- Scansiona nuovamente tutte le cartelle
- Utile se hai aggiunto/modificato entrate manualmente o da altre fonti

### 7. Impostazioni
Menu **File → Impostazioni**:
- Puoi cambiare la cartella base dove l'applicazione cerca le entrate
- Valore predefinito: `~/LabData` (nella tua home directory)

## Struttura dei Dati

### File data_description.json
Ogni cartella di esperimento contiene un file `data_description.json` con questa struttura:

```json
{
  "date": "2026-02-15 14:30",
  "sample": "Campione_A",
  "category": "Sintesi",
  "description": "Testo della descrizione con **grassetto** e <<R>>rosso<</R>>"
}
```

### Markers di Formattazione
Il testo supporta questi markers:
- `**testo**` → Testo in grassetto
- `<<R>>testo<</R>>` → Testo in rosso
- `**<<R>>testo<</R>>**` → Grassetto E rosso

Questi markers rendono il file leggibile anche senza l'applicazione.

## Organizzazione Flessibile delle Cartelle

Puoi organizzare le tue cartelle in **qualsiasi modo**. L'applicazione scansionerà ricorsivamente tutte le sottocartelle fino a trovare i file `data_description.json`.

### Esempi di Organizzazione

#### Esempio 1: Per Progetto
```
LabData/
  ├── Progetto_A/
  │   ├── 20260215_120000_Campione_A_Sintesi/
  │   │   └── data_description.json
  │   ├── 20260216_100000_Campione_A_Test/
  │   │   └── data_description.json
  │   └── Caratterizzazione/
  │       └── 20260217_140000_Campione_A_NMR/
  │           └── data_description.json
  └── Progetto_B/
      └── 20260218_093000_Campione_B_Sintesi/
          └── data_description.json
```

#### Esempio 2: Per Tipo di Esperimento
```
LabData/
  ├── Sintesi/
  │   ├── 20260215_Campione_A/
  │   │   └── data_description.json
  │   └── 20260216_Campione_B/
  │       └── data_description.json
  ├── Caratterizzazione/
  │   └── NMR/
  │       └── 20260217_Campione_A/
  │           └── data_description.json
  └── Test/
```

#### Esempio 3: Piatto (senza sottocartelle)
```
LabData/
  ├── 20260215_120000_Campione_A_Sintesi/
  │   └── data_description.json
  ├── 20260216_100000_Campione_B_Test/
  │   └── data_description.json
  └── 20260217_140000_Campione_A_NMR/
      └── data_description.json
```

**L'applicazione funziona con tutti questi approcci!**

## Suggerimenti d'Uso

### Per Tracciare la Storia di un Campione
1. Usa il filtro "Campione"
2. Inserisci il nome del campione
3. Clicca "Applica Filtri"
4. Vedrai tutte le entrate relative a quel campione in ordine cronologico

### Per Organizzare i Dati
- Salva sempre i file di risultati (grafici, tabelle, PDF) nella cartella dell'esperimento
- Puoi creare sottocartelle per organizzare meglio (es. "Immagini", "Spettri", "Dati_Raw")
- Nella descrizione, fai riferimento ai file salvati

### Per Cercare Esperimenti Specifici
- Usa il filtro "Ricerca testo" per trovare esperimenti che contengono parole chiave specifiche
- Ad esempio: cerca "temperatura" per trovare tutti gli esperimenti dove hai annotato la temperatura

### Workflow Consigliato
1. **Prima dell'esperimento**: Crea nuova entrata con parametri pianificati
2. **Durante l'esperimento**: Aggiungi note, evidenzia parametri critici in rosso
3. **Dopo l'esperimento**: 
   - Salva i risultati nella cartella
   - Aggiorna la descrizione con osservazioni finali
4. **Giorni/settimane dopo**: Filtra per campione per vedere tutta la storia

### Modificare Manualmente le Entrate
Puoi anche modificare i file `data_description.json` direttamente con un editor di testo:
1. Apri il file con un editor di testo
2. Modifica i campi JSON
3. In Lab Logbook: Menu → File → Ricarica Entrate

## Backup e Portabilità

### Backup
Per fare backup dei tuoi dati:
1. Copia semplicemente l'intera cartella `LabData`
2. Opzionale: copia anche `logbook_config.json` per preservare le impostazioni

### Portabilità
Per trasferire il logbook su un altro computer:
1. Copia la cartella `LabData`
2. Installa Lab Logbook sul nuovo computer
3. Nelle impostazioni, imposta il percorso della cartella `LabData`

### Sincronizzazione Cloud
Puoi mettere `LabData` in Dropbox, Google Drive, OneDrive, ecc.:
- Le modifiche si sincronizzeranno automaticamente
- Usa "Ricarica Entrate" se modifichi da più dispositivi

## Risoluzione Problemi

### L'applicazione non trova le mie entrate
- Controlla che le cartelle contengano il file `data_description.json`
- Verifica il percorso nelle Impostazioni
- Usa "File → Ricarica Entrate"

### Il file data_description.json è corrotto
Se un file è danneggiato:
1. Aprilo con un editor di testo
2. Correggi il JSON (usa un validatore JSON online se necessario)
3. Ricarica le entrate

### La formattazione non appare correttamente
- Controlla di aver usato i marker corretti: `**` per grassetto, `<<R>>` e `<</R>>` per rosso
- Assicurati che i marker di apertura e chiusura siano bilanciati

## Note Tecniche

- I dati sono salvati in formato JSON per massima portabilità
- La scansione ricorsiva si ferma quando trova `data_description.json` (non scansiona sottocartelle di esperimenti)
- Le entrate sono sempre ordinate cronologicamente per data
- La formattazione usa markers testuali per mantenere leggibilità
- L'applicazione è compatibile con Windows, macOS e Linux

## Contatti e Supporto

Il codice è open source e modificabile. È ampiamente commentato per facilitare personalizzazioni.
