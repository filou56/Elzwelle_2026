from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import uvicorn
import threading

import elzwelle_global as glob

class WebProvider:
    def __init__(self, data_buffer=None, manager=None, port=8080):
        self.app = FastAPI()
        self.data_buffer = data_buffer
        self.port        = port
        self.manager     = manager
        
        # Mountet den lokalen Ordner "static" unter dem URL-Pfad "/static"
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

        # Templates-Ordner für HTML-Dateien
        self.templates = Jinja2Templates(directory="templates")

        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            # Rendert die index.html mit den aktuellen Daten
            return self.templates.TemplateResponse("index.html", {
                "request": request, 
                "data": list(self.data_buffer),
                "theme_file": f"{glob.current_theme}.css"
            })

        @self.app.get("/api/data")
        async def get_json_data():        
            return {
                "now":  self.manager.get_sync_time_stamp(),
                "data": list(data_buffer) # Deine Deque
            }
        #   return list(self.data_buffer)

    def start_thread(self):
        threading.Thread(target=lambda: uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="error"), daemon=True).start()


# import uvicorn
# from fastapi import FastAPI
# import threading
#
# class WebProvider:
#     def __init__(self, data_buffer=None, port=8080):
#         self.app         = FastAPI()
#         self.data_buffer = data_buffer  # Das ist deine collections.deque
#         self.port        = port
#         # Route definieren
#         @self.app.get("/data")
#         async def get_data():
#             # Konvertiert deque zu einer Liste für JSON-Export
#             return list(self.data_buffer)
#
#         @self.app.get("/status")
#         async def status():
#             return {"status": "running", "items_in_buffer": len(self.data_buffer)}
#
#     def run(self):
#         # Startet den Server (Uvicorn)
#         uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="error")
#
#     def start_thread(self):
#         """Startet den Webserver in einem Hintergrund-Thread"""
#         threading.Thread(target=self.run, daemon=True).start()

