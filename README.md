# VERDANT — Stadium Microclimate Observatory
Standalone website for the IoT & Cloud Integration project at Jordan University of Science and Technology. Conceptually inspired by [DT-simulator](https://github.com/sif404/DT-simulator); independent implementation with no external libraries or runtime cloud credentials.

Open `index.html` locally or upload the files to a new GitHub repository (e.g. `VERDANT`), then enable GitHub Pages: Settings → Pages → Deploy from a branch → main / root → Save.

## Data and boundaries
- NASA POWER hourly archive, 31.91°N, 36.37°E, UTC, 2020–2024: selected days 2022-04-16 and 2023-08-13. T2M, RH2M and ALLSKY_SFC_SW_DWN. Source: https://power.larc.nasa.gov/
- Illuminance estimate = irradiance × 109 lm/W × (1 − shade fraction); illustrative shade, not a spatial shading calculation.
- 48 archived records from the actual Azure storage test, sanitized to remove unnecessary metadata. 7 temperature, 20 humidity, 21 light. Not a complete message delivery audit.
- Replay, stadium geometry, and Twin buttons are offline demonstrations; no live Azure or MQTT connection, and no new cloud commands are sent. The real deployment used DPS, Azure IoT Hub S1, MQTT/TLS, and three storage endpoints.
- Local file import validates records against the selected expected container. File contents stay in the browser. Exports include only allowlisted fields.
- Research foundation: https://www.researchgate.net/publication/405299911

Author: Saif Mutlq. No student ID or private keys are published in this public web edition.
