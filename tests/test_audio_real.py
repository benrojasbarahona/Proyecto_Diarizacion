"""Regresión con los cuatro audios y cantidades confirmadas por el usuario.

Pruebas reales, sin sustituir el modelo y sin pasar num_speakers=2.
Las variantes se generan en un directorio temporal; el original no se cambia.
"""
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import diarizacion as d


@unittest.skipUnless((ROOT / 'data/audio1.wav').exists(), 'Se necesita data/audio1.wav')
class AudioRealTests(unittest.TestCase):
    def comprobar(self, ruta, esperado=2):
        reporte = d.ejecutar_diarizacion(ruta)
        self.assertEqual(reporte['hablantes_detectados'], esperado)
        self.assertAlmostEqual(reporte['tiempo_total_voz_seg'] + reporte['tiempo_silencio_seg'],
                               reporte['duracion_total_archivo_seg'], delta=0.02)
        return reporte

    def test_cuatro_audios_cantidad_automatica(self):
        for archivo, esperado in [('audio1.wav', 2), ('audio2.ogg', 2),
                                  ('audio3.wav', 1), ('audio4.wav', 2)]:
            with self.subTest(archivo=archivo):
                self.comprobar(ROOT / 'data' / archivo, esperado)

    def test_m4a_con_mas_de_dos_personas(self):
        # El usuario confirmó >2, pero todavía no el número exacto.
        # No fijar 5/4 como referencia solo porque sea la salida del modelo.
        archivos = list((ROOT / 'data').glob('Nueva*.m4a'))
        archivos += list((ROOT / 'data').glob('audio8.m4a'))
        if len(archivos) != 2:
            self.skipTest('Se necesitan los dos nuevos M4A del usuario')
        for ruta in archivos:
            with self.subTest(archivo=ruta.name):
                reporte = d.ejecutar_diarizacion(ruta)
                self.assertGreater(reporte['hablantes_detectados'], 2)
                self.assertAlmostEqual(reporte['tiempo_total_voz_seg'] +
                    reporte['tiempo_silencio_seg'], reporte['duracion_total_archivo_seg'], delta=.02)

    def test_grabacion_larga_con_mismas_personas(self):
        wav, sr = d.librosa.load(ROOT / 'data/audio1.wav', sr=16000)
        # Más de doce minutos: repetir el audio no añade personas nuevas.
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / 'reunion_larga.wav'
            with sf.SoundFile(ruta, 'w', samplerate=sr, channels=1) as salida:
                for _ in range(12):
                    salida.write(wav)
            reporte = self.comprobar(ruta)
            self.assertLessEqual(reporte['diagnostico_conteo']['referencias_utilizadas'],
                                 d.MAX_REFERENCIAS)

    def test_pausas_volumen_y_tono(self):
        wav, sr = d.librosa.load(ROOT / 'data/audio1.wav', sr=16000)
        referencia = self.comprobar(ROOT / 'data/audio1.wav')
        variantes = {}
        # Cambios de volumen en distintos tramos, conservando las identidades.
        volumen = wav.copy()
        volumen[:20 * sr] *= 0.4
        volumen[40 * sr:] *= 0.6
        variantes['volumen'] = volumen
        # Una pausa artificial no debe crear ni reiniciar hablantes.
        variantes['pausa'] = np.concatenate([wav[:30 * sr], np.zeros(3 * sr), wav[30 * sr:]])
        # Cambio moderado de altura de voz en un tramo, manteniendo su duración.
        tono = wav.copy()
        tono[8 * sr:16 * sr] = d.librosa.effects.pitch_shift(
            wav[8 * sr:16 * sr], sr=sr, n_steps=2)
        variantes['tono'] = tono
        with tempfile.TemporaryDirectory() as tmp:
            for nombre, audio in variantes.items():
                with self.subTest(variante=nombre):
                    ruta = Path(tmp) / f'{nombre}.wav'
                    sf.write(ruta, audio, sr)
                    resultado = self.comprobar(ruta)
                    if nombre == 'tono':
                        # Mantener la identidad, además de acertar el conteo.
                        for segundo in (9, 11, 13, 15):
                            def voz_en(reporte):
                                return next(s['hablante'] for s in reporte['segmentos']
                                            if s['inicio'] <= segundo < s['fin'])
                            self.assertEqual(voz_en(resultado), voz_en(referencia))


if __name__ == '__main__':
    unittest.main()
