# Registro de validação — 08/09/2026

| Verificação | Resultado |
|---|---|
| Dataset oficial | 156 linhas, seis colunas, quatro culturas; zero ausentes e zero linhas inteiras duplicadas |
| Integridade | SHA-256 `07b3335f497e08e705b5835ee334426ac16cb24732c1bfaa994254d39f771b1b` |
| Separação | 31 grupos climáticos no treino, oito no teste; nenhuma sobreposição |
| Notebook | 14 células de código executadas, sem saída de erro |
| Algoritmos | Linear, árvore, floresta aleatória, gradient boosting e SVR |
| Seleção | Floresta aleatória escolhida pelo menor MAE em validação cruzada por grupos |
| Teste reservado | MAE 3.669,24; RMSE 5.172,42; R² 0,9944 na escala original de Yield |
| Comparação simples | Média por cultura: MAE 4.077,38 no teste; ganho relativo de MAE do modelo: 10,01% |
| Agrupamento | K-Means com três grupos; silhueta 0,3987 |
| Persistência do modelo | Artefato salvo e recarregado com previsões equivalentes |
| API | Seis testes passaram: inferência, extrapolação, cultura desconhecida, campos inválidos/ausentes, SQLite e falta do modelo de saúde |
| Arquivos | Sintaxe Python e referências locais da documentação verificadas |
| Gráficos | Inspeção visual; rótulos de correlação ajustados para leitura |
| AWS | Duas regiões cotadas na calculadora; link salvo e capturas incluídos |

Os testes da API usam leituras sintéticas identificadas e banco temporário; não constituem coleta física. O programa do ESP32 foi verificado em sintaxe, mas não executado em placa. O classificador de saúde está implementado e aguarda medições reais rotuladas para treinamento e validação. Os vídeos exigidos permanecem a cargo de uma pessoa, conforme o escopo solicitado.

O R² global não deve ser lido isoladamente: há R² negativos em cacau e palma no teste. O relatório mantém essa limitação e não afirma prontidão de produção ou garantia de nota.
