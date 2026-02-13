
import time
from time import sleep
import socket
import http.server
import platform
import threading
#import tkinter
import os
import serial
import configparser
import googlesheet
import gc
import uuid
import paho.mqtt.client as paho

from   paho import mqtt
from   pathlib import Path

# Google Spreadsheet ID for publishing times
# Elzwelle SPREADSHEET_ID = '1obtfHymwPSGoGoROUialryeGiMJ1vkEUWL_Gze_hyfk'
# FilouWelle spreadsheet_xxx, err := service.FetchSpreadsheet("1M05W0igR6stS4UBPfbe7-MFx0qoe5w6ktWAcLVCDZTE")
SPREADSHEET_ID = '1M05W0igR6stS4UBPfbe7-MFx0qoe5w6ktWAcLVCDZTE'

#CLIENT_SECRET_JSON = 'client_secret.json'

# How many time stamps should be stored and shown on the web page
KEEP_NUM_TIME_STAMPS = 20

# 10.02.2018 HM
NUMBER_OF_EVENT = 300

# define length for shortest pulse in seconds
#IGNORE_PULSE_LENGTH_SEC = 0.05

# GPIO pins for start and stop sensor
START_GPIO_PIN  = 20
FINISH_GPIO_PIN = 21

# Port number for the web server
PORT_NUMBER = 8080 # Maybe set this to 9000.

# host name (or IP address) for the web server
# copy-paste from the internet
# TODO: do not crash when network is unreachable.
HOST_NAME = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

# some global variables
program_launch_time_stamp = float(int(time.time()))

time_stamps_start  = [program_launch_time_stamp] * KEEP_NUM_TIME_STAMPS
time_stamps_finish = [program_launch_time_stamp] * KEEP_NUM_TIME_STAMPS

# 12.01.2024 WF
time_stamps_start_dirty  = False
time_stamps_finish_dirty = False

update_time_stamp        = False
serial_time_stamp        = 0

serial_time_stamp_start  = 0
serial_time_stamp_finish = 0

view_time_stamp_start    = 0
view_time_stamp_finish   = 0

# 10.02.2018 HM
time_stamps_start_all  = [program_launch_time_stamp] * NUMBER_OF_EVENT
time_stamps_finish_all = [program_launch_time_stamp] * NUMBER_OF_EVENT

# For publishing times in Google spreadsheet_xxx
#start_sheet  = Spreadsheet(spreadsheet_id=SPREADSHEET_ID, tab_name='Start')
#finish_sheet = Spreadsheet(spreadsheet_id=SPREADSHEET_ID, tab_name='Ziel')

def StartSensorTriggered():
    global time_stamps_start_dirty 
    global serial_time_stamp_start
    global view_time_stamp_start

    if serial_time_stamp_start == 0:
        t = time.time()
    else:
        t = serial_time_stamp_start
        serial_time_stamp_start = 0

    t2 = t - program_launch_time_stamp
    print(("adding start timestamp: {:.2f} ".format(t2)))
    time_stamps_start.insert(0, t)
    while( len(time_stamps_start) > KEEP_NUM_TIME_STAMPS):
        time_stamps_start.pop()

    time_stamps_start_all.insert(0, t)
    while( len(time_stamps_start_all) > NUMBER_OF_EVENT):
        time_stamps_start_all.pop()
#TODO    start_sheet.add_entry([time.strftime('%H:%M:%S', time.localtime(t)), t2])

    if config.getboolean('mqtt', 'enabled'):
        mqtt_client.publish("elzwelle/stopwatch/start", 
                            payload=time.strftime('%H:%M:%S', time.localtime(t)) 
                            + " {:.2f} 0".format(t2).replace(".",","), 
                            qos=1)
    time_stamps_start_dirty = True
    view_time_stamp_start = t
  
def FinishSensorTriggered():
    global time_stamps_finish_dirty
    global serial_time_stamp_finish
    global view_time_stamp_finish

    if serial_time_stamp_finish == 0:
        t = time.time()
    else:
        t = serial_time_stamp_finish
        serial_time_stamp_finish = 0

    t2 = t - program_launch_time_stamp
    print(("adding finish timestamp: {:.2f} ".format(t2)))
    time_stamps_finish.insert(0, t)
    while( len(time_stamps_finish) > KEEP_NUM_TIME_STAMPS):
        time_stamps_finish.pop()
    
    time_stamps_finish_all.insert(0, t)
    while( len(time_stamps_finish_all) > NUMBER_OF_EVENT):
        time_stamps_finish_all.pop()
