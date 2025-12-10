import json
import time
import random
from datetime import datetime, timezone
from azure.eventhub import EventHubProducerClient, EventData

# ------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------
EVENT_HUB_CONNECTION_STR = "TU_CONNECTION_STRING"
EVENT_HUB_NAME = "eh-weather"

# Intervalo entre envíos (segundos)
INTERVALO = 120

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
        "wind_raw": round(random.uniform(0, 20), 2),
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