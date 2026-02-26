"""
Laboratory Logbook Application
Un'applicazione per tracciare esperimenti di laboratorio con gestione automatica delle cartelle
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
import re
from __version__ import version


class LabLogbook:
    def __init__(self, root):
        self.root = root
        self.root.title("Laboratory Logbook v" + version)
        # 75% di 1536x864 (risoluzione logica con scala 125% su 1920x1080), centrata
        self.root.geometry("1152x648+192+108")
        self.root.option_add("*Font", "{\"Segoe UI\"} 9")
        
        # Configurazione percorsi
        self.config_file = "logbook_config.json"
        self.data_description_filename = "data_description.json"
        self.load_config()
        
        # Categorie predefinite
        self.categories = [
            "Sintesi",
            "Caratterizzazione",
            "Purificazione",
            "Analisi",
            "Test",
            "Altro"
        ]
        
        # Markers per formattazione
        self.BOLD_START = "**"
        self.BOLD_END = "**"
        self.RED_START = "<<R>>"
        self.RED_END = "<</R>>"

        # Liste per autocomplete (popolate dopo scan)
        self.existing_samples = []
        self.all_categories = list(self.categories)
        self._tree_row_tags = set()
        
        self.create_widgets()
        self.scan_and_load_entries()
        self.refresh_entries_list()
        
    def load_config(self):
        """Carica la configurazione dell'applicazione"""
        default_config = {
            "base_data_folder": str(Path.home() / "LabData")
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
            
    def save_config(self):
        """Salva la configurazione"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
            
    def scan_and_load_entries(self):
        """Scansiona ricorsivamente la cartella base per trovare tutte le entrate"""
        self.entries = []
        base_folder = self.config["base_data_folder"]
        
        if not os.path.exists(base_folder):
            os.makedirs(base_folder, exist_ok=True)
            return
            
        self._scan_folder_recursive(base_folder)
        
        # Ordina per data (piu' recenti prima)
        self.entries.sort(key=lambda x: x["date"], reverse=True)

        # Raccogli valori unici per autocomplete
        self.existing_samples = sorted(set(e["sample"] for e in self.entries if e.get("sample")))
        self.all_categories = sorted(set(e["category"] for e in self.entries if e.get("category")))

        # Aggiorna i combobox se gia' esistono
        if hasattr(self, 'entry_sample'):
            self.entry_sample.config(values=self.existing_samples)
        if hasattr(self, 'entry_category'):
            self.entry_category.config(values=self.all_categories)
        if hasattr(self, 'filter_category'):
            self.filter_category.config(values=self.all_categories)
        
    def _scan_folder_recursive(self, folder_path):
        """Scansiona ricorsivamente una cartella per trovare file data_description"""
        try:
            data_file = os.path.join(folder_path, self.data_description_filename)
            
            if os.path.exists(data_file):
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        entry = json.load(f)
                        entry["folder"] = folder_path
                        self.entries.append(entry)
                except Exception as e:
                    print(f"Errore leggendo {data_file}: {e}")
                return
            
            try:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isdir(item_path):
                        self._scan_folder_recursive(item_path)
            except PermissionError:
                pass
                
        except Exception as e:
            print(f"Errore scansionando {folder_path}: {e}")
            
    def create_widgets(self):
        """Crea l'interfaccia grafica"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Ricarica Entrate", command=self.reload_entries)
        file_menu.add_command(label="Impostazioni", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Informazioni", command=self.show_about)
        
        # Frame principale con PanedWindow per resize colonna sinistra
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        outer_frame = ttk.Frame(self.root, padding="10")
        outer_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        outer_frame.columnconfigure(0, weight=1)
        outer_frame.rowconfigure(0, weight=1)

        paned = tk.PanedWindow(outer_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED,
                               sashwidth=6, bg="#cccccc")
        paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # LEFT PANEL - Lista entrate e filtri
        left_panel = ttk.Frame(paned)
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(2, weight=1)
        paned.add(left_panel, minsize=200)
        
        # Filtri
        filter_frame = ttk.LabelFrame(left_panel, text="Filtri", padding="5")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        filter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(filter_frame, text="Campione:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.filter_sample = ttk.Entry(filter_frame)
        self.filter_sample.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(filter_frame, text="Ricerca testo:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.filter_text = ttk.Entry(filter_frame)
        self.filter_text.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(filter_frame, text="Categoria:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.filter_category = ttk.Combobox(filter_frame, values=self.all_categories, state="normal")
        self.filter_category.set("")
        self.filter_category.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        self.filter_category.bind("<KeyRelease>", self._update_category_filter_autocomplete)
        
        filter_buttons = ttk.Frame(filter_frame)
        filter_buttons.grid(row=3, column=0, columnspan=2, pady=(5, 0))
        ttk.Button(filter_buttons, text="Applica Filtri", command=self.apply_filters).pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_buttons, text="Reset", command=self.reset_filters).pack(side=tk.LEFT, padx=2)
        
        # Pulsanti azione principali
        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        ttk.Button(btn_frame, text="+ Nuova Entrata", command=self.new_entry,
                   style="Accent.TButton").grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 2))
        ttk.Button(btn_frame, text="Registra esistente", command=self.register_existing_folder
                   ).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(2, 2))
        ttk.Button(btn_frame, text="Duplica", command=self.duplicate_entry
                   ).grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(2, 0))
        
        # Lista entrate
        list_frame = ttk.LabelFrame(left_panel, text="Entrate del Logbook", padding="5")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview per le entrate
        columns = ("Data", "Campione", "Categoria")
        style = ttk.Style()
        style.configure("Treeview", rowheight=36, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("Data", text="Data")
        self.tree.column("Data", width=100)
        self.tree.heading("Campione", text="Campione")
        self.tree.column("Campione", width=100)
        self.tree.heading("Categoria", text="Categoria")
        self.tree.column("Categoria", width=100)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_entry)
        
        # RIGHT PANEL - Dettagli entrata
        right_panel = ttk.Frame(paned)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        paned.add(right_panel, minsize=400)

        # Form per nuova entrata / visualizzazione
        self.form_frame = ttk.LabelFrame(right_panel, text="Dettagli Entrata", padding="10")
        self.form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.form_frame.columnconfigure(1, weight=1)
        
        # Campi del form
        FORM_FONT = ("Segoe UI", 11)
        row = 0
        ttk.Label(self.form_frame, text="Data:", font=FORM_FONT).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_date = ttk.Entry(self.form_frame, state="readonly", font=FORM_FONT)
        self.entry_date.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        
        row += 1
        ttk.Label(self.form_frame, text="Campione:", font=FORM_FONT).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_sample = ttk.Combobox(self.form_frame, values=self.existing_samples, state="normal", font=FORM_FONT)
        self.entry_sample.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.entry_sample.bind("<KeyRelease>", self._update_sample_autocomplete)
        self.entry_sample.bind("<Down>", lambda e: self.entry_sample.event_generate("<ButtonPress-1>") or "break")
        
        row += 1
        ttk.Label(self.form_frame, text="Categoria:", font=FORM_FONT).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_category = ttk.Combobox(self.form_frame, values=self.all_categories, state="normal", font=FORM_FONT)
        self.entry_category.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        self.entry_category.bind("<Down>", lambda e: self.entry_category.event_generate("<ButtonPress-1>") or "break")
        
        row += 1
        ttk.Label(self.form_frame, text="Cartella dati:", font=FORM_FONT).grid(row=row, column=0, sticky=tk.W, pady=5)
        folder_frame = ttk.Frame(self.form_frame)
        folder_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        self.entry_folder = ttk.Entry(folder_frame, state="readonly")
        self.entry_folder.grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(folder_frame, text="Apri", command=self.open_folder, width=8).grid(row=0, column=1, padx=(5, 0))
        
        row += 1
        desc_label_frame = ttk.Frame(self.form_frame)
        desc_label_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        ttk.Label(desc_label_frame, text="Descrizione:").pack(side=tk.LEFT)
        
        # Pulsanti formattazione
        format_frame = ttk.Frame(desc_label_frame)
        format_frame.pack(side=tk.RIGHT)
        ttk.Button(format_frame, text="B", command=self.toggle_bold, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(format_frame, text="R", command=self.toggle_red, width=3).pack(side=tk.LEFT, padx=2)
        
        row += 1
        text_frame = ttk.Frame(self.form_frame)
        text_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        self.form_frame.rowconfigure(row, weight=1)
        
        self.entry_description = tk.Text(text_frame, height=1, wrap=tk.WORD, font=("Segoe UI", 11))
        self.entry_description.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        desc_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.entry_description.yview)
        desc_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.entry_description.configure(yscrollcommand=desc_scrollbar.set)
        
        # Configurazione tag per formattazione
        self.entry_description.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        self.entry_description.tag_configure("red", foreground="red")
        self.entry_description.tag_configure("bold_red", font=("Segoe UI", 11, "bold"), foreground="red")

        # Scorciatoie da tastiera (return "break" previene il comportamento default di tkinter)
        def _shortcut_bold(e):
            self.toggle_bold()
            return "break"
        def _shortcut_red(e):
            self.toggle_red()
            return "break"
        self.entry_description.bind("<Control-b>", _shortcut_bold)
        self.entry_description.bind("<Control-B>", _shortcut_bold)
        self.entry_description.bind("<Control-r>", _shortcut_red)
        self.entry_description.bind("<Control-R>", _shortcut_red)
        
        # Pulsanti azione
        row += 1
        button_frame = ttk.Frame(self.form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))
        
        self.btn_save = ttk.Button(button_frame, text="Salva", command=self.save_entry)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        self.btn_cancel = ttk.Button(button_frame, text="Annulla", command=self.cancel_edit)
        self.btn_cancel.pack(side=tk.LEFT, padx=5)
        
        self.set_view_mode()

    # ------------------------------------------------------------------ #
    #  Autocomplete campione                                               #
    # ------------------------------------------------------------------ #

    def _update_sample_autocomplete(self, event=None):
        """Filtra la lista del combobox campione in base al testo digitato"""
        typed = self.entry_sample.get().lower()
        if typed:
            filtered = [s for s in self.existing_samples if typed in s.lower()]
        else:
            filtered = self.existing_samples
        self.entry_sample.config(values=filtered)

    def _update_category_filter_autocomplete(self, event=None):
        """Filtra i suggerimenti del filtro categoria in base al testo digitato"""
        typed = self.filter_category.get().lower()
        if typed:
            filtered = [c for c in self.all_categories if typed in c.lower()]
        else:
            filtered = self.all_categories
        self.filter_category.config(values=filtered)

    # ------------------------------------------------------------------ #
    #  Nuova entrata / Registra cartella esistente                        #
    # ------------------------------------------------------------------ #

    def new_entry(self):
        """Prepara il form per una nuova entrata"""
        self.current_entry_folder = None
        self.set_edit_mode()
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.entry_date.config(state="normal")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, current_date)
        
        self.entry_sample.set("")
        self.entry_sample.config(values=self.existing_samples)
        self.entry_category.set("")
        self.entry_folder.config(state="normal")
        self.entry_folder.delete(0, tk.END)
        self.entry_folder.insert(0, "[Verra' creata automaticamente]")
        self.entry_folder.config(state="readonly")
        self.entry_description.delete("1.0", tk.END)
        
        self.form_frame.config(text="Nuova Entrata")

    def duplicate_entry(self):
        """Crea una nuova entrata copiando la descrizione dell'entrata selezionata"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un'entrata da duplicare")
            return
        
        item = self.tree.item(selection[0])
        entry_index = int(item["text"])
        source_entry = self.entries[entry_index]
        
        # Prepara una nuova entrata (come new_entry)
        self.current_entry_folder = None
        self.set_edit_mode()
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.entry_date.config(state="normal")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, current_date)
        
        self.entry_sample.set(source_entry["sample"])
        self.entry_sample.config(values=self.existing_samples)
        self.entry_category.set(source_entry["category"])
        
        self.entry_folder.config(state="normal")
        self.entry_folder.delete(0, tk.END)
        self.entry_folder.insert(0, "[Verra' creata automaticamente]")
        self.entry_folder.config(state="readonly")
        
        self.entry_description.config(state="normal")
        self.entry_description.delete("1.0", tk.END)
        self.apply_text_from_markers(source_entry["description"])
        
        self.form_frame.config(text="Nuova Entrata (duplicata)")

    def register_existing_folder(self):
        """Registra una cartella esistente aggiungendo un file data_description"""
        folder = filedialog.askdirectory(
            title="Seleziona la cartella con i dati da registrare",
            initialdir=self.config["base_data_folder"]
        )
        if not folder:
            return

        # Controlla se esiste gia' un data_description
        data_file = os.path.join(folder, self.data_description_filename)
        if os.path.exists(data_file):
            messagebox.showwarning(
                "Attenzione",
                "Questa cartella ha gia' un file data_description.\n"
                "Selezionala dalla lista per modificarla."
            )
            return

        # Imposta la cartella e prepara il form
        self.current_entry_folder = folder
        self.set_edit_mode()

        # Usa la data di modifica della cartella come data predefinita
        try:
            mtime = os.path.getmtime(folder)
            folder_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            folder_date = datetime.now().strftime("%Y-%m-%d %H:%M")

        self.entry_date.config(state="normal")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, folder_date)

        self.entry_sample.set("")
        self.entry_sample.config(values=self.existing_samples)
        self.entry_category.set("")

        self.entry_folder.config(state="normal")
        self.entry_folder.delete(0, tk.END)
        self.entry_folder.insert(0, folder)
        self.entry_folder.config(state="readonly")

        self.entry_description.config(state="normal")
        self.entry_description.delete("1.0", tk.END)

        folder_name = os.path.basename(folder)
        self.form_frame.config(text=f"Registra: {folder_name}")
        self.entry_sample.focus()

    # ------------------------------------------------------------------ #
    #  Salvataggio                                                         #
    # ------------------------------------------------------------------ #

    def save_entry(self):
        """Salva l'entrata corrente"""
        sample = self.entry_sample.get().strip()
        category = self.entry_category.get().strip()
        date_str = self.entry_date.get().strip()
        
        if not sample:
            messagebox.showerror("Errore", "Il campo 'Campione' e' obbligatorio")
            return
        
        # Valida formato data
        try:
            datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Errore", "Formato data non valido. Usa: YYYY-MM-DD HH:MM")
            return
        
        # Se nuova entrata (nessuna cartella pre-esistente), crea la cartella
        if self.current_entry_folder is None:
            folder_date_prefix = datetime.now().strftime("%Y-%m-%d")
            folder_name = f"{folder_date_prefix}_{sample}_{category}".replace(" ", "_")
            default_subfolder = os.path.join(self.config["base_data_folder"], "general")
            folder_path = os.path.join(default_subfolder, folder_name)
            
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile creare la cartella:\n{str(e)}")
                return
        else:
            # Usa la cartella esistente (modifica o registrazione di cartella esistente)
            folder_path = self.entry_folder.get()
        
        formatted_description = self.get_formatted_text_with_markers()
        
        entry_data = {
            "date": date_str,
            "sample": sample,
            "category": category,
            "description": formatted_description
        }
        
        data_file_path = os.path.join(folder_path, self.data_description_filename)
        try:
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare i dati:\n{str(e)}")
            return
        
        self.scan_and_load_entries()
        self.refresh_entries_list()
        self.set_view_mode()
        
    def cancel_edit(self):
        """Annulla la modifica corrente"""
        self.set_view_mode()
        
    def on_select_entry(self, event):
        """Gestisce la selezione di un'entrata dalla lista"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        entry_index = int(item["text"])
        
        if entry_index < len(self.entries):
            entry = self.entries[entry_index]
            self.current_entry_folder = entry["folder"]
            self.display_entry(entry)
        
    def display_entry(self, entry):
        """Visualizza un'entrata nel pannello dettagli"""
        self.set_edit_mode()
        
        self.entry_date.config(state="normal")
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, entry["date"])
        
        self.entry_sample.set(entry["sample"])
        self.entry_category.set(entry["category"])
        
        self.entry_folder.config(state="normal")
        self.entry_folder.delete(0, tk.END)
        self.entry_folder.insert(0, entry["folder"])
        self.entry_folder.config(state="readonly")
        
        self.entry_description.delete("1.0", tk.END)
        self.apply_text_from_markers(entry["description"])
        
        folder_name = os.path.basename(entry["folder"])
        self.form_frame.config(text=f"Entrata: {folder_name}")
        
    def get_formatted_text_with_markers(self):
        """Ottiene il testo con markers per formattazione (**, <<R>>)"""
        result = []
        current_pos = "1.0"
        
        while True:
            next_pos = self.entry_description.index(f"{current_pos} + 1 chars")
            if self.entry_description.compare(next_pos, ">=", tk.END):
                break
            
            char = self.entry_description.get(current_pos, next_pos)
            tags = self.entry_description.tag_names(current_pos)
            
            prev_pos = self.entry_description.index(f"{current_pos} - 1 chars")
            prev_tags = self.entry_description.tag_names(prev_pos) if self.entry_description.compare(current_pos, ">", "1.0") else []
            
            is_bold = "bold" in tags or "bold_red" in tags
            is_red = "red" in tags or "bold_red" in tags
            was_bold = "bold" in prev_tags or "bold_red" in prev_tags
            was_red = "red" in prev_tags or "bold_red" in prev_tags
            
            if is_bold and not was_bold:
                result.append(self.BOLD_START)
            if is_red and not was_red:
                result.append(self.RED_START)
            if was_bold and not is_bold:
                result.append(self.BOLD_END)
            if was_red and not is_red:
                result.append(self.RED_END)
            
            result.append(char)
            current_pos = next_pos
        
        last_tags = self.entry_description.tag_names(self.entry_description.index("end - 2 chars"))
        if "bold" in last_tags or "bold_red" in last_tags:
            result.append(self.BOLD_END)
        if "red" in last_tags or "bold_red" in last_tags:
            result.append(self.RED_END)
        
        return "".join(result)
    
    def apply_text_from_markers(self, text):
        """Applica la formattazione da testo con markers"""
        self.entry_description.delete("1.0", tk.END)
        
        i = 0
        insert_pos = "1.0"
        bold_active = False
        red_active = False
        bold_start_pos = None
        red_start_pos = None
        
        while i < len(text):
            if text[i:i+len(self.BOLD_START)] == self.BOLD_START:
                if not bold_active:
                    bold_active = True
                    bold_start_pos = insert_pos
                else:
                    bold_active = False
                    if red_active:
                        self.entry_description.tag_add("bold_red", bold_start_pos, insert_pos)
                    else:
                        self.entry_description.tag_add("bold", bold_start_pos, insert_pos)
                i += len(self.BOLD_START)
                continue
            
            if text[i:i+len(self.RED_START)] == self.RED_START:
                red_active = True
                red_start_pos = insert_pos
                i += len(self.RED_START)
                continue
            
            if text[i:i+len(self.RED_END)] == self.RED_END:
                red_active = False
                if bold_active:
                    self.entry_description.tag_add("bold_red", red_start_pos, insert_pos)
                else:
                    self.entry_description.tag_add("red", red_start_pos, insert_pos)
                i += len(self.RED_END)
                continue
            
            self.entry_description.insert(insert_pos, text[i])
            insert_pos = self.entry_description.index(f"{insert_pos} + 1 chars")
            i += 1
                
    def toggle_bold(self):
        """Applica/rimuove grassetto al testo selezionato"""
        try:
            start = self.entry_description.index(tk.SEL_FIRST)
            end = self.entry_description.index(tk.SEL_LAST)
            
            current_tags = self.entry_description.tag_names(start)
            
            if "bold" in current_tags or "bold_red" in current_tags:
                self.entry_description.tag_remove("bold", start, end)
                if "bold_red" in current_tags:
                    self.entry_description.tag_remove("bold_red", start, end)
                    self.entry_description.tag_add("red", start, end)
            else:
                if "red" in current_tags:
                    self.entry_description.tag_remove("red", start, end)
                    self.entry_description.tag_add("bold_red", start, end)
                else:
                    self.entry_description.tag_add("bold", start, end)
        except tk.TclError:
            messagebox.showwarning("Attenzione", "Seleziona del testo prima di applicare la formattazione")
            
    def toggle_red(self):
        """Applica/rimuove colore rosso al testo selezionato"""
        try:
            start = self.entry_description.index(tk.SEL_FIRST)
            end = self.entry_description.index(tk.SEL_LAST)
            
            current_tags = self.entry_description.tag_names(start)
            
            if "red" in current_tags or "bold_red" in current_tags:
                self.entry_description.tag_remove("red", start, end)
                if "bold_red" in current_tags:
                    self.entry_description.tag_remove("bold_red", start, end)
                    self.entry_description.tag_add("bold", start, end)
            else:
                if "bold" in current_tags:
                    self.entry_description.tag_remove("bold", start, end)
                    self.entry_description.tag_add("bold_red", start, end)
                else:
                    self.entry_description.tag_add("red", start, end)
        except tk.TclError:
            messagebox.showwarning("Attenzione", "Seleziona del testo prima di applicare la formattazione")
            
    def open_folder(self):
        """Apre la cartella dati dell'entrata corrente"""
        folder = self.entry_folder.get()
        if not folder or not os.path.exists(folder):
            messagebox.showerror("Errore", "La cartella non esiste")
            return
            
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder])
        else:
            subprocess.run(["xdg-open", folder])
            
    def refresh_entries_list(self):
        """Aggiorna la lista delle entrate"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for idx, entry in enumerate(self.entries):
            date_short = entry["date"].split()[0]
            sample_display = entry["sample"].replace(", ", "\n").replace(",", "\n")
            self.tree.insert("", tk.END, text=str(idx),
                           values=(date_short, sample_display, entry["category"]))
                           
    def apply_filters(self):
        """Applica i filtri alla lista delle entrate"""
        sample_filter = self.filter_sample.get().strip().lower()
        text_filter = self.filter_text.get().strip().lower()
        category_filter = self.filter_category.get().strip().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        filtered_entries = []
        for idx, entry in enumerate(self.entries):
            if sample_filter and sample_filter not in entry["sample"].lower():
                continue
            if category_filter and category_filter not in entry["category"].lower():
                continue
            description_clean = entry["description"]
            description_clean = description_clean.replace(self.BOLD_START, "").replace(self.BOLD_END, "")
            description_clean = description_clean.replace(self.RED_START, "").replace(self.RED_END, "")
            if text_filter and text_filter not in description_clean.lower():
                continue
            filtered_entries.append((idx, entry))
            
        for idx, entry in filtered_entries:
            date_short = entry["date"].split()[0]
            sample_display = entry["sample"].replace(", ", "\n").replace(",", "\n")
            self.tree.insert("", tk.END, text=str(idx),
                           values=(date_short, sample_display, entry["category"]))
                           
        if not filtered_entries:
            messagebox.showinfo("Filtri", "Nessuna entrata corrisponde ai filtri selezionati")
            
    def reset_filters(self):
        """Resetta i filtri"""
        self.filter_sample.delete(0, tk.END)
        self.filter_text.delete(0, tk.END)
        self.filter_category.set("")
        self.refresh_entries_list()
        
    def set_edit_mode(self):
        """Imposta la modalita' di modifica"""
        self.entry_sample.config(state="normal")
        self.entry_category.config(state="normal")
        self.entry_description.config(state="normal")
        self.btn_save.config(state="normal")
        self.btn_cancel.config(state="normal")
            
    def set_view_mode(self):
        """Imposta la modalita' visualizzazione (campi disabilitati, form pulito)"""
        self.btn_save.config(state="disabled")
        self.btn_cancel.config(state="disabled")
        
        self.entry_date.config(state="normal")
        self.entry_date.delete(0, tk.END)
        self.entry_date.config(state="readonly")
        
        self.entry_sample.set("")
        self.entry_sample.config(state="disabled")
        
        self.entry_category.set("")
        self.entry_category.config(state="disabled")
        
        self.entry_folder.config(state="normal")
        self.entry_folder.delete(0, tk.END)
        self.entry_folder.config(state="readonly")
        
        self.entry_description.config(state="normal")
        self.entry_description.delete("1.0", tk.END)
        self.entry_description.config(state="disabled")
        
        self.form_frame.config(text="Seleziona un'entrata")
        self.current_entry_folder = None
        
    def reload_entries(self):
        """Ricarica tutte le entrate scansionando nuovamente le cartelle"""
        self.scan_and_load_entries()
        self.refresh_entries_list()
        self.set_view_mode()
        messagebox.showinfo("Ricarica", f"Trovate {len(self.entries)} entrate nel logbook")
    
    def show_settings(self):
        """Mostra la finestra delle impostazioni"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Impostazioni")
        settings_window.geometry("500x200")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Cartella base per i dati:").grid(row=0, column=0, sticky=tk.W, pady=10)
        
        folder_frame = ttk.Frame(frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        folder_frame.columnconfigure(0, weight=1)
        
        folder_entry = ttk.Entry(folder_frame)
        folder_entry.insert(0, self.config["base_data_folder"])
        folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        def browse_folder():
            folder = filedialog.askdirectory(initialdir=folder_entry.get())
            if folder:
                folder_entry.delete(0, tk.END)
                folder_entry.insert(0, folder)
                
        ttk.Button(folder_frame, text="Sfoglia", command=browse_folder).grid(row=0, column=1, padx=(5, 0))
        
        def save_settings():
            self.config["base_data_folder"] = folder_entry.get()
            self.save_config()
            messagebox.showinfo("Impostazioni", "Impostazioni salvate!")
            settings_window.destroy()
            
        ttk.Button(frame, text="Salva", command=save_settings).grid(row=2, column=0, pady=20)
        
    def show_about(self):
        """Mostra la finestra informazioni"""
        messagebox.showinfo("Informazioni", 
                          "Laboratory Logbook v1.1\n\n"
                          "Un'applicazione per tracciare esperimenti di laboratorio\n"
                          "con gestione automatica delle cartelle dati.\n\n"
                          "Funzionalita':\n"
                          "- Logbook con data, campione, categoria\n"
                          "- Formattazione testo (grassetto, rosso)\n"
                          "- Creazione automatica cartelle\n"
                          "- Registrazione di cartelle dati esistenti\n"
                          "- Filtri per campione, categoria e testo\n"
                          "- Autocomplete campione e categoria")


def main():
    root = tk.Tk()
    app = LabLogbook(root)
    root.mainloop()


if __name__ == "__main__":
    main()
