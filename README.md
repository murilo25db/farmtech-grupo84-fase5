# FarmTech Solutions — Grupo 84

**Murilo Dias Brandão · RM 573633**  
FIAP · Fase 5 — Machine Learning na cabeça · 08/09/2026

Este projeto investiga o rendimento de quatro culturas, compara cinco algoritmos de regressão e estima a infraestrutura AWS para uma API de inferência. O código busca manter o experimento simples de acompanhar e reproduzir.

## Entrega 1 — Machine Learning

**Comece pelo [notebook executado](MuriloDiasBrandao_rm573633_pbl_fase4.ipynb).** Ele contém a análise exploratória, agrupamentos, outliers, seleção dos modelos, avaliação e conclusões. A [versão HTML](relatorio_notebook.html) pode ser baixada e aberta no navegador. O sufixo `pbl_fase4` segue a nomenclatura exigida pelo enunciado da Fase 5.

O CSV tem 156 registros, quatro culturas e 39 perfis climáticos. A divisão e a validação mantêm cada perfil inteiro em uma única partição. A floresta aleatória foi escolhida pela validação cruzada. O notebook explica por que seu R² global alto não significa bom desempenho dentro de todas as culturas e confronta os modelos com uma referência baseada apenas na cultura.

Fonte do dataset: [assets disponibilizados na atividade](https://drive.google.com/drive/folders/1ey9Zjs7LUVRAAK_Fvy8oiGvHd6jPH-6p). O arquivo original está em `crop_yield.csv`, sem alterações. Seu hash e a ressalva sobre unidades constam no notebook. As previsões mantêm a escala original de `Yield`; não há conversão arbitrária para toneladas/hectare.

### Executar

Use Python 3.12, abra um terminal na pasta do projeto e crie um ambiente:

```bash
python -m venv .venv
```

Ative com `.venv\Scripts\activate` no Windows ou `source .venv/bin/activate` no Linux/macOS. Depois:

```bash
python -m pip install -r requirements.txt
python -m jupyterlab
```

Abra o notebook e execute todas as células. Para execução sem interface:

```bash
python executar_notebook.py
```

Os gráficos, tabelas CSV e o modelo exportado são gerados pelo próprio notebook. O modelo reajustado em todos os dados é para demonstração de inferência; as métricas do relatório foram calculadas antes desse reajuste.

### API de demonstração

```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

Abra [a documentação local](http://127.0.0.1:8000/docs). Em `POST /prever`, use o JSON de `exemplo_previsao.json`. A API rejeita campos inválidos e culturas não treinadas e informa quando os valores extrapolam as faixas observadas. Não exige AWS para funcionar.

```bash
python testar_api.py
```

Os testes verificam a previsão contra o artefato, os dados inválidos, o aviso de extrapolação, a persistência em SQLite e a indisponibilidade correta da classificação de saúde sem dados reais. O banco dos testes é temporário e separado das leituras de uso.

## Entrega 2 — comparação AWS

Cotação realizada em **08/09/2026**, em USD, na [AWS Pricing Calculator — estimativa salva](https://calculator.aws/#/estimate?id=73bd5ec2c477a08457b608772130b43e4c73ae4e). O link contém **duas alternativas**, não duas máquinas que devem ser contratadas juntas. O total de US$ 24,41 mostrado no cabeçalho da calculadora é a soma das alternativas; o custo para escolher uma região é o valor da linha correspondente.

### Configuração idêntica nas duas regiões

- Uma EC2 **t4g.micro**, Linux, tenancy compartilhada.
- **2 vCPUs, 1 GiB de RAM e rede de até 5 Gbps**.
- **On-Demand, 100% de uso, 730 horas/mês**, sem reserva, Savings Plans, Spot ou crédito de gratuidade.
- **50 GB de EBS Magnetic (previous generation)** para interpretar literalmente “HD”.
- Sem snapshots, monitoramento detalhado ou transferência de dados configurados, pois o enunciado não informa seus volumes.

A t4g.micro foi a opção de menor preço observada na calculadora entre as famílias compatíveis com os recursos pedidos. Usa arquitetura ARM/Graviton2. A t3.micro e a t3a.micro também atendem a CPU, RAM e rede, mas têm preço maior nas regiões consultadas. A compatibilidade ARM das dependências e o consumo de memória precisam ser validados antes de implantação. “Até 5 Gbps” é limite de rajada, não uma taxa contínua garantida. Consulte as [especificações oficiais de instâncias](https://aws.amazon.com/ec2/instance-types/general-purpose/).

| Item | Virgínia do Norte (`us-east-1`) | São Paulo (`sa-east-1`) |
|---|---:|---:|
| EC2 por hora | US$ 0,0084 | US$ 0,0134 |
| EC2 × 730 h | US$ 6,132 | US$ 9,782 |
| HD por GB/mês | US$ 0,05 | US$ 0,12 |
| HD de 50 GB | US$ 2,50 | US$ 6,00 |
| **Base mensal exibida** | **US$ 8,63** | **US$ 15,78** |
| 12 meses, como exibido na calculadora | US$ 103,56 | US$ 189,36 |

As contas sem arredondamento são `730 × 0,0084 + 50 × 0,05 = 8,632` e `730 × 0,0134 + 50 × 0,12 = 15,782`. A diferença é **US$ 7,15/mês**: São Paulo custa aproximadamente **82,8% a mais** nesse recorte. A coluna anual reproduz o arredondamento mensal da calculadora, sem pressupor compromisso de 12 meses.

![Comparação de custo mensal](custos_aws.png)

![Duas alternativas na calculadora AWS](aws_comparacao_calculadora.png)

Memórias de cálculo: [São Paulo](aws_sao_paulo_calculo.png) e [Virgínia](aws_virginia_calculo.png). Os números tabulados também estão em [custos_aws.csv](custos_aws.csv).

### A ressalva do HD e o custo completo

Os HDD atuais `st1` e `sc1` começam em 125 GiB e não servem como volume de boot. O magnético legado aceita 50 GB e é uma opção literal para a especificação, mas oferece desempenho inferior para pequenas operações aleatórias. A [documentação EBS](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html) distingue essas famílias e seus limites.

**O total acima é EC2 + capacidade de disco, não uma conta completa de produção.** O magnético tem cobrança por operações de I/O, que não foi acrescentada nesse formulário da calculadora. Sem quantidade de operações informada, não há como fechar esse adicional. Também ficam fora impostos, tráfego de saída, eventual IPv4 público, snapshots, suporte e créditos excedentes de CPU em modo Unlimited. Confira [preços EBS](https://aws.amazon.com/ebs/pricing/) e [premissas da calculadora](https://aws.amazon.com/calculator/calculator-assumptions/).

Para uso real da API, eu avaliaria **gp3 de 50 GB**: a mesma consulta retornou US$ 4,00/mês de disco na Virgínia e US$ 7,60 em São Paulo, levando os totais básicos a **US$ 10,13 e US$ 17,38**, respectivamente. Essa é uma alternativa SSD explicitamente diferente do HD pedido; as 3.000 IOPS e 125 MiB/s básicos do gp3 evitam a cobrança por operação do magnético. O acréscimo de capacidade de disco em São Paulo seria de US$ 1,60/mês. O cenário gp3 da Virgínia também foi [registrado](aws_virginia.png).

### Qual região escolher?

**A Virgínia é a mais barata; para o cenário com restrição de armazenamento no exterior, escolheria São Paulo.** A restrição é uma premissa do exercício, não uma afirmação de que toda legislação brasileira proíbe armazenamento fora do país. A opção brasileira mantém a região principal dos dados no Brasil e tende a reduzir a distância da fazenda à aplicação, embora a latência real dependa da operadora e deva ser medida.

A política precisaria abranger também backups, logs e réplicas, evitando cópias fora do território permitido. Se a conexão cair, uma fila local pode preservar as leituras até a retomada. O protótipo ESP32 atual registra falhas, mas ainda não implementa essa fila.

Uma instância de 1 GiB é pequena: treinaria os modelos fora dela e enviaria apenas o artefato para inferência, com um processo da API e teste de carga antes de uso. Não foram provisionados recursos nem geradas cobranças na AWS. A escolha definitiva entre HD legado e gp3 depende do perfil de I/O e da possibilidade de flexibilizar a exigência de armazenamento.

## Ir Além

O código e o guia dos dois extras estão em [IR_ALEM.md](IR_ALEM.md): ESP32 com DHT22 e sensor capacitivo, envio por Wi-Fi para SQLite e um pipeline de classificação da saúde do tomate. A arquitetura está ilustrada e os passos de montagem/calibração estão descritos.

**Limite da entrega dos extras:** a placa real, a coleta de campo e os rótulos de saúde dependem de execução humana. O classificador não foi treinado com dados fictícios. O serviço informa que ele está indisponível até existir um modelo treinado com medições reais.

## Vídeos

Os vídeos foram excluídos do escopo de execução automática solicitado. Os [roteiros de até cinco minutos](ROTEIROS_VIDEO.md) estão prontos para gravação.

| Vídeo exigido | Situação |
|---|---|
| Entrega 1 — notebook e funcionamento | Pendente de gravação humana e link não listado |
| Entrega 2 — calculadora e justificativa | Pendente de gravação humana e link não listado |
| Extras escolhidos | Dependem primeiro de montagem e validação real |

Sem esses links, os critérios de vídeo do barema permanecem incompletos. Após a entrega formal, respeitar a orientação do enunciado de não adicionar commits fora do prazo.
