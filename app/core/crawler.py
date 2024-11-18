import logging
import time

from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.common.by import By

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Driver:
    def __init__(
        self,
        max_length: int = 50,
        remote: bool = True,
        action_wait_second: int = 3,
        load_wait_second: int = 15,
    ) -> None:
        self._max_length = max_length
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
        self._driver.get(url)
        time.sleep(self._load_wait_second)

    def close_current_tab(self) -> None:
        self._driver.close()
        self._driver.switch_to.window(self._driver.window_handles[-1])
        logger.info(
            f"Closed current tab. Waiting for {self._action_wait_second} seconds..."
        )
        time.sleep(self._action_wait_second)

    def open_link(self, url: str) -> None:
        self._driver.execute_script(f"window.open('{url}', '_blank');")
        self._driver.switch_to.window(self._driver.window_handles[-1])
        logger.info(
            f"Opened link in a new tab. Waiting for {self._load_wait_second} seconds..."
        )
        time.sleep(self._load_wait_second)

    def quit(self) -> None:
        self._driver.quit()
        logger.info("Closed browser.")

    def scroll_to_bottom(self) -> None:
        self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.info(
            f"Scrolled to the bottom of the page. Waiting for {self._load_wait_second} seconds..."
        )
        time.sleep(self._action_wait_second)

    def click_link(self, selector: str) -> None:
        self.open_link(
            self._driver.find_element(By.CSS_SELECTOR, selector).get_attribute("href")
        )

    def click_button(self, selector: str) -> None:
        self._driver.find_element(By.CSS_SELECTOR, selector).click()
        logger.info(
            f"Clicked button. Waiting for {self._action_wait_second} seconds..."
        )
        time.sleep(self._action_wait_second)

    def get_text(self, selector: str) -> str:
        element = self._driver.find_element(By.CSS_SELECTOR, selector)
        if element:
            return element.text
        else:
            return ""

    def get_image(self, selector: str) -> str:
        element = self._driver.find_element(By.CSS_SELECTOR, selector)
        if element:
            return element.get_attribute("src")
        else:
            return ""

    def find_elements(self, selector: str):
        self.scroll_to_bottom()
        elements = self._driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            logger.info(f"Found {len(elements)} elements with selector.")
            return elements
        else:
            logger.info("No elements found with selector.")
            return []
