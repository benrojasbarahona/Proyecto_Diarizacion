import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import modelo_voz as m


class ModeloTests(unittest.TestCase):
    def test_descarga_verificada_y_reutilizacion_sin_red(self):
        contenido = b'modelo de prueba'
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(m, 'CARPETA', Path(tmp)), \
                patch.object(m, 'SHA256', hashlib.sha256(contenido).hexdigest()), \
                patch.object(m.urllib.request, 'urlopen', return_value=io.BytesIO(contenido)) as red:
            ruta = m.obtener_modelo()
            self.assertEqual(ruta.read_bytes(), contenido)
            self.assertEqual(m.obtener_modelo(), ruta)
            red.assert_called_once()

    def test_descarga_incompleta_no_se_instala(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(m, 'CARPETA', Path(tmp)), \
                patch.object(m.urllib.request, 'urlopen', return_value=io.BytesIO(b'incompleto')):
            with self.assertRaises(ValueError):
                m.obtener_modelo()
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_modelo_danado_no_se_carga(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CARPETA', Path(tmp)):
            (Path(tmp) / m.MODELO).write_bytes(b'incompleto')
            with self.assertRaises(ValueError):
                m.obtener_modelo()