#TODO    finish_sheet.add_entry([time.strftime('%H:%M:%S', time.localtime(t)), t2])
    if config.getboolean('mqtt', 'enabled'):
        mqtt_client.publish("elzwelle/stopwatch/finish", 
                            payload=time.strftime('%H:%M:%S', time.localtime(t)) 
                            + " {:.2f} 0".format(t2).replace(".",","), 
                            qos=1)
    view_time_stamp_finish = t
    time_stamps_finish_dirty = True

#-------------------------------------------------------------------
# This is the webserver.
#-------------------------------------------------------------------
class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if self.path == "/start":
            # web page for start time stamps
            # Zusatz von Joerg mit autom. Aktualisierung vom 18.03.2017 funktioniert
            # aber beim Aktualisieren wird Markierung fuer copy/paste geloescht!!
            # Deshalb wird nur alle 10 Sekunden aktualisiert
            self.wfile.write(bytes("<html><head><title>Start Zeitstempel</title><meta http-equiv=\"refresh\" content=\"10\" /></head>", "utf-8"))
            # s.wfile.write("<html><head><title>Start Zeitstempel</title></head>")
            self.wfile.write(bytes("<body><h1>Start Zeitstempel (aktualisiert {})</h1>".format(time.strftime("%H:%M:%S")), "utf-8"))
            for t in time_stamps_start:
                t2 = t - program_launch_time_stamp
                self.wfile.write(bytes("{:.2f}<br>".format(t2).replace(".",","), "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        elif self.path == "/ziel":
            # web page for finish time stamps
            # <meta http-equiv=\"refresh\" content=\"10\" />
            self.wfile.write(bytes("<html><head><title>Ziel Zeitstempel</title><meta http-equiv=\"refresh\" content=\"10\" /></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Ziel Zeitstempel (aktualisiert {})</h1>".format(time.strftime("%H:%M:%S")), "utf-8"))
            for t in time_stamps_finish:
                t2 = t - program_launch_time_stamp
                self.wfile.write(bytes("{:.2f}<br>".format(t2).replace(".",","), "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

            # 10.02.2018 HM start_all und ziel_all eingefuegt
        elif self.path == "/start_all":
            # web page for ALL start time stamps
            # <meta http-equiv=\"refresh\" content=\"10\" />
            self.wfile.write(bytes("<html><head><title>Alle Start Zeitstempel</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Alle Start Zeitstempel (aktualisiert {})</h1>".format(time.strftime("%H:%M:%S")), "utf-8"))
            for t in time_stamps_start_all:
                t2 = t - program_launch_time_stamp
                self.wfile.write(bytes("{:.2f}<br>".format(t2).replace(".",","), "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

        elif self.path == "/ziel_all":
            # web page for ALL finish time stamps
            # <meta http-equiv=\"refresh\" content=\"10\" />
            self.wfile.write(bytes("<html><head><title>Alle Ziel Zeitstempel</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Alle Ziel Zeitstempel (aktualisiert {})</h1>".format(time.strftime("%H:%M:%S")), "utf-8"))
            for t in time_stamps_finish_all:
                t2 = t - program_launch_time_stamp
                self.wfile.write(bytes("{:.2f}<br>".format(t2).replace(".",","), "utf-8"))
            self.wfile.writ(bytes("</body></html>", "utf-8"))

        else:
            # standard webpage for everything else
            self.wfile.write(bytes("<html><head><title>Elzslalom</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Elzslalom</h1>", "utf-8"))
            self.wfile.write(bytes("<ul><li><a href='/start'>Zeitstempel Start</a></li>", "Utf-8"))
            self.wfile.write(bytes("<li><a href='/ziel'>Zeitstempel Ziel</a></li></ul>", "utf-8"))
            #10.02.2018 HM  start_all und ziel_all eingefuegt
            self.wfile.write(bytes("<li><a href='/start_all'>Zeitstempel Start alle</a></li>", "utf-8"))
            self.wfile.write(bytes("<li><a href='/ziel_all'>Zeitstempel Ziel alle</a></li></ul>", "utf-8"))

            self.wfile.write(bytes("</body></html>", "utf-8"))

#-------------------------------------------------------------------
# Define the GUI
#---------------------

import ttkbootstrap as ttk
import tkinter as tk

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
        StartSensorTriggered()
        #self.start_table.insert_row('end', [self.start_id,"00:00:00", 0])
        self.start_id = self.start_id + 1
        self.scroll_to_last(self.start_table)
        self.finish_table.load_table_data()

    def finish_button_clicked(self):
        FinishSensorTriggered()
        #self.finish_table.insert_row('end', [self.finish_id,"00:00:00", 0])
        self.finish_id = self.finish_id + 1
        self.scroll_to_last(self.finish_table)
        self.finish_table.load_table_data()
       
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
 
    def Refresh(self):
        global time_stamps_start_dirty 
        global time_stamps_finish_dirty
        global update_time_stamp
        global serial_time_stamp
        global view_time_stamp_start
        global view_time_stamp_finish
        
        if update_time_stamp or not config.getboolean('serial', 'enabled'):
            if serial_time_stamp == 0:
                t = time.time()
            else:
                t = serial_time_stamp
                
            self.labelVariable.set("{}    |    {}    |    ".format(HOST_NAME, time.strftime("%H:%M:%S"))+
                                   "{:.2f}".format(t-program_launch_time_stamp).replace(".",","))
            update_time_stamp = False
        
        if time_stamps_start_dirty:
            self.start_table.insert_row('end', [self.start_id,
                                                "{}".format(time.strftime("%H:%M:%S")),
                                                "{:.2f}".format(view_time_stamp_start-program_launch_time_stamp).replace(".",",")
                                                ])
            self.start_id = self.start_id + 1
            self.scroll_to_last(self.start_table)
            self.finish_table.load_table_data()
            time_stamps_start_dirty = False

        if time_stamps_finish_dirty:
            self.finish_table.insert_row('end', [self.finish_id,
                                                 "{}".format(time.strftime("%H:%M:%S")),
                                                 "{:.2f}".format(view_time_stamp_finish-program_launch_time_stamp).replace(".",",")
                                                 ])
            self.finish_id = self.finish_id + 1
            self.scroll_to_last(self.finish_table)
            self.finish_table.load_table_data()
            time_stamps_finish_dirty = False
            
        gc.collect()
        self.after(500, self.Refresh)
        
# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )

        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)
        
    # subscribe to all topics of encyclopedia by using the wildcard "#"
    client.subscribe("elzwelle/stopwatch/#", qos=1)
    
    # a single publish, this can also be done in loops, etc.
    client.publish("elzwelle/monitor", payload="running", qos=1)
    

FIRST_RECONNECT_DELAY   = 1
RECONNECT_RATE          = 2
MAX_RECONNECT_COUNT     = 12
MAX_RECONNECT_DELAY     = 60

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        print("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            print("Reconnected successfully!")
            return
        except Exception as err:
            print("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    print("Reconnect failed after %s attempts. Exiting...", reconnect_count)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )

        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Publish: mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing

        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )

        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    
#---------------------- End MQTT Callbacks ---------------------------------

#-------------------------------------------------------------------
# Main program
#-------------------------------------------------------------------
if __name__ == '__main__':    
    GPIO = None
   
    #gc.set_debug(gc.DEBUG_LEAK)
   
    myPlatform = platform.system()
    print("OS in my system : ", myPlatform)
    myArch = platform.machine()
    print("ARCH in my system : ", myArch)

    config = configparser.ConfigParser()
    # Defaults Linux Raspberry Pi
    config['serial'] = {'enabled':'no',
                        'port':'/dev/ttyUSB1',
                        'baud':'57600',
                        'timeout':'10'}
    
    config['http']   = {'port':PORT_NUMBER,
                        'enabled':'true'}
    
    config['google'] = {'spreadsheet_id':SPREADSHEET_ID}
    
    config['gpio']   = {'enabled':'no',
                        'start_gpio_pin':START_GPIO_PIN,
                        'finish_gpio_pin':FINISH_GPIO_PIN,
                        'bouncetime':300
                        }
    
    config['mqtt']   = {'enabled':'no'}
    
    # Platform specific
    if myPlatform == 'Windows':
        # Platform defaults
        config['serial']['port'] = 'COM4'
        config.read('windows.ini') 
    if myPlatform == 'Linux':
        config.read('linux.ini')

    try:
        googlesheet.client_secret_file = config.get('google', 'client_secret_json')
        if googlesheet.client_secret_file.startswith(".elzwelle"):
            home_dir = Path.home()
            print( f'Path: { home_dir } !' )
            googlesheet.client_secret_file = os.path.join(home_dir,googlesheet.client_secret_file)
        print("Setup GOOGLE: ",googlesheet.client_secret_file)
    except:
        print("Setup GOOGLE with defaults ")
    
    start_sheet  = googlesheet.Spreadsheet(spreadsheet_id=config.get('google', 'spreadsheet_id'), tab_name='Start')
    finish_sheet = googlesheet.Spreadsheet(spreadsheet_id=config.get('google', 'spreadsheet_id'), tab_name='Ziel')
            
    if config.getboolean('http', 'enabled'):
        # setup and start webserver in separate thread
        server_class = http.server.HTTPServer
        httpd = server_class((HOST_NAME, config.getint('http', 'port')), MyHandler)
        print(time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, config.getint('http', 'port')))
        try:
            thread = threading.Thread(target=httpd.serve_forever)
            thread.start()
            print(time.asctime(), "Server is running")
        except KeyboardInterrupt:
            pass
        #print("It works! Version für Py3.7  Elz_2021_12_a.py  neu")
    #----------------------------End HTTP -----------------------------------------------
    
    if config.getboolean('serial', 'enabled'):
        
        # Initialize the port    
        serialPort = serial.Serial(config.get('serial', 'port'),
                               config.getint('serial', 'baud'), 
                               timeout=config.getint('serial', 'timeout'))
            
        # Function to call whenever there is data to be read
        def readFunc(port):
            global update_time_stamp
            global serial_time_stamp
            global serial_time_stamp_start
            global serial_time_stamp_finish
            global program_launch_time_stamp
             
            time.sleep(2)   
            print('Read RTC')
            port.write(str.encode('r'))  
            time.sleep(0.5)
            
            unix_epoch = int(program_launch_time_stamp) 
            print('Set Epoch: {0:d}'.format(unix_epoch))
            port.write(str.encode('e{0:d}'.format(unix_epoch)))      
                      
            while True:
                try:
                    line = port.readline().decode("utf-8")
                    #print('Line: '+line[0:-1])
                    if len(line) > 0:
                        if line[0] == '#':
                            try:
                                serial_time_stamp = float(line[1:-1])
                                print('Time\t{0:.2f} -- {1:.2f}'.format(serial_time_stamp,time.time()))
                                update_time_stamp = True
                            except ValueError:
                                print("EXCEPTION serial_time_stamp:  Not a float")
                        if line[0] == 'S':
                            try:
                                serial_time_stamp_start = float(line[1:-1])
                                print('Start\t{0:.2f}'.format(serial_time_stamp_start))
                                StartSensorTriggered()
                            except ValueError:
                                print("EXCEPTION serial_time_stamp_start:  Not a float")
                        if line[0] == 'F':
                            try:
                                serial_time_stamp_finish = float(line[1:-1])
                                print('Finish\t{0:.2f}'.format(serial_time_stamp_finish))
                                FinishSensorTriggered()
                            except ValueError:
                                print("EXCEPTION serial_time_stamp_finish:  Not a float")      
                except Exception as e:
                    print("EXCEPTION in readline: ",e) 
            
            print("DONE readline")
                           
        # Configure threading
        usbReader = threading.Thread(target = readFunc, args=[serialPort])
        usbReader.start()
    #-------------------------------End GPIO --------------------------------------------
    
    if config.getboolean('mqtt', 'enabled'):
        mqtt_client = paho.Client(client_id="elzwelle_"+str(uuid.uuid4()), userdata=None, protocol=paho.MQTTv311)
    
        # enable TLS for secure connection
        if config.getboolean('mqtt','tls_enabled'):
            mqtt_client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        if config.getboolean('mqtt','auth_enabled'):
            mqtt_client.username_pw_set(config.get('mqtt','user'),
                                    config.get('mqtt','password'))
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        mqtt_client.connect(config.get('mqtt','url'), config.getint('mqtt','port'))
       
        # setting callbacks, use separate functions like above for better visibility
        mqtt_client.on_connect      = on_connect
        mqtt_client.on_subscribe    = on_subscribe
        mqtt_client.on_message      = on_message
        mqtt_client.on_publish      = on_publish
        
        mqtt_client.loop_start()
        
        # subscribe to all topics of encyclopedia by using the wildcard "#"
        mqtt_client.subscribe("elzwelle/timestamp/#", qos=1)
        
        # a single publish, this can also be done in loops, etc.
        mqtt_client.publish("elzwelle/stoppwatch", payload="running", qos=1)
        #mqtt_client.loop_start()
    #-------------------------------- End MQTT -------------------------------------------
    
#    tracemalloc.start() 
       
if __name__ == "__main__":
    app = SimpleApp()
    app.Refresh()
    app.mainloop()

    if config.getboolean('http', 'enabled'):
        httpd.server_close()
        print(time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, config.getint('http', 'port')))
        
    # Stop all dangling threads
    os.abort()