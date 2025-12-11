# Proyecto End-to-End Meteo en Azure

Este repositorio contiene todos los recursos utilizados para el desarrollo del proyecto **Meteo End-to-End en Azure**, un flujo completo de ingesta, procesamiento y consumo de datos meteorológicos tanto en *streaming* como en *batch*, siguiendo la arquitectura **medallion** (Bronze → Silver → Gold).

> [!IMPORTANT] 
> # Para seguir el tutorial hay que leerse el siguiente archivo: [Tutorial end2end](./docs/tutorial_end2end_meteo.md)

## 📁 Estructura del repositorio

### `docs/`

Contiene la documentación del proyecto, incluyendo:

* Descripción funcional y técnica.
* Arquitectura del sistema.
* Diseño del Lakehouse.
* Explicación de los servicios de Azure utilizados.
* Procesos de ingesta, transformación y publicación.

---

### `notebooks_databricks/`

Incluye los **notebooks de Azure Databricks** utilizados para:

* Procesamiento Bronze → Silver.
* Limpieza, normalización y validación de datos.
* Generación de tablas Gold para análisis.

Cada notebook está preparado para ejecutarse directamente en un clúster de Databricks.

---

### `scripts/`

Scripts auxiliares del proyecto, tales como:

* Generación de datos meteorológicos sintéticos.
* Simulación de envío de datos en *streaming* a Event Hubs.

---

## 🚀 Objetivo del proyecto

Crear una pipeline completa de datos meteorológicos usando servicios cloud de Azure, almacenando datos históricos en un Lakehouse y permitiendo su visualización en tiempo real mediante Power BI.

## 🛠️ Servicios principales utilizados

* **Azure Event Hubs** – Ingesta en *streaming*.
* **Azure Data Lake Storage Gen2** – Lakehouse estructurado por niveles.
* **Azure Databricks** – Procesamiento ETL.
* **Power BI** – Dashboards conectados al *tier Gold*.
