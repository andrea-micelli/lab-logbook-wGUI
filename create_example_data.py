"""
Script di esempio per popolare il logbook con dati di test
Esegui questo script per aggiungere alcune entrate di esempio al tuo logbook
"""

import json
from datetime import datetime, timedelta
import os
from pathlib import Path

def create_example_data():
    """Crea file di esempio per il logbook con nuova struttura"""
    
    base_folder = Path("LabData")
    
    # Esempi di entrate con diversa organizzazione delle cartelle
    examples = [
        {
            "path": "Progetto_A/Sintesi/20260210_120000_Campione_A_Sintesi",
            "data": {
                "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M"),
                "sample": "Campione_A",
                "category": "Sintesi",
                "description": "Sintesi del composto organico tramite reazione di condensazione.\n\n**Parametri importanti:**\n- Temperatura: <<R>>80°C<</R>>\n- Tempo: 4 ore\n- Resa: **78%**\n\n<<R>>ATTENZIONE: Usare cappa aspirante<</R>>"
            }
        },
        {
            "path": "Progetto_A/Caratterizzazione/20260211_140000_Campione_A_Caratterizzazione",
            "data": {
                "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M"),
                "sample": "Campione_A",
                "category": "Caratterizzazione",
                "description": "Analisi NMR e IR del prodotto.\n\n**Risultati:**\n- Picchi caratteristici confermati\n- Purezza: **95%**\n\nVedere file spettri nella cartella 'Spettri'."
            }
        },
        {
            "path": "Progetto_B/20260212_100000_Campione_B_Sintesi",
            "data": {
                "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M"),
                "sample": "Campione_B",
                "category": "Sintesi",
                "description": "Nuovo tentativo di sintesi con catalizzatore modificato.\n\n<<R>>**ATTENZIONE: reazione molto esotermica**<</R>>\n\nResa migliorata al **85%** rispetto al tentativo precedente (78%)."
            }
        },
        {
            "path": "Progetto_A/Purificazione/20260213_093000_Campione_A_Purificazione",
            "data": {
                "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
                "sample": "Campione_A",
                "category": "Purificazione",
                "description": "Ricristallizzazione da etanolo.\n\n**Procedura:**\n1. Tre cicli di purificazione\n2. Filtrazione a freddo\n3. Essiccazione sotto vuoto\n\n**Risultato finale:**\n- Purezza: <<R>>**99.2%**<</R>>\n- Perdita di materiale: 15%"
            }
        },
        {
            "path": "Test_Stabilita/20260214_150000_Campione_C_Test",
            "data": {
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
                "sample": "Campione_C",
                "category": "Test",
                "description": "Test di stabilità termica.\n\nCampione esposto a **150°C** per 24h.\n\n**Risultato:**\n- Stabile fino a <<R>>120°C<</R>>\n- Degradazione oltre questa temperatura\n- Vedere grafico TGA nella cartella"
            }
        },
        {
            "path": "20260215_110000_Campione_D_Analisi",
            "data": {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "sample": "Campione_D",
                "category": "Analisi",
                "description": "Analisi elementare e spettroscopia di massa.\n\n**Composizione trovata:**\n- C: 65.2% (teorico: 65.1%)\n- H: 5.8% (teorico: 5.9%)\n- N: 12.1% (teorico: 12.0%)\n\n**Massa molecolare:** 342.5 Da"
            }
        }
    ]
    
    # Crea le cartelle e i file data_description
    for example in examples:
        folder_path = base_folder / example["path"]
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Salva il file data_description.json
        data_file = folder_path / "data_description.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(example["data"], f, indent=2, ensure_ascii=False)
        
        # Crea un file README di esempio nella cartella
        readme_path = folder_path / "README.txt"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"Cartella dati per: {example['data']['sample']}\n")
            f.write(f"Esperimento: {example['data']['category']}\n")
            f.write(f"Data: {example['data']['date']}\n\n")
            f.write("In questa cartella puoi salvare:\n")
            f.write("- Grafici e immagini\n")
            f.write("- Tabelle Excel\n")
            f.write("- Spettri (NMR, IR, MS, ecc.)\n")
            f.write("- Foto del setup sperimentale\n")
            f.write("- Report PDF\n")
            f.write("- Qualsiasi altro file di dati\n")
        
        # Crea alcune sottocartelle di esempio
        (folder_path / "Immagini").mkdir(exist_ok=True)
        (folder_path / "Dati_Raw").mkdir(exist_ok=True)
    
    # Crea anche la configurazione
    config = {
        "base_data_folder": str(base_folder)
    }
    
    with open("logbook_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print("✓ Dati di esempio creati!")
    print(f"✓ Create {len(examples)} entrate di esempio")
    print(f"✓ Struttura cartelle:")
    print(f"   LabData/")
    print(f"   ├── Progetto_A/")
    print(f"   │   ├── Sintesi/")
    print(f"   │   ├── Caratterizzazione/")
    print(f"   │   └── Purificazione/")
    print(f"   ├── Progetto_B/")
    print(f"   ├── Test_Stabilita/")
    print(f"   └── [altre cartelle senza struttura fissa]")
    print()
    print("Ogni cartella con data_description.json è una entrata del logbook.")
    print("Puoi organizzare le cartelle come preferisci!")
    print("\nOra puoi avviare l'applicazione con: python lab_logbook.py")
    print("L'applicazione scansionerà automaticamente tutte le cartelle.")

if __name__ == "__main__":
    print("Creazione dati di esempio per Laboratory Logbook...")
    print("=" * 60)
    
    # Verifica se esistono già dati
    if os.path.exists("LabData"):
        risposta = input("\nLa cartella LabData esiste già. Vuoi sovrascrivere? (s/n): ")
        if risposta.lower() != 's':
            print("Operazione annullata.")
            exit()
    
    create_example_data()
