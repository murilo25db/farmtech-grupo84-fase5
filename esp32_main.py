"""Copie como main.py no ESP32 com MicroPython; veja conexões em IR_ALEM.md."""
import time
import network
import dht
from machine import Pin, ADC
try:
    import requests
except ImportError:
    import urequests as requests
from config import WIFI_SSID, WIFI_SENHA, API_URL, DISPOSITIVO, ADC_SECO, ADC_MOLHADO

sensor_ar = dht.DHT22(Pin(4))
# GPIO34 pertence ao ADC1: pode ser lido enquanto o Wi-Fi está ativo.
sensor_solo = ADC(Pin(34))
sensor_solo.atten(ADC.ATTN_11DB)
sensor_solo.width(ADC.WIDTH_12BIT)
wifi = network.WLAN(network.STA_IF)


def conectar_wifi():
    if wifi.isconnected():
        return
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_SENHA)
    inicio = time.ticks_ms()
    while not wifi.isconnected():
        if time.ticks_diff(time.ticks_ms(), inicio) > 20000:
            raise OSError('Wi-Fi não conectou em 20 segundos')
        time.sleep_ms(250)


def ler_solo():
    # Média curta reduz ruído; os dois extremos precisam ser calibrados no sensor real.
    leituras = []
    for _ in range(10):
        leituras.append(sensor_solo.read())
        time.sleep_ms(20)
    if ADC_SECO == ADC_MOLHADO:
        raise ValueError('Calibração inválida: extremos iguais')
    valor = sum(leituras) / len(leituras)
    percentual = 100 * (ADC_SECO - valor) / (ADC_SECO - ADC_MOLHADO)
    return max(0, min(100, percentual))


falhas = 0
while True:
    resposta = None
    try:
        conectar_wifi()
        sensor_ar.measure()
        leitura = {'dispositivo': DISPOSITIVO, 'temperatura': sensor_ar.temperature(),
                   'umidade_ar': sensor_ar.humidity(), 'umidade_solo': round(ler_solo(), 1),
                   'simulado': False}
        resposta = requests.post(API_URL + '/leituras', json=leitura, timeout=10)
        if resposta.status_code != 201:
            raise OSError('API retornou HTTP ' + str(resposta.status_code))
        print('Leitura enviada:', leitura)
        falhas = 0
    except (OSError, ValueError) as erro:
        falhas += 1
        print('Falha na coleta/envio:', erro)
    finally:
        if resposta is not None:
            resposta.close()
    # Em falhas, a espera aumenta até um minuto para não sobrecarregar a rede.
    time.sleep(min(60, 10 * max(1, falhas)))
