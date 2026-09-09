"""Verifica inferência, validação e persistência sem tocar no banco de uso real."""
import json
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
import api


class TesteFarmTech(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporario = tempfile.TemporaryDirectory()
        api.BANCO = Path(cls.temporario.name) / 'teste.db'
        cls.cliente = TestClient(api.app)
        cls.exemplo = json.loads((api.PASTA / 'exemplo_previsao.json').read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        cls.cliente.close()
        cls.temporario.cleanup()

    def test_previsao_reproduz_artefato(self):
        resposta = self.cliente.post('/prever', json=self.exemplo)
        self.assertEqual(resposta.status_code, 200)
        modelo, info = api.carregar_modelo()
        esperado = modelo.predict(api.pd.DataFrame([self.exemplo], columns=info['atributos']))[0]
        self.assertAlmostEqual(resposta.json()['rendimento_previsto'], esperado)
        self.assertFalse(resposta.json()['fora_da_amostra'])

    def test_rejeita_cultura_desconhecida(self):
        self.assertEqual(self.cliente.post('/prever', json={**self.exemplo, 'cultura': 'desconhecida'}).status_code, 422)

    def test_rejeita_umidade_invalida_e_campo_ausente(self):
        self.assertEqual(self.cliente.post('/prever', json={**self.exemplo, 'umidade_relativa': 101}).status_code, 422)
        incompleto = {k: v for k, v in self.exemplo.items() if k != 'chuva'}
        self.assertEqual(self.cliente.post('/prever', json=incompleto).status_code, 422)

    def test_avisa_extrapolacao(self):
        resposta = self.cliente.post('/prever', json={**self.exemplo, 'temperatura': 35})
        self.assertTrue(resposta.json()['fora_da_amostra'])

    def test_coleta_persiste_e_identifica_simulacao(self):
        leitura = {'dispositivo': 'teste-local', 'temperatura': 26, 'umidade_ar': 60,
                   'umidade_solo': 45, 'simulado': True}
        recebido = self.cliente.post('/leituras', json=leitura)
        self.assertEqual(recebido.status_code, 201)
        itens = self.cliente.get('/leituras?limite=1').json()
        self.assertEqual(itens[0]['id'], recebido.json()['id'])
        self.assertEqual(itens[0]['simulado'], 1)
        self.assertEqual(itens[0]['umidade_solo'], 45)

    def test_saude_nao_inventa_modelo(self):
        if (api.PASTA / 'modelo_saude.joblib').exists():
            self.skipTest('Já existe modelo real de saúde neste ambiente.')
        leitura = {'dispositivo': 'teste', 'temperatura': 26, 'umidade_ar': 60, 'umidade_solo': 45, 'simulado': True}
        self.assertEqual(self.cliente.post('/classificar-saude', json=leitura).status_code, 503)


if __name__ == '__main__':
    unittest.main(verbosity=2)
