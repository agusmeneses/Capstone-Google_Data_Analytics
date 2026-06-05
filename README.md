# Documentación del Proyecto de Análisis: Impacto Climático y Focos de Calor en Corrientes

## Introducción y Móvil del Análisis

Durante el primer trimestre de 2022, la provincia de Corrientes atravesó una de las crisis ambientales, económicas y operativas más severas de su historia reciente. En un contexto marcado por una sequía extrema prolongada y la bajante histórica del río Paraná, los incendios forestales y rurales consumieron, hacia mediados de febrero de ese año, un total de 785.238 hectáreas. La magnitud de la catástrofe se evidenció en un ritmo de progresión del fuego que alcanzó las 30.000 hectáreas diarias, desbordando las capacidades logísticas tradicionales y requiriendo un despliegue sin precedentes de brigadistas, aeronaves y recursos nacionales y locales.

<p align="center">
  <img src="assets/images/mapa_incendios_corrientes.png" alt="Mapa de incendios de la provincia de Corrientes en el periodo 2021 - 2022" width="80%">
  <br>
  <em><a href="URL_DEL_ARTICULO_AQUI" target="_blank">Imagen de Corrientes: el mapa de los incendios - La Patriada Web - Mapa de incendios de la provincia de Corrientes en el periodo 2021 - 2022</a></em>
</p>

Este evento expuso la profunda vulnerabilidad de nuestro territorio ante la combinación de factores climáticos adversos y la falta de un seguimiento de los mismos. El impacto amenazó a la matriz productiva y a la biodiversidad, afectando severamente a la Reserva Provincial del Iberá —el segundo humedal más grande del mundo— y a especies autóctonas en peligro de extinción.

Este proyecto nace como una iniciativa para estructurar, limpiar y cruzar volúmenes masivos de datos históricos provenientes de satélites de la NASA y sensores terrestres del INTA. El móvil principal de este análisis es demostrar empíricamente las correlaciones entre los factores climáticos y la ignición territorial y proveer al gobierno de Corrientes de un dataset validado e íntegro que permita identificar patrones históricos.

---

## Fases del Proyecto

### 1. Fase de Definición (ASK)

* **Identificación de la tarea empresarial:** El objetivo principal radicó en analizar y cuantificar la relación histórica entre las variables meteorológicas (escasez de precipitaciones, temperaturas máximas) y la propagación de incendios forestales en la región norte de la Provincia de Corrientes durante la última década (2016-2026), con especial énfasis en las anomalías del período 2020-2022.
* **Determinación de los Interesados:** El análisis está diseñado para aportar valor a entidades gubernamentales, organismos de respuesta a emergencias, el sector agrónomo y organizaciones de conservación ambiental que requieran optimizar sus sistemas de alerta temprana.
* **Selección del Conjunto de Datos:** Se seleccionaron datos satelitales de anomalías térmicas provistos por la NASA (satélites VIIRS y MODIS) y registros meteorológicos históricos del Instituto Nacional de Tecnología Agropecuaria (INTA), específicamente de estaciones como las de "El Sombrerito", "Colonia Benítez", entre otras.
* **Establecimiento de Métricas Clave:** Las métricas seleccionadas para el seguimiento del objetivo fueron: Volumen de Precipitaciones Mensuales (mm), Temperatura Máxima Promedio Mensual (°C), Frecuencia de Focos de Calor (N°) e Intensidad Radiativa del Fuego (FRP).

### 2. Fase de Preparación (PREPARE)

* **Descarga y Almacenamiento Estructurado:** Los volúmenes de datos brutos (archivos CSV masivos de los sitios de la NASA y el INTA) fueron descargados de sus portales oficiales y alojados de manera segura en el entorno Cloud de Databricks.
* **Clasificación y Filtrado Geospacial:** Se aplicó un Bounding Box para aislar geográficamente los incidentes ocurridos exclusivamente en el norte de Corrientes, garantizando el aislamiento espacial del área de estudio.

