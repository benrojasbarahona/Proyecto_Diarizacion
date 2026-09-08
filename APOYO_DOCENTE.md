# Retroalimentación inicial — proyecto de diarización

Esta rama contiene una revisión exploratoria del prototipo actual, realizada sin modificar la rama `main`.

## Hallazgos principales

### 1. Reproducibilidad

La implementación utiliza `resemblyzer`, pero esta dependencia no aparece actualmente en `requerimientos.txt`. En el entorno de prueba también fue necesario usar `setuptools<82` debido a una dependencia de `webrtcvad` sobre `pkg_resources`.

### 2. Pipeline observado

Audio → `preprocess_wav()` → Resemblyzer/VoiceEncoder → embeddings parciales → selección de k mediante silhouette score → Spectral Clustering → resumen por cluster.

### 3. Duración original y preprocesada

Para `audio1.wav`:

- duración original: 62.392 s
- duración después de `preprocess_wav()`: 56.310 s

El preprocesamiento aplica VAD y elimina regiones de la señal. Por tanto, la duración preprocesada no corresponde directamente a la duración del archivo original ni necesariamente al tiempo efectivo de habla.

### 4. Interpretación de los porcentajes

Para `audio1.wav` se obtuvieron 83 embeddings:

- 25 embeddings → cluster 1 = 30.1 %
- 58 embeddings → cluster 2 = 69.9 %

Los porcentajes actuales representan principalmente la proporción de embeddings asignados a cada cluster, no tiempo de habla demostrado.

> El nombre de una variable expresa la interpretación que queremos darle; la matemática del algoritmo determina qué está midiendo realmente.

### 5. Geometría temporal

Con `rate=1.5`, Resemblyzer produjo ventanas de aproximadamente 1.6 s separadas unos 0.67 s, por lo que existe solapamiento entre ventanas. Los `wav_splits` contienen la geometría temporal real de los embeddings.

### 6. Reloj original

Como el VAD elimina muestras, el reloj de la señal preprocesada difiere del reloj original. Por ejemplo:

- 17.215 s preprocesados ≈ 18.055 s del archivo original.

El desfase cambia a lo largo del audio.

### 7. Número de clusters

Para `audio1.wav`:

- k=2: silhouette = 0.4923
- k=3: silhouette = 0.2644
- k=4: silhouette = 0.2492
- k=5: silhouette = 0.1381

El criterio interno favorece k=2. Sin embargo, la escucha permitió percibir al menos tres speakers en la primera parte del archivo.

Al forzar k=3, las primeras fronteras aparecieron cerca de 18.160 s y 22.405 s y coincidieron razonablemente con cambios perceptibles de speaker. Más adelante aparecieron cambios de cluster sin cambio perceptible de speaker.

Por tanto:

`cambio de cluster ≠ necesariamente cambio de speaker`

Silhouette score evalúa la geometría de los embeddings, no directamente la calidad de diarización.

## Próximos pasos sugeridos

1. completar y fijar el entorno reproducible;
2. conservar explícitamente `wav_splits` y el reloj original;
3. distinguir duración original, duración preprocesada y tiempo efectivo de habla;
4. construir un pequeño ground truth manual;
5. evaluar contra esa referencia;
6. incorporar posteriormente métricas propias de diarización, como DER/JER.

El prototipo actual constituye una base interesante para avanzar desde embeddings y clustering hacia una diarización temporal evaluable.
