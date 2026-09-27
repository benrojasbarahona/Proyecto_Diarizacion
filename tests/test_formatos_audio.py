"""Pruebas de decodificación real y de selección en el menú, sin video."""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import diarizacion as d
import menu


class FormatosAudioTests(unittest.TestCase):
    def convertir(self, origen, destino, codec):
        subprocess.run([d._ffmpeg(), '-nostdin', '-hide_banner', '-loglevel', 'error',
                        '-i', str(origen), '-c:a', codec, '-y', str(destino)],
                       check=True, capture_output=True)

    def test_decodificacion_formatos_reales(self):
        # Dos canales distintos permiten comprobar también la mezcla mono.
        sr = 44100
        t = np.arange(sr) / sr
        stereo = np.stack([0.1 * np.sin(2 * np.pi * 220 * t),
                           0.1 * np.sin(2 * np.pi * 440 * t)], axis=1)
        formatos = [('mp3', 'libmp3lame'), ('m4a', 'aac'), ('aac', 'aac'),
                    ('flac', 'flac'), ('ogg', 'libvorbis'), ('opus', 'libopus'),
                    ('aiff', 'pcm_s16be'), ('wma', 'wmav2')]
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / 'original.wav'
            sf.write(original, stereo, sr)
            for extension, codec in formatos:
                with self.subTest(formato=extension):
                    destino = Path(tmp) / f'grabación con espacios.{extension.upper()}'
                    self.convertir(original, destino, codec)
                    wav = d._cargar_audio(destino)
                    self.assertEqual(wav.ndim, 1)
                    self.assertEqual(wav.dtype, np.float32)
                    self.assertTrue(np.isfinite(wav).all())
                    self.assertGreater(np.max(np.abs(wav)), 0.01)
                    self.assertAlmostEqual(len(wav) / d.SAMPLE_RATE, 1, delta=0.15)
            self.assertEqual(sf.info(original).samplerate, sr)

    def test_diarizacion_m4a_real(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / 'entrevista.m4a'
            self.convertir(ROOT / 'data/audio1.wav', destino, 'aac')
            reporte = d.ejecutar_diarizacion(destino)
            self.assertEqual(reporte['nombre_archivo'], 'entrevista.m4a')
            self.assertEqual(reporte['hablantes_detectados'], 2)
            self.assertAlmostEqual(reporte['duracion_total_archivo_seg'], 62.39, delta=0.15)

    def test_archivo_invalido_da_error_legible(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / 'roto.m4a'
            destino.write_text('esto no es audio')
            with self.assertRaisesRegex(d.ErrorAudio, 'No se pudo leer'):
                d._cargar_audio(destino)

    def test_video_no_se_procesa(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = Path(tmp) / 'video.MP4'
            destino.touch()
            with patch.object(d, '_ffmpeg') as ffmpeg:
                with self.assertRaisesRegex(d.ErrorAudio, 'no formatos de video'):
                    d._cargar_audio(destino)
            ffmpeg.assert_not_called()

    def test_menu_filtra_y_ordena_sin_depender_de_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            for nombre in ['B.M4A', 'a.mp3', 'c.FLAC', 'video.mp4', 'notas.txt', '.oculto.wav']:
                (carpeta / nombre).touch()
            (carpeta / 'carpeta.wav').mkdir()
            with patch.object(menu, 'DATA_DIR', carpeta):
                self.assertEqual(menu.listar_audios(), ['a.mp3', 'B.M4A', 'c.FLAC'])
        self.assertEqual(menu.DATA_DIR, ROOT / 'data')

    def test_menu_se_recupera_de_archivo_invalido(self):
        salida = io.StringIO()
        with patch.object(menu, 'ejecutar_diarizacion', side_effect=d.ErrorAudio('Archivo dañado')):
            with contextlib.redirect_stdout(salida):
                self.assertFalse(menu.procesar_archivo('roto.m4a'))
        self.assertIn('Archivo dañado', salida.getvalue())

    def test_temporal_se_elimina_aunque_conversion_falle(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / 'incorrecto.m4a'
            ruta.touch()
            temporales = []
            def fallar(comando, **kwargs):
                temporales.append(Path(comando[-1]).parent)
                return subprocess.CompletedProcess(comando, 1, '', 'invalid data')
            with patch.object(d.subprocess, 'run', side_effect=fallar):
                with self.assertRaises(d.ErrorAudio):
                    d._cargar_audio(ruta)
            self.assertTrue(temporales)
            self.assertTrue(all(not p.exists() for p in temporales))


if __name__ == '__main__':
    unittest.main()
