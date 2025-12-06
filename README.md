# Sistema de Control de Acceso con Raspberry Pi Pico W  
Proyecto final – Microcontroladores | UCQ

---

## Descripción General
Este proyecto implementa un **sistema de control de acceso tipo residencial** utilizando una **Raspberry Pi Pico W**, un **sensor ultrasónico HC-SR04** y control remoto a través de **WiFi** mediante una interfaz web accesible desde cualquier dispositivo móvil.

El sistema permite:
- Apertura y cierre del acceso desde navegador móvil.
- Modo automático basado en detección de distancia.
- Indicadores visuales mediante LEDs.
- Lectura continua del entorno usando el sensor ultrasónico.
- Operación silenciosa para evitar saturar la consola.

---

## Características Principales

### 1. Control desde dispositivo móvil
Un servidor web corre directamente en la Pico W, permitiendo:
- Abrir el acceso
- Cerrar el acceso
- Activar modo automático

Todo desde una página web moderna y responsive.

### 2. Detección de vehículos
El sensor ultrasónico detecta objetos cercanos (como un auto o maqueta Hot Wheels) y actúa según la distancia:
- Menos de 15 cm: abrir acceso
- Más de 20 cm: cerrar acceso

### 3. Indicadores LED
- **Rojo:** acceso cerrado  
- **Verde:** acceso abierto  
- **Transición:** parpadeo  
- **LED interno:** actividad del sistema  

### 4. Operación silenciosa
El sistema evita imprimir información innecesaria para garantizar un funcionamiento estable de largo plazo.

---

## Componentes Utilizados

| Componente | Descripción |
|-----------|-------------|
| Raspberry Pi Pico W | Microcontrolador con WiFi integrado |
| Sensor ultrasónico HC-SR04 | Medición de distancia |
| LED Rojo | Indica estado de cierre |
| LED Verde | Indica estado de apertura |
| LED interno | Indica actividad de sistema |
| Resistencias 220 Ω | Para los LEDs |
| Cables Dupont | Conexión de pines |
| Fuente 5V USB | Alimentación de la Pico W |

---

## Conexiones del Hardware

### Sensor ultrasónico
| Componente | Pin Pico W |
|-----------|-------------|
| TRIG | GP0 |
| ECHO | GP1 |

### LEDs
| LED | Pin Pico W |
|-----|-------------|
| Rojo | GP4 |
| Verde | GP3 |
| LED Pico | Pin interno |

---

## Cómo Ejecutarlo en la Raspberry Pi Pico W

1. Instalar **MicroPython** en la Pico W.  
2. Conectar la Pico a la PC vía USB.  
3. Abrir **Thonny** y seleccionar:
   - Interpreter → Raspberry Pi Pico W
4. Cargar el archivo `main.py` en la Pico W.
5. Modificar credenciales WiFi en el código:
   ```python
   WIFI_SSID = "TU_RED"
   WIFI_PASSWORD = "TU_PASSWORD"
