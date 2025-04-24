import data
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# no modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""

    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')

    def __init__(self, driver):
        self.driver = driver

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    def set_from(self, from_address):
        input_from = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.from_field))
        input_from.clear()
        input_from.send_keys(from_address)
        input_from.send_keys(Keys.TAB)

    def set_to(self, to_address):
        input_to = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.to_field))
        input_to.clear()
        input_to.send_keys(to_address)
        input_to.send_keys(Keys.TAB)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    def select_comfort_tariff(self):
        comfort_button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-for="tariff-card-4"]'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", comfort_button)
        self.driver.execute_script("arguments[0].click();", comfort_button)

    def click_add_phone(self):
        add_phone_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'add-phone'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", add_phone_button)
        add_phone_button.click()

    def add_credit_card(self, number, cvv):
        self.driver.find_element(By.ID, 'add-card').click()
        self.driver.find_element(By.ID, 'card-number').send_keys(number)

        cvv_input = self.driver.find_element(By.ID, 'code')
        cvv_input.send_keys(cvv)
        cvv_input.send_keys(Keys.TAB)

        link_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'link'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", link_button)
        link_button.click()

    def write_message(self, message):
        comment_input = self.driver.find_element(By.ID, 'comment')
        comment_input.send_keys(message)

    def request_items(self):
        self.driver.find_element(By.ID, 'blanket').click()
        self.driver.find_element(By.ID, 'tissues').click()
        ice_cream_input = self.driver.find_element(By.ID, 'ice-cream')
        ice_cream_input.clear()
        ice_cream_input.send_keys("2")

    def request_taxi(self):
        # Buscar el botón por su texto
        taxi_button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Pedir un taxi")]'))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", taxi_button)

        # Ejecutar el clic directamente vía JS
        self.driver.execute_script("arguments[0].click();", taxi_button)


class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # no lo modifiques, ya que necesitamos un registro adicional habilitado para recuperar el código de confirmación del teléfono
        from selenium.webdriver import ChromeOptions

        options = ChromeOptions()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        cls.driver = webdriver.Chrome(options=options)

    def test_set_route(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

    def test_full_taxi_order(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)

        # Paso 1: Establecer direcciones
        routes_page.set_from(data.address_from)
        routes_page.set_to(data.address_to)

        # Paso 2: Seleccionar tarifa Comfort
        routes_page.select_comfort_tariff()

        # Paso 3: Ingresar teléfono
        routes_page.enter_phone(data.phone_number)

        # Paso 4: Agregar tarjeta de crédito
        routes_page.add_credit_card(data.card_number, data.card_code)

        # Paso 5: Obtener código de verificación (si la app lo pide)
        code = retrieve_phone_code(self.driver)
        print(f"Código de verificación: {code}")
        code_input = self.driver.find_element(By.ID, 'code')
        code_input.send_keys(Keys.TAB)

        # Paso 6: Escribir mensaje al conductor
        routes_page.write_message(data.message_for_driver)

        # Paso 7: Pedir manta, pañuelos, y 2 helados
        routes_page.request_items()

        # Paso 8: Pedir taxi
        routes_page.request_taxi()

        # Paso 9: Esperar a que se muestre el bloque con el rating del conductor
        WebDriverWait(self.driver, 30).until(
            lambda d: "Tu conductor" in d.page_source or "4,9" in d.page_source
        )

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()
