import time

from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from app.core.config import settings
from app.logging import get_logger

logger = get_logger(__name__)


class Driver:
    def __init__(self, remote: bool = True, loading: int = 5) -> None:
        options = ChromeOptions()
        if remote:
            self._driver = Remote(
                command_executor=settings.SELENIUM_URL, options=options
            )
        else:
            self._driver = Chrome(options=options)

        self.loading = loading
        self._driver.maximize_window()

    def get(self, url: str) -> None:
        try:
            self._driver.get(url)
            time.sleep(self.loading)
            logger.info(f"Opened browser with URL: {url}")
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to get URL.")

    def close_current_tab(self) -> None:
        try:
            self._driver.close()
            self._driver.switch_to.window(self._driver.window_handles[-1])
            time.sleep(0.5)
            logger.info("Closed current tab.")
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to close current tab.")

    def open_link(self, url: str) -> None:
        try:
            self._driver.execute_script(f"window.open('{url}', '_blank');")
            self._driver.switch_to.window(self._driver.window_handles[-1])
            time.sleep(self.loading)
            logger.info(f"Opened link in new tab: {url}")
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to open link in new tab.")

    def quit(self) -> None:
        try:
            self._driver.quit()
            logger.info("Closed browser.")
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to close browser.")

    def scroll_to_bottom(self) -> None:
        try:
            self._driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(0.5)
            logger.info("Scrolled to the bottom of the page.")
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to scroll to the bottom of the page.")

    def click_link(self, selector: str) -> None:
        try:
            self.open_link(self.get_attribute(selector, "href"))
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to click link.")

    def click_button(self, selector: str) -> None:
        try:
            self._driver.find_element(By.CSS_SELECTOR, selector).click()
            time.sleep(0.5)
            logger.info("Clicked button.")
        except Exception as e:
            logger.error(e)
            raise Exception("Failed to click button.")

    def get_attribute(self, selector: str, attribute: str) -> str:
        try:
            element = self._driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute(attribute)
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to get attribute from element.")

    def get_text(self, selector: str) -> str:
        try:
            return self._driver.find_element(By.CSS_SELECTOR, selector).text
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to get text from element.")

    def get_html(self, selector: str) -> str:
        try:
            element = self._driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute("outerHTML")
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to get HTML from element.")

    def find_elements(self, selector: str) -> list[WebElement]:
        try:
            elements = self._driver.find_elements(By.CSS_SELECTOR, selector)
            print("Number of elements found:", len(elements))
            return elements
        except Exception as e:
            logger.error(e)
            raise RuntimeError("Failed to find elements.")
