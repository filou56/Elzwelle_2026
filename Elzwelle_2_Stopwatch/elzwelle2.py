import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.tableview import Tableview
from ttkbootstrap.constants import SUCCESS, PRIMARY, DANGER

class SimpleApp(ttk.Window):
    def __init__(self, **kwargs):
        # Initialisiere die Window-Klasse mit Theme und Titel
        super().__init__(themename="cosmo", title="Elzwelle Stopuhr", **kwargs)
        # 1. Vollbildmodus aktivieren
        #self.attributes("-fullscreen", True)
        
        # 2. ESC-Taste binden, um Vollbild zu verlassen
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        # optional 
        self.geometry("800x500")
        self.style.configure('.', font=('Helvetica', 16))
        self.initialize()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.configure(background='#dddddd') 

    def initialize(self):
        self.start_id = 1;
        self.finish_id = 1;
        # Widgets hier erstellen
        # In ttkbootstrap nutzt man bevorzugt ttk-Widgets
        button1= ttk.Button(self, text="Start",command=self.StartButtonClicked, bootstyle=SUCCESS)
        button1.grid(row=1,column=0,sticky="EW",padx=10, pady=5)
        
        #Add a button that says 'Ziel' at (1,1)
        button2 = ttk.Button(self,text="Ziel",command=self.FinishButtonClicked, bootstyle=DANGER)
        button2.grid(row=1,column=1,sticky="EW",padx=10, pady=5)
        
        start_header = [
            {"text":"ID"},
            {"text":"Startzeit","stretch":True},
            {"text":"Zeitstempel","stretch":True},
        ]
        
        start_data = [
        ]
        
        # Create Tableview Widget
        self.start_table = Tableview(
            master=self,
            paginated=False,                    # Enable pagination
            coldata=start_header,               # Column headers
            rowdata=start_data,                 # Table data
            searchable=False,                   # Enable search feature
            bootstyle=PRIMARY,                  # Bootstrap style
            stripecolor=(self.style.colors.light, None),   # Row stripe colors
            yscrollbar=True
        )

        self.start_table.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')
        
        # Autofit columns to match content
        self.start_table.autofit_columns()

        # Rechtsklick NUR auf die interne View binden
        self.start_table.view.bind("<Button-3>", self.StartCopyMenu)
        self.start_table.view.unbind("<Button-1>")
        
        # Strg+C an das Fenster oder die Tableview binden
        self.start_table.view.bind("<Control-c>", self.StartControl_C)
       
        finish_header = [
            {"text":"ID"},
            {"text":"Zielzeit","stretch":True},
            {"text":"Zeitstempel","stretch":True},
        ]
        
        finish_data = [
        ]
        
        # Create Tableview Widget
        self.finish_table = Tableview(
            master=self,
            paginated=False,                    # Enable pagination
            coldata=finish_header,              # Column headers
            rowdata=finish_data,                # Table data
            searchable=False,                   # Enable search feature
            bootstyle=PRIMARY,                  # Bootstrap style
            stripecolor=(self.style.colors.light, None),   # Row stripe colors
            yscrollbar=True
        )
   
        self.finish_table.grid(row=2, column=1, padx=10, pady=5, sticky='nsew')
        
        # Autofit columns to match content
        self.finish_table.autofit_columns()
        
        # Rechtsklick NUR auf die interne View binden
        self.finish_table.view.bind("<Button-3>", self.FinishCopyMenu)
        self.finish_table.view.unbind("<Button-1>")
        
        # Strg+C an das Fenster oder die Tableview binden
        self.finish_table.view.bind("<Control-c>", self.FinishControl_C)
        
    def StartControl_C(self, event=None):
        # 1. Die aktuell fokussierte Zeile und Spalte finden
        row_id = self.start_table.view.focus()
        row_data = self.start_table.view.item(row_id)['values']
        # 3. In Zwischenablage kopieren
        self.clipboard_clear()
        self.clipboard_append(str(row_data))
        self.update() # Synchronisiert mit dem OS-Clipboard
        print(row_data)
    
    def FinishControl_C(self, event=None):
        # 1. Die aktuell fokussierte Zeile und Spalte finden
        row_id = self.finish_table.view.focus()
        row_data = self.finish_table.view.item(row_id)['values']
        # 3. In Zwischenablage kopieren
        self.clipboard_clear()
        self.clipboard_append(str(row_data))
        self.update() # Synchronisiert mit dem OS-Clipboard
        print(row_data)
        
    def ScrollToLast(self,table):
        # 1. Alle Zeilen-IDs aus der internen Treeview abrufen
        all_rows = table.view.get_children()
        
        if all_rows:
            last_row_id = all_rows[-1] # Die ID der letzten Zeile
            
            # 2. Die letzte Zeile markieren (optional)
            table.view.selection_set(last_row_id)
            
            # 3. Den Fokus auf die letzte Zeile setzen und dorthin scrollen
            table.view.focus(last_row_id)
            table.view.see(last_row_id)
            
    def StartButtonClicked(self):
        #start_sensor_triggered(None)
        self.start_table.insert_row('end', [self.start_id,"00:00:00", 0])
        self.start_id = self.start_id + 1
        self.ScrollToLast(self.start_table)

    def FinishButtonClicked(self):
        #finish_sensor_triggered(None)
        self.finish_table.insert_row('end', [self.finish_id,"00:00:00", 0])
        self.finish_id = self.finish_id + 1
        self.ScrollToLast(self.finish_table)
       
    def StartCopyMenu(self, event):
        # Identifiziere die Zelle
        row_id = self.start_table.view.identify_row(event.y)
        column_id = self.start_table.view.identify_column(event.x)
        
        if row_id and column_id:
            # Spaltenindex berechnen
            col_idx = int(column_id.replace('#', '')) - 1
            # Wert extrahieren
            cell_value = self.start_table.view.item(row_id)['values'][col_idx]

            # Neues, sauberes Menü ohne andere Optionen
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(
                label=f"Wert kopieren: {cell_value}", 
                command=lambda: self.CopyToClipboard(cell_value)
            )
            # Menü an Mausposition anzeigen
            menu.post(event.x_root, event.y_root)

    def FinishCopyMenu(self, event):
        # Identifiziere die Zelle
        row_id = self.finish_table.view.identify_row(event.y)
        column_id = self.finish_table.view.identify_column(event.x)
        
        if row_id and column_id:
            # Spaltenindex berechnen
            col_idx = int(column_id.replace('#', '')) - 1
            # Wert extrahieren
            cell_value = self.finish_table.view.item(row_id)['values'][col_idx]

            # Neues, sauberes Menü ohne andere Optionen
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(
                label=f"Wert kopieren: {cell_value}", 
                command=lambda: self.CopyToClipboard(cell_value)
            )
            # Menü an Mausposition anzeigen
            menu.post(event.x_root, event.y_root)
            
    def CopyToClipboard(self, value):
        self.clipboard_clear()
        self.clipboard_append(str(value))
        # Optional: Kleiner Hinweis in der Statuszeile oder Konsole
        print(f"Kopiert: {value}")
        
if __name__ == "__main__":
    app = SimpleApp()
    app.mainloop()



# start_table.insert_row('end', ['Marzale LLC', 26])