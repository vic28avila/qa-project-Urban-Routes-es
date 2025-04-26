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

    def click_first_order_button(self):
        first_order_button = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Pedir un taxi")]'))
        )
        self.driver.execute_script("arguments[0].click();", first_order_button)

    def select_comfort_tariff(self):
        button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-for="tariff-card-4"]'))
        )
        self.driver.execute_script("arguments[0].click();", button)

    def click_add_phone(self):
        add_phone_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'add-phone'))
        )
        self.driver.execute_script("arguments[0].click();", add_phone_button)

    def enter_phone(self, phone_number):
        phone_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'phone'))
        )
        phone_input.send_keys(phone_number)
        phone_input.send_keys(Keys.TAB)

    def click_add_card(self):
        add_card_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'add-card'))
        )
        self.driver.execute_script("arguments[0].click();", add_card_button)

    def add_credit_card(self, number, cvv):
        self.driver.find_element(By.ID, 'card-number').send_keys(number)
        cvv_input = self.driver.find_element(By.ID, 'code')
        cvv_input.send_keys(cvv)
        cvv_input.send_keys(Keys.TAB)
        link_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'link'))
        )
        self.driver.execute_script("arguments[0].click();", link_button)

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
        taxi_button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Pedir un taxi")]'))
        )
        self.driver.execute_script("arguments[0].click();", taxi_button)

class TestUrbanRoutes:
    driver = None

    @classmethod
    def setup_class(cls):
        from selenium.webdriver import ChromeOptions
        options = ChromeOptions()
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        cls.driver = webdriver.Chrome(options=options)

    def setup_method(self):
        self.driver.get(data.urban_routes_url)
        self.routes_page = UrbanRoutesPage(self.driver)

    def test_set_route(self):
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        assert data.address_from in self.driver.page_source
        assert data.address_to in self.driver.page_source

    def test_select_tariff(self):
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        self.routes_page.click_first_order_button()
        self.routes_page.select_comfort_tariff()
        assert "comfort" in self.driver.page_source.lower()

    def test_add_phone_and_enter_number(self):
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        self.routes_page.click_first_order_button()
        self.routes_page.select_comfort_tariff()
        self.routes_page.click_add_phone()
        self.routes_page.enter_phone(data.phone_number)
        assert "+" in self.driver.page_source

    def test_add_card_and_enter_details(self):
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        self.routes_page.click_first_order_button()
        self.routes_page.select_comfort_tariff()
        self.routes_page.click_add_phone()
        self.routes_page.enter_phone(data.phone_number)
        self.routes_page.click_add_card()
        self.routes_page.add_credit_card(data.card_number, data.card_code)
        assert "****" in self.driver.page_source or "1234" in self.driver.page_source

    def test_write_message(self):
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        self.routes_page.click_first_order_button()
        self.routes_page.select_comfort_tariff()
        self.routes_page.click_add_phone()
        self.routes_page.enter_phone(data.phone_number)
        self.routes_page.click_add_card()
        self.routes_page.add_credit_card(data.card_number, data.card_code)
        self.routes_page.write_message(data.message_for_driver)
        assert data.message_for_driver in self.driver.page_source

    def test_request_items(self):
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        self.routes_page.click_first_order_button()
        self.routes_page.select_comfort_tariff()
        self.routes_page.click_add_phone()
        self.routes_page.enter_phone(data.phone_number)
        self.routes_page.click_add_card()
        self.routes_page.add_credit_card(data.card_number, data.card_code)
        self.routes_page.write_message(data.message_for_driver)
        self.routes_page.request_items()
        assert "ice" in self.driver.page_source.lower()

    def test_request_taxi(self):
        self.routes_page.set_from(data.address_from)
        self.routes_page.set_to(data.address_to)
        self.routes_page.click_first_order_button()
        self.routes_page.select_comfort_tariff()
        self.routes_page.click_add_phone()
        self.routes_page.enter_phone(data.phone_number)
        self.routes_page.click_add_card()
        self.routes_page.add_credit_card(data.card_number, data.card_code)
        self.routes_page.write_message(data.message_for_driver)
        self.routes_page.request_items()
        self.routes_page.request_taxi()
        assert "conductor" in self.driver.page_source.lower() or "buscando" in self.driver.page_source.lower()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()