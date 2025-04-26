# Proyecto QA Automatizado: Urban Routes

Este proyecto automatiza el flujo de solicitud de un taxi en la aplicación **Urban Routes**, utilizando **Python**, **Selenium WebDriver** y **Pytest**.

##  Descripción

Las pruebas cubren:

- Ingreso de direcciones de origen y destino.
- Selección de la tarifa Comfort.
- Ingreso del número de teléfono (tras hacer clic en "Agregar teléfono").
- Ingreso de tarjeta de crédito (tras hacer clic en "Agregar tarjeta").
- Escribir un mensaje para el conductor.
- Pedido de manta, pañuelos y dos helados.
- Solicitud final de taxi y verificación de asignación de conductor.

##  Tecnologías utilizadas

- Python 3.10
- Selenium WebDriver
- Pytest
- ChromeDriver

##  Cómo ejecutar las pruebas

1. Clona el repositorio:

   ```bash
   git clone git@github.com:vic28avila/qa-project-Urban-Routes-es.git

pip install -r requirements.txt
pytest main.py
