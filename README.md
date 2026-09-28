# Diarización de Hablantes

Proyecto en Python, actualmente con interfaz de consola y una interfaz web planificada, que recibe un archivo de audio —por ejemplo, una reunión, una clase o una entrevista— y analiza **quién habló, cuándo habló y cuánto tiempo participó cada persona**.

El proyecto busca trabajar también con **habla simultánea (overlapping speech)** y dejar preparada una arquitectura que, como extensión, permita realizar **separación de fuentes de audio** cuando sea necesario.

>  Proyecto desarrollado para el ramo **Acústica Computacional con Python 

---

## ¿Qué problema resuelve?

En una reunión o una clase puede ser difícil reconstruir posteriormente **quién intervino, durante cuánto tiempo y en qué momentos hubo participación simultánea**.

La propuesta utiliza **diarización de hablantes (speaker diarization)**, es decir, la identificación temporal de los distintos hablantes presentes en una grabación.

### Casos de uso

- **Reuniones de trabajo:** analizar la participación de cada integrante y apoyar la elaboración de minutas.
- **Salas de clases:** identificar los segmentos correspondientes al profesor o a distintos alumnos.
- **Entrevistas y podcasts:** separar temporalmente las intervenciones de entrevistadores y entrevistados.
- **Estudios de participación:** calcular segundos y porcentaje de tiempo hablado por cada participante.

---

## Objetivo

Diseñar e implementar una herramienta que, a partir de un audio con múltiples hablantes:

1. detecte los segmentos donde existe voz;
2. identifique y agrupe los segmentos pertenecientes a cada hablante;
3. detecte situaciones de habla simultánea;
4. calcule el tiempo de habla y el porcentaje de participación de cada hablante; y
5. presente los resultados mediante una interfaz web sencilla.

### Alcance importante

**Diarización y separación de fuentes no son exactamente lo mismo.**

- La **diarización** responde principalmente a *“¿quién habló y cuándo?”*.
- La **separación de fuentes** intenta recuperar señales de audio independientes cuando las voces están mezcladas.

El sistema actual agrupa voces con ERes2Net y scikit-learn. Si el objetivo futuro incluye generar audio independiente durante el solapamiento, será necesario incorporar separación de fuentes; esa función no está implementada.

---

## ¿Cómo funciona?

```text
Audio (.wav / .mp3)
        │
        ▼
┌─────────────────────────────┐
│ 1. Preprocesamiento / VAD   │
│ 2. Segmentación de voz      │
│ 3. Embeddings de hablante   │
│ 4. Clustering / etiquetado  │
│ 5. Detección de solapamiento│
└─────────────────────────────┘
        │
        ▼
Segmentos por hablante
        │
        ├──► Tiempo hablado
        ├──► % de participación
        └──► Línea de tiempo
```

Si se incorpora separación de fuentes:

```text
Segmentos con overlap
        │
        ▼
Speech Separation
(SepFormer / Asteroid u otro modelo)
        │
        ▼
Fuentes de audio estimadas
```

---

## Stack tecnológico

| Capa | Herramientas | Función |
|---|---|---|
| Diarización | `ERes2Net` (sherpa-onnx) + `scikit-learn` | Huellas vocales y agrupamiento de hablantes |
| Procesamiento | `librosa` | Carga, análisis y espectrogramas |
| VAD | `Silero-VAD` / `webrtcvad` | Detección de actividad de voz |
| Embeddings | `SpeechBrain` / `Resemblyzer` | Representación de características de voz |
| Clustering | `scikit-learn` | Agrupamiento de segmentos similares |
| Separación (extensión) | `SpeechBrain` / `Asteroid` | Separación de fuentes en habla mezclada |
| Backend | `FastAPI` | API para recibir audio y devolver resultados |
| Frontend | `React` o HTML/JS | Carga y visualización de resultados |
| Visualización | `Matplotlib` | Espectrogramas y línea de tiempo |

---

## 📈 Métricas / KPIs

- **DER (Diarization Error Rate):** métrica principal para evaluar la calidad de la diarización.
- **JER (Jaccard Error Rate):** métrica complementaria para evaluar la diarización.
- **Tiempo de habla por persona:** segundos y porcentaje del total.
- **Precisión del VAD:** calidad de la detección de voz frente a silencio/ruido.
- **Tiempo de procesamiento:** tiempo requerido para procesar una determinada duración de audio.
- **Si se implementa separación:** se podrán incorporar métricas específicas de separación, como SI-SNRi.

