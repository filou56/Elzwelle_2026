import asyncio
import uuid

from aiomqtt import Client
#from gnuradio.grc.core.ports import port

class MQTTProvider:
    def __init__(self, broker = 'localhost', topic = "+/#", callback = None, port = 1883):
        self.broker     = broker
        self.topic      = topic
        self.callback   = callback
        self.port       = port
        self.id         = "elzwelle_"+str(uuid.uuid4())
        
    async def start(self):   
        self.loop = asyncio.get_running_loop()   
        while True:
            try:
                async with Client(self.broker, port = self.port, identifier = self.id) as client:
                    self.client = client # Client-Referenz speichern
                    await client.subscribe(self.topic+"/#")
                    async for message in client.messages:
                        data = message.payload.decode()
                        self.callback("MQTT", data)
            except Exception as e:
                print(f"MQTT Fehler: {e}. Reconnect in 5s")
                await asyncio.sleep(5)
                
    def publish_sync(self, sub_topic, payload):
        """Erlaubt das Senden aus anderen Threads (wie Serial)"""
        if self.loop and self.client:
            full_topic = f"{self.topic}/{sub_topic}"
            # Plant das Publish im asynchronen Loop ein
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self.client.publish(full_topic, payload))
            )