<p align="center">
  <img src="assets/images/bbox_limites.png" alt="Imagen de Bbox - Límites geográficos" width="60%">
  <br>
  <em>Imagen de Bbox - De aquí surgieron los límites geográficos para especificar la zona de estudio</em>
</p>

* **Evaluación de la Credibilidad del Dato:** Se garantizó la calidad bajo el marco ROCCC. Se identificaron y documentaron sesgos físicos en la recolección, tales como la ceguera satelital por cobertura de nubes (Cumulonimbus) y la falla de sensores pluviométricos en tierra en meses específicos.

### 3. Fase de Procesamiento (PROCESS)

* **Elección de Herramientas Tecnológicas:** Se seleccionó el entorno de Databricks utilizando el lenguaje PySpark debido a la necesidad de procesar Big Data de forma distribuida, ejecutar limpieza en memoria y asegurar la reproducibilidad del código (Notebooks).
* **Auditoría y Detección de Errores:** Se detectaron anomalías críticas: tipos de datos inconsistentes (texto en columnas numéricas por ejemplo), valores nulos por fallas de sensores climáticos y "falsos ceros" temporales por la ausencia de filas en meses sin detecciones.
* **Transformación y Limpieza:**
  * **Filtro de Confianza:** Se aislaron exclusivamente los focos de calor sobre vegetación (type == 0) descartando reflejos solares y anomalías industriales mediante filtros de confianza satelital (confidence >= 70).
  * **Imputación por Proxy:** Se desarrolló un algoritmo de imputación condicional (coalesce) que detectó los días con sensores rotos en una estación y reemplazó automáticamente los vacíos con datos de otra estación de respaldo.
  * **Calendario Maestro:** Se generó un bloque temporal ininterrumpido (2016-2026) en PySpark para cruzar los datos mediante un LEFT JOIN, garantizando la existencia de todos los meses y transformando los vacíos satelitales en verdaderos numéricos de 0 focos.
  * **Documentación del Código:** El proceso de limpieza (ETL) fue documentado y segmentado en un notebook de Databricks garantizando la trazabilidad de los datos.

<p align="center">
  <img src="assets/images/databricks_catalogo.png" alt="Catálogo de datos en Databricks" width="80%">
  <br>
  <em>Imagen de Databricks: Leading Data and AI Platform for Enterprises - Donde se muestra el catálogo de datos de origen y el dataset final generado</em>
</p>

### 4. Fase de Análisis (ANALYZE)

* **Agregación y Consolidación de Datos:** Se aplicaron funciones de agregación espacial y temporal (GROUP BY Anio, Mes), reduciendo cientos de miles de registros crudos a una "Tabla Analítica Final" de alta densidad informativa y bajo peso computacional (una fila por mes exacto).
* **Organización y Formateo:** La tabla resultante fue estructurada bajo convenciones estándar de tipado (Enteros para conteos, Flotantes decimales para precipitaciones y temperatura), preparada para su ingesta en software de Inteligencia de Negocios.
* **Ejecución de Cálculos y Relleno de Vacíos:** Se realizaron operaciones de suma total (sum) para lluvias y FRP, y cálculos de promedios (avg) para temperaturas, forzando matemáticamente los campos vacíos (fillna) a 0 para mantener la integridad de los gráficos de series de tiempo.
* **Identificación Temprana de Tendencias y Hallazgos:** Durante la revisión tabular se identificaron relaciones complejas que enriquecen el análisis:
  * **Latencia del Suelo:** Se comprobó que meses de sequía severa no generan incendios inmediatos si están precedidos por meses de alta saturación hídrica.
  * **Agotamiento de Biomasa:** Se identificó una reducción significativa de focos de calor post-crisis 2022 a pesar de condiciones climáticas favorables para incendios, validando el impacto de la ausencia de combustible biológico.