> La meta `DER < 15–20%` se plantea como hipótesis de trabajo y deberá validarse experimentalmente; no se asume como un resultado garantizado.

---

## Datasets de referencia

- **AMI Meeting Corpus:** reuniones reales con múltiples hablantes; especialmente relevante para este proyecto.
- **VoxCeleb:** útil para tareas relacionadas con reconocimiento/verificación de hablantes.
- **LibriSpeech:** audio de habla principalmente limpia.
- **CALLHOME:** conversaciones telefónicas, incluyendo situaciones con solapamiento.
- **WSJ0Mix / LibriMix:** especialmente útiles si se estudia la separación de fuentes de habla.

Los datasets permiten evaluar el sistema frente a una referencia conocida (*ground truth*) y, si corresponde, realizar experimentos de entrenamiento o fine-tuning.

---

## Proyectos open source relacionados

Las fuentes utilizadas en la implementación actual se explican en la sección
«Referencias y para qué se utilizaron», al final de este documento. Los pasos
principales usan WebRTC VAD, ERes2Net mediante sherpa-onnx, scikit-learn, NumPy y código propio. Resemblyzer queda disponible como alternativa.
Librosa y SoundFile se conservan para la lectura y preparación del audio.
No se necesita crear cuentas, configurar tokens ni contratar servicios.

---

## Roadmap

- [ ] Revisar y probar proyectos open source de diarización y separación.
- [ ] Seleccionar el modelo base de diarización.
- [ ] Probar el pipeline con audios de 2 o más hablantes.
- [ ] Implementar VAD y diarización.
- [ ] Calcular tiempo y porcentaje de habla por persona.
- [ ] Implementar detección y visualización de solapamiento.
- [ ] Evaluar con DER/JER y datasets de referencia.
- [ ] Desarrollar backend en Python.
- [ ] Desarrollar interfaz web.
- [ ] Evaluar si se incorpora separación de fuentes para generar audios individuales.
- [ ] Documentar resultados y preparar la presentación final.

---

## Flujo de uso esperado

1. El usuario entra a la aplicación.
2. Sube un archivo `.wav` o `.mp3`.
3. El sistema procesa el audio.
4. Se muestran los hablantes detectados y sus segmentos.
5. Se calcula el tiempo y porcentaje de participación.
6. Se visualiza una línea de tiempo con las intervenciones.
7. Si se implementa separación de fuentes, se podrán descargar las fuentes de audio estimadas.



## Implementación actual

Se ejecuta por consola con `python3 src/menu.py`. La interfaz web y la separación
de voces simultáneas siguen siendo objetivos futuros.

### Funcionamiento explicado por etapas

1. **Leer audio:** SoundFile/FFmpeg decodifican el archivo y Librosa lo prepara
   en mono a 16 kHz. Se conserva la línea de tiempo original.
2. **Encontrar voz:** WebRTC VAD analiza marcos de 30 ms, ahora con agresividad
   0. Se unen pausas de hasta 0.3 s para formar contextos; esas pausas **no** se
   suman a los tiempos de habla. Se descartan contextos aislados menores de 0.5 s.
3. **Extraer huellas vocales:** ERes2Net analiza contextos de hasta 3.2 s con
   avance de 0.8 s. La señal se normaliza en volumen. Las huellas se normalizan
   a longitud unitaria para comparar su distancia coseno.
4. **Agrupar voces:** agrupamiento jerárquico por distancia coseno promedio,
   con corte adaptado al mayor salto entre las distancias de fusión a partir
   de 0.6. No se fija el número de personas. Contextos menores de 1.2 s
   se asignan después a las voces de referencia.
5. **Asignar y sumar:** cada instante de voz se atribuye una sola vez, aunque
   las ventanas de análisis se solapen. Se numeran las etiquetas por primera
   aparición: `Hablante 1`, `Hablante 2`, etc.

Las distancias de fusión son las distancias promedio entre todas las parejas
de huellas de dos grupos. Si ninguna alcanza 0.6 se conserva un grupo; si hay
fusiones candidatas se corta antes de la que presente el mayor aumento de
distancia. El diagnóstico incluye ese salto y el corte elegido.

