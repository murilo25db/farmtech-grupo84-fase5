"""API local da FarmTech. Inicie com: uvicorn api:app --host 127.0.0.1 --port 8000."""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import sqlite3

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

PASTA = Path(__file__).resolve().parent
BANCO = Path(os.getenv('FARMTECH_DB', str(PASTA / 'leituras.db')))
app = FastAPI(title='FarmTech Solutions', version='1.0', description='Previsão de rendimento e coleta experimental de sensores.')
modelo = None
metadados = None


class Previsao(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    cultura: str = Field(min_length=1, max_length=80)
    chuva: float = Field(ge=0)
    umidade_especifica: float = Field(ge=0)
    umidade_relativa: float = Field(ge=0, le=100)
    temperatura: float = Field(ge=-50, le=70)


class Leitura(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)
    dispositivo: str = Field(min_length=1, max_length=64)
    temperatura: float = Field(ge=-40, le=80)
    umidade_ar: float = Field(ge=0, le=100)
    umidade_solo: float = Field(ge=0, le=100)
    simulado: bool = False


def carregar_modelo():
    global modelo, metadados
    if modelo is None:
        arquivo = PASTA / 'modelo_rendimento.joblib'
        info = PASTA / 'modelo_metadados.json'
        if not arquivo.exists() or not info.exists():
            raise HTTPException(503, 'Execute o notebook para gerar o modelo e seus metadados.')
        # O joblib é um artefato local produzido pelo notebook deste projeto.
        modelo = joblib.load(arquivo)
        metadados = json.loads(info.read_text(encoding='utf-8'))
    return modelo, metadados


def conectar():
    con = sqlite3.connect(BANCO, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('''CREATE TABLE IF NOT EXISTS leituras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recebido_em TEXT NOT NULL, dispositivo TEXT NOT NULL,
        temperatura REAL NOT NULL, umidade_ar REAL NOT NULL,
        umidade_solo REAL NOT NULL, simulado INTEGER NOT NULL)''')
    return con


@app.get('/saude')
def saude():
    return {'status': 'ok', 'modelo_disponivel': (PASTA / 'modelo_rendimento.joblib').exists()}


@app.post('/prever')
def prever(entrada: Previsao):
    estimador, info = carregar_modelo()
    valores = entrada.model_dump()
    if valores['cultura'] not in info['culturas']:
        raise HTTPException(422, {'erro': 'Cultura não representada no treinamento.', 'culturas': info['culturas']})
    avisos = [f'{nome} fora da faixa observada [{faixa["min"]}, {faixa["max"]}].'
              for nome, faixa in info['faixas'].items()
              if not faixa['min'] <= valores[nome] <= faixa['max']]
    resultado = float(estimador.predict(pd.DataFrame([valores], columns=info['atributos']))[0])
    return {'rendimento_previsto': resultado, 'unidade': info['unidade_alvo'],
            'modelo': info['modelo'], 'fora_da_amostra': bool(avisos), 'avisos': avisos}


@app.post('/leituras', status_code=201)
def registrar(entrada: Leitura):
    recebido = datetime.now(timezone.utc).isoformat()
    # Parâmetros separados do SQL evitam interpretar o nome do dispositivo como comando.
    with conectar() as con:
        cursor = con.execute('''INSERT INTO leituras
            (recebido_em, dispositivo, temperatura, umidade_ar, umidade_solo, simulado)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (recebido, entrada.dispositivo, entrada.temperatura, entrada.umidade_ar,
             entrada.umidade_solo, int(entrada.simulado)))
        identificador = cursor.lastrowid
    return {'id': identificador, 'recebido_em': recebido, 'simulado': entrada.simulado}


@app.get('/leituras')
def listar(limite: int = 20):
    if not 1 <= limite <= 200:
        raise HTTPException(422, 'O limite precisa estar entre 1 e 200.')
    with conectar() as con:
        linhas = con.execute('SELECT * FROM leituras ORDER BY id DESC LIMIT ?', (limite,)).fetchall()
    return [dict(linha) for linha in linhas]


@app.post('/classificar-saude')
def classificar_saude(entrada: Leitura):
    arquivo = PASTA / 'modelo_saude.joblib'
    if not arquivo.exists():
        raise HTTPException(503, 'Modelo de saúde ainda não treinado com medições reais rotuladas. Consulte IR_ALEM.md.')
    # Esse modelo só é criado após coleta e rotulagem reais, separadas do CSV de rendimento.
    pacote = joblib.load(arquivo)
    valores = pd.DataFrame([entrada.model_dump()])[pacote['atributos']]
    classe = int(pacote['modelo'].predict(valores)[0])
    probabilidades = pacote['modelo'].predict_proba(valores)[0]
    classes = list(pacote['modelo'].classes_)
    return {'classe': 'Saudável' if classe == 1 else 'Não saudável',
            'probabilidade_saudavel': float(probabilidades[classes.index(1)]),
            'aviso': 'Resultado experimental; requer avaliação agronômica e acompanhamento.'}
