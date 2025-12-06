"""
====================================================================
 SISTEMA DE CONTROL DE ACCESO CON RASPBERRY PI PICO W
--------------------------------------------------------------------
Proyecto académico: Control de acceso tipo residencial utilizando
Raspberry Pi Pico W, sensor ultrasónico y control desde navegador
web en dispositivo móvil.

Autor: [Tu Nombre]
Repositorio: MCaccescontrol
Versión: 1.0
====================================================================

FUNCIONALIDADES
1. Control desde celular vía WiFi mediante servidor web integrado.
2. Lectura de distancia por sensor ultrasónico HC-SR04.
3. Control de LEDs para representar estados (abierto, cerrado, etc.).
4. Modo automático que abre/cierra según distancia detectada.
5. Página web con interfaz gráfica moderna.
6. Operación silenciosa sin saturación de consola.

NOTA IMPORTANTE
Antes de publicar en GitHub, modifica las credenciales WiFi en 
las variables WIFI_SSID y WIFI_PASSWORD. Nunca publiques datos 
reales de acceso a redes.
====================================================================
"""

from machine import Pin
import time
import network
import socket

# =============================================================
# CONFIGURACIÓN WIFI
# =============================================================

WIFI_SSID = "CAMBIAR"        # Modificar antes de publicar
WIFI_PASSWORD = "CAMBIAR"    # Modificar antes de publicar

# =============================================================
# HARDWARE
# =============================================================

# LEDs
LED_VERDE = Pin(3, Pin.OUT)     # GP3  Pin 5
LED_ROJO = Pin(4, Pin.OUT)      # GP4  Pin 6
LED_PICO = Pin("LED", Pin.OUT)  # LED interno de la Pico W

# Sensor ultrasónico
TRIG = Pin(0, Pin.OUT)          # GP0  Pin 1
ECHO = Pin(1, Pin.IN)           # GP1  Pin 2

# Variables de sistema
ip_address = "Sin conexión"
estado_sistema = "CERRADO"
modo_control = "auto"  # auto, manual, telefono
ultima_conexion = 0

# =============================================================
# FUNCIONES DEL SENSOR ULTRASÓNICO
# =============================================================

def medir_distancia():
    """
    Mide la distancia utilizando el sensor ultrasónico HC-SR04.
    Retorna la distancia en centímetros o -1 si ocurre un error.
    """
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    timeout = time.ticks_us() + 30000

    while ECHO.value() == 0:
        if time.ticks_us() > timeout:
            return -1
    inicio = time.ticks_us()

    while ECHO.value() == 1:
        if time.ticks_us() > timeout:
            return -1
    fin = time.ticks_us()

    distancia = (fin - inicio) * 0.0343 / 2
    return distancia if 2 < distancia < 400 else -1

# =============================================================
# CONTROL DE LEDS
# =============================================================

def actualizar_leds(estado):
    """
    Actualiza los LEDs dependiendo del estado del sistema.
    Estados posibles: cerrado, abierto, alerta, transicion.
    """
    if estado == "cerrado":
        LED_ROJO.value(1)
        LED_VERDE.value(0)
        LED_PICO.value(0)

    elif estado == "abierto":
        LED_ROJO.value(0)
        LED_VERDE.value(1)
        LED_PICO.value(1)

    elif estado == "alerta":
        toggle = time.ticks_ms() % 200 < 100
        LED_ROJO.value(toggle)
        LED_VERDE.value(0)

    elif estado == "transicion":
        toggle = time.ticks_ms() % 300 < 150
        LED_ROJO.value(1)
        LED_VERDE.value(toggle)

# =============================================================
# CONEXIÓN WIFI
# =============================================================

def conectar_wifi():
    """
    Conecta la Pico W a la red WiFi y retorna True si lo logra.
    """
    global ip_address

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(0.5)

    if wlan.isconnected():
        ip_address = wlan.ifconfig()[0]
        return True
    else:
        return False

# =============================================================
# INTERFAZ WEB
# =============================================================