La red ERes2Net viene preentrenada; no se entrena con estos audios. Nuestra
integración, preparación de contextos, selección de referencias y reporte son
código propio. La extracción de huellas se ejecuta mediante la API de sherpa-onnx.

### Corrección de los dos M4A

La lectura M4A funcionaba: el error estaba en el análisis posterior. En
`Nueva grabación 7.m4a`, el VAD anterior fragmentaba demasiado la voz y dejaba
solo dos ventanas de referencia largas. En `audio8.m4a`, ninguna partición
superaba los filtros de silueta/separación y el código devolvía una sola voz.

Se sustituyó el motor predeterminado por ERes2Net y el conteo por agrupamiento
jerárquico. Se conservan frases a través de pausas cortas y se amplía el contexto.
Un corte absoluto sobredividía una variante de tono y una grabación repetida.
Por eso se busca el mayor salto entre fusiones: el punto donde unir grupos
empieza a juntar huellas mucho más distintas que en el paso anterior. Es una
heurística propia, no una garantía estadística de identidad.
La silueta se muestra como diagnóstico de separación, sin usarla para rechazar
cualquier partición y reducir automáticamente el resultado a una persona.
**Un solo grupo no confirma una sola persona**; el reporte ahora lo advierte.

Los parámetros son heurísticos, comunes para todos los archivos y elegidos
con estas grabaciones de desarrollo; no son una calibración independiente.
No se consultan los nombres de archivos para decidir el conteo. Tampoco se
introducen las cantidades esperadas en el análisis.

| Parámetro | Predeterminado | Efecto |
|---|---:|---|
| Agresividad de WebRTC VAD | 0 | Conserva más voz débil; también puede admitir más ruido |
| Pausa máxima en un contexto | 0.3 s | Evita fragmentar una frase por pausas pequeñas |
| Ventana / avance | 3.2 s / 0.8 s | Más contexto vocal, con menor resolución en cambios breves |
| Duración mínima de referencia | 1.2 s | Evita usar fonemas aislados como identidades |
| Distancia mínima de fusión candidata | 0.6 | Busca el mayor salto entre fusiones que alcancen esta distancia; no es un corte absoluto |
| Referencias máximas | 512 | Acota el coste del agrupamiento |

`max_speakers=None` no impone un máximo de cinco ni de dos. Cuando hay más de
512 referencias, se muestrean a lo largo del archivo; una intervención poco
frecuente puede quedar fuera. Todas las ventanas reciben etiqueta por lotes.
Se carga la señal completa en memoria: no es procesamiento en tiempo real.

### Instalación y uso

```bash
python3 -m pip install -r requerimientos.txt
python3 src/menu.py
```

Sin registro, token ni servicio de pago. En la primera ejecución con voz,
se descarga un modelo público de aproximadamente 25 MB desde GitHub a
`modelos/`. Se verifica su SHA-256 y se reutiliza sin red. **El audio nunca se
sube a Internet.** Esta copia del proyecto ya tiene el modelo preparado.
Los pesos no se incluyen en Git; al copiar solo el repositorio se descargarán
nuevamente. WebRTC VAD puede necesitar herramientas de compilación.

Modelo: `3dspeaker_speech_eres2net_sv_en_voxceleb_16k.onnx`.
SHA-256: `c59158379255ad66e161679cca6af8d52d51e389e3224ab7d7a7baae295c2db5`.
El archivo y la URL están definidos en `src/modelo_voz.py`; una descarga parcial
no se instala. Un error de descarga o dependencia se presenta desde el menú.

Desde Python, con `src` en la ruta de importación:

```python
from diarizacion import ejecutar_diarizacion

reporte = ejecutar_diarizacion("data/audio8.m4a")
print(reporte["hablantes_detectados"])
print(reporte["segmentos"])
print(reporte["advertencias"])
print(reporte["diagnostico_conteo"])

# Alternativa anterior, disponible para comparar; no es el motor del menú.
reporte_anterior = ejecutar_diarizacion("data/audio8.m4a", motor="resemblyzer")
```

