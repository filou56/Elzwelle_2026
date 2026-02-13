import time
import threading
import elzwelle_global as glob

class DataManager:
    def __init__(self,gui_queue,web_data):
        self.mqtt_prov = None  # Wird später gesetzt
        self.gui_queue = gui_queue
        self.web_data  = web_data
        # self.sheet_manager = GoogleSheetsManager()
        
        self.sync_time_stamp = "00:00:00"
        # Das Schloss (Lock) für den sicheren Zugriff
        self._value_lock = threading.Lock()

    def update_sync_time_stamp(self, new_val):
        """Wird von MQTT oder Serial aufgerufen"""
        with self._value_lock:
            self.sync_time_stamp = new_val

    def get_sync_time_stamp(self):
        """Wird von der GUI oder dem Webserver aufgerufen"""
        with self._value_lock:
            return self.sync_time_stamp

    def set_mqtt_provider(self, mqtt_instance):
        self.mqtt_prov = mqtt_instance

    def dispatch(self, source, data):
        t = time.strftime('%H:%M:%S', time.localtime(time.time()))
        
        # print("Dispatcher put",source,data)
        
        # # 1. In die Deque für den Webserver
        if source == "Start" or source == "Finish" :
            payload = {"src": source, "val": data, "time": t}
            self.web_data.append(payload)
        
        # 2. In die Queue für die GUI 
        self.gui_queue.put((source, data))
        
        # # 3. Serial -> MQTT (jetzt ist mqtt_prov bekannt!)
        if source == "Start" :
            self.mqtt_prov.publish_sync("stopwatch/start", t+" "+data.replace(".",","))
        
        if source == "Finish" :
            self.mqtt_prov.publish_sync("stopwatch/finish", t+" "+data.replace(".",","))
        
        if glob.start_sheet != None:
            if source == "Start" :
                glob.start_sheet.add_entry([t, data.replace(".",",")])
                
        if glob.finish_sheet != None:      
            if source == "Finish" :
                glob.finish_sheet.add_entry([t, data.replace(".",",")])
                
            
# filou@sambesi:~$ mosquitto_sub -v -t +/#
# elzwelle/stopwatch/start 16:10:24 22,56 0
# elzwelle/stopwatch/finish 16:10:27 25,56 0
