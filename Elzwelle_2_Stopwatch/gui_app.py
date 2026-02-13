import time
import ttkbootstrap as ttk
import tkinter as tk
import elzwelle_global as glob

from ttkbootstrap.widgets.tableview import Tableview
from ttkbootstrap.constants import SUCCESS, PRIMARY, DANGER

from elzwelle_config import HOST_NAME 
#from elzwelle_global import program_launch_time_stamp

from queue import Empty

class MainApp(ttk.Window):
    def __init__(self, gui_queue, manager):
        # Initialisiere die Window-Klasse mit Theme und Titel
        super().__init__(themename="cosmo", title="Elzwelle Stopuhr")
        
        self.gui_queue = gui_queue
        
        # Speichere die Referenz auf den DataManager
        self.manager = manager
        
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
        # Tableview uses Treeview style
        self.style.map("Treeview", rowheight=[("!disabled", 20)])
        
    def initialize(self):
        self.start_id = 1;
        self.finish_id = 1;
        # Widgets hier erstellen
        
        self.labelVariable = ttk.StringVar()
        label = ttk.Label(self,textvariable=self.labelVariable,anchor="w",
                          foreground="#3498db",  # Ein schönes Blau
                          background="#f8f9fa")  # Sehr helles Grau
        label.grid(row=0,column=0,columnspan=2,sticky="EW",padx=10, pady=5)
        self.labelVariable.set(HOST_NAME)
        
        start_button = ttk.Button(self, text="Start",command=self.start_button_clicked, bootstyle=SUCCESS)
        start_button.grid(row=1,column=0,sticky="EW",padx=10, pady=5)
        
        #Add a button that says 'Ziel' at (1,1)
        finish_button = ttk.Button(self,text="Ziel",command=self.finish_button_clicked, bootstyle=DANGER)
        finish_button.grid(row=1,column=1,sticky="EW",padx=10, pady=5)
        
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
            paginated=False,                                # Enable pagination
            coldata=start_header,                           # Column headers
            rowdata=start_data,                             # Table data
            searchable=False,                               # Enable search feature
            bootstyle=PRIMARY,                              # Bootstrap style
            stripecolor=(self.style.colors.light, None),    # Row stripe colors
            yscrollbar=True
        )

        self.start_table.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')
        
        # Autofit columns to match content
        self.start_table.autofit_columns()

        # Rechtsklick NUR auf die interne View binden
        self.start_table.view.bind("<Button-3>", self.start_copy_menu)
        self.start_table.view.unbind("<Button-1>")
        
        # Strg+C an das Fenster oder die Tableview binden
        self.start_table.view.bind("<Control-c>", self.start_control_c)
       
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
            paginated=False,                                # Enable pagination
            coldata=finish_header,                          # Column headers
            rowdata=finish_data,                            # Table data
            searchable=False,                               # Enable search feature
            bootstyle=PRIMARY,                              # Bootstrap style
            stripecolor=(self.style.colors.light, None),    # Row stripe colors
            yscrollbar=True
        )
   
        self.finish_table.grid(row=2, column=1, padx=10, pady=5, sticky='nsew')
        
        # Autofit columns to match content
        self.finish_table.autofit_columns()
        
        # Rechtsklick NUR auf die interne View binden
        self.finish_table.view.bind("<Button-3>", self.finish_copy_menu)
        self.finish_table.view.unbind("<Button-1>")
        
        # Strg+C an das Fenster oder die Tableview binden
        self.finish_table.view.bind("<Control-c>", self.finish_control_c)
        
        help_label = ttk.Label(self, text="Zurück zum Fenstermodus mit ESC", font=("Helvetica", 9) )
        help_label.grid(row=3,column=0,sticky="EW",padx=10, pady=5, columnspan = 2)
        
        # Start Polling
        self.after(100, self.poll_queue)
       
    def start_control_c(self, event=None):
        # 1. Die aktuell fokussierte Zeile und Spalte finden
        row_id = self.start_table.view.focus()
        row_data = self.start_table.view.item(row_id)['values']
        # 3. In Zwischenablage kopieren
        self.clipboard_clear()
        self.clipboard_append(str(row_data))
        self.update() # Synchronisiert mit dem OS-Clipboard
        print(row_data)
    
    def finish_control_c(self, event=None):
        # 1. Die aktuell fokussierte Zeile und Spalte finden
        row_id = self.finish_table.view.focus()
        row_data = self.finish_table.view.item(row_id)['values']
        # 3. In Zwischenablage kopieren
        self.clipboard_clear()
        self.clipboard_append(str(row_data))
        self.update() # Synchronisiert mit dem OS-Clipboard
        print(row_data)
        
    def scroll_to_last(self,table):
        # 1. Alle Zeilen-IDs aus der internen Treeview abrufen
        all_rows = table.view.get_children()
        
        if all_rows:
            last_row_id = all_rows[-1] # Die ID der letzten Zeile           
            # 2. Die letzte Zeile markieren (optional)
            table.view.selection_set(last_row_id)           
            # 3. Den Fokus auf die letzte Zeile setzen und dorthin scrollen
            table.view.focus(last_row_id)
            table.view.see(last_row_id)
            
    def start_button_clicked(self):
        pl = "{:.2f}".format(time.time() - glob.program_launch_time_stamp)
        self.manager.dispatch("Start", pl)
    
    def finish_button_clicked(self):
        pl = "{:.2f}".format(time.time() - glob.program_launch_time_stamp)
        self.manager.dispatch("Finish",pl)
       
    def start_copy_menu(self, event):
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
                command=lambda: self.copy_to_clipboard(cell_value)
            )
            # Menü an Mausposition anzeigen
            menu.post(event.x_root, event.y_root)

    def finish_copy_menu(self, event):
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
                command=lambda: self.copy_to_clipboard(cell_value)
            )
            # Menü an Mausposition anzeigen
            menu.post(event.x_root, event.y_root)
            
    def copy_to_clipboard(self, value):
        self.clipboard_clear()
        self.clipboard_append(str(value))
        # Optional: Kleiner Hinweis in der Statuszeile oder Konsole
        print(f"Kopiert: {value}")   
    
    def poll_queue(self):
        try:
            while True:
                source, data = self.gui_queue.get_nowait()
                # print(f"GUI poll: {source} {data}")
                t = time.strftime('%H:%M:%S', time.localtime(time.time()))
                        
                try:
                    if source != "MQTT":
                        s = float(data)
                        d = (time.time() - glob.program_launch_time_stamp) - s
                        f = "{:.2f}".format(s).replace(".",",")
                        print('Delta\t{:.3f}'.format(d))
                        print('Stamp\t{0:.3f} -- {1:.3f}'.format(s,time.time() - glob.program_launch_time_stamp))
                               
                        if source == "Finish":
                            self.finish_table.insert_row('end', [self.finish_id, t, f])
                            self.finish_id = self.finish_id + 1
                            self.scroll_to_last(self.finish_table)
                            self.finish_table.load_table_data()
                    
                        if source == "Start":
                            self.start_table.insert_row('end', [self.start_id, t, f])
                            self.start_id = self.start_id + 1
                            self.scroll_to_last(self.start_table)
                            self.start_table.load_table_data()
                        
                        if source == "Stamp":
                            # f = "{:.2f}".format(s).replace(".",",")
                            sync_time_stamp = "{}      |      {}      |      ".format(HOST_NAME, t) + f
                            self.labelVariable.set(sync_time_stamp) 
                            self.manager.update_sync_time_stamp(sync_time_stamp)
                            
                except ValueError:
                    print("EXCEPTION serial_time_stamp:  Not a float")
                     
        except Empty:
            pass
        finally:
            self.after(100, self.poll_queue)