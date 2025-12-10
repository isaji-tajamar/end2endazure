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
FOLDER = "bronze/batch/weather"

STORAGE_KEY = "TU_KEY"

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