"""Local read-only Azure IoT Hub bridge; never publish credentials."""
import os, json, math, threading
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from getpass import getpass
from azure.eventhub import EventHubConsumerClient, TransportType

ROOT = Path(__file__).resolve().parent.parent
SENSORS = {"Sensor01": ("temperature", "temperatureC"), "Sensor02": ("humidity", "humidity"), "Sensor03": ("light", "lightLux")}
records = {k: deque(maxlen=120) for k in SENSORS}
lock = threading.Lock()
status = "waiting"

def on_event(context, event):
    global status
    if event is None:
        return
    try:
        body = event.body_as_json()
        device = body["deviceId"]
        kind, field = SENSORS[device]
        props = event.system_properties or {}
        app = event.properties or {}
        def prop(mapping, key):
            value = mapping.get(key, mapping.get(key.encode()))
            return value.decode() if isinstance(value, bytes) else value
        if prop(props, "iothub-connection-device-id") != device:
            return
        if body["measurementType"] != kind or prop(app, "measurementType") != kind:
            return
        value = body[field]
        if type(value) not in (int, float) or not math.isfinite(value):
            return
        if kind == "humidity" and not 0 <= value <= 100 or kind == "light" and value < 0:
            return
        stamp = body["timestamp"]
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return
        item = dict(deviceId=device, measurementType=kind, value=value,
                    timestamp=parsed.astimezone(timezone.utc).isoformat(),
                    enqueuedUtc=event.enqueued_time.astimezone(timezone.utc).isoformat())
        with lock:
            records[device].append(item)
            status = "receiving"
        print(device, value, item["enqueuedUtc"], flush=True)
    except (KeyError, ValueError, TypeError, AttributeError, UnicodeError):
        return

def on_error(context, error):
    global status
    with lock:
        status = "disconnected"
    print("Azure receiver error:", type(error).__name__, flush=True)

def receive(secret):
    global status
    try:
        client = EventHubConsumerClient.from_connection_string(
            secret, consumer_group=os.getenv("VERDANT_CONSUMER_GROUP", "$Default"),
            transport_type=TransportType.AmqpOverWebsocket)
        with client:
            client.receive(on_event=on_event, on_error=on_error, starting_position="@latest")
    except Exception as error:
        on_error(None, error)
    finally:
        with lock:
            status = "disconnected"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def do_GET(self):
        if self.path == "/api/telemetry":
            with lock:
                payload = json.dumps({"status": status, "records": [x for q in records.values() for x in q]}, allow_nan=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif self.path in ("/", "/index.html"):
            super().do_GET()
        else:
            self.send_error(404)

if __name__ == "__main__":
    secret = os.getenv("VERDANT_EVENTHUB_CONNECTION") or getpass("Event Hubs-compatible connection string (hidden): ")
    if not secret.startswith("Endpoint=sb://"):
        raise SystemExit("Use the Event Hubs-compatible connection string, not a device key.")
    threading.Thread(target=receive, args=(secret,), daemon=True).start()
    print("Open http://127.0.0.1:8765 and choose Live Cloud.", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