def crear_pagina_principal():
    """
    Genera el código HTML de la página principal del sistema.
    """
    distancia = medir_distancia()

    # Estado del sensor
    if distancia < 0:
        estado_sensor = "ERROR"
        color_sensor = "#ff4444"
    elif distancia < 15:
        estado_sensor = f"AUTO: {distancia:.1f} cm"
        color_sensor = "#ffaa00"
    else:
        estado_sensor = f"LIBRE: {distancia:.1f} cm"
        color_sensor = "#44ff44"

    # Estado de LEDs
    if LED_ROJO.value() and LED_VERDE.value():
        estado_leds = "TRANSICION"
        color_leds = "#ffaa00"
    elif LED_ROJO.value():
        estado_leds = "CERRADO"
        color_leds = "#ff4444"
    elif LED_VERDE.value():
        estado_leds = "ABIERTO"
        color_leds = "#44ff44"
    else:
        estado_leds = "APAGADO"
        color_leds = "#666666"

    # HTML completo
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Acceso</title>
    <style>
        body {{
            font-family: Arial;
            background: #1a1a2e;
            color: white;
            text-align: center;
            padding: 20px;
        }}
        .container {{
            background: #16213e;
            padding: 20px;
            border-radius: 18px;
            box-shadow: 0 0 20px black;
            max-width: 360px;
            margin: auto;
        }}
        .status-box {{
            border-left: 5px solid {color_leds};
            background: #0f3460;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        .sensor-box {{
            border-left: 5px solid {color_sensor};
            background: #0f3460;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        button {{
            width: 100%;
            padding: 18px;
            border: none;
            border-radius: 12px;
            margin: 8px 0;
            font-size: 18px;
            cursor: pointer;
        }}
        .open {{ background: #4caf50; }}
        .close {{ background: #d32f2f; }}
        .auto  {{ background: #1976d2; }}
    </style>
</head>

<body>
    <div class="container">
        <h2>Sistema de Control de Acceso</h2>

        <div class="status-box">
            <h3>Estado Actual</h3>
            <p style="font-size: 26px;">{estado_leds}</p>
        </div>

        <div class="sensor-box">
            <h4>Sensor Ultrasónico</h4>
            <p style="font-size: 22px;">{estado_sensor}</p>
        </div>

        <button class="open" onclick="location.href='/abrir'">Abrir Acceso</button>
        <button class="close" onclick="location.href='/cerrar'">Cerrar Acceso</button>
        <button class="auto" onclick="location.href='/auto'">Modo Automático</button>

        <p style="margin-top: 20px; opacity: 0.7;">
            IP del Sistema: {ip_address}
        </p>
    </div>
</body>
</html>
"""

# =============================================================
# PETICIONES WEB
# =============================================================

def manejar_cliente(cliente):
    """
    Procesa solicitudes del navegador.
    """
    global modo_control, estado_sistema

    try:
        request = cliente.recv(1024)
        if not request:
            cliente.close()
            return

        request_str = request.decode()

        if "GET /abrir" in request_str:
            actualizar_leds("abierto")
            estado_sistema = "ABIERTO"
            modo_control = "telefono"
            respuesta = "Acceso abierto"

        elif "GET /cerrar" in request_str:
            actualizar_leds("cerrado")
            estado_sistema = "CERRADO"
            modo_control = "telefono"
            respuesta = "Acceso cerrado"

        elif "GET /auto" in request_str:
            modo_control = "auto"
            respuesta = "Modo automático activado"

        else:
            respuesta = crear_pagina_principal()

        cliente.send("HTTP/1.0 200 OK\r\n")
        cliente.send("Content-Type: text/html\r\n\r\n")
        cliente.sendall(respuesta.encode())

    except Exception as e:
        print("Error con cliente:", e)

    finally:
        cliente.close()

# =============================================================
# MODO AUTOMÁTICO
# =============================================================

def modo_automatico_silencioso():
    """
    Abre o cierra el acceso según la distancia detectada.
    """
    distancia = medir_distancia()

    if distancia > 0:
        if distancia < 15 and not LED_VERDE.value():
            actualizar_leds("transicion")
            time.sleep(1)
            actualizar_leds("abierto")
            return True

        elif distancia > 20 and not LED_ROJO.value():
            actualizar_leds("transicion")
            time.sleep(1)
            actualizar_leds("cerrado")
            return True

    return False

# =============================================================
# SERVIDOR WEB
# =============================================================

def iniciar_servidor_silencioso():
    """
    Inicia el servidor web principal.
    """
    global ip_address

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server = socket.socket()
    server.bind(addr)
    server.listen(1)
    server.settimeout(1)

    try:
        while True:
            try:
                cliente, _ = server.accept()
                manejar_cliente(cliente)
            except OSError:
                if modo_control == "auto":
                    modo_automatico_silencioso()

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Servidor detenido.")

# =============================================================
# PROGRAMA PRINCIPAL
# =============================================================

def main():
    actualizar_leds("cerrado")
    LED_PICO.value(1)
    time.sleep(1)

    if conectar_wifi():
        iniciar_servidor_silencioso()
    else:
        while True:
            modo_automatico_silencioso()
            time.sleep(0.5)

# =============================================================
# EJECUCIÓN
# =============================================================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error crítico:", e)
        time.sleep(3)
        import machine
        machine.reset()
