# Ir Além — sensores e saúde da plantação

O software dos dois extras está preparado. **Não houve conexão com um ESP32 físico nesta execução.** Os testes locais validam a API e os dados de teste são marcados como simulados. Montagem, calibração, coleta real, rotulagem agronômica e vídeo permanecem como etapas humanas. Não há métricas de campo inventadas.

## Opção 1 — coleta com dois sensores

Escolhi **DHT22** para temperatura e umidade relativa do ar, e um **sensor capacitivo de umidade do solo** para acompanhar a água disponível no canteiro. São dois sensores físicos diferentes; duas grandezas do DHT22, sozinhas, não seriam dois sensores. O capacitivo evita os eletrodos expostos comuns nos sensores resistivos, mas continua precisando de calibração para o solo usado.

O contexto é um canteiro experimental de tomate. O objetivo inicial é observar ambiente e solo ao longo do dia, sem acionar irrigação automaticamente. O ESP32 envia JSON por Wi-Fi para a API Python, que grava em SQLite e permite consultar as últimas leituras. Essa opção de servidor HTTP com SQLite atende ao serviço local permitido no enunciado e mantém o protótipo simples de reproduzir.

![Arquitetura do circuito e dados](arquitetura_iot.png)

### Ligações

| Componente | Terminal | ESP32 |
|---|---|---|
| DHT22 | VCC | 3V3 |
| DHT22 | GND | GND |
| DHT22 | DATA | GPIO4, com pull-up de 10 kΩ para 3V3 se o módulo não tiver |
| Capacitivo | VCC | 3V3, conferindo a tensão suportada pelo módulo |
| Capacitivo | GND | GND comum |
| Capacitivo | AOUT | GPIO34 (ADC1) |

Não aplique 5 V em uma entrada do ESP32. O GPIO34 pertence ao ADC1, adequado à leitura enquanto o Wi-Fi está em uso. O desenho é uma orientação de ligação, não uma evidência de montagem real.

### Colocar em funcionamento

1. Instale o firmware MicroPython adequado à placa ESP32 e confirme que `dht`, `network` e `requests` (ou `urequests`) estão disponíveis. Consulte a [referência oficial](https://docs.micropython.org/en/latest/esp32/quickref.html).
2. Na pasta do projeto, instale `requirements.txt` e execute `python -m uvicorn api:app --host 0.0.0.0 --port 8000` apenas na rede de laboratório. O PC e o ESP32 devem estar na mesma rede. O endereço `127.0.0.1` no ESP32 apontaria para a própria placa, não para o PC.
3. Copie `config.example.py` para `config.py` na placa e preencha SSID, senha, IP do PC e identificação do dispositivo. **Não envie `config.py` para o GitHub.**
4. Meça o ADC com o sensor na referência seca e na referência molhada e ajuste `ADC_SECO` e `ADC_MOLHADO`. Os valores fornecidos são exemplos, não uma calibração pronta.
5. Copie `esp32_main.py` para a placa com o nome `main.py`. O programa tenta reconectar o Wi-Fi, limita o tempo de espera e fecha as conexões HTTP. Falhas aumentam o intervalo até 60 s; leituras que falham não são armazenadas localmente para reenvio.
6. Observe as mensagens pela serial. Abra `http://IP_DO_PC:8000/docs`, consulte `GET /leituras` e confirme o mesmo dispositivo, valores e horário de recebimento no servidor. O arquivo `leituras.db` guarda os registros.
7. Desligue o roteador por alguns segundos, religue e confira a recuperação. Compare o DHT22 com uma referência e faça leituras de solo seco/úmido para registrar a calibração.

HTTP sem autenticação é limitado ao laboratório isolado. Para publicar na internet, adicionar HTTPS, autenticação dos dispositivos, controle de taxa, política de retenção e proteção do banco. Não é necessário contratar a AWS para demonstrar este protótipo.

**Rendimento e telemetria não são intercambiáveis:** o DHT22 não mede precipitação nem umidade específica, e a umidade do solo não substitui nenhuma dessas colunas. Por isso `/leituras` não inventa os atributos que faltam para `/prever`. A integração com o modelo de rendimento exige sensores adicionais, confirmação das unidades e agregação no mesmo período do dataset.

## Opção 2 — classificação da saúde

`treinar_saude.py` implementa um classificador para **tomate**, usando temperatura, umidade do ar e umidade do solo. O rótulo `saudavel` precisa vir de avaliação humana da planta: 1 para saudável, 0 para não saudável. Não rotulamos a saúde automaticamente com um limiar de umidade, pois isso apenas ensinaria o modelo a reproduzir a regra e não a condição da planta.

Use `coleta_saude_template.csv` com estas colunas:

| Campo | Preenchimento |
|---|---|
| data_hora | Momento real da coleta, ISO 8601 com fuso |
| planta_id | Identificador pseudônimo da planta |
| cultura | `tomate` |
| temperatura | °C medidos pelo DHT22 |
| umidade_ar | % medido pelo DHT22 |
| umidade_solo | % relativo aos extremos calibrados do sensor |
| saudavel | 0 ou 1, após inspeção humana e protocolo consistente |
| simulado | `False` para registros físicos reais |

O mínimo de 50 linhas em cinco dias é uma barreira inicial para evitar treinar com quase nenhum dado; **não comprova suficiência estatística**. Colete múltiplas plantas, dias e ambas as classes. Alinhe cada rótulo à planta e à janela da medição; dados de outra planta ou de outro dia não devem receber o mesmo rótulo por conveniência.

```bash
python treinar_saude.py coleta_real_rotulada.csv
```

O código reserva os últimos dias para teste, treina uma floresta com pesos balanceados, compara com a classe majoritária e exporta precisão, recall, F1, acurácia balanceada e matriz de confusão. Ele interrompe o treino se faltarem classes, dias, colunas ou se houver dados simulados. O modelo avaliado é salvo em `modelo_saude.joblib`, sem reajuste no teste.

Após o treinamento real, envie uma nova leitura a `POST /classificar-saude`. A resposta contém a classe e a probabilidade estimada. Essa probabilidade não foi calibrada e não deve ser interpretada como certeza clínica/agronômica. Sem artefato real, a API retorna 503 com uma mensagem explicativa; não usa um modelo fictício.

O teste temporal pode conter as mesmas plantas do treino. Ele avalia novos dias das plantas acompanhadas, e não generalização para novas fazendas ou plantas. Uma próxima rodada deve reservar plantas/talhões inteiros e uma safra posterior. Sensores ambientais sozinhos podem não detectar pragas, doenças ou deficiências nutricionais.

## Evidência que falta registrar em campo

- Foto legível da placa e das ligações.
- Valores de calibração e comparação com referência.
- Medições reais recebidas no SQLite e recuperação após queda de Wi-Fi.
- Para a opção 2: CSV real rotulado, métricas geradas e classificação de leituras posteriores ao treinamento.
- Vídeo não listado de até cinco minutos para cada opção escolhida.

O [roteiro de gravação](ROTEIROS_VIDEO.md) separa o que pode ser demonstrado agora do que depende dessas etapas.
