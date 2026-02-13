import queue
import asyncio
import threading
import platform
import configparser
import os
import googlesheet
import time
import elzwelle_global as glob

from collections import deque
from pathlib import Path
from serial_provider import SerialProvider
from web_provider import WebProvider
from mqtt_provider import MQTTProvider
from gui_app import MainApp
from data_manager import DataManager

from elzwelle_config import PORT_NUMBER, SPREADSHEET_ID 

# Zentrale Ressourcen
web_data = deque(maxlen=200)
gui_queue = queue.Queue()

if __name__ == "__main__":
    #global program_launch_time_stamp
    
    manager = DataManager(gui_queue, web_data)

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
    
    # config['gpio']   = {'enabled':'no',
    #                     'start_gpio_pin':START_GPIO_PIN,
    #                     'finish_gpio_pin':FINISH_GPIO_PIN,
    #                     'bouncetime':300
    #                     }
    
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
    
    glob.start_sheet  = googlesheet.Spreadsheet(spreadsheet_id=config.get('google', 'spreadsheet_id'), tab_name='Start')
    glob.finish_sheet = googlesheet.Spreadsheet(spreadsheet_id=config.get('google', 'spreadsheet_id'), tab_name='Ziel')
    
    if config.getboolean('serial', 'enabled'):
        # Start Serial
        ser_proc = SerialProvider(port=config.get('serial', 'port'),
                                  baudrate=config.getint('serial', 'baud'),
                                  callback=manager.dispatch)
        ser_proc.start()

    if config.getboolean('mqtt', 'enabled'):

        # userdata=None
        # protocol=paho.MQTTv311
        #
        # # enable TLS for secure connection
        # if config.getboolean('mqtt','tls_enabled'):
        #     tls_version=mqtt.client.ssl.PROTOCOL_TLS
        # # set username and password
        # if config.getboolean('mqtt','auth_enabled'):
        #     username = config.get('mqtt','user'),
        #     password = config.get('mqtt','password')
            
        mqtt_broker  = config.get('mqtt','url')
        mqtt_port    = config.getint('mqtt','port')
        
        # Start MQTT in einem Helper-Thread für Asyncio
        def run_mqtt():
            mqtt_prov = MQTTProvider(broker   = mqtt_broker,
                                     topic    = "elzwelle",
                                     port     = mqtt_port,
                                     callback = manager.dispatch)
            # Wichtig: Dem Manager die MQTT-Instanz bekannt machen
            manager.set_mqtt_provider(mqtt_prov)
            asyncio.run(mqtt_prov.start())
        
        threading.Thread(target=run_mqtt, daemon=True).start()
    
    if config.getboolean('http', 'enabled'):
        # Webserver initialisieren und starten
        web_server = WebProvider(web_data, port=8888, manager=manager)
        web_server.start_thread()

    # Start GUI (Hauptthread)
    glob.program_launch_time_stamp = float(int(time.time()))
    app = MainApp(gui_queue, manager)
    app.mainloop()
