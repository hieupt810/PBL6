import logging
import time

from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Driver:
    def __init__(
        self,
        remote: bool = True,
        action_wait_second: int = 3,
        load_wait_second: int = 10,
    ) -> None:
        self._action_wait_second = action_wait_second
        self._load_wait_second = load_wait_second

        options = ChromeOptions()
        if remote:
            self._driver = Remote(
                command_executor=settings.SELENIUM_URL, options=options
            )
        else:
            self._driver = Chrome(options=options)
            self._driver.maximize_window()

    def get(self, url: str) -> None:
        try:
            self._driver.get(url)
            time.sleep(self._load_wait_second)
        except Exception:
            raise Exception(f"Error while getting URL.")

    def close_current_tab(self) -> None:
        try:
            self._driver.close()
            self._driver.switch_to.window(self._driver.window_handles[-1])
            logger.info(
                f"Closed current tab. Waiting for {self._action_wait_second} seconds..."
            )
            time.sleep(self._action_wait_second)
        except Exception:
            raise Exception("Error while closing current tab.")

    def open_link(self, url: str) -> None:
        try:
            self._driver.execute_script(f"window.open('{url}', '_blank');")
            self._driver.switch_to.window(self._driver.window_handles[-1])
            logger.info(
                f"Opened link in a new tab. Waiting for {self._load_wait_second} seconds..."
            )
            time.sleep(self._load_wait_second)
        except Exception:
            raise Exception("Error while opening link.")

    def quit(self) -> None:
        try:
            self._driver.quit()
            logger.info("Closed browser.")
        except Exception:
            logger.error("Error while closing browser.")

    def scroll_to_bottom(self) -> None:
        try:
            self._driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            logger.info(
                f"Scrolled to the bottom of the page. Waiting for {self._load_wait_second} seconds..."
            )
            time.sleep(self._action_wait_second)
        except Exception:
            raise Exception("Error while scrolling to the bottom of the page.")

    def click_link(self, selector: str) -> None:
        try:
            self.open_link(self.get_attribute(selector, "href"))
        except Exception:
            raise Exception("Error while clicking link.")

    def click_button(self, selector: str) -> None:
        try:
            self._driver.find_element(By.CSS_SELECTOR, selector).click()
            logger.info(
                f"Clicked button. Waiting for {self._action_wait_second} seconds..."
            )
            time.sleep(self._action_wait_second)
        except Exception:
            raise Exception("Error while clicking button.")

    def get_attribute(self, selector: str, attribute: str) -> str:
        try:
            element = self._driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute)
        except Exception:
            raise Exception("Error while getting attribute from element.")

    def get_text(self, selector: str) -> str:
        try:
            return self._driver.find_element(By.CSS_SELECTOR, selector).text
        except Exception:
            raise Exception("Error while getting text from element.")

    def find_elements(self, selector: str) -> list[WebElement]:
        self.scroll_to_bottom()
        try:
            elements = self._driver.find_elements(By.CSS_SELECTOR, selector)
            logger.info(f"Found {len(elements)} elements with selector.")
            return elements
        except Exception:
            raise Exception("Error while finding elements.")
