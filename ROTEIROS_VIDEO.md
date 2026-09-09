# Roteiros para gravação

Não há links fictícios. Grave cada vídeo em até cinco minutos, envie ao YouTube como **não listado** e inclua o endereço na seção Vídeos do README antes da entrega formal.

## Vídeo 1 — Machine Learning (4min40s)

| Tempo | Mostrar e explicar |
|---|---|
| 0:00–0:25 | Apresentar Murilo Dias Brandão, Grupo 84, objetivo e repositório. |
| 0:25–1:00 | Abrir notebook executado, conferir CSV, 156 linhas, quatro culturas e ressalva de unidades. |
| 1:00–1:35 | Mostrar 39 cenários climáticos e divisão por grupos sem sobreposição. |
| 1:35–2:15 | Gráficos por cultura, correlações, três clusters e flags de outliers preservadas. |
| 2:15–3:10 | Tabela dos cinco algoritmos, MAE/RMSE/R² e escolha pela validação, sem escolher pelo teste. |
| 3:10–3:55 | Mostrar o teste e a média por cultura; explicar R² global alto e R² negativos em algumas culturas. |
| 3:55–4:25 | Demonstrar a API local em `/docs`, enviar `exemplo_previsao.json` e mostrar a previsão. |
| 4:25–4:40 | Concluir com limites da amostra e necessidade de validação em novas safras. |

Antes de gravar, deixe a API iniciada e o notebook aberto. Não tente executar toda a busca de modelos ao vivo se isso comprometer o tempo; mostre as células já executadas e explique o comando de reprodução.

## Vídeo 2 — AWS (4min30s)

| Tempo | Mostrar e explicar |
|---|---|
| 0:00–0:25 | Contexto: hospedar API de sensores e inferência. |
| 0:25–1:15 | Abrir link salvo da calculadora; duas regiões são alternativas. Mostrar t4g.micro, Linux, 2 vCPUs, 1 GiB e até 5 Gbps. |
| 1:15–2:00 | Mostrar On-Demand 100%, 730 h e 50 GB Magnetic; conta da Virgínia, US$ 8,63. |
| 2:00–2:40 | Mostrar mesma configuração em São Paulo, US$ 15,78, diferença US$ 7,15. |
| 2:40–3:20 | Explicar magnético legado, I/O não quantificado e alternativa SSD gp3. |
| 3:20–4:10 | Justificar São Paulo pela restrição do exercício, proximidade, dados e backups na região; latência exige medição. |
| 4:10–4:30 | Explicar limites de 1 GiB, inferência separada do treinamento e itens de custo não incluídos. |

## Extra 1 — somente após montagem física (4min30s)

Mostre os dois sensores e as ligações, explique a calibração, exiba a serial do ESP32 e o registro correspondente em `GET /leituras`. Interrompa e restaure o Wi-Fi para demonstrar recuperação. Mostre a figura e os arquivos no GitHub. Não exponha a senha de `config.py` na gravação.

## Extra 2 — somente após coleta e rotulagem reais (4min30s)

Apresente a cultura tomate e o protocolo de rótulos. Mostre o arquivo real, o corte temporal, as métricas e a matriz de confusão produzidas por `treinar_saude.py`. Colete uma leitura nova, envie para `/classificar-saude` e explique a classe retornada e a limitação dos sensores ambientais. Não substitua validação real por dados sintéticos.
