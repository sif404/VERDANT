# VERDANT live cloud bridge

The public GitHub Pages site defaults to the verified Azure archive. Scientific Simulation is a separate NASA POWER replay. Live Cloud uses a same-origin local read-only API; no credentials are embedded in the website. It will not connect from GitHub Pages itself.

1. In verdant-iothub-s1 > Message routing, add an enabled Device Telemetry Messages route to the built-in endpoint (messages/events), query `true`. Preserve the existing three storage routes.
2. In Built-in endpoints, obtain an Event Hubs-compatible connection string using a service-connect policy. Keep it private. Prefer a dedicated consumer group and set VERDANT_CONSUMER_GROUP accordingly; stop other consumers using the same group.
3. Clone/download this repository and run from its root:
   `python -m pip install -r bridge/requirements.txt`
   `python bridge/server.py`
4. Enter the connection string locally when prompted. Open http://127.0.0.1:8765 and select Live Cloud. Start the existing three cloud_sensor.py publishers, using the S1 hub and their own device keys.
5. Confirm each sensor has received records with new Azure enqueue times. Stop publishers and bridge after the demonstration.

The bridge binds to loopback only. It retains at most 120 messages per device in memory, validates source identity and measurement type, and exposes no secrets. Archive and live data are never automatically mixed. The bridge has not been tested against the user's active Azure account. Azure trial expiry and charges still apply. Public remote live access requires separate authenticated HTTPS hosting.
