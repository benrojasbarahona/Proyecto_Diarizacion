"""Modelo público ERes2Net de 3D-Speaker, ejecutado localmente con sherpa-onnx.

Procedencia y uso: README.md. Solo se descarga el modelo; nunca se envía audio.
"""
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import urllib.error
import urllib.request

import numpy as np

MODELO = "3dspeaker_speech_eres2net_sv_en_voxceleb_16k.onnx"
URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/" + MODELO
SHA256 = "c59158379255ad66e161679cca6af8d52d51e389e3224ab7d7a7baae295c2db5"
CARPETA = Path(__file__).resolve().parents[1] / "modelos"


def _verificar(ruta):
    with open(ruta, "rb") as archivo:
        return hashlib.file_digest(archivo, "sha256").hexdigest() == SHA256


def obtener_modelo():
    ruta = CARPETA / MODELO
    if ruta.is_file():
        if not _verificar(ruta):
            raise ValueError(f"Modelo dañado: elimina {ruta} para descargarlo nuevamente.")
        return ruta
    CARPETA.mkdir(parents=True, exist_ok=True)
    print("Descargando modelo de voz gratuito (25 MB, solo la primera vez)...", file=sys.stderr)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(dir=CARPETA, suffix=".part", delete=False) as salida:
            temporal = Path(salida.name)
            with urllib.request.urlopen(URL, timeout=60) as entrada:
                while bloque := entrada.read(1024 * 1024):
                    salida.write(bloque)
        if not _verificar(temporal):
            raise ValueError("La descarga del modelo está incompleta o no coincide con la versión esperada.")
        os.replace(temporal, ruta)
    except (OSError, urllib.error.URLError) as exc:
        raise ValueError("No se pudo descargar el modelo de voz. Conéctate a Internet para la primera ejecución; no necesitas cuenta ni token.") from exc
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)
    return ruta


class EncoderERes2Net:
    def __init__(self):
        try:
            import sherpa_onnx
        except ImportError as exc:
            raise ValueError("Falta sherpa-onnx. Ejecuta: python3 -m pip install -r requerimientos.txt") from exc
        self.extractor = sherpa_onnx.SpeakerEmbeddingExtractor(
            sherpa_onnx.SpeakerEmbeddingExtractorConfig(
                model=str(obtener_modelo()), num_threads=2))

    def embed_utterance(self, wav):
        flujo = self.extractor.create_stream()
        flujo.accept_waveform(16000, np.asarray(wav, dtype=np.float32))
        flujo.input_finished()
        if not self.extractor.is_ready(flujo):
            raise ValueError("El fragmento es demasiado breve para obtener una huella vocal.")
        return np.asarray(self.extractor.compute(flujo))
