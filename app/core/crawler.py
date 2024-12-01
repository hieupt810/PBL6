import time

from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.core.config import settings
from app.logger import get_logger

logger = get_logger(__name__)


class Driver:
    def __init__(
        self,
        remote: bool = True,
        action_wait: int = 2,
        load_wait: int = -1,
    ) -> None:
        self._action_wait = action_wait
        self._load_wait = load_wait if load_wait > 0 else action_wait * 3

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
            time.sleep(self._load_wait)
            logger.info(f"Successfully got URL: {url}")
        except Exception:
            raise Exception(f"Failed to get URL: {url}")

    def close_current_tab(self) -> None:
        try:
            self._driver.close()
            self._driver.switch_to.window(self._driver.window_handles[-1])
            time.sleep(self._action_wait)
            logger.info("Successfully closed current tab")
        except Exception as e:
            raise Exception("Failed to close current tab")

    def open_link(self, url: str) -> None:
        try:
            self._driver.execute_script(f"window.open('{url}', '_blank');")
            self._driver.switch_to.window(self._driver.window_handles[-1])
            time.sleep(self._load_wait)
            logger.info(f"Succesfully opened link: {url}")
        except Exception:
            raise Exception(f"Failed to open link in new tab: {url}")

    def quit(self) -> None:
        try:
            self._driver.quit()
            logger.info("Successfully closed browser")
        except Exception:
            logger.error("Failed to close browser")

    def scroll_to_bottom(self) -> None:
        try:
            self._driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(self._action_wait)
            logger.info("Successfully scrolled to the bottom of the page")
        except Exception:
            raise Exception("Failed to scroll to the bottom of the page")

    def click_link(self, selector: str) -> None:
        try:
            self.open_link(self.get_attribute(selector, "href"))
        except Exception:
            raise Exception("Failed to click link")

    def click_button(self, selector: str) -> None:
        try:
            self._driver.find_element(By.CSS_SELECTOR, selector).click()
            time.sleep(self._action_wait)
            logger.info("Successfully clicked button")
        except Exception:
            raise Exception("Failed to click button")

    def get_attribute(self, selector: str, attribute: str) -> str:
        try:
            element = self._driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute)
        except Exception:
            raise Exception("Failed to get attribute from element")

    def get_text(self, selector: str) -> str:
        try:
            return self._driver.find_element(By.CSS_SELECTOR, selector).text
        except Exception:
            raise Exception("Failed to get text from element")

    def find_elements(self, selector: str) -> list[WebElement]:
        self.scroll_to_bottom()
        try:
            elements = self._driver.find_elements(By.CSS_SELECTOR, selector)
            logger.info(f"Successfully found {len(elements)} elements")
            return elements
        except Exception:
            raise Exception("Failed to find elements")
