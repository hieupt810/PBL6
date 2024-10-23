from selenium.webdriver import ChromeOptions, Remote
from selenium.webdriver.common.by import By

from app.core.config import settings


class Driver:
    def __init__(self, max_length: int = 250) -> None:
        self.__max_length = max_length
        options = ChromeOptions()
        self.__driver = Remote(command_executor=settings.SELENIUM_URL, options=options)

    def open_new_tab(self, url: str):
        self.__driver.execute_script(f"window.open('{url}', '_blank');")
        self.__driver.switch_to.window(self.__driver.window_handles[-1])

    def close_current_tab(self):
        self.__driver.close()
        self.__driver.switch_to.window(self.__driver.window_handles[-1])

    def scroll_to_bottom(self):
        self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.__driver.implicitly_wait(2)

    def get(self, url: str):
        self.__driver.get(url)
        self.__driver.implicitly_wait(2)

    def find_by_css_selector(self, selector: str):
        while True:
            list_elements = self.__driver.find_elements(By.CSS_SELECTOR, selector)
            if len(list_elements) >= self.__max_length:
                break

            self.scroll_to_bottom()

        return self.__driver.find_elements(By.CSS_SELECTOR, selector)[
            : self.__max_length
        ]

    def find_one_by_css_selector(self, selector: str):
        return self.__driver.find_element(By.CSS_SELECTOR, selector)

    def close(self):
        self.__driver.close()
