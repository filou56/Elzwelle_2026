import serial
import threading
import time

class SerialProvider(threading.Thread):
    def __init__(self, port, baudrate, callback):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.callback = callback  # Funktion, die bei Daten aufgerufen wird
        self.running = True

    def run(self):
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                    while self.running:
                        line = ser.readline().decode('utf-8').strip()
                        print(line)
                        if line:
                            if line[0] == '#':
                                self.callback("Stamp", line[1:-1])
                            if line[0] == 'S':
                                self.callback("Start", line[1:-1])
                            if line[0] == 'F':
                                self.callback("Finish", line[1:-1])    
            except (serial.SerialException, OSError):
                print("Serial Port verloren... Reconnect in 5s")
                time.sleep(5)