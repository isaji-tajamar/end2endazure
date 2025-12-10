# Presentación del Proyecto End-to-End Meteo en Azure

Este documento ofrece una explicación clara, estructurada y orientada a presentación sobre los **servicios utilizados**, la **arquitectura general** y el **flujo de datos** del proyecto Meteo End-to-End desplegado en Azure.

---

## 1. Servicios Utilizados en la Arquitectura

### 1.0 Simulación de la estación meteorológica
Se utilizan dos scripts de python para simular la estación meteorológica. En mi caso se ejecutan en local pero se podrían ejecutar en una máquina virtual en la nube.

Más información: [tutorial_scripts_meteo.md](./tutorial_scripts_meteo.md)

### 1.1 Azure Resource Group

Agrupa todos los recursos del proyecto para una gestión unificada, permitiendo control de costes, permisos y despliegues centralizados.

### 1.2 Azure Storage Account (ADLS Gen2)

Es el punto central de almacenamiento y funciona como **Lakehouse** del proyecto. Se utiliza con *Hierarchical Namespace* activado para soportar operaciones tipo Hadoop y Delta Lake.

Estructura de carpetas empleada:

```
/landing/weather_batch
/bronze/streaming/weather
/bronze/batch/weather
/silver/weather
/gold/weather_station_hourly
/gold/weather_station_daily
```

### 1.3 Azure Event Hubs

Servicio de ingesta en streaming. Recibe datos meteorológicos generados por un script en Python que simula una estación meteo.

Se crean:

* **Namespace** `ehns-meteo`
* **Event Hub** `eh-weather`
* Políticas SAS: `send-policy` y `listen-policy`

### 1.4 Azure Databricks

Servicio principal de procesamiento. Permite ejecutar notebooks de PySpark para implementar la arquitectura Medallion.

Utilizado para:

* Procesamiento streaming (Event Hubs → Bronze)
* Procesamiento batch (CSV → Bronze)
* Transformaciones Bronze → Silver
* Agregaciones Silver → Gold
* Orquestación mediante **Databricks Jobs**

### 1.5 Python Scripts Externos

Scrips desarrollados para simular una estación meteorológica en dos modos:

* **Streaming** (envío continuo de datos a Event Hubs)
* **Batch** (generación de ficheros CSV horarios)

---

## 2. Arquitectura General del Proyecto

El proyecto se basa en un enfoque **Lakehouse** con la metodología **Medallion Architecture** para estructurar el flujo de datos.

### 2.1 Capa Bronze

Almacena datos **sin procesar**, provenientes de dos fuentes:

* **Streaming** desde Event Hubs
* **Batch** desde los ficheros CSV generados

Los datos se guardan en formato **Delta Lake**, sin modificaciones.

### 2.2 Capa Silver

Realiza la **limpieza y estandarización** de los datos:

* Conversión de tipos
* Normalización de nombres
* Eliminación de duplicados
* Enriquecimiento: origen de los datos (batch/streaming)

El objetivo es obtener un dataset fiable y uniforme.

### 2.3 Capa Gold

Genera datos listos para análisis y consumo analítico:

* Cálculos **horarios** (medias, máximos, mínimos)
* Cálculos **diarios**
* Organización por particiones para acelerar consultas

Gold es la capa recomendada para Power BI u otros sistemas de análisis.

---

## 3. Flujo de Datos End-to-End

La siguiente secuencia representa el recorrido completo de los datos dentro del sistema.

### 3.1 Generación de Datos

* Un script de Python simula una estación meteorológica.
* En modo **streaming**, envía datos JSON a Event Hubs.
* En modo **batch**, genera un CSV cada hora.

### 3.2 Ingesta en Azure

**Streaming:** Event Hubs recibe los datos en tiempo real.

**Batch:** Los CSV se copian en la carpeta `bronze/batch/weather` de ADLS.

### 3.3 Procesos en Databricks — Arquitectura Medallion

#### 3.3.1 Bronze (ingesta)

* Un notebook escucha Event Hubs continuamente y escribe en Bronze.
* Otro notebook ingiere los CSV y los añade a Bronze Batch.

#### 3.3.2 Silver (transformación)

* Los notebooks limpian, convierten tipos, eliminan duplicados y etiquetan el origen.

#### 3.3.3 Gold (analítica)

* Agregaciones horarias y diarias
* Escritura en carpetas optimizadas para consulta

### 3.4 Automatización con Databricks Jobs

Los notebooks se ejecutan automáticamente mediante Jobs:

* **Streaming Job**: ejecución continua
* **Batch Job**: cada hora
* **Bronze → Silver**: cada 5 minutos
* **Silver → Gold**: cada 10 minutos

Esto garantiza que el flujo permanezca sincronizado y actualizado.

---

## 4. Resumen Final de la Arquitectura

El sistema completo combina una ingesta híbrida (streaming + batch), un Lakehouse basado en Delta Lake, y un procesamiento escalable mediante Databricks. La arquitectura garantiza:

* Flujo continuo y confiable de datos
* Limpieza y estandarización automatizada
* Datos optimizados para BI
* Extensibilidad hacia Power BI, Synapse o Fabric

La arquitectura queda preparada para integrar visualización a tiempo real en el futuro.