`num_speakers` permite introducir un conteo conocido y `max_speakers` limitarlo;
las pruebas de conteo automático no usan ninguno. `agresividad_vad` acepta 0–3.
El motor `resemblyzer` conserva ventanas de 1.6 s y KMeans con selección por
silueta (mínima 0.25, margen 0.08 y separación entre centros 0.15). También
recibe la mejora de contextos y VAD. Los umbrales de ambos modelos pertenecen
a espacios distintos: **no son intercambiables**. `estimar_num_hablantes`
conserva el criterio anterior para huellas externas; la ruta predeterminada
completa es `ejecutar_diarizacion`.

### Referencias y para qué se utilizaron

| Repositorio | Aplicación en el proyecto |
|---|---|
| [modelscope/3D-Speaker](https://github.com/modelscope/3D-Speaker) | Modelo preentrenado ERes2Net de verificación de hablantes, empleado para extraer huellas vocales más separables. Proyecto con licencia Apache-2.0; no se copió su código fuente. |
| [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | Ejecución local del modelo ONNX mediante `SpeakerEmbeddingExtractor`. Se consultó su [ejemplo de identificación](https://github.com/k2-fsa/sherpa-onnx/blob/master/python-api-examples/speaker-identification.py). Los pesos públicos se obtienen de sus [releases de modelos](https://github.com/k2-fsa/sherpa-onnx/releases/tag/speaker-recongition-models). Proyecto Apache-2.0; integración propia mediante su API. |
| [resemble-ai/Resemblyzer](https://github.com/resemble-ai/Resemblyzer) | Modelo alternativo, conservado para comparar con el motor anterior. Se revisaron [audio.py](https://github.com/resemble-ai/Resemblyzer/blob/master/resemblyzer/audio.py) y [voice_encoder.py](https://github.com/resemble-ai/Resemblyzer/blob/master/resemblyzer/voice_encoder.py) para conservar la línea de tiempo y entender las ventanas. |
| [Demo de diarización de Resemblyzer](https://github.com/resemble-ai/Resemblyzer/blob/master/demo02_diarization.py) | Referencia para comparar huellas con perfiles de voz. El ejemplo original usa personas conocidas; nuestro conteo automático es una integración propia y no está resuelto por esa demo. |
| [wiseman/py-webrtcvad](https://github.com/wiseman/py-webrtcvad) | Detección de actividad vocal con marcos PCM de 16 bits, mono a 16 kHz y 30 ms. Se conservan intervalos, sin concatenar ni borrar silencios del archivo. |
| [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn) | [KMeans](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html) para agrupar huellas; [silhouette_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html) para comparar particiones; [AgglomerativeClustering](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.AgglomerativeClustering.html) con enlace promedio y distancia coseno para el nuevo motor principal. |
| [numpy/numpy](https://github.com/numpy/numpy) | Normalización, similitud entre huellas, selección de referencias y acumulación de tiempos. |
| [librosa/librosa](https://github.com/librosa/librosa) | Carga y remuestreo del audio. Las pruebas usan cambios de tono para comprobar el comportamiento ante una modificación controlada. |
| [bastibe/python-soundfile](https://github.com/bastibe/python-soundfile) | Lectura/escritura de archivos de audio y generación de copias temporales para pruebas. |
| [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) ([documentación](https://ffmpeg.org/ffmpeg.html)) | Decodificación de formatos que SoundFile no puede abrir directamente; selección de la primera pista de audio y conversión temporal a mono de 16 kHz. |
| [imageio/imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | Obtención del ejecutable de FFmpeg incluido en los paquetes para plataformas habituales, mediante `get_ffmpeg_exe()`. Evita requerir una cuenta o una instalación manual adicional de FFmpeg en esas plataformas. |

Se consultó también [wenet-e2e/wespeaker](https://github.com/wenet-e2e/wespeaker)
y su agrupador espectral durante las comparaciones; no se incorporó su modelo
ni se copió su algoritmo. Los experimentos CAM++ y segmentación adicional se
descartaron; no son dependencias del programa.

También se consultó [wq2012/SpectralCluster](https://github.com/wq2012/SpectralCluster)
como alternativa de agrupamiento, pero no se incorporó esa biblioteca ni se
copió su algoritmo. Los criterios, límites, selección de referencias y reporte
son propios; se usan las bibliotecas mediante sus APIs.

### Interpretación y límites

- No se infiere sexo o género. Las etiquetas distinguen voces en un archivo.
- No se separan dos personas hablando simultáneamente.
- Una persona que solo habla en fragmentos breves puede no quedar identificada.
- Silhouette es una medida de separación, **no una probabilidad de acierto**.
  Si la partición elegida tiene una puntuación menor de 0.35, se muestra una
  advertencia de separación débil y se recomienda revisar el resultado.
- `tiempo_silencio_seg` incluye todo el tiempo sin voz atribuida: también ruido
  y detecciones descartadas. Los porcentajes usan el total de voz atribuida.
- Los seis audios se usan para desarrollar esta corrección. Acertar en ellos
  no demuestra que se acierte en cualquier grabación futura; faltan audios
  independientes y anotaciones de turnos para evaluar DER/JER.

### Pruebas

```bash
python3 -B -m unittest discover -s tests -v
```

La batería comprueba el conteo sin indicar la cantidad al algoritmo en los
cuatro archivos. Los valores esperados fueron confirmados por el usuario:

| Archivo | Personas esperadas | Resultado automático |
|---|---:|---:|
| audio1.wav | 2 | 2 |
| audio2.ogg | 2 | 2 |
| audio3.wav | 1 | 1 |
| audio4.wav | 2 | 2 |
| Nueva grabación 7.m4a | Más de 2; cantidad exacta pendiente | 3 |
| audio8.m4a | Más de 2; cantidad exacta pendiente | 4 |

Los dos M4A adicionales tienen más de dos personas según el usuario. La prueba
comprueba ese límite inferior; **todavía falta confirmar el número exacto**.
No se utiliza la salida del modelo como si fuera una anotación verdadera.
**Verificación local: 30 pruebas pasaron en 100.4 segundos**, el 27 de
septiembre de 2026, incluyendo los seis audios, formatos, tono, pausas,
volumen y la grabación repetida de más de doce minutos. `audio8.m4a`
presenta separación débil (silueta 0.2884), por lo que sus cuatro grupos
requieren revisión. `audio2.ogg` también muestra esa advertencia (0.3425). Acertar el conteo no demuestra que cada turno esté bien
asignado; faltan anotaciones temporales para medir DER/JER.

También se prueban silencio, parámetros inválidos, conservación del tiempo,
pausas cortas que no deben contarse como voz, huellas sintéticas, muestreo de
referencias, descarga íntegra/reutilización local del modelo y variantes reales
de pausa, volumen y tono. Una copia temporal repite `audio1.wav` doce veces
(más de doce minutos): evalúa continuidad, no diversidad de una reunión real.
Los originales no se modifican.

### Formatos de audio

El menú acepta MP3, M4A, M4B, WAV, OGG, FLAC, AAC, Opus, AIFF, WMA, AMR,
CAF y otros formatos de audio habituales. Reconoce extensiones en mayúsculas
y nombres con espacios o acentos. La carpeta `data` se busca junto al proyecto,
aunque el programa se ejecute desde otra ubicación.

**Los formatos de video, incluido MP4, quedan fuera del alcance actual.**
El menú los oculta y `ejecutar_diarizacion` rechaza sus extensiones conocidas.

Para actualizar el lector:

```bash
python3 -m pip install -r requerimientos.txt
```

Se intenta primero la lectura directa con SoundFile. Si no puede abrir el
formato, se usa FFmpeg instalado en el sistema o el incluido en `imageio-ffmpeg`.
La conversión se realiza en una carpeta temporal que se elimina al terminar,
también si ocurre un error. El original conserva su nombre y su contenido.
En archivos de audio con varias pistas se analiza la primera.

La compatibilidad depende de los códecs disponibles: un archivo protegido,
corrupto o sin audio decodificable no se puede analizar por tener una extensión
válida. En esos casos el menú muestra el error y permite seleccionar otro
archivo sin cerrar el programa. No hay cuentas ni servicios de pago.

Las pruebas adicionales generan archivos reales MP3, M4A, AAC, FLAC, OGG,
Opus, AIFF y WMA; comprueban su lectura, mezcla a mono y duración. También
prueban una diarización completa en M4A, errores de lectura, limpieza temporal,
selección de archivos y exclusión de video.

## Página web local

La página permite seleccionar o arrastrar un audio desde el equipo, escucharlo
antes de analizarlo y pulsar **Diarizar audio**. Debajo se muestran el conteo
estimado, duración, tiempo de voz, participación por persona y turnos de habla.
Las advertencias del motor aparecen en **rojo**. El reporte completo se puede
descargar en JSON. La interfaz se adapta a pantallas pequeñas.

```bash
python3 -m pip install -r requerimientos.txt
cp .env.example .env  # Solo la primera vez; conserva tu .env si ya existe.
python3 src/servidor.py
```

Abre `http://127.0.0.1:8000`. Para detener el servidor, usa Ctrl+C en su terminal.
El menú anterior sigue disponible con `python3 src/menu.py`. No se modificó
`diarizacion.py` para incorporar la web: ambos accesos usan su misma función.

`.env` configura `APP_HOST` (127.0.0.1), `APP_PORT` (8000) y `MAX_AUDIO_MB`
(200). Reinicia el servidor después de cambiarlo. `.env` se excluye de Git;
`.env.example` documenta la configuración sin necesitar cuentas ni claves.
El servidor está pensado para uso local, con depuración desactivada.

Si prefieres aislar las dependencias, antes de instalarlas puedes ejecutar
`python3 -m venv .venv` y `source .venv/bin/activate` (macOS/Linux).

### Organización

```text
Proyecto_Diarizacion/
├── .env.example           # Ejemplo de configuración
├── requerimientos.txt     # Dependencias de audio y web
├── src/
│   ├── diarizacion.py     # Análisis existente, compartido por ambas interfaces
│   ├── modelo_voz.py      # Carga del modelo
│   ├── menu.py            # Menú de consola conservado
│   └── servidor.py        # Servidor Flask y API JSON
├── web/
│   ├── templates/index.html
│   └── static/
│       ├── styles.css
│       └── app.js
├── data/                  # Audios existentes, conservados
├── modelos/               # Pesos locales del modelo
└── tests/                 # Pruebas de audio, formatos, modelo y servidor
```

La API `POST /api/diarizar` recibe un formulario con el archivo en el campo
`audio` y devuelve el reporte JSON existente. En caso de error devuelve
`{"error": "mensaje"}` con un estado HTTP adecuado. Solo admite un análisis a
la vez para no ejecutar simultáneamente el modelo compartido. La interfaz
muestra el tiempo transcurrido, sin inventar un porcentaje de avance.

Las cargas se guardan en carpetas temporales y se eliminan incluso si falla
el análisis. No se escriben en `data/` ni se conservan historiales. Los nombres
del archivo se muestran como texto, sin interpretarlos como HTML. Los videos
siguen fuera del alcance. El reproductor depende de los formatos que soporte
el navegador; el análisis utiliza el lector de audio del proyecto.

### Fuentes de la interfaz

- [pallets/flask](https://github.com/pallets/flask): servidor y respuestas JSON.
  Se consultó su [documentación de cargas](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/)
  para recibir archivos y limitar el tamaño de las peticiones.
- [theskumar/python-dotenv](https://github.com/theskumar/python-dotenv): lectura
  de la configuración `.env` sin escribirla directamente en el servidor.
- HTML, CSS y JavaScript propios, sin plantillas copiadas, fuentes externas,
  bibliotecas de interfaz ni servicios de pago.

Pruebas del servidor: `python3 -B -m unittest discover -s tests -p test_servidor.py -v`.
Cubren carga, respuesta JSON, archivos vacíos/no admitidos, límite de tamaño,
errores del análisis, limpieza temporal y solicitudes simultáneas.

### Error `No module named 'pkg_resources'` en el entorno virtual

`webrtcvad` 2.0.10 todavía importa `pkg_resources`. El entorno con setuptools
84 no lo incluye; [setuptools lo retiró desde la versión 82](https://setuptools.pypa.io/en/latest/deprecated/pkg_resources.html).
Por compatibilidad, `requerimientos.txt` ahora declara `setuptools>=80.9,<81`.
Esta corrección no modifica el algoritmo ni `diarizacion.py`.

Con el entorno activado, actualiza las dependencias y vuelve a iniciar:

```bash
source .venv/bin/activate
python -m pip install -r requerimientos.txt
python src/servidor.py
```
