
# Tutorial — Scripts de Simulación de Estación Meteorológica  
## Streaming + Batch (Azure Event Hubs + ADLS)

Este documento explica paso a paso cómo crear **dos scripts Python** que simulan una estación meteorológica:

1. **Streaming** → Envía datos en tiempo real a **Azure Event Hubs**.  
2. **Batch** → Genera un CSV cada hora y lo sube a **ADLS Gen2**.

---

# 1. Script STREAMING (Real-Time hacia Event Hubs)

## 1.1. Instalación de dependencias

```bash
pip install azure-eventhub azure-identity
```

---

## 1.2. Crear archivo `streaming_producer.py`

```python
import json
import time
import random
from datetime import datetime, timezone
from azure.eventhub import EventHubProducerClient, EventData

# ------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------
EVENT_HUB_CONNECTION_STR = "<CONNECTION_STRING_SEND_POLICY>"
EVENT_HUB_NAME = "eh-weather"

# Intervalo entre envíos (segundos)
INTERVALO = 5

# IP simulada del sensor
SENSOR_IP = "192.168.1.50"


# ------------------------------------------------------
# FUNCIÓN PARA GENERAR UNA LECTURA
# ------------------------------------------------------
def generar_lectura():
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": SENSOR_IP,
        "temperature": round(random.uniform(10, 30), 2),
        "humidity": round(random.uniform(30, 90), 2),
        "pm25": round(random.uniform(1, 80), 2),
        "light": random.randint(100, 800),
        "uv_level": random.randint(0, 10),
        "pressure": round(random.uniform(980, 1030), 2),
        "rain_raw": random.randint(0, 1000),
        "wind_raw": round(random.uniform(0, 20), 2),  # decimal
        "vibration": random.randint(0, 3),
    }


# ------------------------------------------------------
# ENVIAR A EVENT HUBS
# ------------------------------------------------------
def main():
    print("Iniciando estación meteo en streaming...")

    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR, 
        eventhub_name=EVENT_HUB_NAME
    )

    while True:
        lectura = generar_lectura()
        payload = json.dumps(lectura)

        event_data = EventData(payload)
        producer.send_batch([event_data])

        print(f"Enviado: {payload}")
        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
```

---

## 1.3. Ejecutar el script

```bash
python streaming_producer.py
```

---

# 2. Script BATCH (Generar CSV por hora y subir a ADLS)

## 2.1. Instalación de dependencias

```bash
pip install pandas azure-storage-blob
```

---

## 2.2. Crear archivo `batch_generator.py`

```python
import pandas as pd
import random
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient
import io

# ------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------
STORAGE_ACCOUNT_NAME = "stmeteoend2end"
CONTAINER_NAME = "datalake"
FOLDER = "landing/weather_batch"

STORAGE_KEY = "<TU_STORAGE_KEY>"

NUM_REGISTROS = 60
SENSOR_IP = "192.168.1.50"


# ------------------------------------------------------
# GENERAR LECTURAS PARA UNA HORA COMPLETA
# ------------------------------------------------------
def generar_batch():
    ahora = datetime.now(timezone.utc)
    inicio = ahora - timedelta(hours=1)

    timestamps = [inicio + timedelta(minutes=i) for i in range(NUM_REGISTROS)]

    data = {
        "timestamp": [t.isoformat() for t in timestamps],
        "ip": [SENSOR_IP] * NUM_REGISTROS,
        "temperature": [round(random.uniform(10, 30), 2) for _ in range(NUM_REGISTROS)],
        "humidity": [round(random.uniform(30, 90), 2) for _ in range(NUM_REGISTROS)],
        "pm25": [round(random.uniform(1, 80), 2) for _ in range(NUM_REGISTROS)],
        "light": [random.randint(100, 800) for _ in range(NUM_REGISTROS)],
        "uv_level": [random.randint(0, 10) for _ in range(NUM_REGISTROS)],
        "pressure": [round(random.uniform(980, 1030), 2) for _ in range(NUM_REGISTROS)],
        "rain_raw": [random.randint(0, 1000) for _ in range(NUM_REGISTROS)],
        "wind_raw": [round(random.uniform(0, 20), 2) for _ in range(NUM_REGISTROS)],
        "vibration": [random.randint(0, 3) for _ in range(NUM_REGISTROS)],
    }

    df = pd.DataFrame(data)
    return df


# ------------------------------------------------------
# SUBIDA A ADLS GEN2
# ------------------------------------------------------
def subir_a_adls(df):
    ahora = datetime.now(timezone.utc)
    nombre = ahora.strftime("weather_%Y%m%d_%H.csv")

    url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
    blob_service = BlobServiceClient(
        account_url=url,
        credential=STORAGE_KEY
    )

    blob_path = f"{FOLDER}/{nombre}"
    blob_client = blob_service.get_blob_client(
        container=CONTAINER_NAME, blob=blob_path
    )

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    blob_client.upload_blob(buffer.getvalue(), overwrite=True)

    print(f"Subido a ADLS: {blob_path}")


# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
def main():
    print("Generando datos batch...")
    df = generar_batch()
    subir_a_adls(df)


if __name__ == "__main__":
    main()
```

---

## 2.3. Ejecutar el script

```bash
python batch_generator.py
```

Subirá un archivo como:

```
landing/weather_batch/weather_20250115_22.csv
```

---

# 3. Programar ejecución automática

## Linux (cron)

```bash
crontab -e
```

Añadir:

```
0 * * * * /usr/bin/python3 /ruta/batch_generator.py
```

---

## Windows (Task Scheduler)
1. Abrir *Programador de tareas*  
2. Crear *Basic Task*  
3. Trigger → Daily → Repeat every 1 hour  
4. Action → Start a program:  
   - Program: `python`  
   - Arguments: ruta completa a `batch_generator.py`

---

# 4. Resumen

| Script | Tipo | Objetivo | Destino |
|--------|------|----------|---------|
| `streaming_producer.py` | Streaming | Enviar lecturas cada pocos segundos | Event Hubs |
| `batch_generator.py` | Batch | Crear CSV por hora | ADLS Landing |

---

