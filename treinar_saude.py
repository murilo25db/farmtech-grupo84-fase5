"""Treina o extra 2 com dados reais rotulados; não fabrica classes nem medições."""
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, balanced_accuracy_score
from sklearn.dummy import DummyClassifier

ATRIBUTOS = ['temperatura', 'umidade_ar', 'umidade_solo']


def treinar(arquivo, destino):
    dados = pd.read_csv(arquivo)
    obrigatorias = ['data_hora', 'planta_id', 'cultura', 'saudavel', 'simulado'] + ATRIBUTOS
    if not set(obrigatorias).issubset(dados.columns):
        raise ValueError('Colunas obrigatórias: ' + ', '.join(obrigatorias))
    if len(dados) < 50:
        raise ValueError('Colete pelo menos 50 observações reais antes do experimento.')
    if dados[obrigatorias].isna().any().any():
        raise ValueError('Existem campos ausentes; revise as medições e os rótulos.')
    if not dados.simulado.astype(str).str.lower().isin(['false', '0']).all():
        raise ValueError('O experimento de saúde aceita somente dados reais (simulado=False).')
    if set(dados.saudavel.unique()) != {0, 1}:
        raise ValueError('É necessário ter rótulos 0 e 1, atribuídos por avaliação humana.')
    if not np.isfinite(dados[ATRIBUTOS].to_numpy(dtype=float)).all():
        raise ValueError('Medições devem ser números finitos.')
    if dados.cultura.nunique() != 1:
        raise ValueError('Este experimento foi definido para uma única cultura: tomate.')
    if set(dados.cultura.str.lower().str.strip()) != {'tomate'}:
        raise ValueError('Use a cultura tomate, conforme o protocolo documentado.')
    if not dados.umidade_ar.between(0, 100).all() or not dados.umidade_solo.between(0, 100).all():
        raise ValueError('Umidades precisam estar entre 0 e 100%.')
    dados['data_hora'] = pd.to_datetime(dados.data_hora, utc=True, errors='raise')
    dados = dados.sort_values('data_hora')
    dias = dados.data_hora.dt.floor('D')
    dias_unicos = dias.drop_duplicates().sort_values()
    if len(dias_unicos) < 5:
        raise ValueError('Colete dados em pelo menos cinco dias distintos.')
    corte = dias_unicos.iloc[max(1, int(len(dias_unicos) * .8))]
    treino, teste = dados[dados.data_hora < corte], dados[dados.data_hora >= corte]
    if treino.saudavel.nunique() < 2 or teste.saudavel.nunique() < 2:
        raise ValueError('Treino e teste temporal precisam conter as duas classes; amplie a coleta.')
    modelo = RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_leaf=3,
                                    class_weight='balanced', random_state=42, n_jobs=1)
    modelo.fit(treino[ATRIBUTOS], treino.saudavel)
    pred = modelo.predict(teste[ATRIBUTOS])
    baseline = DummyClassifier(strategy='most_frequent').fit(treino[ATRIBUTOS], treino.saudavel)
    relatorio = {'corte_temporal_utc': corte.isoformat(), 'n_treino': len(treino), 'n_teste': len(teste),
                 'balanced_accuracy': balanced_accuracy_score(teste.saudavel, pred),
                 'baseline_balanced_accuracy': balanced_accuracy_score(teste.saudavel, baseline.predict(teste[ATRIBUTOS])),
                 'matriz_confusao_0_1': confusion_matrix(teste.saudavel, pred, labels=[0, 1]).tolist(),
                 'por_classe': classification_report(teste.saudavel, pred, output_dict=True, zero_division=0),
                 'limite': 'Validação em dias posteriores; mesmas plantas podem aparecer nas duas partes.'}
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    # Guardamos o modelo avaliado, sem reajustar no teste temporal.
    joblib.dump({'modelo': modelo, 'atributos': ATRIBUTOS, 'cultura': 'tomate'}, destino / 'modelo_saude.joblib')
    (destino / 'metricas_saude.json').write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', help='Arquivo de medições reais rotuladas conforme IR_ALEM.md')
    parser.add_argument('--destino', default='.')
    args = parser.parse_args()
    treinar(args.csv, args.destino)
