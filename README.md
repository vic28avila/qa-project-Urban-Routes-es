# Proyecto QA: Urban Routes

Este proyecto automatiza el flujo completo de solicitud de un taxi en la aplicación **Urban Routes**, usando Selenium y Pytest.

## Descripción del flujo probado

Las pruebas cubren:

- Ingreso de direcciones de origen y destino
- Selección de tarifa (Comfort)
- Ingreso de número de teléfono (tras clic en “Agregar teléfono”)
- Ingreso de tarjeta de crédito (tras clic en “Agregar tarjeta”)
- Envío de mensaje al conductor
- Solicitud de manta, pañuelos y helados
- Solicitud final del taxi y validación de asignación de conductor

## Tecnologías utilizadas

- Python 3.10
- Selenium WebDriver
- Pytest
- ChromeDriver

## Cómo ejecutar las pruebas

1. Clona el repositorio
2. Instala dependencias:

   ```bash
   pip install -r requirements.txt
